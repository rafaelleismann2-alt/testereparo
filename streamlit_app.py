import streamlit as st
import pandas as pd

# Configuração da página do site
st.set_page_config(page_title="Controle de Consertos Externos", layout="wide")

st.title("🛠️ Painel de Consertos Externos")
st.write("Visualização prática e organizada para o controle de retornos.")

# --- ÁREA DE ARRASTAR O ARQUIVO EXCEL ---
st.markdown("### 📥 Atualizar Dados do Painel")
arquivo_enviado = st.file_uploader(
    "Arraste ou selecione a sua planilha baixada do SharePoint aqui (.xlsx)", 
    type=["xlsx"]
)

# Função para carregar os dados do arquivo arrastado
def carregar_dados(arquivo):
    try:
        return pd.read_excel(arquivo, engine='openpyxl')
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return None

# Se o usuário arrastou um arquivo, mostra os dados
if arquivo_enviado is not None:
    df = carregar_dados(arquivo_enviado)
    
    if df is not None:
        st.markdown("---")
        
        # --- FILTROS VISUAIS DINÂMICOS ---
        st.sidebar.header("🔍 Filtros Rápidos")
        
        # Cria filtros automáticos baseados nas colunas que existirem na sua planilha
        # Exemplo: Se tiver uma coluna chamada 'Status', cria o filtro na hora
        colunas_disponiveis = df.columns.tolist()
        
        # Procura por colunas comuns de status ou situação para criar filtros automáticos
        coluna_status = next((c for c in colunas_disponiveis if 'status' in c.lower() or 'situa' in c.lower()), None)
        if coluna_status:
            status_selecionado = st.sidebar.multiselect(
                f"Filtrar por {coluna_status}", 
                options=df[coluna_status].unique(), 
                default=df[coluna_status].unique()
            )
            df = df[df[coluna_status].isin(status_selecionado)]

        # --- CARTÕES DE RESUMO ---
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Total de Registros Carregados", value=len(df))
        with col2:
            st.success("✅ Tabela gerada com sucesso! Use a barra de pesquisa ou clique no topo das colunas para ordenar.")

        st.markdown("---")

        # --- TABELA INTERATIVA PRINCIPAL ---
        st.subheader("📋 Lista de Envios e Retornos")
        
        # Exibe a planilha de forma linda, interativa e interativa
        st.dataframe(df, use_container_width=True, hide_index=True)
else:
    # Mensagem inicial enquanto não arrasta o arquivo
    st.info("💡 Como usar: Vá no SharePoint, clique em 'Baixar' (Download) na sua planilha de consertos e arraste o arquivo baixado para a caixinha acima!")
