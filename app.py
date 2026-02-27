import streamlit as st
import pandas as pd
from datetime import datetime, date

# Configuração da Página
st.set_page_config(page_title="Gestão de Manutenção Automotiva", layout="wide")

# Nome do arquivo de banco de dados
DB_FILE = "manutencao.csv"

# Função para carregar dados
def load_data():
    try:
        df = pd.read_csv(DB_FILE)
        df['data'] = pd.to_datetime(df['data']).dt.date
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["peça_serviço", "local", "data", "km", "motivo", "proxima_troca_km", "proxima_troca_data"])

# --- Interface Principal ---
st.title("🚗 Meu Diário de Manutenção")

df = load_data()

# Sidebar para Cadastro
st.sidebar.header("Nova Manutenção")
with st.sidebar.form("form_registro"):
    peca = st.text_input("Peça ou Serviço")
    local = st.text_input("Onde foi feito?")
    data_servico = st.date_input("Quando?", date.today())
    km_atual = st.number_input("Kilometragem Atual", min_value=0, step=1)
    motivo = st.selectbox("Motivo", ["Preventiva", "Corretiva", "Estética", "Upgrade"])
    
    st.markdown("---")
    st.write("**Alertas para o futuro:**")
    prazo_km = st.number_input("Trocar com quantos KM? (0 se não aplicar)", min_value=0)
    prazo_data = st.date_input("Trocar em qual data? (Opcional)", date.today())
    
    submit = st.form_submit_button("Registrar")

if submit:
    new_data = pd.DataFrame([[peca, local, data_servico, km_atual, motivo, prazo_km, prazo_data]], 
                            columns=df.columns)
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.sidebar.success("Registrado com sucesso!")
    st.rerun()

# --- DASHBOARD ---
col1, col2, col3 = st.columns(3)

if not df.empty:
    ultima_km = df['km'].max()
    total_servicos = len(df)
    gasto_estimado = "R$ --" # Opcional: adicionar coluna de custo
    
    col1.metric("Última KM Registrada", f"{ultima_km} km")
    col2.metric("Total de Registros", total_servicos)
    col3.metric("Status Geral", "✅ Em dia")

    # --- SISTEMA DE ALERTAS ---
    st.subheader("🚨 Alertas de Manutenção")
    alertas = False
    
    # Lógica simples de alerta
    for index, row in df.iterrows():
        if row['proxima_troca_km'] > 0 and ultima_km >= (row['proxima_troca_km'] - 500):
            st.warning(f"**Atenção:** Está na hora (ou perto) de trocar: **{row['peça_serviço']}** (Previsto: {row['proxima_troca_km']} km)")
            alertas = True
        
        # Alerta por data (ex: 6 meses)
        if isinstance(row['proxima_troca_data'], date) and row['proxima_troca_data'] <= date.today():
             st.error(f"**Vencido por Data:** {row['peça_serviço']} (Prazo: {row['proxima_troca_data']})")
             alertas = True

    if not alertas:
        st.info("Nenhuma manutenção crítica pendente no momento.")

    # --- TABELA DE HISTÓRICO ---
    st.subheader("📋 Histórico Completo")
    st.dataframe(df.sort_values(by='data', ascending=False), use_container_width=True)
else:
    st.write("Nenhum registro encontrado. Comece cadastrando na barra lateral!")
