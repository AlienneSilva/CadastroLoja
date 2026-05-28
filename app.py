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

# =====================
# PLANILHA VENDAS
# =====================

try:

    planilha_vendas = cliente.open(
        "Cadastros"
    )

    aba_vendas = (
        planilha_vendas.sheet1
    )

except Exception as erro:

    print(
        "Erro ao abrir planilha Cadastros:"
    )

    print(erro)


# =====================
# PLANILHA COMPOSICAO
# =====================

try:

    planilha_composicao = cliente.open(
        "COMPOSICAO"
    )

    aba_composicao = (
        planilha_composicao.sheet1
    )

except Exception as erro:

    print(
        "Erro ao abrir composição:"
    )

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

@app.route("/composicao")
def composicao():

    return render_template(
        "composicao.html"
    )

@app.route("/dashboard")
def dashboard():
    vendas = aba_vendas.get_all_records()
    estoque = aba_estoque.get_all_records()
    composicoes = aba_composicao.get_all_records()
    
    
    receita = 0
    custo_total_vendido = 0
    custo_estoque = 0
    produtos_estoque = {}
    produtos_vendidos = {}
    materiais_consumidos = {}

# =====================
# ESTOQUE
# =====================

    for item in estoque:
        try:
            produto = (item["Itens"].strip().lower())
            quantidade = int(item["Quantidade"])
            valor_pago = converter_valor(item["Valor Pago"])
            valor_unitario = converter_valor(item["Valor Unitário"])
            custo_estoque += valor_pago
            if produto in produtos_estoque:
                produtos_estoque[produto]["quantidade"] += quantidade
                produtos_estoque[produto]["valor_pago"] += valor_pago
                produtos_estoque[produto]["custo"] = (produtos_estoque[produto]["valor_pago"]
                                                      /
                                                      produtos_estoque[produto]["quantidade"]
                                                      )
            else:
                produtos_estoque[produto] = {"quantidade": quantidade,"valor_pago": valor_pago,"custo": valor_unitario}
        except Exception as erro:
            print("ERRO ESTOQUE:")
            print(erro)
            print(item)
        continue


# =====================
# VENDAS
# =====================

    

# Lê vendas
    for venda in vendas:

        try:

            produto = (venda["Produto"].strip().lower())
            qtd_vendida = int(venda["Peças"])
            valor_total = converter_valor(venda["Valor Total"])
            receita += valor_total
            tem_composicao = False

        # PROCURA COMPOSIÇÃO
            for comp in composicoes:

                produto_comp = (comp["Produto"].strip().lower())
                if produto == produto_comp:
                    tem_composicao = True
                    material = (comp["Material"].strip().lower())
                    qtd_material = float(comp["Quantidade Usada"])
                    if material in produtos_estoque:
                        consumo = (qtd_vendida * qtd_material)
                        materiais_consumidos[material] = (materiais_consumidos.get(material,0) + consumo)
                        custo_material = (produtos_estoque[material]["custo"])
                        custo_total_vendido += (consumo * custo_material)
        # PRODUTO SEM COMPOSIÇÃO
            if not tem_composicao:
                if produto in produtos_estoque:
                    custo_unitario = (produtos_estoque[produto]["custo"])
                    custo_total_vendido += (qtd_vendida * custo_unitario)

        except Exception as erro:
            print("ERRO VENDAS:")
            print(erro)
            print(venda)
            continue
    print("Receita:", receita)
    print("Custo total vendido:", custo_total_vendido)

    lucro = receita - custo_total_vendido

    print("Lucro:", lucro)

    estoque_atual = {}

    for produto in produtos_estoque:

        quantidade_comprada = (
            produtos_estoque[produto]["quantidade"]
        )

        consumido = materiais_consumidos.get(
            produto,
            0
        )

        restante = (
            quantidade_comprada
            -
            consumido
        )

        estoque_atual[produto] = {

            "restante": restante,

            "valor_pago": round(
                produtos_estoque[produto]["valor_pago"],
                2
            ),

            "valor_unitario": round(
                produtos_estoque[produto]["custo"],
                2
            )
        }

    return render_template(
        "dashboard.html",
        receita=round(receita,2),
        custo=round(custo_total_vendido,2),
        lucro=round(lucro,2),
        estoque=estoque_atual,
        custo_estoque=round(custo_estoque,2),
        investimento=round(custo_estoque,2))

@app.route("/consulta")
def consulta():

    # PESQUISA VENDAS
    termo_venda = request.args.get(
        "pesquisa_vendas",
        ""
    ).lower()

    registros_vendas = aba_vendas.get_all_values()

    cabecalho_v = registros_vendas[0]
    dados_v = registros_vendas[1:]

    vendas = []

    for i, linha in enumerate(dados_v, start=2):

        venda = dict(
            zip(cabecalho_v, linha)
        )

        venda["linha"] = i

        vendas.append(venda)

    if termo_venda:

        vendas = [

            venda for venda in vendas

            if termo_venda in venda["Nome"].lower()

            or termo_venda in venda["Produto"].lower()

        ]


    # PESQUISA ESTOQUE
    termo_estoque = request.args.get(
        "pesquisa_estoque",
        ""
    ).lower()

    registros_estoque = aba_estoque.get_all_values()

    cabecalho_e = registros_estoque[0]
    dados_e = registros_estoque[1:]

    estoque = []

    for i, linha in enumerate(dados_e, start=2):

        item = dict(
            zip(cabecalho_e, linha)
        )

        item["linha"] = i

        estoque.append(item)

    if termo_estoque:

        estoque = [

            item for item in estoque

            if termo_estoque in item["Itens"].lower()

            or termo_estoque in item["Responsável"].lower()

        ]


    return render_template(

        "consulta.html",

        vendas=vendas,

        estoque=estoque

    )
@app.route("/excluir/<int:linha>")
def excluir(linha):

    aba_vendas.delete_rows(linha)

    return redirect(url_for("consulta"))
@app.route("/excluir_estoque/<int:linha>")
def excluir_estoque(linha):

    aba_estoque.delete_rows(linha)

    return redirect(
        url_for(
            "consulta",
            tipo="estoque"
        )
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

@app.route(
    "/gravar_composicao",
    methods=["POST"]
)
def gravar_composicao():

    produto = (
        request.form["produto"]
        .strip()
        .lower()
    )

    material = (
        request.form["material"]
        .strip()
        .lower()
    )  


    quantidade = (
        request.form["quantidade"]
    )

    aba_composicao.append_row([

        produto,
        material,
        quantidade

    ])

    return redirect(
        url_for("composicao")
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)