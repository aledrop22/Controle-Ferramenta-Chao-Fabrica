import streamlit as st
import pandas as pd
import os
import pytz
import plotly.express as px

# --- CONFIGURAÇÃO INICIAL DA PÁGINA ---
st.set_page_config(page_title="Controle de Ferramentas - Chão de Fábrica", layout="wide")

# --- VERIFICAÇÃO DE ACESSO VIA URL ---
# Verifica se o parâmetro acesso=chao está presente na URL
query_params = st.query_params
if 'acesso' in query_params and query_params['acesso'] != 'chao':
    st.switch_page("app_qualidade.py")

# CSS para responsividade
st.markdown("""
<style>
    @media (max-width: 768px) {
        .stColumns > div {
            flex-direction: column !important;
        }
    }
</style>
""", unsafe_allow_html=True)

ARQUIVO_CSV = 'registro_movimentacao_instrumentos.csv'
FUSO_HORARIO_BRASIL = pytz.timezone('America/Sao_Paulo')

# --- FUNÇÃO DE LEITURA (SOMENTE LEITURA) ---
def carregar_dados():
    if os.path.exists(ARQUIVO_CSV):
        try:
            df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str).fillna("")
            # Se o CSV antigo não tiver a coluna 'Setor', nós adicionamos para não dar erro
            if 'Setor' not in df.columns:
                df.insert(4, 'Setor', 'Não Informado')
            return df
        except Exception as e:
            st.error(f"❌ Erro ao ler dados do CSV: {str(e)}")
            return pd.DataFrame(columns=['ID', 'Instrumento', 'Especificacao', 'Operador', 'Setor', 'Maquina', 'Data_Retirada', 'Hora_Retirada', 'Data_Retorno', 'Hora_Retorno', 'Status'])
    else:
        return pd.DataFrame(columns=['ID', 'Instrumento', 'Especificacao', 'Operador', 'Setor', 'Maquina', 'Data_Retirada', 'Hora_Retirada', 'Data_Retorno', 'Hora_Retorno', 'Status'])

# ==========================================
# TELA: CHÃO DE FÁBRICA (APENAS VISUALIZAÇÃO)
# ==========================================
st.title("🏭 Ferramentas no Chão de Fábrica")
st.markdown("*Painel estático para visualização. Retiradas devem ser feitas na Qualidade.*")

col_refresh, _ = st.columns([2, 8])
with col_refresh:
    # Recarrega os dados do CSV
    if st.button("🔄 Atualizar Tela", use_container_width=True):
        st.rerun()
        
st.markdown("---")

# --- FILTROS ---
st.subheader("🔍 Filtros")
col_filtros1, col_filtros2, col_filtros3 = st.columns(3)

df = carregar_dados()
df_uso = df[df['Status'] == 'Em Uso']

# Extrair valores únicos para os filtros
maquinas_disponiveis = ["Todas"] + sorted(df_uso['Maquina'].unique().tolist()) if not df_uso.empty else ["Todas"]
operadores_disponiveis = ["Todos"] + sorted(df_uso['Operador'].unique().tolist()) if not df_uso.empty else ["Todos"]
instrumentos_disponiveis = ["Todos"] + sorted(df_uso['Instrumento'].unique().tolist()) if not df_uso.empty else ["Todos"]

with col_filtros1:
    filtro_maquina = st.selectbox("Máquina:", maquinas_disponiveis)
with col_filtros2:
    filtro_operador = st.selectbox("Operador:", operadores_disponiveis)
with col_filtros3:
    filtro_instrumento = st.selectbox("Tipo de Ferramenta:", instrumentos_disponiveis)

# Aplicar filtros
df_filtrado = df_uso.copy()
if filtro_maquina != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Maquina'] == filtro_maquina]
if filtro_operador != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Operador'] == filtro_operador]
if filtro_instrumento != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Instrumento'] == filtro_instrumento]

st.markdown("---")

# --- GRÁFICO DE FERRAMENTAS MAIS USADAS ---
st.subheader("📊 Ferramentas Mais Usadas")
if not df_uso.empty:
    # Contar uso por tipo de ferramenta
    contagem_ferramentas = df_uso['Instrumento'].value_counts().reset_index()
    contagem_ferramentas.columns = ['Instrumento', 'Quantidade']
    
    fig = px.bar(
        contagem_ferramentas,
        x='Instrumento',
        y='Quantidade',
        title='Ferramentas Mais Utilizadas',
        color='Quantidade',
        color_continuous_scale='Blues'
    )
    fig.update_layout(xaxis_title="Tipo de Ferramenta", yaxis_title="Quantidade em Uso")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nenhum dado disponível para o gráfico.")

st.markdown("---")

# --- LISTA DE FERRAMENTAS EM USO (COM FILTROS) ---
st.subheader("🔧 Ferramentas em Uso")
if not df_filtrado.empty:
    colunas_por_linha = 3
    cols = st.columns(colunas_por_linha)
    
    for index, row in df_filtrado.reset_index().iterrows():
        with cols[index % colunas_por_linha]:
            st.markdown(f"""
                <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 6px solid #007BFF; margin-bottom: 15px;'>
                    <h4 style='margin-top:0; color: #333;'>{row['Instrumento']}</h4>
                    <p style='margin:0; font-size: 16px;'><strong>Detalhe:</strong> {row['Especificacao']}</p>
                    <p style='margin:5px 0 0 0;'>👤 <strong>{row['Operador']}</strong> ({row['Setor']})</p>
                    <p style='margin:0;'>🏭 <strong>{row['Maquina']}</strong></p>
                    <hr style='margin: 10px 0; border: 0; border-top: 1px solid #ddd;'>
                    <p style='margin:0; font-size: 13px; color: #666;'>📅 Retirado: {row['Data_Retirada']} às {row['Hora_Retirada']}</p>
                </div>
            """, unsafe_allow_html=True)
else:
    st.success("✅ Nenhuma ferramenta retida no chão de fábrica no momento.")

st.markdown("---")
st.info("ℹ️ Este painel é apenas para visualização. Para realizar retiradas ou devoluções, acesse o sistema da Qualidade.")
