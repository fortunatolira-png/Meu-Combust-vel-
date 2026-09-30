import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração básica do app
st.set_page_config(page_title="Controle de Combustivel", layout="wide")
st.title("⛽ Acompanhamento de Combustível")

# Arquivos para salvar os dados
DATA_FILE = "dados_combustivel.csv"
VEICULOS_FILE = "dados_veiculos.csv"

def carregar_dados():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['Data'] = pd.to_datetime(df['Data'])
        return df.sort_values(by='Data').reset_index(drop=True)
    return pd.DataFrame(columns=["Data", "Carro", "Combustivel", "Odometro", "Litros", "Preco_Litro", "Custo_Total", "Tanque_Cheio", "KM_Rodado", "Consumo_KML"])

def carregar_veiculos():
    if os.path.exists(VEICULOS_FILE):
        return pd.read_csv(VEICULOS_FILE)['Nome'].tolist()
    return ["Meu Carro Padrão"]

def salvar_dados(df):
    df.to_csv(DATA_FILE, index=False)

def salvar_veiculos(lista_veiculos):
    pd.DataFrame({"Nome": lista_veiculos}).to_csv(VEICULOS_FILE, index=False)

df = carregar_dados()
lista_veiculos = carregar_veiculos()

# Menu lateral para entrada de dados
st.sidebar.header("📝 Novo Abastecimento")
carro_selecionado = st.sidebar.selectbox("Selecione o Veículo", lista_veiculos)
data = st.sidebar.date_input("Data", datetime.now())
combustivel = st.sidebar.selectbox("Combustível", ["Gasolina", "Etanol", "Diesel"])
odometro = st.sidebar.number_input("Odômetro Atual (KM)", min_value=0, step=1)
preco_litro = st.sidebar.number_input("Preço por Litro (R$)", min_value=0.0, step=0.01, format="%.2f")
custo = st.sidebar.number_input("Valor Total Pago (R$)", min_value=0.0, step=1.0, format="%.2f")

# Marcador de tanque cheio
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
            # Filtrar histórico específico APENAS do carro selecionado
            df_carro = df[df['Carro'] == carro_selecionado]
            df_tanque_cheio = df_carro[df_carro['Tanque_Cheio'] == True]
            
            if not df_tanque_cheio.empty and tanque_cheio:
                ultimo_registro_cheio = df_tanque_cheio.iloc[-1]
                ultimo_odometro = ultimo_registro_cheio['Odometro']
                
                if odometro > ultimo_odometro:
                    km_rodado = odometro - ultimo_odometro
                    consumo = km_rodado / litros_calculados if litros_calculados > 0 else 0
            elif not df_carro.empty:
                ultimo_odometro = df_carro['Odometro'].max()
                if odometro > ultimo_odometro:
                    km_rodado = odometro - ultimo_odometro
                
        novo_registro = pd.DataFrame([{
            "Data": str(data), "Carro": carro_selecionado, "Combustivel": combustivel, "Odometro": odometro,
            "Litros": round(litros_calculados, 2), "Preco_Litro": round(preco_litro, 2), "Custo_Total": custo,
            "Tanque_Cheio": tanque_cheio, "KM_Rodado": km_rodado, "Consumo_KML": round(consumo, 2)
        }])
        
        df = pd.concat([df, novo_registro], ignore_index=True)
        salvar_dados(df)
        st.sidebar.success(f"Abastecimento do {carro_selecionado} salvo!")
        st.rerun()

# Abas do Aplicativo
aba1, aba2, aba3, aba4 = st.tabs(["📊 Relatórios e Gráficos", "📅 Histórico", "🚗 Cadastrar Carros", "⚙️ Gerenciar Dados"])

