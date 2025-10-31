
import streamlit as st
import pandas as pd
import random

# Simulação de dados
def gerar_dados():
    return {
        "Umidade (%)": random.randint(10, 90),
        "Fósforo (P)": random.randint(5, 50),
        "Potássio (K)": random.randint(5, 50),
        "pH": round(random.uniform(4.5, 8.0), 1),
        "Irrigação": random.choice(["Ligada", "Desligada"]),
        "Clima": random.choice(["Sol", "Chuva", "Nublado", "Seco"])
    }

def sugestao_irrigacao(clima, umidade):
    if clima == "Chuva":
        return "Não irrigar — chuva prevista"
    elif umidade < 30:
        return "Irrigação recomendada — solo seco"
    elif clima == "Seco":
        return "Monitorar — clima seco"
    else:
        return "Sem necessidade imediata"

# Interface Streamlit
st.set_page_config(page_title="Dashboard de Irrigação", layout="wide")
st.title("🌾 Monitoramento Agrícola")

dados = gerar_dados()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔬 Níveis do Solo")
    st.metric("Umidade (%)", dados["Umidade (%)"])
    st.metric("Fósforo (P)", dados["Fósforo (P)"])
    st.metric("Potássio (K)", dados["Potássio (K)"])
    st.metric("pH", dados["pH"])

with col2:
    st.subheader("🚿 Irrigação")
    st.metric("Status", dados["Irrigação"])
    st.metric("Clima", dados["Clima"])
    st.info(sugestao_irrigacao(dados["Clima"], dados["Umidade (%)"]))

st.caption("Dados simulados para fins de prototipagem.")