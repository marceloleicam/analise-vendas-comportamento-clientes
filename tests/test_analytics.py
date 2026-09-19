from io import BytesIO

import pandas as pd
import pytest

from src.analytics import SalesValidationError, analyze_sales, build_excel_report


def sample_sales() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"order_id": "P1", "order_date": "2026-01-10", "customer_id": "C1", "customer_name": "Ana", "product": "Notebook", "category": "Eletrônicos", "quantity": 1, "unit_price": 4000, "discount_pct": 10, "payment_method": "Cartão", "status": "Concluída", "region": "Sudeste"},
            {"order_id": "P2", "order_date": "2026-01-15", "customer_id": "C2", "customer_name": "Bruno", "product": "Mouse", "category": "Acessórios", "quantity": 2, "unit_price": 100, "discount_pct": 0, "payment_method": "Pix", "status": "Concluída", "region": "Sul"},
            {"order_id": "P3", "order_date": "2026-02-01", "customer_id": "C1", "customer_name": "Ana", "product": "Monitor", "category": "Eletrônicos", "quantity": 1, "unit_price": 1000, "discount_pct": 0, "payment_method": "Cartão", "status": "Cancelada", "region": "Sudeste"},
        ]
    )


def test_calculates_main_indicators() -> None:
    result = analyze_sales(sample_sales())
    assert result.summary["net_revenue"] == 3800
    assert result.summary["completed_orders"] == 2
    assert result.summary["average_ticket"] == 1900
    assert result.summary["items_sold"] == 3
    assert result.summary["active_customers"] == 2
    assert result.summary["cancellation_rate"] == pytest.approx(33.33)


def test_applies_discount_only_to_completed_sales() -> None:
    result = analyze_sales(sample_sales())
    sales = result.sales.set_index("order_id")
    assert sales.loc["P1", "discount_value"] == 400
    assert sales.loc["P1", "net_revenue"] == 3600
    assert sales.loc["P3", "net_revenue"] == 0


def test_builds_customer_ranking() -> None:
    result = analyze_sales(sample_sales())
    assert result.customer_metrics.iloc[0]["customer_name"] == "Ana"
    assert result.customer_metrics.iloc[0]["revenue"] == 3600


def test_builds_product_and_category_metrics() -> None:
    result = analyze_sales(sample_sales())
    assert result.product_metrics.iloc[0]["product"] == "Notebook"
    assert result.category_metrics.iloc[0]["category"] == "Eletrônicos"


def test_rejects_missing_columns() -> None:
    with pytest.raises(SalesValidationError, match="region"):
        analyze_sales(sample_sales().drop(columns="region"))


def test_detects_quality_problems() -> None:
    invalid = sample_sales()
    invalid.loc[0, "quantity"] = 0
    invalid.loc[1, "discount_pct"] = 120
    checks = analyze_sales(invalid).quality_checks.set_index("check")
    assert checks.loc["invalid_quantity", "issue_count"] == 1
    assert checks.loc["invalid_discount", "issue_count"] == 1


def test_excel_report_contains_expected_sheets() -> None:
    report = build_excel_report(analyze_sales(sample_sales()))
    workbook = pd.ExcelFile(BytesIO(report))
    assert set(workbook.sheet_names) == {"resumo", "vendas", "clientes", "produtos", "categorias", "evolucao_mensal", "qualidade"}

