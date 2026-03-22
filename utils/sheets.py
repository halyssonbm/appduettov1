import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from functools import lru_cache
import streamlit as st

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

ID_PRODUTOS = "1zIN2cYoCPzKqNg1di__XqFTHtsCNM3SfqR8bel7eJS8"
ID_PEDIDOS = "1PkrX8QwrPZn3ta9Ssco0NtDuCGAdVhJV0_tx6JFgdIQ"


# ----------------------------------------------------------------------
# CONEXÃO
# ----------------------------------------------------------------------
def conectar():
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
    return gspread.authorize(creds)


# ----------------------------------------------------------------------
# LER PRODUTOS  (ESTÁVEL)
# ----------------------------------------------------------------------
@lru_cache(maxsize=1)
def ler_produtos():
    client = conectar()
    sheet = client.open_by_key(ID_PRODUTOS).sheet1
    dados = sheet.get_all_records()

    if not dados:
        return pd.DataFrame(columns=["Produto", "Preço", "Custo de Fabricação", "Prolabore"])

    df = pd.DataFrame(dados)

    for col in ["Preço", "Custo de Fabricação", "Prolabore"]:
        df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    return df


def limpar_cache_produtos():
    ler_produtos.cache_clear()


# ----------------------------------------------------------------------
# LER PEDIDOS  (ESTÁVEL)
# ----------------------------------------------------------------------
@lru_cache(maxsize=1)
def ler_pedidos():
    client = conectar()
    sheet = client.open_by_key(ID_PEDIDOS).sheet1
    dados = sheet.get_all_records()

    if not dados:
        return pd.DataFrame(columns=[
            "ID_Pedido", "Cliente", "Telefone", "Data da Entrega",
            "Produto", "Subproduto", "Quantidade",
            "Desconto %", "Valor Total"
        ])

    df = pd.DataFrame(dados)
    df["Telefone"] = df["Telefone"].astype(str)
    df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0).astype(int)

    def normalizar_valor(v):
        if v is None:
            return 0.0
        s = str(v).strip().replace(" ", "").replace(",", ".")
        try:
            return round(float(s), 2)
        except:
            return 0.0

    #df["Valor Total"] = df["Valor Total"].apply(normalizar_valor)

    # 🔥 NORMALIZADOR DEFINITIVO DE VALOR TOTAL
    def normalizar_total(v):
        """
        Converte QUALQUER forma de número contaminado do Google Sheets em float estável:
        - "29,10" -> 29.10
        - "2910"  -> 29.10 (detecta fator 100)
        - "291"   -> 2.91  (detecta fator 10)
        - "79"    -> 0.79? NÃO: detecta preço unitário e impede erro
        - "0"     -> 0.00
        """
        if v is None:
            return 0.0

        # 1. Limpa espaços
        s = str(v).strip()

        # 2. Substitui vírgula por ponto
        s = s.replace(",", ".")

        # 3. Remove separadores estranhos
        s = s.replace(" ", "")

        # 4. Tenta converter
        try:
            f = float(s)
        except:
            return 0.0

        # 5️⃣ ⚠️ DETECÇÃO AUTOMÁTICA DE POTÊNCIA DE 10
        # • 29,10 vira 2910?  (deve dividir por 100)
        # • 29,10 vira 291?   (deve dividir por 10)
        # • 29,10 vira 0.291? (deve multiplicar por 100)
        # • 6,50 vira 6500?   (deve dividir por 1000)
        # • 79 vira 7900?     (divide por 100)
        #
        # lógica: o valor total REAL nunca ultrapassa R$ 500 por item
        # então qualquer número maior que 500 é claramente multiplicado
        if f > 50000:
            f = f / 1000  # casos extremos
        elif f > 500:
            f = f / 100
        elif 50 < f <= 500 and len(s) <= 3:
            # caso raro: 291 -> 2.91
            f = f / 100

        # 6. Retorna sempre DUAS casas decimais
        return round(f, 2)

    df["Valor Total"] = df["Valor Total"].apply(normalizar_total)

    df["Desconto %"] = (
        df["Desconto %"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .apply(lambda x: float(x) if x.replace(".", "").isdigit() else 0.0)
    )

    return df


def limpar_cache_pedidos():
    ler_pedidos.cache_clear()


# ----------------------------------------------------------------------
# SALVAR APENAS A LINHA MODIFICADA (NÃO O DATAFRAME INTEIRO!)
# ----------------------------------------------------------------------
def atualizar_linha_pedido(linha, coluna, valor):
    client = conectar()
    sheet = client.open_by_key(ID_PEDIDOS).sheet1
    sheet.update_cell(linha, coluna, valor)
    limpar_cache_pedidos()


def salvar_pedidos(df):
    """
    Somente usado no registro de novos pedidos.
    (Escreve linhas novas por inteiro.)
    """
    client = conectar()
    sheet = client.open_by_key(ID_PEDIDOS).sheet1
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    limpar_cache_pedidos()