import cx_Oracle
import os

# Atualização confirmada em 03/11/2025

# Solicita a data ao usuário
data_input = input("Digite a data no formato DD/MM/YY: ").strip()

# Conexão com o banco Oracle
dsn = cx_Oracle.makedsn("oracle.fiap.com.br", 1521, sid="ORCL")
conn = cx_Oracle.connect(user="RM567800", password="fiap25", dsn=dsn)
cursor = conn.cursor()

# Consulta os dados filtrados pela data
query = """
SELECT UMIDADE_PERCENT, PH, FOSFORO, POTASSIO, NITROGENIO, IRRIGACAO, DATA
FROM dados_irrigacao
WHERE DATA = TO_DATE(:data, 'DD/MM/YY')
"""
cursor.execute(query, data=data_input)
rows = cursor.fetchall()

# Gera HTML com layout em cartões
if rows:
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Dados de {data_input}</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body {{
                font-family: 'Roboto', sans-serif;
                background: #f0f4f8;
                margin: 0;
                padding: 30px;
            }}
            h1 {{
                text-align: center;
                color: #2e7d32;
                margin-bottom: 40px;
            }}
            .container {{
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
            }}
            .card {{
                background-color: #ffffff;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                padding: 20px;
                width: 260px;
                text-align: center;
                transition: transform 0.2s;
            }}
            .card:hover {{
                transform: scale(1.03);
            }}
            .card i {{
                font-size: 28px;
                color: #388e3c;
                margin-bottom: 10px;
            }}
            .label {{
                font-weight: bold;
                color: #555;
                margin-bottom: 6px;
            }}
            .value {{
                font-size: 18px;
                color: #333;
            }}
        </style>
    </head>
    <body>
        <h1><i class="fas fa-leaf"></i> Dados de {data_input}</h1>
        <div class="container">
    """
    for row in rows:
        html += f"""
            <div class="card">
                <i class="fas fa-tint"></i>
                <div class="label">Umidade</div>
                <div class="value">{row[0]}</div>
            </div>
            <div class="card">
                <i class="fas fa-vial"></i>
                <div class="label">pH</div>
                <div class="value">{row[1]}</div>
            </div>
            <div class="card">
                <i class="fas fa-leaf"></i>
                <div class="label">Fósforo</div>
                <div class="value">{row[2]}</div>
            </div>
            <div class="card">
                <i class="fas fa-leaf"></i>
                <div class="label">Potássio</div>
                <div class="value">{row[3]}</div>
            </div>
            <div class="card">
                <i class="fas fa-leaf"></i>
                <div class="label">Nitrogênio</div>
                <div class="value">{row[4]}</div>
            </div>
            <div class="card">
                <i class="fas fa-water"></i>
                <div class="label">Irrigação</div>
                <div class="value">{row[5]}</div>
            </div>
            <div class="card">
                <i class="fas fa-calendar-day"></i>
                <div class="label">Data</div>
                <div class="value">{row[6]}</div>
            </div>
        """

    html += """
        </div>
    </body>
    </html>
    """
else:
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Dados de {data_input}</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Roboto', sans-serif;
                background-color: #f4f6f8;
                margin: 0;
                padding: 30px;
                text-align: center;
            }}
            h1 {{
                color: #2c3e50;
                margin-bottom: 20px;
            }}
            p {{
                font-size: 18px;
                color: #7f8c8d;
            }}
        </style>
    </head>
    <body>
        <h1>Dados de {data_input}</h1>
        <p>Nenhum registro encontrado para esta data.</p>
    </body>
    </html>
    """

# Salva o HTML na mesma pasta do script
caminho_base = os.path.dirname(os.path.abspath(__file__))
caminho_html = os.path.join(caminho_base, "contagem_por_data.html")

with open(caminho_html, "w", encoding="utf-8") as file:
    file.write(html)

print(f"✅ HTML gerado com sucesso em:\n{caminho_html}")

# Encerra conexão
cursor.close()
conn.close()