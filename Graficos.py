from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
import os
import webbrowser
from datetime import datetime, timedelta

# Caminho base
caminho_base = os.path.dirname(os.path.abspath(__file__))
caminho_graficos = os.path.join(caminho_base, 'graficos')
os.makedirs(caminho_graficos, exist_ok=True)

# Conexão Oracle
engine = create_engine('oracle+cx_oracle://RM567800:fiap25@oracle.fiap.com.br:1521/?service_name=ORCL')

# Entrada de data
data_input = input("Digite a data inicial (formato DD/MM/AA): ").strip()
try:
    data_inicio = datetime.strptime(data_input, "%d/%m/%y")
    data_fim = data_inicio + timedelta(days=7)
except ValueError:
    print("❌ Formato inválido. Use DD/MM/AA.")
    exit()

# Consulta dados de irrigação
query_irrigacao = '''
SELECT IRRIGACAO, DATA, UMIDADE_PERCENT, PH, FOSFORO, POTASSIO, NITROGENIO
FROM dados_irrigacao
'''
df = pd.read_sql(query_irrigacao, engine)
df.columns = [col.upper() for col in df.columns]
df['DATA'] = pd.to_datetime(df['DATA'], format="%d/%m/%y", errors='coerce')
df = df.dropna(subset=['DATA'])

# Filtro por intervalo
df_periodo = df[(df['DATA'] >= data_inicio) & (df['DATA'] <= data_fim)]
if df_periodo.empty:
    print(f"⚠️ Nenhum dado entre {data_inicio.strftime('%d/%m/%Y')} e {data_fim.strftime('%d/%m/%Y')}. Usando todos os dados.")
    df_periodo = df.copy()
else:
    print(f"✅ Analisando dados de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}.")

# Cálculo das médias
media_ph = df[df['DATA'] == data_inicio]['PH'].mean()

media_fosforo = round(df_periodo['FOSFORO'].mean())
media_potassio = round(df_periodo['POTASSIO'].mean())
media_nitrogenio = round(df_periodo['NITROGENIO'].mean())

# Consulta perfil de culturas
query_culturas = 'SELECT * FROM PERFIL_CULTURAS'
culturas = pd.read_sql(query_culturas, engine)
culturas.columns = [col.upper() for col in culturas.columns]

# Avaliação de compatibilidade
resultados = []
for _, row in culturas.iterrows():
    score = 0
    motivos = []

    if row['PH_MINIMO'] <= media_ph <= row['PH_MAXIMO']:
        score += 1
    else:
        motivos.append(f"pH fora do ideal ({media_ph:.1f})")

    if row['FOSFORO_IDEAL'] == media_fosforo:
        score += 1
    else:
        motivos.append(f"fósforo esperado: {row['FOSFORO_IDEAL']}, encontrado: {media_fosforo}")

    if row['POTASSIO_IDEAL'] == media_potassio:
        score += 1
    else:
        motivos.append(f"potássio esperado: {row['POTASSIO_IDEAL']}, encontrado: {media_potassio}")

    if row['NITROGENIO_IDEAL'] == media_nitrogenio:
        score += 1
    else:
        motivos.append(f"nitrogênio esperado: {row['NITROGENIO_IDEAL']}, encontrado: {media_nitrogenio}")

    resultados.append({
        'cultura': row['CULTURA'],
        'score': score,
        'motivos': motivos
    })

# Selecionar top 3
resultados_ordenados = sorted(resultados, key=lambda x: x['score'], reverse=True)
melhores = resultados_ordenados[:3]
restantes = resultados_ordenados[3:]

# Gráfico 1: Frequência de Irrigação
contagem_irrigacao = df_periodo['IRRIGACAO'].value_counts()
plt.figure(figsize=(6, 4))
contagem_irrigacao.plot(kind='bar', color=['green', 'red'])
plt.title('Frequência de Irrigação')
plt.xlabel('Estado')
plt.ylabel('Quantidade')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(caminho_graficos, 'frequencia_irrigacao.png'))
plt.close()

# Gráfico 2: Umidade ao longo do tempo
plt.figure(figsize=(6, 4))
df_periodo.plot(x='DATA', y='UMIDADE_PERCENT', kind='line', marker='o', color='blue', legend=False)
plt.title('Umidade (%) ao Longo do Tempo')
plt.xlabel('Data')
plt.ylabel('Umidade (%)')
plt.tight_layout()
plt.savefig(os.path.join(caminho_graficos, 'umidade_tempo.png'))
plt.close()

