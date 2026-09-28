import pytest

from dental_procurement_intelligence.api.app import create_app


def test_api_exposes_versioned_analytics_routes() -> None:
    pytest.importorskip("fastapi")

    app = create_app("data/analytics.duckdb")
    paths = {route.path for route in app.routes}

    assert "/" in paths
    assert "/health" in paths
    assert "/api/v1/normalize" in paths
    assert "/api/v1/domains" in paths
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
    assert "Demo pública" in response.text
    assert "não simula preços" in response.text
