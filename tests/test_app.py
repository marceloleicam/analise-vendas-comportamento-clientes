from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_dashboard_starts_with_sample_data() -> None:
    app_file = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_file).run(timeout=20)
    assert not app.exception
    assert [tab.label for tab in app.tabs[:4]] == [
        "Visão geral",
        "Produtos e categorias",
        "Clientes",
        "Dados e qualidade",
    ]
