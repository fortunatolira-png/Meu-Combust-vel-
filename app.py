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
    return pd.DataFrame(columns=["Data", "Combustivel", "Odometro", "Litros", "Preco_Litro", "Custo_Total", "Tanque_Cheio", "KM_Rodado", "Consumo_KML"])

def salvar_dados(df):
    df.to_csv(DATA_FILE, index=False)

df = carregar_dados()

# Menu lateral para entrada de dados
st.sidebar.header("📝 Novo Abastecimento")
data = st.sidebar.date_input("Data", datetime.now())
combustivel = st.sidebar.selectbox("Combustível", ["Gasolina", "Etanol", "Diesel"])
odometro = st.sidebar.number_input("Odômetro Atual (KM)", min_value=0, step=1)
preco_litro = st.sidebar.number_input("Preço por Litro (R$)", min_value=0.0, step=0.01, format="%.2f")
custo = st.sidebar.number_input("Valor Total Pago (R$)", min_value=0.0, step=1.0, format="%.2f")

# MARCADOR DE TANQUE CHEIO
tanque_cheio = st.sidebar.checkbox("Completou o Tanque? (Tanque Cheio)", value=True)

# Cálculo automático de litros na tela
litros_calculados = custo / preco_litro if preco_litro > 0 else 0.0
st.sidebar.info(f"⛽ Litros calculados: {litros_calculados:.2f} L")

if st.sidebar.button("Salvar Registro"):
    if preco_litro <= 0 or custo <= 0 or odometro <= 0:
        st.sidebar.error("Por favor, preencha todos os campos corretamente!")
    else:
        km_rodado = 0
        consumo = 0
        
        if not df.empty:
            # Buscar o último abastecimento onde o tanque TAMBÉM foi cheio
            df_tanque_cheio = df[df['Tanque_Cheio'] == True]
            
            if not df_tanque_cheio.empty and tanque_cheio:
                ultimo_registro_cheio = df_tanque_cheio.iloc[-1]
                ultimo_odometro = ultimo_registro_cheio['Odometro']
                
                if odometro > ultimo_odometro:
                    km_rodado = odometro - ultimo_odometro
                    # Consumo baseado nos litros necessários para voltar a encher o tanque
                    consumo = km_rodado / litros_calculados if litros_calculados > 0 else 0
            else:
                # Se o anterior ou o atual não for cheio, calcula apenas os KM rodados gerais
                ultimo_odometro = df['Odometro'].max()
                if odometro > ultimo_odometro:
                    km_rodado = odometro - ultimo_odometro
                
        novo_registro = pd.DataFrame([{
            "Data": str(data), "Combustivel": combustivel, "Odometro": odometro,
            "Litros": round(litros_calculados, 2), "Preco_Litro": round(preco_litro, 2), "Custo_Total": custo,
            "Tanque_Cheio": tanque_cheio, "KM_Rodado": km_rodado, "Consumo_KML": round(consumo, 2)
        }])
        
        df = pd.concat([df, novo_registro], ignore_index=True)
        salvar_dados(df)
        st.sidebar.success("Abastecimento salvo com sucesso!")
        st.rerun()

# Abas do Aplicativo
aba1, aba2, aba3 = st.tabs(["📊 Relatórios e Gráficos", "📅 Histórico (Calendário)", "⚙️ Gerenciar Dados"])

with aba1:
    if not df.empty:
        st.subheader("📈 Resumo Geral")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Gasto", f"R$ {df['Custo_Total'].sum():,.2f}")
        col2.metric("Total Litros", f"{df['Litros'].sum():,.1f} L")
        col3.metric("KM Total Rodado", f"{df['KM_Rodado'].sum()} km")
        
        st.subheader("Média de Consumo (Apenas Tanque Cheio)")
        df_valid = df[df['Consumo_KML'] > 0]
        if not df_valid.empty:
            medias = df_valid.groupby('Combustivel')['Consumo_KML'].mean()
            st.bar_chart(medias)
        else:
            st.info("A média de consumo aparecerá assim que você registrar o SEGUNDO abastecimento de tanque cheio consecutivamente.")
    else:
        st.info("Nenhum dado cadastrado. Use o menu lateral.")

with aba2:
    st.subheader("📅 Histórico de Abastecimentos")
    if not df.empty:
        df_exibicao = df.copy()
        df_exibicao['Data'] = df_exibicao['Data'].dt.strftime('%Y-%m-%d')
        df_exibicao['Tanque_Cheio'] = df_exibicao['Tanque_Cheio'].map({True: "Sim", False: "Não"})
        st.dataframe(df_exibicao[["Data", "Combustivel", "Odometro", "Preco_Litro", "Custo_Total", "Litros", "Tanque_Cheio", "KM_Rodado", "Consumo_KML"]], use_container_width=True)
    else:
        st.text("Nenhum registro encontrado.")

with aba3:
    st.subheader("🗑️ Remover Registros")
    if not df.empty:
        st.write("Selecione um registro abaixo para apagar permanentemente:")
        df_exibicao_del = df.copy()
        df_exibicao_del['Data'] = df_exibicao_del['Data'].dt.strftime('%Y-%m-%d')
        
        opcoes = [f"ID {idx} | {row['Data']} - {row['Combustivel']} (R$ {row['Custo_Total']:.2f})" for idx, row in df_exibicao_del.iterrows()]
        registro_para_deletar = st.selectbox("Escolha o abastecimento:", opciones)
        
        if st.button("Apagar Registro Selecionado", type="primary"):
            idx_deletar = int(registro_para_deletar.split(" ")[1])
            df = df.drop(idx_deletar).reset_index(drop=True)
            salvar_dados(df)
            st.success("Registro removido com sucesso!")
            st.rerun()
    else:
        st.info("Nenhum dado para remover.")
