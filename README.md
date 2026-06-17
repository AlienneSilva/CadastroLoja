Sistema de Controle de Vendas e Gestão Financeira

Aplicação web desenvolvida com o objetivo de automatizar o processo de controle de vendas, estoque e gestão financeira de uma loja, centralizando informações operacionais e auxiliando na tomada de decisão através de indicadores de desempenho.

O sistema foi projetado para simular um cenário real de negócio, permitindo o gerenciamento de vendas, controle automatizado de estoque, cadastro de despesas operacionais e acompanhamento financeiro da operação.

Objetivo do Projeto

O principal objetivo deste projeto foi desenvolver uma solução capaz de organizar e automatizar processos internos de uma loja, reduzindo controles manuais e facilitando o acompanhamento de informações estratégicas como faturamento, custos e movimentação de estoque.

Funcionalidades Implementadas
Cadastro de Vendas

O sistema permite registrar vendas realizadas contendo:

Nome do cliente
Responsável pela venda
Quantidade de produtos vendidos
Valor unitário do produto
Canal de venda utilizado
Conta vinculada ao canal de venda

Todas as informações são armazenadas automaticamente para consulta e geração de relatórios.

Controle de Estoque

O usuário pode cadastrar produtos e materiais disponíveis em estoque, informando:

Nome do item
Quantidade disponível
Valor pago na compra
Cálculo automático do valor unitário
Composição de Produtos

Foi implementado um sistema de composição que permite relacionar quais materiais são utilizados para fabricar cada produto.

Exemplo:

Para produzir 20 chaveiros, o sistema entende automaticamente que são necessários:

1 MDF
20 Argolas
1 Papel Adesivo

Com isso, cada venda gera baixa automática dos materiais utilizados no estoque.

Gestão de Despesas

Controle de despesas operacionais da loja, permitindo registrar:

Investimentos em anúncios (ADS)
Frete
Energia
Internet
Outras despesas administrativas
Dashboard Financeiro

Painel central com indicadores consolidados, exibindo:

Receita total de vendas
Valor investido em estoque
Custos operacionais
Despesas cadastradas
Controle financeiro geral do negócio
Armazenamento de Dados

Como banco de dados, o sistema utiliza integração com planilhas online, permitindo persistência dos dados sem necessidade de banco relacional tradicional.

Os dados ficam disponíveis para consulta e geração de relatórios futuros.

Tecnologias Utilizadas
Python
Flask
HTML5
CSS3
JavaScript
Google Sheets API
Git e GitHub
Render (Deploy em produção)
Aprendizados Desenvolvidos

Durante o desenvolvimento deste projeto foram trabalhados conceitos importantes como:

Desenvolvimento Backend com Flask
Criação e consumo de APIs
Estruturação de rotas e arquitetura web
Manipulação de dados em planilhas via API
Deploy de aplicações em ambiente cloud
Lógica de negócio aplicada a cenários reais
Controle automatizado de estoque e movimentação de produtos
Organização e manutenção de código em projeto real
Deploy

Projeto publicado em ambiente de produção:

cadastroloja-s2ea.onrender.com

Próximas Melhorias
Sistema de autenticação de usuários
Dashboard com gráficos interativos
Banco de dados SQL
Relatórios avançados
Controle de permissões por usuário
Histórico detalhado de movimentação de estoque
Desenvolvedora

Alienne Silva

Estudante de Engenharia da Computação em transição para desenvolvimento de software, com foco em Backend, automação e desenvolvimento de aplicações web.

GitHub: github.com/AlienneSilva
