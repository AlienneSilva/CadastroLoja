from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread
import os
import json

app = Flask(__name__)

# =====================
# Conexão Google Sheets
# =====================

escopos = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


# Render
if "GOOGLE_CREDENTIALS" in os.environ:

    credenciais_json = json.loads(
        os.environ["GOOGLE_CREDENTIALS"]
    )

    credenciais = Credentials.from_service_account_info(
        credenciais_json,
        scopes=escopos
    )

# Local
else:

  credenciais = Credentials.from_service_account_file(
    "cadastro-497420-0dfc8c86c2dc.json",
    scopes=escopos
)
cliente = gspread.authorize(credenciais)


# =====================
# PLANILHA VENDAS
# =====================

try:
   planilha_vendas = cliente.open("Cadastros")
   aba_vendas = planilha_vendas.sheet1

except Exception as erro:
    print("Erro ao abrir planilha Cadastros:")
    print(erro)

cabecalho_vendas = [
    "Nome",
    "Responsável",
    "Peças",
    "Produto",
    "Valor Unitário",
    "Canal",
    "Conta",
    "Valor Total",
    "Data Registro"
]

if aba_vendas.row_values(1) != cabecalho_vendas:
   aba_vendas.insert_row(cabecalho_vendas, 1)

# ======================
 #PLANILHA ESTOQUE
# =====================

try:
   planilha_estoque = cliente.open("Estoque")
   aba_estoque = planilha_estoque.sheet1

except Exception as erro:
    print("Erro ao abrir planilha Estoque:")
    print(erro)

cabecalho_estoque = [
    "Responsável",
    "Quantidade",
    "Itens",
    "Valor Pago",
    "Data Registro"
]

if aba_estoque.row_values(1) != cabecalho_estoque:
    aba_estoque.insert_row(cabecalho_estoque, 1)


# =====================
# ROTAS
# =====================

@app.route("/")
def inicio():
    return render_template("home.html")


@app.route("/cadastro")
def cadastro():
    return render_template("index.html")


@app.route("/estoque")
def estoque():
    return render_template("estoque.html")


@app.route("/dashboard")
def dashboard():

    vendas = aba_vendas.get_all_records()
    estoque = aba_estoque.get_all_records()

    receita = 0
    custo_total_vendido = 0

    produtos_estoque = {}
    produtos_vendidos = {}

    # Lê estoque
    for item in estoque:

        try:
            produto = item["Itens"]
            quantidade = int(item["Quantidade"])
            valor_pago = float(item["Valor Pago"])

            # Guarda quantidade e custo unitário
            produtos_estoque[produto] = {
                "quantidade": quantidade,
                "custo": valor_pago
            }

        except:
            continue

    # Lê vendas
    for venda in vendas:

        try:
            produto = venda["Produto"]
            qtd_vendida = int(venda["Peças"])
            valor_total = float(venda["Valor Total"])

            receita += valor_total

            produtos_vendidos[produto] = (
                produtos_vendidos.get(produto, 0)
                + qtd_vendida
            )

            # custo somente dos itens vendidos
            if produto in produtos_estoque:

                custo_unitario = produtos_estoque[produto]["custo"]

                custo_total_vendido += (
                    qtd_vendida * custo_unitario
                )

        except:
            continue


    # Calcula estoque restante
    estoque_atual = {}

    for produto in produtos_estoque:

        comprado = produtos_estoque[produto]["quantidade"]

        vendido = produtos_vendidos.get(produto, 0)

        estoque_atual[produto] = comprado - vendido


    lucro = receita - custo_total_vendido

    return render_template(
    "dashboard.html",
    receita=round(receita,2),
    custo=round(custo_total_vendido,2),
    lucro=round(lucro,2),
    estoque=estoque_atual,

    produtos=list(estoque_atual.keys()),
    quantidades=list(estoque_atual.values())
)

# =====================
# FUNÇÕES
# =====================

def calc(valorUni, pecas):
    return float(valorUni) * int(pecas)


# =====================
# SALVAR VENDAS
# =====================

@app.route("/gravar_venda", methods=["POST"])
def gravar_venda():

    nome = request.form["nome"]
    contato = request.form["contato"]
    pecas = request.form["pecas"]
    produto = request.form["produto"]
    valorUni = request.form["valorUni"]
    canal = request.form["canal"]
    conta = request.form["conta"]

    valorTotal = calc(valorUni, pecas)

    data_registro = datetime.now().strftime("%d/%m/%Y %H:%M")

    aba_vendas.append_row([
        nome,
        contato,
        pecas,
        produto,
        valorUni,
        canal,
        conta,
        valorTotal,
        data_registro
    ])

    return redirect(url_for("cadastro"))


# =====================
# SALVAR ESTOQUE
# =====================

@app.route("/gravar_estoque", methods=["POST"])
def gravar_estoque():

    responsa = request.form["responsa"]
    qtd = request.form["qtd"]
    itens = request.form["itens"]
    valorPago = request.form["valorPago"]

    data_registro = datetime.now().strftime("%d/%m/%Y")

    aba_estoque.append_row([
        responsa,
        qtd,
        itens,
        valorPago,
        data_registro
    ])

    return redirect(url_for("estoque"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)