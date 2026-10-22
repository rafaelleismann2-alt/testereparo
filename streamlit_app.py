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

if arquivo_enviado is not None:
    try:
        # Abre o Excel para ler as abas
        excel_file = pd.ExcelFile(arquivo_enviado, engine='openpyxl')
        abas_disponiveis = excel_file.sheet_names
        
        aba_selecionada = st.selectbox(
            "📂 Selecione a aba correta com os seus dados de conserto:", 
            options=abas_disponiveis,
            index=0
        )
        
        # Menu dinâmico para ajustar o cabeçalho caso os títulos fiquem estranhos
        linha_cabecalho = st.number_input(
            "📏 Ajuste da linha dos títulos (Aumente ou diminua se as colunas não aparecerem certas):", 
            min_value=0, max_value=20, value=0, step=1
        )

        # Carrega os dados tratando células mescladas e espaços em branco
        df = pd.read_excel(
            arquivo_enviado, 
            sheet_name=aba_selecionada, 
            header=linha_cabecalho, 
            engine='openpyxl'
        )
        
        # --- LIMPEZA DE CABEÇALHO ---
        # Remove espaços vazios do início e fim dos nomes das colunas
        df.columns = [str(c).strip() for c in df.columns]
        
        # Filtra colunas falsas geradas por células mescladas ou vazias
        df = df.loc[:, ~df.columns.str.contains('^Unnamed:|^Unnamed')]
        
        # Remove linhas que estejam completamente vazias
        df = df.dropna(how='all')

        if not df.empty:
            st.markdown("---")
            
            # --- FILTROS VISUAIS DINÂMICOS ---
            st.sidebar.header("🔍 Filtros Rápidos")
            colunas_disponiveis = df.columns.tolist()
            
            # Identifica automaticamente se existe alguma coluna de Status/Situação
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
                st.success("✅ Cabeçalho alinhado! Use a barra de pesquisa ou clique no topo das colunas para ordenar.")

            st.markdown("---")

            # --- TABELA INTERATIVA PRINCIPAL ---
            st.subheader("📋 Lista de Envios e Retornos")
            
            # Substitui valores nulos (NaN) por texto limpo para não poluir a tabela
            df_exibicao = df.fillna("").astype(str)
            
            # Exibe a planilha de forma interativa
            st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Nossos filtros limparam a tabela. Tente mudar o número da linha do cabeçalho acima.")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("💡 Como usar: Vá no SharePoint, clique em 'Baixar' (Download) na sua planilha de consertos e arraste o arquivo baixado para a caixinha acima!")
