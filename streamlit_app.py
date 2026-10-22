import streamlit as st
import pandas as pd
import os

# Configuração da página do site para formato limpo de sistema
st.set_page_config(page_title="Controle de Consertos Externos", layout="wide")

st.title("🛠️ Painel de Consertos Externos")
st.write("Dados atualizados em tempo real sincronizados com a Engenharia de Manutenção.")

# --- CONFIGURAÇÕES AUTOMÁTICAS TRAVADAS ---
NOME_DO_ARQUIVO = "2025.Reparo_Externo - PCM.xlsx"
NOME_DA_ABA_CERTA = "2026 - Conserto"  
LINHA_DO_CABECALHO = 3  

@st.cache_data(ttl=10) # Atualiza quase instantaneamente a cada 10 segundos
def carregar_dados_site():
    if os.path.exists(NOME_DO_ARQUIVO):
        try:
            # Lê a planilha que o Power Automate envia automaticamente para o GitHub
            df = pd.read_excel(
                NOME_DO_ARQUIVO, 
                sheet_name=NOME_DA_ABA_CERTA, 
                header=LINHA_DO_CABECALHO, 
                engine='openpyxl'
            )
            # Limpeza automática de colunas e linhas inteiramente vazias
            df = df.dropna(how='all')
            df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed:|^Unnamed')]
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"Erro ao processar o arquivo de dados: {e}")
            return None
    else:
        st.warning("⏱️ Aguardando a primeira sincronização de dados do Power Automate...")
        return None

df = carregar_dados_site()

# --- EXIBIÇÃO DA TABELA DINÂMICA DO SITE ---
if df is not None and not df.empty:
    st.markdown("---")
    
    # --- BARRA LATERAL COM FILTROS DO SITE ---
    st.sidebar.header("🔍 Filtros Rápidos")
    colunas = df.columns.tolist()
    
    # Tenta encontrar colunas de Status ou Situação automaticamente para criar os filtros dinâmicos
    coluna_status = next((c for c in colunas if 'status' in str(c).lower() or 'situa' in str(c).lower() or 'retorno' in str(c).lower()), None)
    if coluna_status:
        status_sel = st.sidebar.multiselect(
            f"Filtrar por {coluna_status}", 
            options=df[coluna_status].dropna().unique(), 
            default=df[coluna_status].dropna().unique()
        )
        df = df[df[coluna_status].isin(status_sel)]

    # --- CARTÕES DE RESUMO ---
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total de Registros no Sistema", value=len(df))
    with col2:
        st.success("✅ Painel operando no formato de sistema nativo com sincronização automática!")

    st.markdown("---")

    # --- TABELA INTERATIVA DO SITE (SEM CARA DE EXCEL) ---
    st.subheader("📋 Lista de Envios e Retornos")
    df_exibicao = df.fillna("").astype(str)
    
    # Renderiza a tabela cinza e branca interativa e limpa do próprio Streamlit
    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
    
    if st.button("🔄 Atualizar Forçado"):
        st.cache_data.clear()
        st.rerun()
