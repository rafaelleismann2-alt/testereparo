import streamlit as st
import pandas as pd
import urllib.parse

# Configuração da página do site
st.set_page_config(page_title="Controle de Consertos Externos", layout="wide")

st.title("🛠️ Painel de Consertos Externos")
st.write("Dados atualizados em tempo real diretamente do SharePoint da Engenharia de Manutenção.")

@st.cache_data(ttl=60)
def carregar_dados():
    try:
        # Puxa o link dos Secrets
        url_original = st.secrets["SHAREPOINT_URL"]
        
        # Converte links de visualização/edição do SharePoint para link de download direto
        if "doc2.aspx" in url_original or "guestfile.aspx" in url_original:
            parsed_url = urllib.parse.urlparse(url_original)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            sourcedoc = query_params.get("sourcedoc", [None])[0]
            if sourcedoc:
                # Reconstrói a URL apontando diretamente para o ID do documento puro
                base_url = url_original.split("/_layouts/")[0]
                url_direta = f"{base_url}/_layouts/15/download.aspx?share=1&sourcedoc={urllib.parse.quote(sourcedoc)}"
            else:
                url_direta = url_original
        else:
            url_direta = url_original

        # Faz a leitura do arquivo Excel
        return pd.read_excel(url_direta, engine='openpyxl')
    except Exception as e:
        st.error(f"Erro ao tentar ler o arquivo do SharePoint: {e}")
        st.info("Verifique se o arquivo está compartilhado corretamente na rede da empresa.")
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
