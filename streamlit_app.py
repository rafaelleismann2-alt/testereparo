import streamlit as st

# Configuração da página do site para ocupar a tela inteira
st.set_page_config(page_title="Controle de Consertos Externos", layout="wide")

st.title("🛠️ Painel de Consertos Externos")
st.write("Dados atualizados em tempo real diretamente da Engenharia de Manutenção.")
st.markdown("---")

try:
    # Puxa o link de incorporação configurado nos Secrets
    url_embed = st.secrets["SHAREPOINT_URL"]
    
    # Adiciona comandos extras no link para forçar a Microsoft a esconder 
    # botões de download, cabeçalhos de aba e barras de comando do Excel
    if "wdHideGridlines" not in url_embed:
        url_embed += "&wdHideGridlines=True&wdAllowInteractivity=True&wdHideHeaders=True&wdDownloadButton=False"

    # Estiliza o contêiner do site para cobrir o Excel com uma moldura limpa e moderna
    st.markdown(
        """
        <style>
        iframe {
            border: 1px solid #4A4A4A !important;
            border-radius: 8px !important;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Exibe os dados integrados sem correr risco de bloqueio 401
    st.components.v1.iframe(url_embed, height=720, scrolling=True)
    
    st.success("✅ Painel conectado com sucesso e operando sem travas de rede!")

except Exception as e:
    st.error(f"Erro ao carregar o visualizador customizado: {e}")
