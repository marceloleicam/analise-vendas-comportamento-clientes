# Sales & Customer Analytics with Python

> Dashboard interativo para analisar vendas, faturamento, produtos e comportamento de clientes.

## Visão geral

Este projeto transforma uma base de vendas em indicadores comerciais prontos para análise. A aplicação permite filtrar os dados, acompanhar resultados, identificar produtos e clientes relevantes e exportar um relatório completo em Excel.

Toda a demonstração utiliza dados fictícios e foi desenvolvida como projeto de portfólio em análise de dados.

## Funcionalidades

- Importação de arquivos CSV
- Base fictícia pronta para demonstração
- Filtros por período, categoria, região e pagamento
- Faturamento líquido e descontos concedidos
- Quantidade de pedidos e itens vendidos
- Ticket médio e clientes ativos
- Taxa de cancelamento
- Evolução mensal do faturamento
- Ranking de produtos, categorias e clientes
- Distribuição por região e forma de pagamento
- Verificações de qualidade dos dados
- Exportação de relatório em Excel
- Testes automatizados com Pytest

## Tecnologias

- Python
- Pandas
- Streamlit
- Plotly
- OpenPyXL
- Pytest

## Estrutura

```text
.
├── .streamlit/config.toml
├── data/sample_sales.csv
├── src/
│   ├── __init__.py
│   └── analytics.py
├── tests/
│   ├── test_analytics.py
│   └── test_app.py
├── app.py
├── requirements.txt
├── README.md
├── SECURITY.md
└── LICENSE
```

## Executar no Windows

Abra o terminal do VS Code dentro da pasta do projeto e execute:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m streamlit run app.py
```

O painel será aberto em `http://localhost:8501`.

## Formato do CSV

| Coluna | Descrição |
|---|---|
| `order_id` | Identificador do pedido |
| `order_date` | Data da venda |
| `customer_id` | Identificador do cliente |
| `customer_name` | Nome do cliente |
| `product` | Produto vendido |
| `category` | Categoria do produto |
| `quantity` | Quantidade vendida |
| `unit_price` | Preço unitário |
| `discount_pct` | Percentual de desconto |
| `payment_method` | Forma de pagamento |
| `status` | Situação do pedido |
| `region` | Região da venda |

## Regras utilizadas

O faturamento considera somente vendas concluídas. O valor líquido é calculado multiplicando a quantidade pelo preço unitário e descontando o percentual informado. Pedidos cancelados entram apenas no cálculo da taxa de cancelamento.

## Como explicar o projeto

O objetivo foi automatizar uma análise comercial que normalmente seria realizada manualmente em planilhas. Separei o motor de análise da interface para facilitar testes e reutilização. O Pandas trata e agrega os dados, o Streamlit cria a aplicação interativa, o Plotly gera os gráficos e o OpenPyXL permite exportar os resultados para Excel.

Também implementei testes automatizados para validar cálculos de faturamento, descontos, ticket médio, cancelamentos, rankings e geração do relatório.

## Próximas evoluções

- Comparação com metas comerciais
- Análise de recorrência e retenção
- Segmentação RFM de clientes
- Previsão de vendas
- Integração com banco de dados
- Publicação na nuvem

## Autor

Desenvolvido por [Marcelo](https://github.com/marceloleicam) como projeto de portfólio em Python e análise de dados.

## Licença

Uso exclusivo para avaliação e demonstração de portfólio. Consulte [LICENSE](LICENSE).

