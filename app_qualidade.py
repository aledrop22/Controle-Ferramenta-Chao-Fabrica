import streamlit as st
import pandas as pd
from datetime import datetime
import os
import pytz
from filelock import FileLock
import plotly.express as px
from dados_comuns import setores_operadores, maquinas_lista, estoque

# --- CONFIGURAÇÃO INICIAL DA PÁGINA ---
st.set_page_config(page_title="Controle de Ferramentas - Qualidade", layout="wide", page_icon="🔧", initial_sidebar_state="expanded")

# CSS para responsividade e tamanho de imagens
st.markdown("""
<style>
    /* Geral - Imagens menores para caber mais colunas */
    img {
        max-width: 70px !important;
        width: 70px !important;
        height: auto !important;
    }
    
    /* Containers com borda - compacto */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        gap: 0.3rem !important;
    }
    
    /* Mobile - Ajustes específicos */
    @media (max-width: 768px) {
        /* Imagens ainda menores em mobile */
        img {
            max-width: 50px !important;
            width: 50px !important;
        }
        
        /* Tabs/Abas - scroll horizontal */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px !important;
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 11px !important;
            padding: 6px 10px !important;
            white-space: nowrap !important;
        }
        
        /* Botões - compactos mas touch-friendly */
        button {
            min-height: 40px !important;
            font-size: 12px !important;
            padding: 8px 12px !important;
        }
        
        /* Texto - tamanho compacto */
        h1, h2, h3, h4 {
            font-size: 1rem !important;
        }
        
        /* Selectbox e inputs - compactos */
        .stSelectbox, .stTextInput {
            font-size: 14px !important;
        }
    }
    
    /* Tablet - médio */
    @media (min-width: 769px) and (max-width: 1024px) {
        img {
            max-width: 60px !important;
            width: 60px !important;
        }
    }
    
    /* Desktop - mantém tamanho padrão */
    @media (min-width: 1025px) {
        img {
            max-width: 70px !important;
            width: 70px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

ARQUIVO_CSV = 'registro_movimentacao_instrumentos.csv'
ARQUIVO_LOCK = 'registro_movimentacao_instrumentos.csv.lock'
FUSO_HORARIO_BRASIL = pytz.timezone('America/Sao_Paulo')

# --- 1. FUNÇÕES DE BANCO DE DADOS (CSV) ---
def carregar_dados():
    if os.path.exists(ARQUIVO_CSV):
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str).fillna("")
        # Se o CSV antigo não tiver a coluna 'Setor', nós adicionamos para não dar erro
        if 'Setor' not in df.columns:
            df.insert(4, 'Setor', 'Não Informado')
        return df
    else:
        return pd.DataFrame(columns=['ID', 'Instrumento', 'Especificacao', 'Operador', 'Setor', 'Maquina', 'Data_Retirada', 'Hora_Retirada', 'Data_Retorno', 'Hora_Retorno', 'Status'])

def salvar_dados(df):
    try:
        # Usa file lock para evitar conflitos de escrita
        with FileLock(ARQUIVO_LOCK, timeout=10):
            df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
        return True
    except Exception as e:
        st.error(f"❌ Erro ao salvar dados no CSV: {str(e)}")
        return False

# Inicialização de variáveis de sessão
if 'df_dados' not in st.session_state:
    st.session_state.df_dados = carregar_dados()
if 'tela_atual' not in st.session_state:
    st.session_state.tela_atual = 'dashboard'
if 'operador_logado' not in st.session_state:
    st.session_state.operador_logado = None
if 'setor_logado' not in st.session_state:
    st.session_state.setor_logado = None
if 'ferramentas_selecionadas' not in st.session_state:
    st.session_state.ferramentas_selecionadas = []
if 'passo_retirada' not in st.session_state:
    st.session_state.passo_retirada = 1


# Geração automática de fotos reais para todos os operadores
todos_operadores = [nome for lista in setores_operadores.values() for nome in lista]
# Usa UI Faces para fotos reais de pessoas aleatórias
fotos_operadores = {nome: f"https://i.pravatar.cc/150?u={nome.replace(' ', '')}&img={i % 70}" for i, nome in enumerate(todos_operadores)}


# ==========================================
# LÓGICA DE NAVEGAÇÃO DE TELAS
# ==========================================

if st.session_state.tela_atual == 'dashboard':
    # --- TELA 1: DASHBOARD EM TEMPO REAL ---
    st.title("📊 Painel de Ferramentas - Qualidade (Interativo)")

    # Botão de ação destacado no topo
    col_btn, col_stats = st.columns([2, 8])
    with col_btn:
        if st.button("➕ Nova Retirada", width='stretch', type="primary"):
            st.session_state.tela_atual = 'retirada'
            st.session_state.operador_logado = None
            st.session_state.setor_logado = None
            st.rerun()
    with col_stats:
        # Estatísticas rápidas
        df = st.session_state.df_dados
        df_uso = df[df['Status'] == 'Em Uso']
        df_devolvidos = df[df['Status'] == 'Devolvido']
        st.metric("🟢 Em Uso", len(df_uso))
        st.metric("🔴 Devolvidas Hoje", len(df_devolvidos[df_devolvidos['Data_Retorno'] == datetime.now(FUSO_HORARIO_BRASIL).strftime("%d/%m/%Y")]))

    st.markdown("---")

    # Layout em duas colunas melhorado
    col_em_uso, col_devolvidos = st.columns(2, gap="large")

    with col_em_uso:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h4 style="margin:0; font-size: 18px;">🟢 Ferramentas em Uso (Tempo Real)</h4>
            </div>
        """, unsafe_allow_html=True)

        if not df_uso.empty:
            # Group by user only (regardless of date and time)
            grouped = df_uso.groupby(['Operador', 'Setor', 'Maquina'])

            for (operador, setor, maquina), group in grouped:
                with st.container(border=True):
                    foto_op = fotos_operadores.get(operador, "https://placehold.co/50x50/CCCCCC/000000?text=?")

                    c1, c2 = st.columns([0.5, 5])
                    with c1:
                        st.image(foto_op, width=60)
                    with c2:
                        st.markdown(f"👤 **{operador}** ({setor}) | 🏭 **{maquina}")
                        st.markdown(f"**{len(group)} ferramenta(s)**")
                        if st.button("🔄 Devolver Tudo", key=f"dev_all_{operador}_{maquina}", type="secondary", use_container_width=True):
                            agora = datetime.now(FUSO_HORARIO_BRASIL)
                            for idx in group.index:
                                st.session_state.df_dados.loc[idx, 'Data_Retorno'] = agora.strftime("%d/%m/%Y")
                                st.session_state.df_dados.loc[idx, 'Hora_Retorno'] = agora.strftime("%H:%M")
                                st.session_state.df_dados.loc[idx, 'Status'] = 'Devolvido'
                            if salvar_dados(st.session_state.df_dados):
                                st.rerun()
                            else:
                                st.error("❌ Não foi possível salvar a devolução. Tente novamente.")
                        st.markdown("---")
                        for num, (idx, row) in enumerate(group.iterrows(), 1):
                            with st.container(border=True):
                                col_num, col_tool, col_btn = st.columns([0.3, 5, 1])
                                with col_num:
                                    st.markdown(f"**{num}**")
                                with col_tool:
                                    st.markdown(f"**{row['Instrumento']}** ({row['Especificacao']})")
                                    st.markdown(f"📅 {row['Data_Retirada']} às {row['Hora_Retirada']}", help="Data de retirada")
                                with col_btn:
                                    if st.button("Devolver", key=f"dev_{row['ID']}", width='stretch'):
                                        agora = datetime.now(FUSO_HORARIO_BRASIL)
                                        st.session_state.df_dados.loc[idx, 'Data_Retorno'] = agora.strftime("%d/%m/%Y")
                                        st.session_state.df_dados.loc[idx, 'Hora_Retorno'] = agora.strftime("%H:%M")
                                        st.session_state.df_dados.loc[idx, 'Status'] = 'Devolvido'
                                        if salvar_dados(st.session_state.df_dados):
                                            st.rerun()
                                        else:
                                            st.error("❌ Não foi possível salvar a devolução. Tente novamente.")
        else:
            st.info("Nenhuma ferramenta retirada no momento.")

    with col_devolvidos:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h4 style="margin:0; font-size: 18px;">🔴 Histórico de Devoluções</h4>
            </div>
        """, unsafe_allow_html=True)

        if not df_devolvidos.empty:
            # Criar colunas combinadas de data/hora
            df_devolvidos = df_devolvidos.copy()
            df_devolvidos['Data/Horas - Retirada'] = df_devolvidos['Data_Retirada'] + ' às ' + df_devolvidos['Hora_Retirada']
            df_devolvidos['Data/Horas - Devolução'] = df_devolvidos['Data_Retorno'] + ' às ' + df_devolvidos['Hora_Retorno']
            df_display = df_devolvidos[['Instrumento', 'Especificacao', 'Operador', 'Maquina', 'Data/Horas - Retirada', 'Data/Horas - Devolução']]
            st.dataframe(df_display, hide_index=True, use_container_width=True)
        else:
            st.info("Nenhuma devolução registrada ainda.")

    # --- GRÁFICO DE FERRAMENTAS MAIS USADAS ---
    st.markdown("---")
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
        fig.update_layout(
            xaxis_title="Tipo de Ferramenta",
            yaxis_title="Quantidade em Uso",
            yaxis=dict(tickmode='linear', tick0=0, dtick=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum dado disponível para o gráfico.")

elif st.session_state.tela_atual == 'retirada':
    # --- TELA 2: FLUXO DE RETIRADA ---
    col_titulo, col_voltar = st.columns([8, 2])
    with col_titulo:
        st.title("🛠️ Nova Retirada")
    with col_voltar:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔙 Cancelar e Voltar", width='stretch'):
            st.session_state.tela_atual = 'dashboard'
            st.session_state.ferramentas_selecionadas = []
            st.session_state.operador_logado = None
            st.session_state.setor_logado = None
            st.session_state.passo_retirada = 1
            st.rerun()

    st.markdown("---")

    # --- PASSO 1: ESCOLHER SETOR ---
    if st.session_state.passo_retirada == 1:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="margin:0;">🏢 Passo 1: Qual é o seu setor?</h3>
            </div>
        """, unsafe_allow_html=True)

        setor_escolhido = st.selectbox("Selecione seu Setor:", ["Selecione..."] + list(setores_operadores.keys()), label_visibility="collapsed")

        if setor_escolhido != "Selecione...":
            st.session_state.setor_logado = setor_escolhido
            st.session_state.passo_retirada = 2
            st.rerun()

    # --- PASSO 2: ESCOLHER NOME ---
    elif st.session_state.passo_retirada == 2:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="margin:0;">👤 Passo 2: Qual é o seu nome?</h3>
                <p style="margin:5px 0 0 0; opacity: 0.9;">Setor: {st.session_state.setor_logado}</p>
            </div>
        """, unsafe_allow_html=True)

        col_voltar_passo, _ = st.columns([1, 9])
        with col_voltar_passo:
            if st.button("⬅️ Voltar", width='stretch'):
                st.session_state.setor_logado = None
                st.session_state.passo_retirada = 1
                st.rerun()

        st.markdown("---")

        nomes_setor = setores_operadores[st.session_state.setor_logado]
        st.write(f"Operadores do setor: **{st.session_state.setor_logado}** (Clique na sua foto)")

        # Mostra as fotos em 6 colunas para aproveitar melhor o espaço
        colunas_por_linha = 6
        for i in range(0, len(nomes_setor), colunas_por_linha):
            cols = st.columns(colunas_por_linha)
            for j in range(colunas_por_linha):
                if i + j < len(nomes_setor):
                    nome_op = nomes_setor[i + j]
                    with cols[j]:
                        st.image(fotos_operadores[nome_op], width=70)
                        if st.button(f"{nome_op}", key=f"btn_login_{nome_op}", width='content'):
                            st.session_state.operador_logado = nome_op
                            st.session_state.passo_retirada = 3
                            st.rerun()

    # --- PASSO 3: ESCOLHER MÁQUINA ---
    elif st.session_state.passo_retirada == 3:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="margin:0;">🏭 Passo 3: Onde você vai usar?</h3>
                <p style="margin:5px 0 0 0; opacity: 0.9;">{st.session_state.operador_logado} - {st.session_state.setor_logado}</p>
            </div>
        """, unsafe_allow_html=True)

        col_voltar_passo, _ = st.columns([1, 9])
        with col_voltar_passo:
            if st.button("⬅️ Voltar", width='stretch'):
                st.session_state.operador_logado = None
                st.session_state.passo_retirada = 2
                st.rerun()

        st.markdown("---")

        maquina_selecionada = st.selectbox("Selecione a Máquina ou Local de Uso:", maquinas_lista)

        if maquina_selecionada != "Selecione...":
            st.session_state.maquina_selecionada = maquina_selecionada
            st.session_state.passo_retirada = 4
            st.rerun()

    # --- PASSO 4: ESCOLHER FERRAMENTAS ---
    elif st.session_state.passo_retirada == 4:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="margin:0;">🔧 Passo 4: O que você vai retirar?</h3>
                <p style="margin:5px 0 0 0; opacity: 0.9;">{st.session_state.operador_logado} - {st.session_state.setor_logado} - {st.session_state.maquina_selecionada}</p>
            </div>
        """, unsafe_allow_html=True)

        col_voltar_passo, _ = st.columns([1, 9])
        with col_voltar_passo:
            if st.button("⬅️ Voltar", width='stretch'):
                st.session_state.maquina_selecionada = None
                st.session_state.passo_retirada = 3
                st.rerun()

        st.markdown("---")

        maquina_selecionada = st.session_state.maquina_selecionada
        
        # Mostrar ferramentas selecionadas
        if st.session_state.ferramentas_selecionadas:
            st.markdown("**Ferramentas selecionadas:**")
            for ferramenta in st.session_state.ferramentas_selecionadas:
                st.markdown(f"- {ferramenta}")
        
        # Adicionada a aba "Outras Ferramentas" no final
        tabs = st.tabs(["Porca Calibradora", "Micrômetros", "Súbitos", "Relógio Comparador", "Paquímetro Digital", "Outras Ferramentas ➕"])

        def item_disponivel(instrumento, especificacao):
            df = st.session_state.df_dados
            em_uso = df[(df['Instrumento'] == instrumento) & (df['Especificacao'] == especificacao) & (df['Status'] == 'Em Uso')]
            return em_uso.empty

        def item_ja_selecionado(categoria, espec):
            return f"{categoria} - {espec}" in st.session_state.ferramentas_selecionadas

        def render_cards(categoria, idx_tab):
            with tabs[idx_tab]:
                st.markdown(f"##### {categoria}")
                itens = estoque[categoria]
                colunas_por_linha = 6
                
                for i in range(0, len(itens), colunas_por_linha):
                    cols = st.columns(colunas_por_linha)
                    for j in range(colunas_por_linha):
                        if i + j < len(itens):
                            espec = itens[i + j]
                            with cols[j]:
                                st.container(border=True)
                                texto_img = espec.replace(' ', '')
                                st.image(f"https://placehold.co/150x150/EEEEEE/31343C?text={texto_img}", width=70)
                                st.markdown(f"**{espec}**")
                                
                                if item_disponivel(categoria, espec):
                                    if item_ja_selecionado(categoria, espec):
                                        col_sel, col_desm = st.columns(2)
                                        with col_sel:
                                            st.success("Selecionado")
                                        with col_desm:
                                            if st.button("Desmarcar", key=f"btn_desm_{categoria}_{espec}", width='stretch'):
                                                ferramenta_key = f"{categoria} - {espec}"
                                                st.session_state.ferramentas_selecionadas.remove(ferramenta_key)
                                                st.rerun()
                                    else:
                                        if st.button("Selecionar", key=f"btn_sel_{categoria}_{espec}", width='stretch'):
                                            ferramenta_key = f"{categoria} - {espec}"
                                            st.session_state.ferramentas_selecionadas.append(ferramenta_key)
                                            st.success(f"Adicionado: {espec}")
                                            st.rerun()
                                else:
                                    st.error("Em uso")

        # Renderiza as abas padrão
        render_cards('Porca Calibradora', 0)
        render_cards('Micrômetro', 1)
        render_cards('Súbito', 2)
        render_cards('Relógio Comparador', 3)
        render_cards('Paquímetro Digital', 4)

        # Aba "Outras Ferramentas" (Campo de Texto)
        with tabs[5]:
            st.markdown("##### 🛠️ Outras Ferramentas (Diversas)")
            st.info("Use este espaço para retirar alicates, martelos, chaves, etc.")
            
            outra_ferramenta = st.text_input("Digite o nome ou descrição da ferramenta:")
            
            col_sel, col_desm = st.columns(2)
            with col_sel:
                if st.button("Selecionar esta ferramenta digitada", width='stretch'):
                    if outra_ferramenta.strip() == "":
                        st.warning("Por favor, digite o nome da ferramenta antes de selecionar.")
                    else:
                        ferramenta_key = f"Ferramenta Diversa - {outra_ferramenta}"
                        if ferramenta_key not in st.session_state.ferramentas_selecionadas:
                            st.session_state.ferramentas_selecionadas.append(ferramenta_key)
                            st.success(f"Adicionado: {outra_ferramenta}")
                            st.rerun()
                        else:
                            st.warning("Esta ferramenta já foi selecionada.")

        st.markdown("---")

        # --- CONFIRMAÇÃO FINAL ---
        if st.button("✅ Confirmo a retirada em meu nome", width='stretch', type="primary"):
            if not st.session_state.ferramentas_selecionadas:
                st.warning("⚠️ Atenção: Por favor, selecione pelo menos uma ferramenta nas abas.")
            else:
                agora = datetime.now(FUSO_HORARIO_BRASIL)
                for ferramenta in st.session_state.ferramentas_selecionadas:
                    categoria, detalhe = ferramenta.split(" - ", 1)
                    novo_id = agora.strftime('%Y%m%d%H%M%S') + str(len(st.session_state.df_dados))

                    novo_registro = {
                        'ID': novo_id,
                        'Instrumento': categoria,
                        'Especificacao': detalhe,
                        'Operador': st.session_state.operador_logado,
                        'Setor': st.session_state.setor_logado,
                        'Maquina': st.session_state.maquina_selecionada,
                        'Data_Retirada': agora.strftime("%d/%m/%Y"),
                        'Hora_Retirada': agora.strftime("%H:%M"),
                        'Data_Retorno': "",
                        'Hora_Retorno': "",
                        'Status': "Em Uso"
                    }

                    df_novo = pd.DataFrame([novo_registro])
                    st.session_state.df_dados = pd.concat([st.session_state.df_dados, df_novo], ignore_index=True)
                if salvar_dados(st.session_state.df_dados):
                    # Limpa tudo e volta para o Dashboard
                    st.session_state.ferramentas_selecionadas = []
                    st.session_state.operador_logado = None
                    st.session_state.setor_logado = None
                    st.session_state.maquina_selecionada = None
                    st.session_state.passo_retirada = 1
                    st.session_state.tela_atual = 'dashboard'
                    st.rerun()
                else:
                    st.error("❌ Não foi possível salvar a retirada. Tente novamente.")
