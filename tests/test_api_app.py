import pytest

from dental_procurement_intelligence.api.app import create_app
from dental_procurement_intelligence.identity.models import ProductCategory


def test_api_exposes_versioned_analytics_routes() -> None:
    pytest.importorskip("fastapi")

    app = create_app("data/analytics.duckdb")
    paths = {route.path for route in app.routes}

    assert "/" in paths
    assert "/health" in paths
    assert "/api/v1/normalize" in paths
    assert "/api/v1/normalize/batch" in paths
    assert "/api/v1/domains" in paths
    assert "/api/v1/parser/categories" in paths
    assert "/api/v1/overview" in paths
    assert "/api/v1/categories" in paths
    assert "/api/v1/quality" in paths
    assert "/api/v1/awards" in paths
    assert "/api/v1/anomalies" in paths
    assert "/api/v1/unrecognized" in paths


def test_public_demo_normalizes_real_example() -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    client = TestClient(create_app("data/analytics.duckdb"))

    response = client.get(
        "/api/v1/normalize",
        params={"description": "RES FOTOP A2 C/2 SERINGAS 4G"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["atlas_version"] == "1.49.0"
    assert payload["classification_method"] == "deterministic_rules"
    assert payload["category"] == "composite_resin"
    assert payload["presentation"] == "syringe"
    assert payload["shade"] == "A2"
    assert payload["package_count"] == 2
    assert payload["unit_quantity"] == {
        "value": "4",
        "unit": "g",
        "dimension": "mass",
    }
    assert payload["total_quantity"] == {
        "value": "8",
        "unit": "g",
        "dimension": "mass",
    }


def test_public_demo_root_is_available_without_analytics_database() -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    client = TestClient(create_app("data/analytics.duckdb"))
    response = client.get("/")

    assert response.status_code == 200
    assert "Teste uma ou várias descrições." in response.text
    assert "O que reconhece hoje" in response.text
    assert "Resina composta" in response.text
    assert "Anestésico local" in response.text
    assert "Não reconhecido" in response.text
    assert "CIMENTO ODONTOLOGICO" in response.text
    assert "Testar agora" in response.text
    assert "Uma descrição por linha" in response.text
    assert "category-button" in response.text
    assert "Atributos técnicos" in response.text
    assert "DOMContentLoaded" in response.text
    assert "Atlas de Compras Públicas v1.49.0" in response.text


def test_health_exposes_current_version() -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    client = TestClient(create_app("data/analytics.duckdb"))
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.49.0"}


@pytest.mark.parametrize("description", ["", "  "])
def test_normalize_rejects_empty_or_blank_input(description: str) -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    client = TestClient(create_app("data/analytics.duckdb"))
    response = client.get(
        "/api/v1/normalize",
        params={"description": description},
    )

    assert response.status_code == 422


def test_normalize_rejects_oversized_input() -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    client = TestClient(create_app("data/analytics.duckdb"))
    response = client.get(
        "/api/v1/normalize",
        params={"description": "A" * 2001},
    )

    assert response.status_code == 422


def test_normalize_rate_limit_is_enforced() -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    client = TestClient(create_app("data/analytics.duckdb"))
    params = {"description": "RESINA COMPOSTA A2 SERINGA 4G"}

    for _ in range(60):
        response = client.get("/api/v1/normalize", params=params)
        assert response.status_code == 200

    response = client.get("/api/v1/normalize", params=params)

    assert response.status_code == 429
    assert response.headers["retry-after"] == "60"


def test_supported_parser_categories_match_product_category_enum() -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    client = TestClient(create_app("data/analytics.duckdb"))
    response = client.get("/api/v1/parser/categories")

    assert response.status_code == 200
    payload = response.json()
    ids = {item["id"] for item in payload}

    assert ids == {category.value for category in ProductCategory}
    assert len(payload) == len(ProductCategory)
    assert sum(item["fallback"] for item in payload) == 1
    assert next(item for item in payload if item["fallback"])["id"] == "unknown"


def test_public_demo_lists_every_supported_category_label() -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    client = TestClient(create_app("data/analytics.duckdb"))
    categories = client.get("/api/v1/parser/categories").json()
    html = client.get("/").text

    for category in categories:
        assert category["label"] in html


def test_public_demo_batch_normalizes_multiple_descriptions() -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    client = TestClient(create_app("data/analytics.duckdb"))
    response = client.post(
        "/api/v1/normalize/batch",
        json=[
            "RES FOTOP A2 C/2 SERINGAS 4G",
            "HIDROXIDO DE CALCIO P.A 10G",
        ],
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2
    assert [item["category"] for item in payload["items"]] == [
        "composite_resin",
        "calcium_hydroxide",
    ]


def test_public_demo_batch_rejects_more_than_twenty_descriptions() -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    client = TestClient(create_app("data/analytics.duckdb"))
    response = client.post(
        "/api/v1/normalize/batch",
        json=["RESINA COMPOSTA A2 SERINGA 4G"] * 21,
    )

    assert response.status_code == 422
