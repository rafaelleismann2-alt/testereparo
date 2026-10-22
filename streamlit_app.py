import streamlit as st
import pandas as pd

# Configuração da página do site
st.set_page_config(page_title="Controle de Consertos Externos", layout="wide")

st.title("🛠️ Painel de Consertos Externos")
st.write("Dados atualizados em tempo real diretamente do SharePoint da Engenharia de Manutenção.")

# Carregar o arquivo enviado de forma segura
@st.cache_data(ttl=60)
def carregar_dados():
    try:
        # Puxa as configurações seguras que faremos no painel do Streamlit
        url_direta = st.secrets["SHAREPOINT_URL"]
        return pd.read_excel(url_direta, engine='openpyxl')
    except Exception as e:
        st.error("Aguardando configuração de conexão segura com o SharePoint corporativo...")
        st.info("Por favor, configure o link nas configurações de 'Secrets' no painel do Streamlit Cloud.")
        return None

df = carregar_dados()

if df is not None:
    # --- CARTÕES DE RESUMO ---
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total de Linhas no Painel", value=len(df))
    with col2:
        st.success("✅ Conectado com sucesso ao SharePoint!")

    st.markdown("---")

    # --- TABELA INTERATIVA PRINCIPAL ---
    st.subheader("📋 Lista de Envios e Retornos")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    if st.button("🔄 Atualizar Dados Agora"):
        st.cache_data.clear()
        st.rerun()
