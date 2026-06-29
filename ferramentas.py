import streamlit as st
import pandas as pd
from datetime import datetime
import os
import pytz
from dados_comuns import setores_operadores, maquinas_lista, estoque

# --- CONFIGURAÇÃO INICIAL DA PÁGINA ---
st.set_page_config(
    page_title="Controle de Ferramentas - Tempo Real", layout="wide")

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

# --- 1. FUNÇÕES DE BANCO DE DADOS (CSV) ---


def carregar_dados():
    if os.path.exists(ARQUIVO_CSV):
        df = pd.read_csv(ARQUIVO_CSV, sep=';',
                         encoding='utf-8-sig', dtype=str).fillna("")
        # Se o CSV antigo não tiver a coluna 'Setor', nós adicionamos para não dar erro
        if 'Setor' not in df.columns:
            df.insert(4, 'Setor', 'Não Informado')
        return df
    else:
        return pd.DataFrame(columns=['ID', 'Instrumento', 'Especificacao', 'Operador', 'Setor', 'Maquina', 'Data_Retirada', 'Hora_Retirada', 'Data_Retorno', 'Hora_Retorno', 'Status'])


def salvar_dados(df):
    try:
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

# Função utilitária para gerar placeholder de foto por nome (uso no modo somente visualização)


def foto_por_nome(nome):
    cores = ['4A90E2', '50E3C2', 'F5A623',
             'D0021B', 'BD10E0', '8B572A', '417505']
    cor = cores[abs(hash(nome)) % len(cores)]
    return f"https://placehold.co/150x150/{cor}/FFFFFF?text={nome.replace(' ', '+')}"


# ==========================================
# DEFINIÇÃO DE ACESSO VIA LINK (URL)
# ==========================================
# Por padrão, usamos o modo interativo (Retirada/Devolução).
# O modo "Chão de Fábrica (Apenas Visão)" permanece acessível via
# parâmetro de URL `?acesso=chao` quando necessário.
modo_acesso = "Qualidade (Interativo)"

# Se `acesso=chao` na URL, exibe apenas a visão pública (somente leitura).
if "acesso" in st.query_params and st.query_params["acesso"] == "chao":
    modo_acesso = "Chão de Fábrica (Apenas Visão)"


# ==========================================
# TELA ESPELHO: CHÃO DE FÁBRICA (LINK NORMAL)
# ==========================================
if modo_acesso == "Chão de Fábrica (Apenas Visão)":
    st.title("🏭 Ferramentas no Chão de Fábrica")
    st.markdown(
        "*Visão simplificada — apenas leitura. Retiradas/Devoluções via Qualidade.*")

    col_refresh, _ = st.columns([2, 8])
    with col_refresh:
        if st.button("🔄 Atualizar Tela", use_container_width=True):
            st.session_state.df_dados = carregar_dados()
            st.rerun()

    st.markdown("---")

    df = st.session_state.df_dados
    df_uso = df[df['Status'] == 'Em Uso']

    if not df_uso.empty:
        grouped = df_uso.groupby(['Operador', 'Setor', 'Maquina'])
        for (operador, setor, maquina), group in grouped:
            with st.container():
                foto_op = foto_por_nome(operador)
                c1, c2 = st.columns([0.5, 5])
                with c1:
                    st.image(foto_op, width=60)
                with c2:
                    st.markdown(
                        f"👤 **{operador}** ({setor}) | 🏭 **{maquina}**")
                    st.markdown(f"**{len(group)} ferramenta(s)**")
                    for idx, row in group.iterrows():
                        st.markdown(
                            f"- **{row['Instrumento']}** ({row['Especificacao']}) — 📅 {row['Data_Retirada']} às {row['Hora_Retirada']}")
    else:
        st.success("✅ Nenhuma ferramenta retida no chão de fábrica no momento.")