with aba1:
    st.subheader("🔍 Filtrar Painel")
    carro_filtro = st.selectbox("Escolha o carro para ver o relatório:", lista_veiculos, key="filtro_painel")
    
    # Filtrar dados para exibição do gráfico/métricas do carro escolhido
    df_filtrado = df[df['Carro'] == carro_filtro] if not df.empty else pd.DataFrame()
    
    if not df_filtrado.empty:
        st.subheader(f"📈 Resumo Geral - {carro_filtro}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Gasto", f"R$ {df_filtrado['Custo_Total'].sum():,.2f}")
        col2.metric("Total Litros", f"{df_filtrado['Litros'].sum():,.1f} L")
        col3.metric("KM Total Rodado", f"{df_filtrado['KM_Rodado'].sum()} km")
        
        st.subheader("Média de Consumo (Apenas Tanque Cheio)")
        df_valid = df_filtrado[df_filtrado['Consumo_KML'] > 0]
        if not df_valid.empty:
            medias = df_valid.groupby('Combustivel')['Consumo_KML'].mean()
            st.bar_chart(medias)
        else:
            st.info("A média aparecerá quando você registrar o SEGUNDO tanque cheio deste veículo.")
    else:
        st.info(f"Nenhum abastecimento cadastrado para o veículo: {carro_filtro}")

with aba2:
    st.subheader("📅 Histórico de Abastecimentos")
    carro_hist_filtro = st.selectbox("Filtrar histórico por veículo:", ["Todos"] + lista_veiculos)
    
    if not df.empty:
        df_exibicao = df.copy()
        df_exibicao['Data'] = df_exibicao['Data'].dt.strftime('%Y-%m-%d')
        df_exibicao['Tanque_Cheio'] = df_exibicao['Tanque_Cheio'].map({True: "Sim", False: "Não"})
        
        if carro_hist_filtro != "Todos":
            df_exibicao = df_exibicao[df_exibicao['Carro'] == carro_hist_filtro]
            
        st.dataframe(df_exibicao[["Data", "Carro", "Combustivel", "Odometro", "Preco_Litro", "Custo_Total", "Litros", "Tanque_Cheio", "KM_Rodado", "Consumo_KML"]], use_container_width=True)
    else:
        st.text("Nenhum registro encontrado.")

with aba4:
    st.subheader("🗑️ Remover Registros")
    if not df.empty:
        st.write("Selecione um registro abaixo para apagar permanentemente:")
        df_exibicao_del = df.copy()
        df_exibicao_del['Data'] = df_exibicao_del['Data'].dt.strftime('%Y-%m-%d')
        
        opcoes = [f"ID {idx} | {row['Carro']} - {row['Data']} - R$ {row['Custo_Total']:.2f}" for idx, row in df_exibicao_del.iterrows()]
        registro_para_deletar = st.selectbox("Escolha o abastecimento:", opcoes)
        
        if st.button("Apagar Registro Selecionado", type="primary"):
            idx_deletar = int(registro_para_deletar.split(" ")[1])
            df = df.drop(idx_deletar).reset_index(drop=True)
            salvar_dados(df)
            st.success("Registro removido com sucesso!")
            st.rerun()
    else:
        st.info("Nenhum dado para remover.")

with aba3:
    st.subheader("🚗 Gerenciar Seus Veículos")
    
    # Formulário para adicionar novos veículos
    novo_veiculo = st.text_input("Nome do Novo Veículo (ex: Fiat Uno, Honda Civic):")
    if st.button("Adicionar Veículo"):
        if novo_veiculo.strip() == "":
            st.error("Digite um nome válido para o carro!")
        elif novo_veiculo in lista_veiculos:
            st.error("Este veículo já está cadastrado!")
        else:
            lista_veiculos.append(novo_veiculo)
            if "Meu Carro Padrão" in lista_veiculos and len(lista_veiculos) > 1:
                lista_veiculos.remove("Meu Carro Padrão") # Remove o padrão provisório se adicionar um real
            salvar_veiculos(lista_veiculos)
            st.success(f"Veículo '{novo_veiculo}' cadastrado com sucesso!")
            st.rerun()
            
    st.write("📋 **Carros cadastrados atualmente:**")
    for v in lista_veiculos:
        st.write(f"- {v}")
