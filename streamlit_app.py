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

# Ajuste manual caso a planilha tenha linhas de título no topo
linha_cabecalho = st.number_input(
    "💡 Se a tabela estiver estranha, mude este número para ajustar a linha dos títulos (Cabeçalho):", 
    min_value=0, max_value=20, value=0, step=1
)

# Função para carregar os dados pulando cabeçalhos tortos
def carregar_dados(arquivo, pular_linhas):
    try:
        # Lê a planilha começando da linha selecionada pelo usuário
        dados = pd.read_excel(arquivo, header=pular_linhas, engine='openpyxl')
        
        # Limpa linhas e colunas completamente vazias
        dados = dados.dropna(how='all')
        dados = dados.loc[:, ~dados.columns.str.contains('^Unnamed:')]
        return dados
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return None

# Se o usuário arrastou um arquivo, mostra os dados
if arquivo_enviado is not None:
    df = carregar_dados(arquivo_enviado, linha_cabecalho)
    
    if df is not None and not df.empty:
        st.markdown("---")
        
        # --- FILTROS VISUAIS DINÂMICOS ---
        st.sidebar.header("🔍 Filtros Rápidos")
        colunas_disponiveis = df.columns.tolist()
        
        # Procura colunas de Status de forma inteligente
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
            st.success("✅ Painel gerado com sucesso!")

        st.markdown("---")

        # --- TABELA INTERATIVA PRINCIPAL ---
        st.subheader("📋 Lista de Envios e Retornos")
        
        # Converte para texto apenas para exibição limpa
        df_exibicao = df.astype(str)
        
        # Exibe a planilha bonita, com busca integrada e ordenação
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Ajuste o número da linha do cabeçalho acima para encontrar os dados da tabela.")
else:
    st.info("💡 Como usar: Vá no SharePoint, clique em 'Baixar' (Download) na sua planilha de consertos e arraste o arquivo baixado para a caixinha acima!")
