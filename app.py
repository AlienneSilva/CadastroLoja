from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Permissões
escopos = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credenciais = Credentials.from_service_account_file(
    "credenciais.json",
    scopes=escopos
)

cliente = gspread.authorize(credenciais)

# Nome da planilha
planilha = cliente.open("Cadastros")
aba = planilha.sheet1


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

    data_registro = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

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

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)