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
    assert "/api/v1/meta" in paths
    assert "/api/v1/domains" in paths
    assert "/api/v1/parser/categories" in paths
    assert "/api/v1/overview" in paths
    assert "/api/v1/products/search" in paths
    assert "/api/v1/products/{product_id}" in paths
    assert "/api/v1/products/{product_id}/history" in paths
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


def test_api_root_redirects_to_react_frontend() -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    client = TestClient(create_app("data/analytics.duckdb"))
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == (
        "https://atlas-compras-publicas-web.onrender.com"
    )


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


def test_parser_categories_expose_readable_labels() -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    client = TestClient(create_app("data/analytics.duckdb"))
    categories = client.get("/api/v1/parser/categories").json()
    labels = {category["label"] for category in categories}

    assert "Resina composta" in labels
    assert "Anestésico local" in labels
    assert "Não reconhecido" in labels


def test_cors_allows_react_frontend() -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    client = TestClient(create_app("data/analytics.duckdb"))
    response = client.options(
        "/api/v1/normalize",
        headers={
            "Origin": "https://atlas-compras-publicas-web.onrender.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == (
        "https://atlas-compras-publicas-web.onrender.com"
    )


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


def test_meta_reports_configured_database(tmp_path, monkeypatch) -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    database = tmp_path / "atlas-demo.duckdb"
    database.touch()
    monkeypatch.setenv("ATLAS_DATABASE_PATH", str(database))
    monkeypatch.setenv(
        "ATLAS_FRONTEND_URL",
        "https://atlas-compras-publicas-web.onrender.com",
    )

    client = TestClient(create_app())
    response = client.get("/api/v1/meta")

    assert response.status_code == 200
    assert response.json() == {
        "version": "1.49.0",
        "database_available": True,
        "database_name": "atlas-demo.duckdb",
        "frontend_url": "https://atlas-compras-publicas-web.onrender.com",
    }
