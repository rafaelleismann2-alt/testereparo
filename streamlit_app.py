import streamlit as st
import pandas as pd

# Configuração da página do site
st.set_page_config(page_title="Controle de Consertos Externos", layout="wide")

st.title("🛠️ Painel de Consertos Externos")
st.write("Dados atualizados em tempo real diretamente do SharePoint da Engenharia de Manutenção.")

# --- CONFIGURAÇÃO AUTOMÁTICA TRAVADAS ---
NOME_DA_ABA_CERTA = "2026 - Conserto"  
LINHA_DO_CABECALHO = 3  

@st.cache_data(ttl=30) # Atualiza o site automaticamente a cada 30 segundos se houver mudanças
def carregar_dados_puros():
    try:
        # Puxa o link de incorporação dos Secrets
        link_embed = st.secrets["SHAREPOINT_URL"]
        
        # Converte o link de visualização do iframe para um link de download de dados puros
        url_download = link_embed.replace("action=embedview", "action=download").replace("Doc.aspx", "download.aspx")
        if "action=" not in url_download:
            url_download = url_download + "&action=download"

        # O Python baixa e processa os dados usando as configurações travadas
        dados = pd.read_excel(
            url_download, 
            sheet_name=NOME_DA_ABA_CERTA, 
            header=LINHA_DO_CABECALHO, 
            engine='openpyxl'
        )
        
        # Limpeza automática de colunas e linhas inteiramente vazias
        dados = dados.dropna(how='all')
        dados = dados.loc[:, ~dados.columns.astype(str).str.contains('^Unnamed:|^Unnamed')]
        dados.columns = [str(c).strip() for c in dados.columns]
        return dados
    except Exception as e:
        st.error(f"Erro ao extrair dados puros do SharePoint: {e}")
        return None

df = carregar_dados_puros()

# --- ÁREA INTERATIVA DO SITE (VISUAL DO SISTEMA) ---
if df is not None and not df.empty:
    st.markdown("---")
    
    # --- FILTROS VISUAIS DINÂMICOS ---
    st.sidebar.header("🔍 Filtros Rápidos")
    colunas_disponiveis = df.columns.tolist()
    
    # Identifica colunas de Status ou Situação automaticamente
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
        st.success("✅ Conectado com sucesso! Dados extraídos de forma limpa e profissional.")

    st.markdown("---")

    # --- TABELA INTERATIVA DO SITE ---
    st.subheader("📋 Lista de Envios e Retornos")
    
    # Mostra a tabela limpa do próprio site, com busca e ordenação rápida
    df_exibicao = df.fillna("").astype(str)
    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
    
    if st.button("🔄 Atualizar Painel"):
        st.cache_data.clear()
        st.rerun()
