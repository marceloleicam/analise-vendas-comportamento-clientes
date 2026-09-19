from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import SalesValidationError, analyze_sales, build_excel_report


BASE_DIR = Path(__file__).resolve().parent
SAMPLE_FILE = BASE_DIR / "data" / "sample_sales.csv"

st.set_page_config(page_title="Análise de Vendas e Clientes", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background: #f6f8fc;
        }

        .block-container {
            max-width: 1480px;
            padding-top: 1.15rem;
            padding-bottom: 2rem;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        .dashboard-hero {
            position: relative;
            overflow: hidden;
            padding: 1.55rem 1.75rem;
            margin-bottom: 1rem;
            border: 1px solid #dbeafe;
            border-radius: 22px;
            background: linear-gradient(120deg, #0f2a27 0%, #1e8a7f 58%, #25ebe8 100%);
            box-shadow: 0 14px 35px rgba(15, 23, 42, 0.14);
        }

        .dashboard-hero::after {
            content: "";
            position: absolute;
            width: 230px;
            height: 230px;
            right: -70px;
            top: -110px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.10);
        }

        .hero-label {
            display: inline-flex;
            padding: 0.34rem 0.68rem;
            margin-bottom: 0.65rem;
            border: 1px solid rgba(255, 255, 255, 0.24);
            border-radius: 999px;
            color: #dbeafe;
            background: rgba(255, 255, 255, 0.08);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .dashboard-hero h1 {
            position: relative;
            z-index: 1;
            margin: 0;
            color: #ffffff;
            font-size: clamp(1.75rem, 3vw, 2.65rem);
            line-height: 1.12;
            letter-spacing: -0.035em;
        }

        .dashboard-hero p {
            position: relative;
            z-index: 1;
            max-width: 760px;
            margin: 0.65rem 0 0;
            color: #dbeafe;
            font-size: 0.98rem;
        }

        .summary-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin: 0.25rem 0 0.75rem;
        }

        .summary-title {
            color: #0f172a;
            font-size: 1.15rem;
            font-weight: 750;
        }

        .period-pill {
            padding: 0.38rem 0.72rem;
            border: 1px solid #dbe4f0;
            border-radius: 999px;
            color: #475569;
            background: #ffffff;
            font-size: 0.78rem;
            font-weight: 600;
        }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.9rem;
            margin-bottom: 1.25rem;
        }

        .kpi-card {
            min-height: 126px;
            padding: 1rem 1.05rem;
            border: 1px solid #e2e8f0;
            border-top: 4px solid var(--accent);
            border-radius: 16px;
            background: #ffffff;
            box-shadow: 0 7px 20px rgba(15, 23, 42, 0.055);
        }

        .kpi-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.5rem;
        }

        .kpi-label {
            color: #64748b;
            font-size: 0.79rem;
            font-weight: 650;
        }

        .kpi-icon {
            display: grid;
            width: 32px;
            height: 32px;
            place-items: center;
            border-radius: 10px;
            color: var(--accent);
            background: color-mix(in srgb, var(--accent) 12%, white);
            font-size: 1rem;
        }

        .kpi-value {
            margin-top: 0.6rem;
            color: #0f172a;
            font-size: clamp(1.45rem, 2.1vw, 2rem);
            font-weight: 780;
            line-height: 1;
            letter-spacing: -0.035em;
        }

        .kpi-note {
            margin-top: 0.5rem;
            color: #94a3b8;
            font-size: 0.7rem;
        }

        div[data-testid="stTabs"] button {
            font-weight: 650;
        }

        @media (max-width: 1050px) {
            .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }

        @media (max-width: 650px) {
            .block-container { padding-top: 0.7rem; }
            .dashboard-hero { padding: 1.25rem; border-radius: 18px; }
            .kpi-grid { grid-template-columns: 1fr; }
            .summary-bar { align-items: flex-start; flex-direction: column; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_sample_data() -> pd.DataFrame:
    return pd.read_csv(SAMPLE_FILE)


def money(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


st.markdown(
    """
    <section class="dashboard-hero">
        <h1>Análise de Vendas e Comportamento de Clientes</h1>
        <p>Visão executiva do desempenho comercial, perfil de compra e principais oportunidades do negócio.</p>
    </section>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.header("Fonte de dados", anchor=False)
    use_sample = st.toggle("Usar dados de demonstração", value=True)
    uploaded_file = None
    if not use_sample:
        uploaded_file = st.file_uploader("Envie seu arquivo CSV", type="csv")

if use_sample:
    source = load_sample_data()
elif uploaded_file is None:
    st.info("Envie um CSV para iniciar a análise.")
    st.stop()
else:
    try:
        source = pd.read_csv(uploaded_file, sep=None, engine="python", encoding="utf-8-sig")
    except Exception as error:
        st.error(f"Não foi possível ler o CSV: {error}")
        st.stop()

try:
    initial_result = analyze_sales(source)
except SalesValidationError as error:
    st.error(str(error))
    st.stop()
except Exception as error:
    st.error(f"Não foi possível processar a base: {error}")
    st.stop()

sales = initial_result.sales
valid_dates = sales["order_date"].dropna()

with st.sidebar:
    st.header("Filtros", anchor=False)
    categories = sorted(sales["category"].dropna().unique())
    regions = sorted(sales["region"].dropna().unique())
    payments = sorted(sales["payment_method"].dropna().unique())
    selected_categories = st.multiselect("Categorias", categories, default=categories)
    selected_regions = st.multiselect("Regiões", regions, default=regions)
    selected_payments = st.multiselect("Formas de pagamento", payments, default=payments)
    if valid_dates.empty:
        date_range = None
    else:
        date_range = st.date_input(
            "Período",
            value=(valid_dates.min().date(), valid_dates.max().date()),
            min_value=valid_dates.min().date(),
            max_value=valid_dates.max().date(),
        )

mask = (
    sales["category"].isin(selected_categories)
    & sales["region"].isin(selected_regions)
    & sales["payment_method"].isin(selected_payments)
)
if date_range and len(date_range) == 2:
    start_date, end_date = date_range
    mask &= sales["order_date"].dt.date.between(start_date, end_date)

filtered = sales.loc[mask, [column for column in sales.columns if column in source.columns]].copy()
if filtered.empty:
    st.warning("Nenhuma venda corresponde aos filtros selecionados.")
    st.stop()

result = analyze_sales(filtered)
summary = result.summary
analysis_dates = result.sales["order_date"].dropna()
period_label = (
    f'{analysis_dates.min():%d/%m/%Y} a {analysis_dates.max():%d/%m/%Y}'
    if not analysis_dates.empty
    else "Período não informado"
)

st.markdown(
    f"""
    <div class="summary-bar">
        <div class="summary-title">Resumo executivo</div>
        <div class="period-pill">Período analisado: {period_label}</div>
    </div>
    <section class="kpi-grid">
        <article class="kpi-card" style="--accent:#2563eb">
            <div class="kpi-top"><span class="kpi-label">Faturamento líquido</span><span class="kpi-icon">R$</span></div>
            <div class="kpi-value">{money(summary["net_revenue"])}</div>
            <div class="kpi-note">Receita das vendas concluídas após descontos</div>
        </article>
        <article class="kpi-card" style="--accent:#7c3aed">
            <div class="kpi-top"><span class="kpi-label">Pedidos concluídos</span><span class="kpi-icon">✓</span></div>
            <div class="kpi-value">{summary["completed_orders"]}</div>
            <div class="kpi-note">Pedidos considerados no faturamento</div>
        </article>
        <article class="kpi-card" style="--accent:#0891b2">
            <div class="kpi-top"><span class="kpi-label">Ticket médio</span><span class="kpi-icon">↗</span></div>
            <div class="kpi-value">{money(summary["average_ticket"])}</div>
            <div class="kpi-note">Valor médio por pedido concluído</div>
        </article>
        <article class="kpi-card" style="--accent:#0f766e">
            <div class="kpi-top"><span class="kpi-label">Itens vendidos</span><span class="kpi-icon">▦</span></div>
            <div class="kpi-value">{summary["items_sold"]}</div>
            <div class="kpi-note">Quantidade total de produtos vendidos</div>
        </article>
        <article class="kpi-card" style="--accent:#16a34a">
            <div class="kpi-top"><span class="kpi-label">Clientes ativos</span><span class="kpi-icon">●</span></div>
            <div class="kpi-value">{summary["active_customers"]}</div>
            <div class="kpi-note">Clientes únicos com compras concluídas</div>
        </article>
        <article class="kpi-card" style="--accent:#d97706">
            <div class="kpi-top"><span class="kpi-label">Descontos concedidos</span><span class="kpi-icon">%</span></div>
            <div class="kpi-value">{money(summary["discount_value"])}</div>
            <div class="kpi-note">Valor total reduzido nas negociações</div>
        </article>
        <article class="kpi-card" style="--accent:#dc2626">
            <div class="kpi-top"><span class="kpi-label">Taxa de cancelamento</span><span class="kpi-icon">×</span></div>
            <div class="kpi-value">{summary["cancellation_rate"]:.1f}%</div>
            <div class="kpi-note">Participação dos pedidos cancelados</div>
        </article>
    </section>
    """,
    unsafe_allow_html=True,
)

overview_tab, products_tab, customers_tab, data_tab = st.tabs(
    ["Visão geral", "Produtos e categorias", "Clientes", "Dados e qualidade"]
)

with overview_tab:
    st.subheader("Evolução mensal do faturamento", anchor=False)
    monthly_chart = px.line(
        result.monthly_metrics,
        x="order_month",
        y="revenue",
        markers=True,
        labels={"order_month": "Mês", "revenue": "Faturamento líquido (R$)"},
    )
    st.plotly_chart(monthly_chart, width="stretch")

    left, right = st.columns(2)
    with left:
        st.subheader("Faturamento por região", anchor=False)
        chart = px.bar(
            result.region_metrics,
            x="region",
            y="revenue",
            color="revenue",
            labels={"region": "Região", "revenue": "Faturamento (R$)"},
            color_continuous_scale="Blues",
        )
        chart.update_layout(coloraxis_showscale=False)
        st.plotly_chart(chart, width="stretch")
    with right:
        st.subheader("Formas de pagamento", anchor=False)
        chart = px.pie(
            result.payment_metrics,
            names="payment_method",
            values="revenue",
            hole=0.45,
            labels={"payment_method": "Pagamento", "revenue": "Faturamento"},
        )
        st.plotly_chart(chart, width="stretch")

with products_tab:
    left, right = st.columns(2)
    with left:
        st.subheader("Produtos com maior faturamento", anchor=False)
        top_products = result.product_metrics.head(10).sort_values("revenue")
        chart = px.bar(
            top_products,
            x="revenue",
            y="product",
            orientation="h",
            labels={"product": "Produto", "revenue": "Faturamento (R$)"},
        )
        st.plotly_chart(chart, width="stretch")
    with right:
        st.subheader("Categorias com maior faturamento", anchor=False)
        chart = px.bar(
            result.category_metrics,
            x="category",
            y="revenue",
            color="category",
            labels={"category": "Categoria", "revenue": "Faturamento (R$)"},
        )
        chart.update_layout(showlegend=False)
        st.plotly_chart(chart, width="stretch")

    product_table = result.product_metrics.rename(
        columns={"product": "Produto", "revenue": "Faturamento", "orders": "Pedidos", "items": "Itens"}
    )
    st.dataframe(
        product_table,
        width="stretch",
        hide_index=True,
        column_config={"Faturamento": st.column_config.NumberColumn(format="R$ %.2f")},
    )

with customers_tab:
    st.subheader("Clientes com maior faturamento", anchor=False)
    customer_table = result.customer_metrics.rename(
        columns={
            "customer_id": "ID do cliente",
            "customer_name": "Cliente",
            "revenue": "Faturamento",
            "orders": "Pedidos",
            "items": "Itens",
            "last_purchase": "Última compra",
            "average_ticket": "Ticket médio",
        }
    )
    st.dataframe(
        customer_table,
        width="stretch",
        hide_index=True,
        column_config={
            "Faturamento": st.column_config.NumberColumn(format="R$ %.2f"),
            "Ticket médio": st.column_config.NumberColumn(format="R$ %.2f"),
            "Última compra": st.column_config.DatetimeColumn(format="DD/MM/YYYY"),
        },
    )

with data_tab:
    quality_tab, sales_tab = st.tabs(["Qualidade dos dados", "Vendas processadas"])
    with quality_tab:
        quality = result.quality_checks.rename(
            columns={"check": "Verificação", "issue_count": "Problemas", "status": "Situação", "detail": "Descrição"}
        )
        st.dataframe(quality, width="stretch", hide_index=True)
    with sales_tab:
        display = result.sales[
            ["order_id", "order_date", "customer_name", "product", "category", "quantity", "net_revenue", "payment_method", "status", "region"]
        ].rename(
            columns={
                "order_id": "Pedido",
                "order_date": "Data",
                "customer_name": "Cliente",
                "product": "Produto",
                "category": "Categoria",
                "quantity": "Quantidade",
                "net_revenue": "Faturamento líquido",
                "payment_method": "Pagamento",
                "status": "Status",
                "region": "Região",
            }
        )
        st.dataframe(
            display,
            width="stretch",
            hide_index=True,
            column_config={"Faturamento líquido": st.column_config.NumberColumn(format="R$ %.2f")},
        )



st.divider()
st.caption("Projeto de portfólio desenvolvido com Python, Pandas, Streamlit, Plotly e dados fictícios.")
