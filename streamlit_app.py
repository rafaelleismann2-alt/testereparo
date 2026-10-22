import streamlit as st

# Configuração da página do site
st.set_page_config(page_title="Controle de Consertos Externos", layout="wide")

st.title("🛠️ Painel de Consertos Externos")
st.write("Dados atualizados em tempo real diretamente do SharePoint da Engenharia de Manutenção.")
st.markdown("---")

try:
    # Puxa o link de incorporação configurado nos Secrets
    url_embed = st.secrets["SHAREPOINT_URL"]
    
    # Exibe a planilha real do SharePoint de forma linda e interativa na tela
    # Esse bloco permite navegar pelas abas (2026 - Conserto) diretamente no site
    st.components.v1.iframe(url_embed, height=750, scrolling=True)
    
    st.success("✅ Painel integrado com sucesso! Você pode visualizar os dados diretamente acima.")

except Exception as e:
    st.error(f"Erro ao carregar o visualizador do SharePoint: {e}")
