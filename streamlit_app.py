import streamlit as st
import pandas as pd
import requests
import io

# Configuração da página do site
st.set_page_config(page_title="Controle de Consertos Externos", layout="wide")

st.title("🛠️ Painel de Consertos Externos")
st.write("Dados atualizados em tempo real diretamente do SharePoint da Engenharia de Manutenção.")

# --- CONFIGURAÇÃO AUTOMÁTICA TRAVADAS ---
NOME_DA_ABA_CERTA = "2026 - Conserto"  
LINHA_DO_CABECALHO = 3  

@st.cache_data(ttl=30) # Atualiza o site automaticamente a cada 30 segundos se houver mudanças
def carregar_dados_sharepoint():
    try:
        # Puxa as credenciais seguras das configurações do Streamlit
        link_original = st.secrets["SHAREPOINT_URL"]
        token_acesso = st.secrets["MICROSOFT_TOKEN"]
        
        # Transforma a URL de visualização do navegador em um link de download direto de API
        # Extrai os parâmetros necessários para autenticação automática de rede
        if "sourcedoc=" in link_original:
            doc_id = link_original.split("sourcedoc=")[1].split("&")[0]
            base_url = link_original.split("/_layouts/")[0]
            url_download = f"{base_url}/_layouts/15/download.aspx?sourcedoc={doc_id}"
        else:
            url_download = link_original

        # Faz a requisição simulando o seu login do navegador de forma segura
        headers = {"Authorization": f"Bearer {token_acesso}"}
        resposta = requests.get(url_download, headers=headers)
        
        if resposta.status_code == 200:
            # Lê o Excel usando as configurações que deram certo no seu teste
            dados = pd.read_excel(
                io.BytesIO(resposta.content), 
                sheet_name=NOME_DA_ABA_CERTA, 
                header=LINHA_DO_CABECALHO, 
                engine='openpyxl'
            )
            # Limpeza automática de colunas e linhas inteiramente vazias
            dados = dados.dropna(how='all')
            dados = dados.loc[:, ~dados.columns.astype(str).str.contains('^Unnamed:|^Unnamed')]
            dados.columns = [str(c).strip() for c in dados.columns]
            return dados
        else:
            st.error(f"Erro de Conexão Corporativa (Código HTTP {resposta.status_code}).")
            st.info("💡 Como resolver: O token de acesso da Microsoft expirou ou precisa ser atualizado nos Secrets do site.")
            return None
    except Exception as e:
        st.error(f"Erro ao processar a planilha do SharePoint: {e}")
        return None

# Carrega os dados direto da nuvem da Microsoft
df = carregar_dados_sharepoint()

# --- ÁREA INTERATIVA DO SITE ---
if df is not None and not df.empty:
    st.markdown("---")
    
    # --- FILTROS VISUAIS DINÂMICOS ---
    st.sidebar.header("🔍 Filtros Rápidos")
    colunas_disponiveis = df.columns.tolist()
    
    coluna_status = next((c for c in colunas_disponiveis if 'status' in str(c).lower() or 'situa' in str(c).lower() or 'retorno' in str(c).lower()), None)
    if coluna_status:
        status_selecionado = st.sidebar.multiselect(
            f"Filtrar por {coluna_status}", 
            options=df[coluna_status].dropna().unique(), 
            default=df[coluna_status].dropna().unique()
        )
        df = df[df[coluna_status].isin(status_selecionado)]

    # --- CARTÕES DE RESUMO ---
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total de Registros Encontrados", value=len(df))
    with col2:
        st.success("✅ Sincronizado! Dados carregados diretamente da nuvem em tempo real.")

    st.markdown("---")

    # --- TABELA INTERATIVA PRINCIPAL ---
    st.subheader("📋 Lista de Envios e Retornos")
    df_exibicao = df.fillna("").astype(str)
    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
    
    if st.button("🔄 Atualizar Painel"):
        st.cache_data.clear()
        st.rerun()
