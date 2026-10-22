import streamlit as st
import pandas as pd
import os

# Configuração da página do site
st.set_page_config(page_title="Controle de Consertos Externos", layout="wide")

st.title("🛠️ Painel de Consertos Externos")
st.write("Dados atualizados em tempo real sincronizados com a Engenharia de Manutenção.")

# --- CONFIGURAÇÕES AUTOMÁTICAS TRAVADAS ---
NOME_DO_ARQUIVO = "2025.Reparo_Externo - PCM.xlsx"  # Nome real da sua planilha
NOME_DA_ABA_CERTA = "2026 - Conserto"  
LINHA_DO_CABECALHO = 3  

# Função para carregar o arquivo automático salvo no GitHub
@st.cache_data(ttl=60)
def carregar_dados_automaticos():
    if os.path.exists(NOME_DO_ARQUIVO):
        try:
            # Lê o Excel usando as configurações que deram certo no seu teste
            dados = pd.read_excel(
                NOME_DO_ARQUIVO, 
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
            st.error(f"Erro ao processar a planilha automática: {e}")
            return None
    else:
        st.info(f"💡 Modo automático pendente: Por favor, faça o upload do arquivo com o nome exato '{NOME_DO_ARQUIVO}' dentro do seu GitHub!")
        return None

# Carrega os dados direto do arquivo do GitHub
df = carregar_dados_automaticos()

# --- ÁREA INTERATIVA DO SITE ---
if df is not None and not df.empty:
    st.markdown("---")
    
    # --- FILTROS VISUAIS DINÂMICOS ---
    st.sidebar.header("🔍 Filtros Rápidos")
    colunas_disponiveis = df.columns.tolist()
    
    # Tenta encontrar colunas de Status, Situação ou Retorno para criar filtros na lateral
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
        st.success("✅ Atualizado! Dados carregados automaticamente do arquivo do repositório.")

    st.markdown("---")

    # --- TABELA INTERATIVA PRINCIPAL ---
    st.subheader("📋 Lista de Envios e Retornos")
    df_exibicao = df.fillna("").astype(str)
    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
    
    # Botão para atualizar o cache caso mude o arquivo no GitHub
    if st.button("🔄 Atualizar Painel"):
        st.cache_data.clear()
        st.rerun()
