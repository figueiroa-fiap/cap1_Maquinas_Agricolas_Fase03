import cx_Oracle

# Substitua com suas credenciais reais
usuario = "RM567800"
senha = "Rdf@9842"
dsn = "localhost:1521/XEPDB1"

try:
    conn = cx_Oracle.connect(user=usuario, password=senha, dsn=dsn)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sua_tabela")
    resultado = cursor.fetchone()
    print(f"Conexão bem-sucedida! Total de registros: {resultado[0]}")
    conn.close()
except cx_Oracle.Error as erro:
    print("Erro ao conectar:", erro)