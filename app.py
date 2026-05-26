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

credenciais_json = json.loads(
    os.environ["GOOGLE_CREDENTIALS"]
)

credenciais = Credentials.from_service_account_info(
    credenciais_json,
    scopes=escopos
)

cliente = gspread.authorize(credenciais)

# =====================
# PLANILHA VENDAS
# =====================

planilha_vendas = cliente.open("Cadastros")
aba_vendas = planilha_vendas.sheet1

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

# =====================
# PLANILHA ESTOQUE
# =====================

planilha_estoque = cliente.open("Estoque")
aba_estoque = planilha_estoque.sheet1

cabecalho_estoque = [
    "Responsável",
    "Quantidade",
    "Itens",
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

    data_registro = datetime.now().strftime("%d/%m/%Y")

    aba_estoque.append_row([
        responsa,
        qtd,
        itens,
        data_registro
    ])

    return redirect(url_for("estoque"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)