# ==========================================
# TELAS DA QUALIDADE (LINK SECRETO)
# ==========================================
elif modo_acesso == "Qualidade (Interativo)":

    # Geração automática de fotos temporárias para todos os operadores
    todos_operadores = [nome for lista in setores_operadores.values()
                        for nome in lista]
    # Cores diferentes para dar um visual legal
    cores = ['4A90E2', '50E3C2', 'F5A623',
             'D0021B', 'BD10E0', '8B572A', '417505']
    fotos_operadores = {
        nome: f"https://placehold.co/150x150/{cores[i % len(cores)]}/FFFFFF?text={nome.replace(' ', '+')}" for i, nome in enumerate(todos_operadores)}

    # ==========================================
    # LÓGICA DE NAVEGAÇÃO DE TELAS
    # ==========================================

    if st.session_state.tela_atual == 'dashboard':
        # --- TELA 1: DASHBOARD EM TEMPO REAL ---
        st.title("📊 Painel de Ferramentas - Tempo Real")

        col_btn, _ = st.columns([2, 8])
        with col_btn:
            if st.button("➕ Nova Retirada", width='stretch', type="primary"):
                st.session_state.tela_atual = 'retirada'
                st.session_state.operador_logado = None
                st.session_state.setor_logado = None
                st.rerun()

        st.markdown("---")

        df = st.session_state.df_dados
        col_em_uso, col_devolvidos = st.columns(2)

        with col_em_uso:
            st.markdown("""
                <div style="background-color: #d4edda; padding: 10px; border-radius: 5px; color: #155724; margin-bottom: 15px;">
                    <h4 style="margin:0;">🟢 Ferramentas em Uso (Tempo Real)</h4>
                </div>
            """, unsafe_allow_html=True)

            df_uso = df[df['Status'] == 'Em Uso']

            if not df_uso.empty:
                # Group by user only (regardless of date and time)
                grouped = df_uso.groupby(['Operador', 'Setor', 'Maquina'])

                for (operador, setor, maquina), group in grouped:
                    with st.container(border=True):
                        foto_op = fotos_operadores.get(
                            operador, "https://placehold.co/50x50/CCCCCC/000000?text=?")

                        c1, c2 = st.columns([0.5, 5])
                        with c1:
                            st.image(foto_op, width=60)
                        with c2:
                            st.markdown(
                                f"👤 **{operador}** ({setor}) | 🏭 **{maquina}")
                            st.markdown(f"**{len(group)} ferramenta(s)**")
                            if st.button("🔄 Devolver Tudo", key=f"dev_all_{operador}_{maquina}", type="secondary"):
                                agora = datetime.now(FUSO_HORARIO_BRASIL)
                                for idx in group.index:
                                    st.session_state.df_dados.loc[idx, 'Data_Retorno'] = agora.strftime("%d/%m/%Y")
                                    st.session_state.df_dados.loc[idx, 'Hora_Retorno'] = agora.strftime("%H:%M")
                                    st.session_state.df_dados.loc[idx, 'Status'] = 'Devolvido'
                                if salvar_dados(st.session_state.df_dados):
                                    st.rerun()
                                else:
                                    st.error("❌ Não foi possível salvar a devolução. Tente novamente.")
                            for num, (idx, row) in enumerate(group.iterrows(), 1):
                                with st.container(border=True):
                                    col_num, col_tool, col_btn = st.columns(
                                        [0.3, 5, 1])
                                    with col_num:
                                        st.markdown(f"**{num}**")
                                    with col_tool:
                                        st.markdown(
                                            f"**{row['Instrumento']}** ({row['Especificacao']})")
                                        st.markdown(
                                            f"📅 {row['Data_Retirada']} às {row['Hora_Retirada']}", help="Data de retirada")
                                    with col_btn:
                                        if st.button("Devolver", key=f"dev_{row['ID']}", width='stretch'):
                                            agora = datetime.now(
                                                FUSO_HORARIO_BRASIL)
                                            st.session_state.df_dados.loc[idx, 'Data_Retorno'] = agora.strftime(
                                                "%d/%m/%Y")
                                            st.session_state.df_dados.loc[idx, 'Hora_Retorno'] = agora.strftime(
                                                "%H:%M")
                                            st.session_state.df_dados.loc[idx,
                                                                          'Status'] = 'Devolvido'
                                            if salvar_dados(st.session_state.df_dados):
                                                st.rerun()
                                            else:
                                                st.error(
                                                    "❌ Não foi possível salvar a devolução. Tente novamente.")
            else:
                st.info("Nenhuma ferramenta retirada no momento.")

        with col_devolvidos:
            st.markdown("""
                <div style="background-color: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24; margin-bottom: 15px;">
                    <h4 style="margin:0;">🔴 Histórico de Devoluções</h4>
                </div>
            """, unsafe_allow_html=True)

            df_devolvidos = df[df['Status'] == 'Devolvido']

            if not df_devolvidos.empty:
                # Criar colunas combinadas de data/hora
                df_devolvidos = df_devolvidos.copy()
                df_devolvidos['Data/Horas - Retirada'] = df_devolvidos['Data_Retirada'] + \
                    ' às ' + df_devolvidos['Hora_Retirada']
                df_devolvidos['Data/Horas - Devolução'] = df_devolvidos['Data_Retorno'] + \
                    ' às ' + df_devolvidos['Hora_Retorno']
                df_display = df_devolvidos[['Instrumento', 'Especificacao', 'Operador',
                                            'Maquina', 'Data/Horas - Retirada', 'Data/Horas - Devolução']]
                st.dataframe(df_display, hide_index=True)
            else:
                st.info("Nenhuma devolução registrada ainda.")

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
                st.rerun()

        st.markdown("---")

        # --- PASSO 1: LOGIN (POR SETOR) ---
        if st.session_state.operador_logado is None:
            st.subheader("👤 Passo 1: Quem é você?")

            # Filtro de setor primeiro
            setor_escolhido = st.selectbox("Selecione seu Setor:", [
                                           "Selecione..."] + list(setores_operadores.keys()))

            if setor_escolhido != "Selecione...":
                st.write(
                    f"Operadores do setor: **{setor_escolhido}** (Clique na sua foto)")
                nomes_setor = setores_operadores[setor_escolhido]

                # Mostra as fotos limitadas a 5 por linha
                colunas_por_linha = 5
                for i in range(0, len(nomes_setor), colunas_por_linha):
                    cols = st.columns(colunas_por_linha)
                    for j in range(colunas_por_linha):
                        if i + j < len(nomes_setor):
                            nome_op = nomes_setor[i + j]
                            with cols[j]:
                                st.image(
                                    fotos_operadores[nome_op], width='stretch')
                                if st.button(f"{nome_op}", key=f"btn_login_{nome_op}", width='content'):
                                    st.session_state.operador_logado = nome_op
                                    st.session_state.setor_logado = setor_escolhido
                                    st.rerun()
            st.stop()  # Interrompe a tela até o operador se identificar

        # --- SE O OPERADOR JÁ ESTIVER LOGADO ---
        col_foto_logado, col_dados_logado, col_trocar = st.columns([1, 8, 2])
        with col_foto_logado:
            st.image(
                fotos_operadores[st.session_state.operador_logado], width=60)
        with col_dados_logado:
            st.markdown(f"### Olá, {st.session_state.operador_logado}!")
            st.write(
                f"Setor: **{st.session_state.setor_logado}** | Siga para os próximos passos.")
        with col_trocar:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Trocar Operador", width='stretch'):
                st.session_state.operador_logado = None
                st.session_state.setor_logado = None
                st.session_state.ferramentas_selecionadas = []
                st.rerun()

        st.markdown("---")

        # --- PASSO 2: MÁQUINA / LOCAL ---
        st.subheader("🏭 Passo 2: Onde você vai usar?")
        maquina_selecionada = st.selectbox(
            "Selecione a Máquina ou Local de Uso:", maquinas_lista)

        st.markdown("---")

        # --- PASSO 3: FERRAMENTA (SÓ APARECE SE MÁQUINA FOR SELECIONADA) ---
        if maquina_selecionada != "Selecione...":
            st.subheader("🔧 Passo 3: O que você vai retirar?")
            st.write(
                f"🏭 Máquina: **{maquina_selecionada}** | Siga para os próximos passos.")

            # Mostrar ferramentas selecionadas
            if st.session_state.ferramentas_selecionadas:
                st.markdown("**Ferramentas selecionadas:**")
                for ferramenta in st.session_state.ferramentas_selecionadas:
                    st.markdown(f"- {ferramenta}")

            # Adicionada a aba "Outras Ferramentas" no final
            tabs = st.tabs(["Porca Calibradora", "Micrômetros", "Súbitos",
                           "Relógio Comparador", "Paquímetro Digital", "Outras Ferramentas ➕"])

            def item_disponivel(instrumento, especificacao):
                df = st.session_state.df_dados
                em_uso = df[(df['Instrumento'] == instrumento) & (
                    df['Especificacao'] == especificacao) & (df['Status'] == 'Em Uso')]
                return em_uso.empty

            def item_ja_selecionado(categoria, espec):
                return f"{categoria} - {espec}" in st.session_state.ferramentas_selecionadas

            def render_cards(categoria, idx_tab):
                with tabs[idx_tab]:
                    st.markdown(f"##### {categoria}")
                    itens = estoque[categoria]
                    colunas_por_linha = 5

                    for i in range(0, len(itens), colunas_por_linha):
                        cols = st.columns(colunas_por_linha)
                        for j in range(colunas_por_linha):
                            if i + j < len(itens):
                                espec = itens[i + j]
                                with cols[j]:
                                    st.container(border=True)
                                    texto_img = espec.replace(' ', '')
                                    st.image(
                                        f"https://placehold.co/150x150/EEEEEE/31343C?text={texto_img}", width='stretch')
                                    st.markdown(f"**{espec}**")

                                    if item_disponivel(categoria, espec):
                                        if item_ja_selecionado(categoria, espec):
                                            col_sel, col_desm = st.columns(2)
                                            with col_sel:
                                                st.success("Selecionado")
                                            with col_desm:
                                                if st.button("Desmarcar", key=f"btn_desm_{categoria}_{espec}", width='stretch'):
                                                    ferramenta_key = f"{categoria} - {espec}"
                                                    st.session_state.ferramentas_selecionadas.remove(
                                                        ferramenta_key)
                                                    st.rerun()
                                        else:
                                            if st.button("Selecionar", key=f"btn_sel_{categoria}_{espec}", width='stretch'):
                                                ferramenta_key = f"{categoria} - {espec}"
                                                st.session_state.ferramentas_selecionadas.append(
                                                    ferramenta_key)
                                                st.success(
                                                    f"Adicionado: {espec}")
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
                st.info(
                    "Use este espaço para retirar alicates, martelos, chaves, etc.")

                outra_ferramenta = st.text_input(
                    "Digite o nome ou descrição da ferramenta:")

                col_sel, col_desm = st.columns(2)
                with col_sel:
                    if st.button("Selecionar esta ferramenta digitada", width='stretch'):
                        if outra_ferramenta.strip() == "":
                            st.warning(
                                "Por favor, digite o nome da ferramenta antes de selecionar.")
                        else:
                            ferramenta_key = f"Ferramenta Diversa - {outra_ferramenta}"
                            if ferramenta_key not in st.session_state.ferramentas_selecionadas:
                                st.session_state.ferramentas_selecionadas.append(
                                    ferramenta_key)
                                st.success(f"Adicionado: {outra_ferramenta}")
                                st.rerun()
                            else:
                                st.warning(
                                    "Esta ferramenta já foi selecionada.")

        st.markdown("---")

        # --- PASSO 4: CONFIRMAÇÃO FINAL ---
        if st.button("✅ Confirmo a retirada em meu nome", width='stretch', type="primary"):
            if maquina_selecionada == "Selecione...":
                st.warning(
                    "⚠️ Atenção: Por favor, selecione a Máquina / Local no Passo 2.")
            elif not st.session_state.ferramentas_selecionadas:
                st.warning(
                    "⚠️ Atenção: Por favor, selecione pelo menos uma ferramenta nas abas do Passo 3.")
            else:
                agora = datetime.now(FUSO_HORARIO_BRASIL)
                for ferramenta in st.session_state.ferramentas_selecionadas:
                    categoria, detalhe = ferramenta.split(" - ", 1)
                    novo_id = agora.strftime(
                        '%Y%m%d%H%M%S') + str(len(st.session_state.df_dados))

                    novo_registro = {
                        'ID': novo_id,
                        'Instrumento': categoria,
                        'Especificacao': detalhe,
                        'Operador': st.session_state.operador_logado,
                        'Setor': st.session_state.setor_logado,
                        'Maquina': maquina_selecionada,
                        'Data_Retirada': agora.strftime("%d/%m/%Y"),
                        'Hora_Retirada': agora.strftime("%H:%M"),
                        'Data_Retorno': "",
                        'Hora_Retorno': "",
                        'Status': "Em Uso"
                    }

                    df_novo = pd.DataFrame([novo_registro])
                    st.session_state.df_dados = pd.concat(
                        [st.session_state.df_dados, df_novo], ignore_index=True)
                if salvar_dados(st.session_state.df_dados):
                    # Limpa tudo e volta para o Dashboard
                    st.session_state.ferramentas_selecionadas = []
                    st.session_state.operador_logado = None
                    st.session_state.setor_logado = None
                    st.session_state.tela_atual = 'dashboard'
                    st.rerun()
                else:
                    st.error(
                        "❌ Não foi possível salvar a retirada. Tente novamente.")
