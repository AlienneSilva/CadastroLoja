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

cabecalhoEstoque = [

    "Responsável",
    "Quantidade",
    "Itens",
    "Valor Pago",
    "Valor Unitário",
    "Data Registro"
]

if aba_estoque.row_values(1) != cabecalhoEstoque:
    aba_estoque.insert_row(cabecalhoEstoque, 1)


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

            valor_unitario = float(
                str(item["Valor Unitário"]).replace(",", ".")
            )

            produtos_estoque[produto] = {

                "quantidade": quantidade,
                "custo": valor_unitario
            }

        except:
            continue

# Lê vendas
    for venda in vendas:

        try:
            produto = venda["Produto"]

            qtd_vendida = int(venda["Peças"])

            valor_total = float(
                str(venda["Valor Total"]).replace(",", ".")
            )

            receita += valor_total

            produtos_vendidos[produto] = (
                produtos_vendidos.get(produto, 0)
                + qtd_vendida
            )

        # custo apenas dos itens vendidos
            if produto in produtos_estoque:

                custo_unitario = produtos_estoque[produto]["custo"]

                custo_total_vendido += (
                    qtd_vendida * custo_unitario
                )

        except Exception as erro:
            print(erro)
        continue

    saidas=[]

    for venda in vendas:

        saidas.append({

            "produto":venda["Produto"],
            "qtd":venda["Peças"],
            "data":venda["Data Registro"]

        })


    # Calcula estoque restante
   # Calcula estoque restante
    estoque_atual = {}

    for produto in produtos_estoque:

        quantidade_comprada = produtos_estoque[produto]["quantidade"]

        vendido = produtos_vendidos.get(produto, 0)

        restante = quantidade_comprada - vendido

        valor_unitario = produtos_estoque[produto]["custo"]

        valor_pago = quantidade_comprada * valor_unitario

        estoque_atual[produto] = {

            "restante": restante,

            "valor_pago": round(valor_pago, 2),

            "valor_unitario": round(valor_unitario, 2)

        }
    lucro = receita - custo_total_vendido

    print("Receita:", receita)
    print("Custo:", custo_total_vendido)
    print("Lucro:", lucro)

    return render_template(
        "dashboard.html",
        receita=round(receita,2),
        custo=round(custo_total_vendido,2),
        lucro=round(lucro,2),
        estoque=estoque_atual,
        saidas=saidas
    )
@app.route("/consulta")
def consulta():

    registros = aba_vendas.get_all_values()

    cabecalho = registros[0]
    dados = registros[1:]

    vendas = []

    for i, linha in enumerate(dados, start=2):

        venda = dict(zip(cabecalho, linha))

        venda["linha"] = i

        vendas.append(venda)

    termo = request.args.get("pesquisa", "")

    if termo:

        vendas = [

            venda for venda in vendas

            if termo.lower() in venda["Nome"].lower()
            or termo.lower() in venda["Produto"].lower()
        ]

    return render_template(
        "consulta.html",
        vendas=vendas
    )
@app.route("/excluir/<int:linha>")
def excluir(linha):

    aba_vendas.delete_rows(linha)

    return redirect(url_for("consulta"))
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

    nome = request.form["nome"].title()
    contato = request.form["contato"].title()
    pecas = request.form["pecas"]
    produto = request.form["produto"]
    valorUni = request.form["valorUni"].replace(",", ".")
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

    responsa = request.form["responsa"].title()
    qtd = request.form["qtd"]
    itens = request.form["itens"]
    valorPago = request.form["valorPago"].replace(",", ".")

    valor_unitario = float(valorPago) / int(qtd)

    data_registro = datetime.now().strftime("%d/%m/%Y")

    aba_estoque.append_row([
       
        responsa,
        qtd,
        itens,
        valorPago,
        round(valor_unitario,2),
        data_registro
    ])


    return redirect(url_for("estoque"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)