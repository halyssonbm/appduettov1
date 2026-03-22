import streamlit as st
import pandas as pd
from datetime import datetime


# 🔄 PASSO 1 — Garantir que a mensagem existe
if "mensagem" not in st.session_state:
    st.session_state["mensagem"] = ""


from utils.sheets import (
    ler_produtos, ler_pedidos,
    salvar_pedidos, atualizar_linha_pedido
)
from PIL import Image, ImageDraw
import io


st.set_page_config(page_title="Pedidos", page_icon="🛍️")

produtos_df = ler_produtos()
precos = dict(zip(produtos_df["Produto"], produtos_df["Preço"]))

SUBPRODUTOS = [
    "Ovo Mini Confete", "Ovo Mini Óreo", "Ovo Mini Kinder",
    "Ovo Mini Ferrero", "Ovo Mini Crocante", "Ovo Mini Lotus",
    "Ovo Mini ao Leite"
]


def calcular_total(lista_produtos, lista_subs, lista_qt, desconto):
    itens = []
    total = 0

    for prod, subs, qt in zip(lista_produtos, lista_subs, lista_qt):

        # Regras especiais – manter como já está
        if prod == "Kit Mini Ovos":
            if not subs or len(subs) != 2 or subs[0] == "" or subs[1] == "":
                return itens, total

        preco_unit = precos[prod]

        # 🔥 subtotal SEM desconto
        subtotal_bruto = preco_unit * qt

        # 🔥 aplica o desconto POR ITEM
        if desconto > 0:
            subtotal_liquido = subtotal_bruto * (1 - desconto / 100)
        else:
            subtotal_liquido = subtotal_bruto

        # acumula no total
        total += subtotal_liquido

        itens.append({
            "Produto": prod,
            "Subproduto": ", ".join(subs),
            "Quantidade": qt,
            "Preço Unitário": preco_unit,
            "Subtotal": round(subtotal_liquido, 2)   # ✔ salva o valor CORRETO
        })

    return itens, round(total, 2)


def gerar_imagem(cliente, telefone, data_entrega, itens, total, desconto):
    txt = f"Cliente: {cliente}\nTelefone: {telefone}\nEntrega: {data_entrega}\n\n"
    for item in itens:
        txt += f"- {item['Produto']} → {item['Quantidade']} un → R$ {item['Subtotal']:.2f}\n"
        if item['Subproduto']:
            txt += f"  Subprodutos: {item['Subproduto']}\n"
    txt += f"\nTOTAL: R$ {total:.2f}"
    if desconto > 0:
        txt += f" (Desconto: {desconto}%)"
    img = Image.new("RGB", (900,700), "white")
    d = ImageDraw.Draw(img)
    d.text((20,20), txt, fill="black")
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return bio


st.title("🛍️ Pedidos")
aba = st.tabs(["Registrar Novo Pedido", "Editar Pedido"])


# -----------------------------------------------------------------------------
# REGISTRAR PEDIDO
# -----------------------------------------------------------------------------
with aba[0]:

    st.subheader("Registrar Pedido")
    
    # mostrar mensagem se houver
    #if st.session_state.get("mensagem"):
        #st.success(st.session_state["mensagem"])
        #st.session_state["mensagem"] = ""

    

    cliente = st.text_input("Cliente *")
    telefone = st.text_input("Telefone *")
    data_entrega = st.date_input("Data da Entrega *")

    st.markdown("---")
    st.subheader("Produtos")

    lista_produtos, lista_subs, lista_qt = [], [], []
    qt_itens = st.number_input("Quantidade de itens:", min_value=1, max_value=20)

    for i in range(qt_itens):

        st.write(f"### Item #{i+1}")
        prod = st.selectbox(
            f"Produto {i+1}",
            ["Selecione"] + list(produtos_df["Produto"]),
            key=f"prod_{i}"
        )

        if prod == "Kit Mini Ovos":
            s1 = st.selectbox("Subproduto 1", SUBPRODUTOS, key=f"s1_{i}")
            s2 = st.selectbox("Subproduto 2", SUBPRODUTOS, key=f"s2_{i}")
            subs = [s1, s2]
        else:
            subs = [""]

        qt = st.number_input(
            f"Quantidade {i+1}",
            min_value=1,
            max_value=9999,
            key=f"qt_{i}"
        )

        lista_produtos.append(prod)
        lista_subs.append(subs)
        lista_qt.append(qt)

    desconto = st.number_input("Desconto %", min_value=0, max_value=100)

    # -----------------------------------------------
# VALIDAR PRODUTOS ANTES DO RESUMO E DO BOTÃO
# -----------------------------------------------

if any(p == "Selecione" for p in lista_produtos):
    st.warning("Selecione todos os produtos para continuar.")