# Gráfico 3: Dispersão pH vs Umidade
plt.figure(figsize=(6, 4))
plt.scatter(df_periodo['PH'], df_periodo['UMIDADE_PERCENT'], color='purple')
plt.title('Dispersão: pH vs Umidade')
plt.xlabel('pH')
plt.ylabel('Umidade (%)')
plt.tight_layout()
plt.savefig(os.path.join(caminho_graficos, 'ph_umidade_dispersao.png'))
plt.close()

# Gráfico 4: Nutrientes por data
df_nutrientes = df_periodo[['DATA', 'FOSFORO', 'POTASSIO', 'NITROGENIO']].set_index('DATA')
df_nutrientes.plot(kind='bar', stacked=True, figsize=(8, 5), colormap='Set2')
plt.title('Nutrientes por Data')
plt.xlabel('Data')
plt.ylabel('Quantidade')
plt.tight_layout()
plt.savefig(os.path.join(caminho_graficos, 'nutrientes_empilhados.png'))
plt.close()

# Gráfico 5: pH ao longo do tempo
plt.figure(figsize=(6, 4))
df_periodo.plot(x='DATA', y='PH', kind='line', marker='s', color='orange', legend=False)
plt.title('pH ao Longo do Tempo')
plt.xlabel('Data')
plt.ylabel('pH')
plt.tight_layout()
plt.savefig(os.path.join(caminho_graficos, 'ph_tempo.png'))
plt.close()

# Gráfico 6: Compatibilidade geral das culturas
# Gráfico 6: Compatibilidade baseada em pH real
ph_medido = media_ph

# Filtrar culturas com PH_MAXIMO >= pH medido
culturas_validas = culturas[abs(culturas['PH_MAXIMO'] - ph_medido) <= 0.5].copy()

if culturas_validas.empty:
    print(f"⚠️ Nenhuma cultura com PH_MAXIMO >= {ph_medido:.1f}")
    melhores_ph = []
else:
    culturas_validas['DIST_MAX'] = abs(culturas_validas['PH_MAXIMO'] - ph_medido)
    culturas_validas['DIST_MIN'] = abs(culturas_validas['PH_MINIMO'] - ph_medido)
    culturas_validas = culturas_validas.sort_values(by=['DIST_MAX', 'DIST_MIN'])
    melhores_ph = culturas_validas.head(3)['CULTURA'].tolist()

nomes_culturas = culturas['CULTURA'].tolist()
valores = [1 if nome in melhores_ph else 0 for nome in nomes_culturas]
cores = ['green' if nome in melhores_ph else 'gray' for nome in nomes_culturas]

plt.figure(figsize=(10, 5))
plt.bar(nomes_culturas, valores, color=cores)
plt.title(f'Melhores Culturas para pH {ph_medido:.1f} ({data_inicio.strftime("%d/%m/%Y")})')
plt.xlabel('Cultura')
plt.ylabel('Compatível (1 = Sim, 0 = Não)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(caminho_graficos, 'compatibilidade_culturas.png'))
plt.close()

# Função para gerar HTML individual de gráfico
def gerar_html_grafico(nome_arquivo, titulo, nome_html):
    caminho_html = os.path.join(caminho_base, nome_html)
    with open(caminho_html, 'w', encoding='utf-8') as f:
        f.write(f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{titulo}</title>
        </head>
        <body>
            <h2>{titulo}</h2>
            <img src="graficos/{nome_arquivo}">
        </body>
        </html>
        """)

# Gerar HTMLs individuais para cada gráfico
gerar_html_grafico('frequencia_irrigacao.png', 'Frequência de Irrigação', 'grafico_frequencia_irrigacao.html')
gerar_html_grafico('umidade_tempo.png', 'Umidade ao Longo do Tempo', 'grafico_umidade_tempo.html')
gerar_html_grafico('ph_umidade_dispersao.png', 'Dispersão: pH vs Umidade', 'grafico_ph_umidade_dispersao.html')
gerar_html_grafico('nutrientes_empilhados.png', 'Nutrientes por Data', 'grafico_nutrientes_empilhados.html')
gerar_html_grafico('ph_tempo.png', 'pH ao Longo do Tempo', 'grafico_ph_tempo.html')
gerar_html_grafico('compatibilidade_culturas.png', 'Compatibilidade das Culturas no Período Selecionado', 'grafico_compatibilidade_culturas.html')