import streamlit as st
import pandas as pd
#from utils.sheets import ler_sheet, gravar_sheet
from utils.sheets import ler_produtos


st.set_page_config(page_title="Cadastro de Produtos", page_icon="📦")

st.title("📦 Produtos Cadastrados")
st.write("Informações sobre valores de preços, custo de fabricação e prolabore. Obs,: Dados não editáveis")
# ------------------------------
# PRODUTOS INICIAIS (APENAS SE A PLANILHA ESTIVER VAZIA)
# ------------------------------

produtos_iniciais = pd.DataFrame([
    ["Cenoura", 25.00, 17.40, 4.60],
    ["Trio Brownie", 29.00, 15.03, 1.53],
    ["Kit Mini Ovos", 30.00, 22.20, 1.53],
    ["Beats", 35.00, 26.04, 1.53],
    ["Mini Confeiteiro", 49.00, 33.65, 3.07],
    ["Ovo Sensação", 79.00, 46.71, 4.60],
    ["Ovo Kinder", 79.00, 51.92, 4.60],
    ["Ovo Ferrero", 79.00, 48.72, 4.60],
    ["Ovo Lótus", 79.00, 43.54, 4.60],
    ["Ovo Brownie", 85.00, 52.99, 4.60],
    ["Bolo Cenoura", 65.00, 44.73, 0.31],
], columns=["Produto", "Preço", "Custo de Fabricação", "Prolabore"])

# ------------------------------
# CARREGAR PLANILHA OU CRIAR AUTOMATICAMENTE
# ------------------------------

try:
    #df = ler_sheet("Produtos")
    df = ler_produtos()
    if df.empty:
        df = produtos_iniciais.copy()
        gravar_sheet("Produtos", df)
except:
    df = produtos_iniciais.copy()
    gravar_sheet("Produtos", df)

# ------------------------------
# CONVERSÃO SEGURA DE NÚMEROS
# ------------------------------

def converter_numero(valor):
    if isinstance(valor, float) or isinstance(valor, int):
        return float(valor)
    if isinstance(valor, str):
        valor = valor.strip()
        if "," in valor:
            valor = valor.replace(".", "").replace(",", ".")
        try:
            return float(valor)
        except:
            return None
    return None

for col in ["Preço", "Custo de Fabricação", "Prolabore"]:
    df[col] = df[col].apply(converter_numero)

# ------------------------------
# TABELA EDITÁVEL
# ------------------------------

df_editado = st.data_editor(
    df,
    width="stretch",   # Substitui use_container_width
    num_rows="dynamic",
    column_config={
        "Preço": st.column_config.NumberColumn(format="%.2f"),
        "Custo de Fabricação": st.column_config.NumberColumn(format="%.2f"),
        "Prolabore": st.column_config.NumberColumn(format="%.2f")
    }
)

# ------------------------------
# BOTÃO DE SALVAMENTO
# ------------------------------

#if st.button("💾 Salvar Alterações"):
    #gravar_sheet("Produtos", df_editado)
 #   salvar_produtos(df_editado)
  #  df_editado.to_csv("data/produtos.csv", index=False, encoding="utf-8")
   # st.success("Alterações salvas no Google Sheets!")

# ------------------------------
# EXIBIR TABELA FINAL
# ------------------------------

#st.subheader("📋 Produtos Atuais")
#st.dataframe(df_editado, width="stretch")