import streamlit as st
import pandas as pd
import plotly.express as px
from utils.sheets import ler_pedidos

st.set_page_config(page_title="Setor de Produção", page_icon="🏭")

st.title("🏭 Setor de Produção")
st.write("Acompanhe a quantidade de produtos, subprodutos e cascas para produção.")

# -------------------------------------------------------------
# LER PEDIDOS
# -------------------------------------------------------------
pedidos_df = ler_pedidos()

if pedidos_df.empty:
    st.info("Nenhum pedido registrado.")
    st.stop()

pedidos_df["Quantidade"] = pedidos_df["Quantidade"].astype(int)

# -------------------------------------------------------------
# PAINEL 1 — PRODUTOS POR DIA
# -------------------------------------------------------------
st.header("📦 Produtos por Data da Entrega")

produtos_filtro = st.multiselect("Filtrar Produtos:", sorted(pedidos_df["Produto"].unique()))
datas_filtro = st.multiselect("Filtrar Datas:", sorted(pedidos_df["Data da Entrega"].unique()))

df1 = pedidos_df.copy()

if produtos_filtro:
    df1 = df1[df1["Produto"].isin(produtos_filtro)]

if datas_filtro:
    df1 = df1[df1["Data da Entrega"].isin(datas_filtro)]

df_produtos = df1.groupby(["Data da Entrega", "Produto"])["Quantidade"].sum().reset_index()

st.dataframe(df_produtos, width="stretch")

fig1 = px.bar(
    df_produtos,
    x="Data da Entrega",
    y="Quantidade",
    color="Produto",
    barmode="group",
    title="Quantidade de Produtos por Data",
    text_auto=".0f"
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# -------------------------------------------------------------
# PAINEL 2 — SUBPRODUTOS POR DIA
# -------------------------------------------------------------
st.header("🍫 Subprodutos por Data")

df_sub = pedidos_df[pedidos_df["Subproduto"] != ""].copy()
df_sub["Subproduto"] = df_sub["Subproduto"].str.split(", ")
df_sub = df_sub.explode("Subproduto")

sub_filtro = st.multiselect("Filtrar Subprodutos:", sorted(df_sub["Subproduto"].unique()))
datas_sub = st.multiselect("Filtrar Datas:", sorted(df_sub["Data da Entrega"].unique()))

df2 = df_sub.copy()

if sub_filtro:
    df2 = df2[df2["Subproduto"].isin(sub_filtro)]

if datas_sub:
    df2 = df2[df2["Data da Entrega"].isin(datas_sub)]

df_subprodutos = df2.groupby(["Data da Entrega", "Subproduto"])["Quantidade"].sum().reset_index()

st.dataframe(df_subprodutos, width="stretch")

fig2 = px.bar(
    df_subprodutos,
    x="Data da Entrega",
    y="Quantidade",
    color="Subproduto",
    barmode="group",
    title="Quantidade de Subprodutos por Data",
    text_auto=".0f"
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# -------------------------------------------------------------
# PAINEL 3 — CASCAS POR DIA
# -------------------------------------------------------------
st.header("🥚 Cascas Necessárias por Data")
st.subheader("📋 Tabela: Quantidade de Cascas por Data (Agrupada)")


def calcular_casca(row):
    prod = row["Produto"]
    qtd  = int(row["Quantidade"])
    cascas = []

    # MINI CONFEITEIRO — receita fixa
    if prod == "Mini Confeiteiro":
        return [
            ("Casca Mini Preta", qtd * 2),
            ("Casca Mini Branca", qtd * 1)
        ]

    # KIT MINI OVOS — cada subproduto gera 1 casca
    if prod == "Kit Mini Ovos":
        subs = row["Subproduto"].split(", ") if row["Subproduto"] else []
        for sub in subs:
            if sub in ["Ovo Mini Confete", "Ovo Mini Kinder", "Ovo Mini Ferrero",
                       "Ovo Mini Crocante", "Ovo Mini ao Leite"]:
                cascas.append(("Casca Mini Preta", qtd))
            if sub in ["Ovo Mini Lotus", "Ovo Mini Óreo"]:
                cascas.append(("Casca Mini Branca", qtd))
        return cascas

    # OVOS GRANDES
    if prod in ["Ovo Ferrero", "Ovo Kinder", "Ovo Brownie", "Ovo Sensação"]:
        cascas.append(("Casca Grande Preta", qtd))

    if prod == "Ovo Lótus":
        cascas.append(("Casca Grande Branca", qtd))

    # SUBPRODUTOS PARA OUTROS PRODUTOS
    if row["Subproduto"]:
        subs = row["Subproduto"].split(", ")
        for sub in subs:
            if sub in ["Ovo Mini Confete", "Ovo Mini Kinder", "Ovo Mini Ferrero",
                       "Ovo Mini Crocante", "Ovo Mini ao Leite"]:
                cascas.append(("Casca Mini Preta", qtd))
            if sub in ["Ovo Mini Lotus", "Ovo Mini Óreo"]:
                cascas.append(("Casca Mini Branca", qtd))

    return cascas


linhas = []
for _, row in pedidos_df.iterrows():
    for tipo, quantidade in calcular_casca(row):
        linhas.append([row["Data da Entrega"], tipo, quantidade])

df_cascas = pd.DataFrame(linhas, columns=["Data da Entrega", "Tipo de Casca", "Quantidade"])



# -------------------------
# FILTROS NOVOS DO PAINEL 3
# -------------------------
filtro_data3 = st.multiselect("Filtrar Datas no Painel 3:", sorted(df_cascas["Data da Entrega"].unique()))
filtro_tipo3 = st.multiselect("Filtrar Tipo de Casca:", sorted(df_cascas["Tipo de Casca"].unique()))

df_cascas_filtrado = df_cascas.copy()

if filtro_data3:
    df_cascas_filtrado = df_cascas_filtrado[df_cascas_filtrado["Data da Entrega"].isin(filtro_data3)]

if filtro_tipo3:
    df_cascas_filtrado = df_cascas_filtrado[df_cascas_filtrado["Tipo de Casca"].isin(filtro_tipo3)]

st.subheader("📋 Tabela: Quantidade de Cascas por Data (Agrupada)")

tabela_cascas = (
    df_cascas_filtrado
    .groupby(["Data da Entrega", "Tipo de Casca"])["Quantidade"]
    .sum()
    .reset_index()
    .sort_values(["Data da Entrega", "Tipo de Casca"])
)

tabela_cascas = tabela_cascas.rename(columns={
    "Data da Entrega": "Data",
    "Tipo de Casca": "Tipo de Casca",
    "Quantidade": "Quantidade Necessária"
})

st.dataframe(tabela_cascas, use_container_width=True)


fig3 = px.bar(
    df_cascas_filtrado.groupby(["Data da Entrega", "Tipo de Casca"])["Quantidade"].sum().reset_index(),
    x="Data da Entrega",
    y="Quantidade",
    color="Tipo de Casca",
    barmode="group",
    title="Quantidade de Cascas Necessárias por Data",
    text_auto=".0f"
)
st.plotly_chart(fig3, use_container_width=True)