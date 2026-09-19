"""Regras reutilizáveis para análise de vendas e comportamento de clientes."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import pandas as pd


REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "customer_id",
    "customer_name",
    "product",
    "category",
    "quantity",
    "unit_price",
    "discount_pct",
    "payment_method",
    "status",
    "region",
]

COMPLETED_STATUSES = {"concluida", "concluido", "paga", "pago", "entregue"}
CANCELED_STATUSES = {"cancelada", "cancelado"}


class SalesValidationError(ValueError):
    """Erro apresentado quando a base de vendas não possui o formato esperado."""


@dataclass(frozen=True)
class SalesAnalysisResult:
    summary: dict[str, int | float]
    sales: pd.DataFrame
    monthly_metrics: pd.DataFrame
    product_metrics: pd.DataFrame
    category_metrics: pd.DataFrame
    customer_metrics: pd.DataFrame
    payment_metrics: pd.DataFrame
    region_metrics: pd.DataFrame
    quality_checks: pd.DataFrame


def _normalize_label(value: object) -> str:
    if pd.isna(value):
        return ""
    translation = str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc")
    return str(value).strip().casefold().translate(translation)


def _validate_columns(frame: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise SalesValidationError(
            "A base não contém as colunas obrigatórias: " + ", ".join(missing) + "."
        )


def prepare_sales(frame: pd.DataFrame) -> pd.DataFrame:
    sales = frame.copy()
    sales.columns = [str(column).strip().lower() for column in sales.columns]
    _validate_columns(sales)
    sales = sales[REQUIRED_COLUMNS].copy()

    text_columns = [
        "order_id",
        "customer_id",
        "customer_name",
        "product",
        "category",
        "payment_method",
        "status",
        "region",
    ]
    for column in text_columns:
        sales[column] = sales[column].astype("string").str.strip()

    sales["order_date"] = pd.to_datetime(sales["order_date"], errors="coerce")
    for column in ["quantity", "unit_price", "discount_pct"]:
        sales[column] = pd.to_numeric(sales[column], errors="coerce")

    sales["discount_pct"] = sales["discount_pct"].fillna(0)
    sales["status_normalized"] = sales["status"].map(_normalize_label)
    sales["is_completed"] = sales["status_normalized"].isin(COMPLETED_STATUSES)
    sales["is_canceled"] = sales["status_normalized"].isin(CANCELED_STATUSES)
    sales["gross_revenue"] = sales["quantity"] * sales["unit_price"]
    sales["discount_value"] = sales["gross_revenue"] * sales["discount_pct"] / 100
    sales["net_revenue"] = sales["gross_revenue"] - sales["discount_value"]
    sales.loc[~sales["is_completed"], ["gross_revenue", "discount_value", "net_revenue"]] = 0
    sales["order_month"] = sales["order_date"].dt.to_period("M").dt.to_timestamp()
    return sales


def _quality_checks(sales: pd.DataFrame) -> pd.DataFrame:
    known_statuses = COMPLETED_STATUSES | CANCELED_STATUSES | {
        "pendente",
        "em processamento",
    }
    checks = [
        ("duplicate_rows", int(sales.duplicated().sum()), "Linhas totalmente duplicadas."),
        ("invalid_order_date", int(sales["order_date"].isna().sum()), "Vendas sem data válida."),
        ("invalid_quantity", int((sales["quantity"].isna() | (sales["quantity"] <= 0)).sum()), "Itens com quantidade vazia ou menor que um."),
        ("invalid_unit_price", int((sales["unit_price"].isna() | (sales["unit_price"] < 0)).sum()), "Itens com preço vazio ou negativo."),
        ("invalid_discount", int((~sales["discount_pct"].between(0, 100)).sum()), "Descontos fora do intervalo de 0% a 100%."),
        ("missing_customer", int(sales["customer_id"].isna().sum()), "Registros sem cliente identificado."),
        ("unknown_status", int((~sales["status_normalized"].isin(known_statuses)).sum()), "Registros com status não reconhecido."),
    ]
    return pd.DataFrame(
        {
            "check": [item[0] for item in checks],
            "issue_count": [item[1] for item in checks],
            "status": ["OK" if item[1] == 0 else "ATENÇÃO" for item in checks],
            "detail": [item[2] for item in checks],
        }
    )


def _summary(sales: pd.DataFrame) -> dict[str, int | float]:
    completed = sales[sales["is_completed"]]
    completed_orders = completed["order_id"].nunique()
    all_orders = sales["order_id"].nunique()
    canceled_orders = sales.loc[sales["is_canceled"], "order_id"].nunique()
    return {
        "net_revenue": round(float(completed["net_revenue"].sum()), 2),
        "completed_orders": int(completed_orders),
        "average_ticket": round(float(completed["net_revenue"].sum() / completed_orders), 2)
        if completed_orders
        else 0.0,
        "items_sold": int(completed["quantity"].sum()),
        "active_customers": int(completed["customer_id"].nunique()),
        "discount_value": round(float(completed["discount_value"].sum()), 2),
        "cancellation_rate": round(float(canceled_orders / all_orders * 100), 2)
        if all_orders
        else 0.0,
    }


def _group_metrics(sales: pd.DataFrame, column: str) -> pd.DataFrame:
    completed = sales[sales["is_completed"]]
    return (
        completed.groupby(column, dropna=False)
        .agg(
            revenue=("net_revenue", "sum"),
            orders=("order_id", "nunique"),
            items=("quantity", "sum"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )


def analyze_sales(frame: pd.DataFrame) -> SalesAnalysisResult:
    sales = prepare_sales(frame)
    completed = sales[sales["is_completed"]]

    monthly = (
        completed.groupby("order_month", dropna=False)
        .agg(revenue=("net_revenue", "sum"), orders=("order_id", "nunique"), items=("quantity", "sum"))
        .reset_index()
        .sort_values("order_month")
    )
    customers = (
        completed.groupby(["customer_id", "customer_name"], dropna=False)
        .agg(
            revenue=("net_revenue", "sum"),
            orders=("order_id", "nunique"),
            items=("quantity", "sum"),
            last_purchase=("order_date", "max"),
        )
        .reset_index()
    )
    customers["average_ticket"] = customers["revenue"].div(customers["orders"]).round(2)
    customers = customers.sort_values("revenue", ascending=False)

    return SalesAnalysisResult(
        summary=_summary(sales),
        sales=sales,
        monthly_metrics=monthly,
        product_metrics=_group_metrics(sales, "product"),
        category_metrics=_group_metrics(sales, "category"),
        customer_metrics=customers,
        payment_metrics=_group_metrics(sales, "payment_method"),
        region_metrics=_group_metrics(sales, "region"),
        quality_checks=_quality_checks(sales),
    )


def build_excel_report(result: SalesAnalysisResult) -> bytes:
    output = BytesIO()
    summary = pd.DataFrame(
        [{"metric": key, "value": value} for key, value in result.summary.items()]
    )
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="resumo", index=False)
        result.sales.drop(columns=["status_normalized"]).to_excel(writer, sheet_name="vendas", index=False)
        result.customer_metrics.to_excel(writer, sheet_name="clientes", index=False)
        result.product_metrics.to_excel(writer, sheet_name="produtos", index=False)
        result.category_metrics.to_excel(writer, sheet_name="categorias", index=False)
        result.monthly_metrics.to_excel(writer, sheet_name="evolucao_mensal", index=False)
        result.quality_checks.to_excel(writer, sheet_name="qualidade", index=False)
    return output.getvalue()
