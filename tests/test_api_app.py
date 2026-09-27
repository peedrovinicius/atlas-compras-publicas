import pytest

from dental_procurement_intelligence.api.app import create_app


def test_api_exposes_versioned_analytics_routes() -> None:
    pytest.importorskip("fastapi")

    app = create_app("data/analytics.duckdb")
    paths = {route.path for route in app.routes}

    assert "/health" in paths
    assert "/api/v1/domains" in paths
    assert "/api/v1/overview" in paths
    assert "/api/v1/categories" in paths
    assert "/api/v1/quality" in paths
    assert "/api/v1/awards" in paths
    assert "/api/v1/anomalies" in paths
    assert "/api/v1/unrecognized" in paths
