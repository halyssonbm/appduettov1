import streamlit as st

st.set_page_config(
    page_title="Gestão Páscoa",
    page_icon="🐰",
    layout="centered"
)

# ---------------------------------------------
# CSS GLOBAL PARA MOBILE (RESPONSIVE DESIGN)
# ---------------------------------------------
st.markdown("""
<style>

html, body, [class*="css"]  {
    -webkit-user-select: none;
    user-select: none;
}

/* Reduz margens laterais em telas pequenas */
@media (max-width: 600px) {
    .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        padding-top: 1rem !important;
    }
}

/* Tabelas responsivas */
.dataframe {
    width: 100% !important;
    overflow-x: auto !important;
    display: block !important;
}

/* Gráficos Plotly para caber na tela */
.js-plotly-plot {
    width: 100% !important;
}

/* Botões maiores e mais fáceis de clicar */
.stButton>button {
    width: 100%;
    padding: 0.8rem;
    font-size: 1.1rem;
}

/* Inputs mais largos */
.stTextInput>div>div>input {
    font-size: 1rem;
    padding: 0.5rem;
}

/* Selectbox mais confortável */
.stSelectbox>div>div {
    font-size: 1rem;
}

/* Cards KPI empilhados no mobile */
@media (max-width: 600px) {
    .row-widget.stHorizontal > div {
        width: 100% !important;
        display: block !important;
        margin-bottom: 1rem !important;
    }
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* Suaviza a rolagem no celular */
html {
    scroll-behavior: smooth;
}

/* Reduz o “ar” entre os elementos no mobile */
.stMarkdown, .stTextInput, .stSelectbox, .stNumberInput {
    margin-bottom: 0.65rem !important;
}

/* Ajuste fino de tabelas — linhas mais compactas */
table td, table th {
    padding: 4px !important;
    font-size: 0.95rem !important;
}

/* Tabs mais amigáveis ao toque */
.stTabs [role="tab"] {
    font-size: 1.05rem !important;
    padding: 0.7rem 1rem !important;
}

/* Evita que KPIs fiquem colados demais */
div[data-testid="column"] {
    padding: 0.2rem !important;
}

</style>
""", unsafe_allow_html=True)


st.title("🐰 Gestão de Vendas – Páscoa 2026")

st.write("Use o menu lateral para acessar as páginas do sistema.")