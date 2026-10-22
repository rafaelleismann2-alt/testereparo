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
        # Abre o Excel apenas para descobrir os nomes de todas as abas existentes
        excel_file = pd.ExcelFile(arquivo_enviado, engine='openpyxl')
        abas_disponiveis = excel_file.sheet_names
        
        # Cria um menu na tela para você escolher qual aba contém os consertos
        aba_selecionada = st.selectbox(
            "📂 O Excel possui mais de uma aba. Selecione a aba correta com os seus dados de conserto:", 
            options=abas_disponiveis,
            index=0
        )
        
        # Controle manual caso a tabela não comece na linha 1
        linha_cabecalho = st.number_input(
            "💡 Linha do cabeçalho (Aumente o número se as colunas ficarem com nomes estranhos):", 
            min_value=0, max_value=20, value=0, step=1
        )

        # Carrega os dados da aba que você escolheu
        df = pd.read_excel(arquivo_enviado, sheet_name=aba_selecionada, header=linha_cabecalho, engine='openpyxl')
        
        # Limpa linhas e colunas vazias
        df = df.dropna(how='all')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed:')]

        if not df.empty:
            st.markdown("---")
            
            # --- FILTROS VISUAIS DINÂMICOS ---
            st.sidebar.header("🔍 Filtros Rápidos")
            colunas_disponiveis = df.columns.tolist()
            
            # Tenta achar uma coluna de status automaticamente
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
                st.metric(label="Total de Registros Carregados", value=len(df))
            with col2:
                st.success("✅ Painel gerado com sucesso!")

            st.markdown("---")

            # --- TABELA INTERATIVA PRINCIPAL ---
            st.subheader("📋 Lista de Envios e Retornos")
            
            # Converte tudo para texto para exibição estável
            df_exibicao = df.astype(str)
            st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Esta aba está vazia. Tente selecionar outra aba no menu acima.")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("💡 Como usar: Vá no SharePoint, clique em 'Baixar' (Download) na sua planilha de consertos e arraste o arquivo baixado para a caixinha acima!")
