from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread
import os
import json

def converter_valor(valor):

    valor = str(valor).strip()

    if valor == "":
        return 0

    valor = (
        valor.replace("R$", "")
              .replace(",", ".")
              .strip()
    )

    return float(valor)

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
    custo_estoque = 0

    produtos_estoque = {}
    produtos_vendidos = {}

    # Lê estoque
    for item in estoque:

        try:

            produto = item["Itens"]

            quantidade = int(item["Quantidade"])

            print("VALOR PAGO BRUTO:", item["Valor Pago"])

            valor_pago = converter_valor(
                item["Valor Pago"]
            )

            print("VALOR UNITÁRIO BRUTO:", item["Valor Unitário"])

            valor_unitario = converter_valor(
                item["Valor Unitário"]
            )

            custo_estoque += valor_pago

            if produto in produtos_estoque:

                # soma quantidade
                produtos_estoque[produto]["quantidade"] += quantidade

                # soma investimento
                produtos_estoque[produto]["valor_pago"] += valor_pago

                # custo médio
                produtos_estoque[produto]["custo"] = (

                    produtos_estoque[produto]["valor_pago"]

                    /

                    produtos_estoque[produto]["quantidade"]

                )
            

            else:

                produtos_estoque[produto] = {

                    "quantidade": quantidade,
                    "valor_pago": valor_pago,
                    "custo": valor_unitario

                }
            

        except Exception as erro:

            print("ERRO ESTOQUE:", erro)
            print(item)
            continue


    # Lê vendas
    for venda in vendas:

        try:

            produto = venda["Produto"]

            qtd_vendida = int(venda["Peças"])

            valor_total = converter_valor(
                venda["Valor Total"]
            )

            receita += valor_total

            produtos_vendidos[produto] = (

                produtos_vendidos.get(
                    produto,0
                )

                + qtd_vendida
            )

            if produto in produtos_estoque:

                custo_unitario = (
                    produtos_estoque[produto]["custo"]
                )

                custo_total_vendido += (

                    qtd_vendida
                    *
                    custo_unitario

                )

        except Exception as erro:

            print("ERRO VENDAS:", erro)
            print(venda)
            continue


    estoque_atual = {}

    for produto in produtos_estoque:

        quantidade_comprada = (

            produtos_estoque[produto]["quantidade"]

        )

        vendido = produtos_vendidos.get(
            produto,0
        )

        restante = quantidade_comprada - vendido

        estoque_atual[produto] = {

            "restante": restante,

            "valor_pago": round(

                produtos_estoque[produto]["valor_pago"],
                2

            ),

            "valor_unitario": round(

                produtos_estoque[produto]["custo"],2

            )
        }

    lucro = receita - custo_total_vendido

    return render_template(

        "dashboard.html",

        receita=round(receita,2),
        custo=round(custo_estoque,2),
        lucro=round(lucro,2),

        estoque=estoque_atual

    )
@app.route("/consulta")
def consulta():

    tipo = request.args.get(
        "tipo",
        "vendas"
    )

    termo = request.args.get(
        "pesquisa",
        ""
    ).lower()


    if tipo == "vendas":

        registros = aba_vendas.get_all_values()

    else:

        registros = aba_estoque.get_all_values()


    cabecalho = registros[0]
    dados = registros[1:]

    resultados = []

    for i, linha in enumerate(dados, start=2):

        item = dict(
            zip(cabecalho, linha)
        )

        item["linha"] = i

        resultados.append(item)


    if termo:

        if tipo == "vendas":

            resultados = [

                item for item in resultados

                if termo in item["Nome"].lower()

                or termo in item["Produto"].lower()

            ]

        else:

            resultados = [

                item for item in resultados

                if termo in item["Itens"].lower()

                or termo in item["Responsável"].lower()

            ]


    return render_template(

        "consulta.html",

        resultados=resultados,

        tipo=tipo
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

    qtd = int(request.form["qtd"])

    itens = request.form["itens"]

    valorPago = request.form["valorPago"]

    valorPago = valorPago.replace(",", ".")

    valor_pago_float = float(valorPago)

    valor_unitario = valor_pago_float / qtd

    data_registro = datetime.now().strftime("%d/%m/%Y")

    print("Valor recebido:", valorPago)

    aba_estoque.append_row(

        [

            responsa,
            qtd,
            itens,

            f"{valor_pago_float:.2f}",

            f"{valor_unitario:.2f}",

            data_registro

        ],

        value_input_option="RAW"

    )

    return redirect(url_for("estoque"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)