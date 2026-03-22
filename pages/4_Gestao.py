import streamlit as st
import pandas as pd
import plotly.express as px
from utils.sheets import ler_produtos, ler_pedidos

# Função para cartão estilizado
def kpi_card(label, value, background="#FFFFFF"):
    st.markdown(
        f"""
        <div style="
            background:{background};
            padding:18px;
            border-radius:10px;
            border:1px solid #CCC;
            text-align:center;
            margin-bottom:10px;">
            <div style="font-size:16px; font-weight:600;">{label}</div>
            <div style="font-size:22px; font-weight:700; margin-top:6px;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.set_page_config(page_title="Gestão", page_icon="📊")

st.title("📊 Gestão – Financeiro e Relatórios")

# -------------------------------------------------------------
# LER PLANILHAS
# -------------------------------------------------------------
df_prod = ler_produtos()
df_ped = ler_pedidos()

if df_ped.empty:
    st.info("Nenhum pedido registrado ainda.")
    st.stop()

df_ped["Quantidade"] = df_ped["Quantidade"].astype(int)
#df_ped["Valor Total"] = df_ped["Valor Total"].astype(float)

df_ped["Valor Total"] = (
    df_ped["Valor Total"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .astype(float)
)


# -------------------------------------------------------------
# UNIR PEDIDOS COM PLANILHA PRODUTOS (Custo e Prolabore)
# -------------------------------------------------------------
df = df_ped.merge(df_prod, on="Produto", how="left")

df["Custo Total"] = df["Custo de Fabricação"] * df["Quantidade"]
df["Prolabore Total"] = df["Prolabore"] * df["Quantidade"]
df["Lucro Líquido"] = df["Valor Total"] - df["Custo Total"] + df["Prolabore Total"]



# -------------------------------------------------------------
# FILTROS
# -------------------------------------------------------------
st.sidebar.header("Filtros")

datas_unicas = sorted(df["Data da Entrega"].unique())
produtos_unicos = sorted(df["Produto"].unique())
clientes_unicos = sorted(df["Cliente"].unique())

f_data = st.sidebar.multiselect("Filtrar Data de Entrega:", datas_unicas)
f_prod = st.sidebar.multiselect("Filtrar Produto:", produtos_unicos)
f_cliente = st.sidebar.multiselect("Filtrar Cliente:", clientes_unicos)

df_filtrado = df.copy()

# -------------------------------------------------------------
# Subtotal por produto (valor correto para faturamento por produto)
# -------------------------------------------------------------
df_filtrado["Subtotal Produto"] = df_filtrado["Valor Total"] * (
    df_filtrado["Quantidade"] /
    df_filtrado.groupby("ID_Pedido")["Quantidade"].transform("sum")
)

if f_data:
    df_filtrado = df_filtrado[df_filtrado["Data da Entrega"].isin(f_data)]

if f_prod:
    df_filtrado = df_filtrado[df_filtrado["Produto"].isin(f_prod)]

if f_cliente:
    df_filtrado = df_filtrado[df_filtrado["Cliente"].isin(f_cliente)]

if df_filtrado.empty:
    st.warning("Nenhum pedido encontrado com os filtros selecionados.")
    st.stop()

# -------------------------------------------------------------
# KPIs (indicadores)
# -------------------------------------------------------------

# -------------------------------------------------------------
# AGRUPAR POR ID_Pedido PARA EVITAR DUPLICAR FATURAMENTO
# -------------------------------------------------------------

agregado = (
    df_filtrado.groupby("ID_Pedido")
    .agg({
        "Valor Total": "first",         # total do pedido (não duplicado)
        "Custo Total": "sum",           # somado por produto
        "Prolabore Total": "sum",       # somado por produto
        "Lucro Líquido": "sum",         # somado por produto
        "Data da Entrega": "first"      # 🔥 FUNDAMENTAL para o gráfico
    })
    .reset_index()
)


# Valores consolidados (NÃO duplicados)
total_fat = agregado["Valor Total"].sum()
total_custo = agregado["Custo Total"].sum()
total_prolab = agregado["Prolabore Total"].sum()

# 🔥 Lucro líquido correto (sem duplicidades)
total_lucro = total_fat - total_custo + total_prolab

# -------------------------------------------------------------
# DESCONTO por ID_Pedido (correto)
# -------------------------------------------------------------

# 1) Selecionar apenas as colunas necessárias
descontos_por_pedido = (
    df_filtrado[["ID_Pedido", "Desconto %"]]
    .groupby("ID_Pedido")
    .agg({"Desconto %": "max"})  # o desconto do pedido é único: o maior (ou o último)
    .reset_index()
)

# 2) Considerar apenas pedidos com desconto > 0
descontos_validos = descontos_por_pedido[descontos_por_pedido["Desconto %"] > 0]

# 3) Quantidade de pedidos com desconto
qtd_com_desconto = len(descontos_validos)

# 4) Desconto médio entre os pedidos que receberam
desconto_medio = (
    descontos_validos["Desconto %"].mean()
    if qtd_com_desconto > 0
    else 0.0
)

# Pedidos únicos (clientes atendidos)
total_pedidos = len(agregado)

# Ticket Médio correto
ticket_medio = total_fat / total_pedidos if total_pedidos > 0 else 0

# Lucro em %
lucro_percent = (total_lucro / total_fat * 100) if total_fat > 0 else 0


st.header("📌 Indicadores Gerais")



# Primeira linha: indicadores principais com destaque
colA, colB, colC = st.columns(3)

with colA:
    kpi_card(
        "Faturamento Total",
        f"R$ {total_fat:.2f}",
        background="#E3F2FD"  # azul claro
    )

with colB:
    kpi_card("Custo Total", f"R$ {total_custo:.2f}")

with colC:
    kpi_card("Prolabore Total", f"R$ {total_prolab:.2f}")

# Segunda linha: lucro com destaque + ticket + total pedidos
colD, colE, colF = st.columns(3)

with colD:
    kpi_card(
        "Lucro Líquido",
        f"R$ {total_lucro:.2f}",
        background="#E8F5E9"  # verde claro
    )

with colE:
    kpi_card("Ticket Médio", f"R$ {ticket_medio:.2f}")

with colF:
    kpi_card("Pedidos Realizados", total_pedidos)

# Terceira linha: lucro (%) e desconto médio
colG, colH = st.columns(2)

with colG:
    kpi_card("Lucro (%)", f"{lucro_percent:.1f}%")

with colH:
    kpi_card(
        "Desconto Médio (clientes que receberam)",
        f"{desconto_medio:.1f}%  •  {qtd_com_desconto} clientes"
    )







# -------------------------------------------------------------
# Cartão: Lucro em %
# -------------------------------------------------------------
lucro_percent = (total_lucro / total_fat * 100) if total_fat > 0 else 0
#st.metric("Lucro (%)", f"{lucro_percent:.1f}%")


# Clientes que receberam desconto
#df_desconto = df_filtrado[df_filtrado["Desconto %"] > 0]

#qtd_com_desconto = df_desconto["ID_Pedido"].nunique()

#if qtd_com_desconto > 0:
    #desconto_medio = df_desconto["Desconto %"].mean()
#else:
    #desconto_medio = 0.0

#st.metric(
    #"Desconto Médio (clientes que receberam)",
   #f"{desconto_medio:.1f}%",
    #f"{qtd_com_desconto} clientes"
#)


# -------------------------------------------------------------
# Tabela detalhada
# -------------------------------------------------------------
st.header("📄 Tabela de Pedidos (com cálculos)")

st.dataframe(df_filtrado, width="stretch")

# -------------------------------------------------------------
# Tabela: Clientes por dia (agenda de entregas)
# -------------------------------------------------------------

# -------------------------------------------------------------
# Tabela: Clientes por dia (agenda de entregas)
# -------------------------------------------------------------
st.header("📅 Entregas por Dia")

# Construindo tabela de agenda com produtos + subprodutos

def juntar_produtos(grupo):
    produtos = []
    for prod, sub, qt in zip(grupo["Produto"], grupo["Subproduto"], grupo["Quantidade"]):

        # Kit Mini Ovos → mostrar subprodutos
        if prod == "Kit Mini Ovos" and sub:
            produtos.append(f"{prod} ({sub}) — {qt} un")
        
        # Produtos com subprodutos (ex.: Ovo com confete)
        elif sub and sub != "":
            produtos.append(f"{prod} ({sub}) — {qt} un")
        
        # Produtos normais
        else:
            produtos.append(f"{prod} — {qt} un")

    return ", ".join(produtos)


agenda = (
    df_filtrado
    .groupby("ID_Pedido")
    .agg({
        "Data da Entrega": "first",
        "Cliente": "first",
        "Telefone": "first",
        "Produto": list,
        "Subproduto": list,
        "Quantidade": list
    })
    .reset_index()
)

agenda["Produtos"] = agenda.apply(lambda row: juntar_produtos(row), axis=1)

agenda = agenda[["Data da Entrega", "Cliente", "Telefone", "Produtos"]]
#agenda["Data da Entrega"] = pd.to_datetime(agenda["Data da Entrega"], format="%d/%m/%Y")
agenda = agenda.sort_values("Data da Entrega")

agenda = agenda.rename(columns={
    "Data da Entrega": "Data",
    "Cliente": "Nome",
    "Telefone": "Telefone"
})

#st.dataframe(agenda, width="stretch")

# -------------------------------------------------------------
# Tabela estilizada com quebra de linha na coluna Produtos
# -------------------------------------------------------------
st.markdown("""
<style>
.table-wrap-produtos td {
    white-space: normal !important;
    word-wrap: break-word !important;
    word-break: break-word !important;
    max-width: 300px !important;
}
.table-wrap-produtos th {
    white-space: normal !important;
}
</style>
""", unsafe_allow_html=True)

# Constrói a tabela HTML manualmente para permitir wrap
html = "<table class='table-wrap-produtos' style='width:100%; border-collapse: collapse;'>"
html += "<tr>"

for col in agenda.columns:
    html += f"<th style='border:1px solid #ccc; padding:6px; text-align:left;'>{col}</th>"
html += "</tr>"

for _, row in agenda.iterrows():
    html += "<tr>"
    for col in agenda.columns:
        valor = row[col]
        html += f"<td style='border:1px solid #ccc; padding:6px; vertical-align:top;'>{valor}</td>"
    html += "</tr>"

html += "</table>"

st.markdown(html, unsafe_allow_html=True)

# -------------------------------------------------------------
# Exportar relatório
# -------------------------------------------------------------
st.download_button(
    "📤 Exportar Relatório em CSV",
    df_filtrado.to_csv(index=False).encode("utf-8"),
    file_name="relatorio_gestao.csv",
    mime="text/csv"
)

st.markdown("---")

# -------------------------------------------------------------
# Gráfico: Faturamento por dia
# -------------------------------------------------------------
# -------------------------------------------------------------
# Gráfico: Faturamento por dia (CORRIGIDO)
# -------------------------------------------------------------
st.header("📈 Faturamento por dia")

df_fat = (
    agregado.groupby("Data da Entrega")["Valor Total"]
    .sum()
    .reset_index()
    #.sort_values("Data da Entrega")
)


df_fat["Data da Entrega"] = pd.to_datetime(df_fat["Data da Entrega"], format="%d/%m/%Y")
df_fat = df_fat.sort_values("Data da Entrega")


fig1 = px.bar(
    df_fat,
    x="Data da Entrega",
    y="Valor Total",
    color="Data da Entrega",
    title="Faturamento Total por Dia",
    labels={"Valor Total": "Faturamento (R$)"},
    text_auto=".2f"
)

fig1.update_layout(showlegend=False)
st.plotly_chart(fig1, width="stretch")


# -------------------------------------------------------------
# Gráfico: Produtos Mais Vendidos
# -------------------------------------------------------------
st.header("🍫 Produtos mais vendidos")

df_prod_count = df_filtrado.groupby("Produto")["Quantidade"].sum().reset_index()
fig3 = px.bar(
    df_prod_count,
    x="Produto",
    y="Quantidade",
    color="Produto",
    title="Produtos Mais Vendidos",
    text_auto=True
)
fig3.update_layout(showlegend=False)


st.plotly_chart(fig3, use_container_width=True)