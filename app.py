import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração básica do app
st.set_page_config(page_title="Controle de Combustivel", layout="wide")
st.title("⛽ Acompanhamento de Combustível")

# Arquivo para salvar os dados
DATA_FILE = "dados_combustivel.csv"

def carregar_dados():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['Data'] = pd.to_datetime(df['Data'])
        return df.sort_values(by='Data').reset_index(drop=True)
    return pd.DataFrame(columns=["Data", "Combustivel", "Odometro", "Litros", "Preco_Litro", "Custo_Total", "KM_Rodado", "Consumo_KML"])

def salvar_dados(df):
    df.to_csv(DATA_FILE, index=False)

df = carregar_dados()

# Menu lateral para entrada de dados
st.sidebar.header("📝 Novo Abastecimento")
data = st.sidebar.date_input("Data", datetime.now())
combustivel = st.sidebar.selectbox("Combustível", ["Gasolina", "Etanol", "Diesel"])
odometro = st.sidebar.number_input("Odômetro Atual (KM)", min_value=0, step=1)
litros = st.sidebar.number_input("Litros", min_value=0.0, step=0.1)
custo = st.sidebar.number_input("Custo Total (R$)", min_value=0.0, step=0.1)

if st.sidebar.button("Salvar Registro"):
    preco_litro = custo / litros if litros > 0 else 0
    km_rodado = 0
    consumo = 0
    
    if not df.empty:
        ultimo_odometro = df['Odometro'].max()
        if odometro > ultimo_odometro:
            km_rodado = odometro - ultimo_odometro
            consumo = km_rodado / litros if litros > 0 else 0
            
    novo_registro = pd.DataFrame([{
        "Data": str(data), "Combustivel": combustivel, "Odometro": odometro,
        "Litros": litros, "Preco_Litro": round(preco_litro, 2), "Custo_Total": custo,
        "KM_Rodado": km_rodado, "Consumo_KML": round(consumo, 2)
    }])
    
    df = pd.concat([df, novo_registro], ignore_index=True)
    salvar_dados(df)
    st.sidebar.success("Abastecimento salvo com sucesso!")
    st.rerun()

# Abas do Aplicativo
aba1, aba2 = st.tabs(["📊 Relatórios e Gráficos", "📅 Histórico (Calendário)"])

with aba1:
    if not df.empty:
        st.subheader("📈 Resumo Geral")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Gasto", f"R$ {df['Custo_Total'].sum():,.2f}")
        col2.metric("Total Litros", f"{df['Litros'].sum():,.1f} L")
        col3.metric("KM Total Rodado", f"{df['KM_Rodado'].sum()} km")
        
        st.subheader("Média de Consumo")
        df_valid = df[df['Consumo_KML'] > 0]
        if not df_valid.empty:
            medias = df_valid.groupby('Combustivel')['Consumo_KML'].mean()
            st.bar_chart(medias)
        else:
            st.info("Insira o próximo abastecimento para calcular a média de km/L.")
    else:
        st.info("Nenhum dado cadastrado. Use o menu lateral.")

with aba2:
    st.subheader("📅 Histórico de Abastecimentos")
    if not df.empty:
        st.dataframe(df[["Data", "Combustivel", "Odometro", "Litros", "Custo_Total", "KM_Rodado", "Consumo_KML"]], use_container_width=True)
    else:
        st.text("Nenhum registro encontrado.")
