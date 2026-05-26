from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread
import os
import json

app = Flask(__name__)

# Página inicial
@app.route("/")
def inicio():
    return render_template("home.html")

# Página cadastro
@app.route("/cadastro")
def cadastro():
    return render_template("index.html")

# Codigo de conexão com google sheets
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
#criar o cabeçalho da planilha
planilha = cliente.open("Cadastros")
aba = planilha.sheet1

cabecalho = [
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

primeira_linha = aba.row_values(1)

if primeira_linha != cabecalho:
    aba.insert_row(cabecalho, 1)
#calcula o valor total da venda
def calc(valorUni, pecas):
    return float(valorUni) * int(pecas)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/gravar", methods=["POST"])
def gravar():

    nome = request.form["nome"]
    contato = request.form["contato"]
    pecas = request.form["pecas"]
    produto = request.form["produto"]
    valorUni = request.form["valorUni"]
    canal = request.form["canal"]
    conta = request.form["conta"]

    valorTotal = calc(valorUni, pecas)
    data_registro = datetime.now().strftime("%d/%m/%Y %H:%M")

    aba.append_row([
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)