else:
    # cálculo somente quando tudo estiver preenchido
    itens, total = calcular_total(lista_produtos, lista_subs, lista_qt, desconto)

    st.markdown("---")
    st.write("### Resumo")
    for item in itens:
        st.write(f"{item['Produto']} → {item['Quantidade']} un → R$ {item['Subtotal']:.2f}")

    st.write(f"### Total → R$ {total:.2f}")

    # botão sempre visível quando tudo estiver correto
    if st.button("Salvar Pedido"):
        df = ler_pedidos()

        if df.empty:
            df = pd.DataFrame(columns=[
                "ID_Pedido","Cliente","Telefone","Data da Entrega",
                "Produto","Subproduto","Quantidade","Desconto %",
                "Valor Total"
            ])

        idp = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + cliente

        for item in itens:
            df.loc[len(df)] = [
                idp,
                cliente,
                telefone,
                data_entrega.strftime("%d/%m/%Y"),
                item["Produto"],
                item["Subproduto"],
                item["Quantidade"],
                desconto,
                total
            ]

        salvar_pedidos(df)
        st.session_state["mensagem"] = "Pedido registrado com sucesso!"
        st.rerun()
    
# -------------------------------------------------------------
# MENSAGEM APÓS SALVAR (APARECE NO LUGAR CERTO)
# -------------------------------------------------------------
    if st.session_state.get("mensagem"):
        st.success(st.session_state["mensagem"])
        st.session_state["mensagem"] = ""
    
    

# -----------------------------------------------------------------------------
# EDITAR PEDIDO
# -----------------------------------------------------------------------------
with aba[1]:
    

    if st.session_state["mensagem"]:
        st.success(st.session_state["mensagem"])
        st.session_state["mensagem"] = ""


    #st.write("DEBUG RAW from ler_pedidos():")
    #df_debug = ler_pedidos()
    #st.write(df_debug)

    st.subheader("Editar Pedido")

    df = ler_pedidos()

    if df.empty:
        st.info("Nenhum pedido.")
        st.stop()

    nome = st.text_input("Buscar por nome:")
    tel = st.text_input("Buscar por telefone:")

    df_f = df.copy()
    if nome:
        df_f = df_f[df_f["Cliente"].str.contains(nome, case=False)]
    if tel:
        df_f = df_f[df_f["Telefone"].astype(str).str.contains(tel)]

    st.dataframe(df_f, width="stretch")

    idx = st.number_input("Linha a editar:", min_value=0, max_value=len(df_f)-1)
    linha_real = df_f.index[idx]
    item = df.loc[linha_real]

    tel_edit = st.text_input("Telefone", value=str(item["Telefone"]))
    data_edit = st.date_input(
        "Data",
        datetime.strptime(item["Data da Entrega"], "%d/%m/%Y")
    )
    prod_edit = st.selectbox("Produto", list(produtos_df["Produto"]),
                             index=list(produtos_df["Produto"]).index(item["Produto"]))

    if prod_edit == "Kit Mini Ovos":
        atual = item["Subproduto"].split(", ")
        s1 = st.selectbox("Sub1", SUBPRODUTOS, index=SUBPRODUTOS.index(atual[0]))
        s2 = st.selectbox("Sub2", SUBPRODUTOS, index=SUBPRODUTOS.index(atual[1]))
        subs_edit = [s1, s2]
    else:
        subs_edit = [""]

    qt_edit = st.number_input("Quantidade", min_value=1, value=int(item["Quantidade"]))
    desc_edit = st.number_input("Desconto %", min_value=0, max_value=100, value=int(item["Desconto %"]))

    


    if st.button("💾 Salvar Alterações"):

        # 1. Atualiza somente a linha editada
        df.loc[linha_real, "Telefone"] = tel_edit
        df.loc[linha_real, "Data da Entrega"] = data_edit.strftime("%d/%m/%Y")
        df.loc[linha_real, "Produto"] = prod_edit
        df.loc[linha_real, "Subproduto"] = ", ".join(subs_edit)
        df.loc[linha_real, "Quantidade"] = qt_edit

        # 2. Identifica o ID_Pedido que está sendo alterado
        id_pedido_atual = df.loc[linha_real, "ID_Pedido"]

        # 🔥 3. Atualiza o desconto em TODAS as linhas do pedido
        df.loc[df["ID_Pedido"] == id_pedido_atual, "Desconto %"] = desc_edit

        # 4. Recalcular o valor total do pedido inteiro
        df_pedido = df[df["ID_Pedido"] == id_pedido_atual].copy()
        lista_prod = df_pedido["Produto"].tolist()
        lista_sub = df_pedido["Subproduto"].apply(lambda s: s.split(", ") if s else [""]).tolist()
        lista_qt = df_pedido["Quantidade"].tolist()

        itens, novo_total = calcular_total(lista_prod, lista_sub, lista_qt, desc_edit)

        # 5. Aplica o novo valor total em todas as linhas
        df.loc[df["ID_Pedido"] == id_pedido_atual, "Valor Total"] = novo_total

        # 6. Salvar
        salvar_pedidos(df)

        st.success("Pedido atualizado com sucesso!")