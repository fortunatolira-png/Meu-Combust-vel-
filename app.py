importar streamlit como st
import pandas as pd
importar data e hora

# Configuração da página
st.set_page_config(page_title="EcoDrive - Consumo", page_icon="â›½", layout="wide")

# Título do aplicativo
st.title("â›½ EcoDrive - Acompanhamento de Consumo")
st.markdown("Gerencie seus abastecimentos, controle custos e veja relacionamentos detalhados de quilometragem.")

# Inicializar dados de estado da sessão
se "abastecimentos" não estiver em st.session_state:
    st.session_state.abastecimentos = pd.DataFrame(
        colunas=["Dados", "Combustível", "Odômetro (km)", "Litros (L)", "Custo Total (R$)", "KM Rodados", "Consumo (km/L)"]
    )

# Barra lateral - Formulário de inscrição
st.sidebar.header("ðŸ“ Novo Registro")
com st.sidebar.form("form_abastecimento", clear_on_submit=True):
    data = st.date_input("Dados do Abastecimento", datetime.date.today())
    combustivel = st.selectbox("Tipo de Combustível", ["Gasolina", "Etanol", "Diesel"])
    odometro = st.number_input("Odômetro Atual (km)", min_value=0, step=1, help="Quilometragem atual no painel")
    litros = st.number_input("Quantidade de Litros (L)", min_value=0,0, step=0,1, format="%.2f")
    custo = st.number_input("Custo Total (R$)", min_value=0.0, step=0.1, format="%.2f")
    
    submetido = st.form_submit_form("Registrar")

se submetido:
    se odometro <= 0 ou litros <= 0 ou custo <= 0:
        st.sidebar.error("Por favor, insira valores maiores que zero.")
    outro:
        # Calcular valores derivados se houver registros anteriores
        km_rodados = 0,0
        consumo = 0,0
        
        se não st.session_state.abastecimentos.empty:
            # Ordene por data e odômetro para encontrar os anteriores
            df_temp = st.session_state.abastecimentos.sort_values(by=["Odômetro (km)"])
            # Obtenha o último odômetro com quilometragem menor que a atual.
            prev_records = df_temp[df_temp["Odômetro (km)"] < odômetro]
            se prev_records não estiver vazio:
                ultimo_odometro = prev_records["Odômetro (km)"].iloc[-1]
                km_rodados = odometro - ultimo_odometro
                se litros > 0:
                    consumo = km_rodados / litros

        # Adicionar nova entrada
        novo_registro = pd.DataFrame([{
            "Dados": dados,
            "CombustÃvel": combustivel,
            "Odômetro (km)": odômetro,
            "Litros (L)": litros,
            "Custo Total (R$)": custo,
            "KM Rodados": km_rodados,
            "Consumo (km/L)": consumo
        }])
        
        st.session_state.abastecimentos = pd.concat([st.session_state.abastecimentos, novo_registro], ignore_index=True)
        st.sidebar.success("Abastecimento registrado com sucesso!")

# Abas do painel principal
tab_dash, tab_hist = st.tabs(["ðŸ“Š Relatórios e Desempenho", "ðŸ“… Histórico & Calendário"])

com tab_dash:
    se st.session_state.abastecimentos.empty:
        st.info("Nenhum dado registrado ainda. Use o painel lateral para cadastrar o primeiro abastecimento.")
    outro:
        df = st.session_state.abastecimentos.copy()
        df["Data"] = pd.to_datetime(df["Data"])
        
        # Linha de métricas
        col1, col2, col3, col4 = st.columns(4)
        com col1:
            st.metric("Total Investido", f"R$ {df['Custo Total (R$)'].sum():,.2f}")
        com col2:
            st.metric("Litros Consumidos", f"{df['Litros (L)'].sum():,.1f} L")
        com col3:
            total_km = df["KM Rodados"].sum()
            st.metric("Total Rodado", f"{total_km:,.1f} km")
        com col4:
            media_geral = df[df["Consumo (km/L)"] > 0]["Consumo (km/L)"].mean()
            st.metric("Consumo Médio Geral", f"{media_geral:.2f} km/L" if not pd.isna(media_geral) else "---")

        st.markdown("---")
        
        # Seção de gráficos
        st.subheader("Desempenho por Combustível")
        c1, c2 = st.columns(2)
        
        com c1:
            # Consumo médio por tipo de combustível
            avg_fuel = df[df["Consumo (km/L)"] > 0].groupby("Combustível")["Consumo (km/L)"].mean()
            se não avg_fuel.empty:
                st.markdown("**Eficiência Média (km/L)**")
                st.bar_chart(avg_fuel)
            outro:
                st.write("Dados insuficientes para calcular mídias por combustível.")
                
        com c2:
            # Despesas por tipo de combustível
            cost_fuel = df.groupby("Combustível")["Custo Total (R$)"].sum()
            st.markdown("**Gastos Totais por Combustível (R$)**")
            st.bar_chart(custo_combustível)

com tab_hist:
    se st.session_state.abastecimentos.empty:
        st.info("Nenhum histórico disponível.")
    outro:
        st.subheader("Todos os Registros")
        # Exibir dataframe editável ou dataframe normal ordenado por data
        df_display = st.session_state.abastecimentos.sort_values(by="Data", ascending=False)
        st.dataframe(df_display, use_container_width=True)
        
        # Botão Baixar Dados
        dados_csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="ðŸ“¥ Exportar dados para Excel/CSV",
            dados=dados_csv,
            file_name="histórico_abastecimento.csv",
            mime="texto/csv"
)
