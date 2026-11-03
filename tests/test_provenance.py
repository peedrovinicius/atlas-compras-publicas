"""Teste da persistência de origem e dos contratos públicos da API."""

from pathlib import Path

import duckdb
import pytest
from fastapi.testclient import TestClient

from dental_procurement_intelligence.analytics.provenance import (
    read_provenance,
    write_provenance,
)
from dental_procurement_intelligence.api.app import create_app


@pytest.fixture
def database(tmp_path: Path) -> Path:
    path = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(path)) as connection:
        connection.execute("CREATE TABLE silver_awards (award_key VARCHAR)")
        connection.execute("INSERT INTO silver_awards VALUES ('a1'), ('a2')")
    return path


def test_missing_and_old_metadata_never_claims_real_prices(database: Path) -> None:
    assert read_provenance("nonexistent.duckdb")["source_type"] == "unknown"
    assert read_provenance(database)["source_type"] == "unknown"
    client = TestClient(create_app(database))
    for route in ("/health", "/ready", "/api/v1/meta"):
        response = client.get(route)
        assert response.status_code == 200
        assert response.json()["provenance"]["source_type"] == "unknown"


@pytest.mark.parametrize(
    ("source", "keys"),
    [
        ("pncp_sample", ("pncp:15126437000305:2026:212",)),
        ("offline_synthetic", ("pncp:00000000000000:2026:1",)),
    ],
)
def test_database_persists_and_api_exposes_source(
    database: Path, source: str, keys: tuple[str, ...]
) -> None:
    write_provenance(
        database,
        source_type=source,
        procurement_keys=keys,
        result_count=3,
        observation_count=2,
    )
    data = read_provenance(database)
    assert data["source_type"] == source
    assert data["procurement_keys"] == list(keys)
    assert data["procurement_count"] == 1
    assert data["result_count"] == 3
    assert data["observation_count"] == 2
    assert data["captured_at"].endswith("+00:00")
    client = TestClient(create_app(database))
    for route in ("/health", "/ready", "/api/v1/meta"):
        assert client.get(route).json()["provenance"] == data


def test_corrupted_observation_count_fails_closed(database: Path) -> None:
    write_provenance(
        database,
        source_type="pncp_sample",
        procurement_keys=("pncp:15126437000305:2026:212",),
        result_count=3,
        observation_count=2,
    )
    with duckdb.connect(str(database)) as connection:
        connection.execute("INSERT INTO silver_awards VALUES ('a3')")
    assert read_provenance(database)["source_type"] == "unknown"


@pytest.mark.parametrize(
    ("source", "keys"),
    [
        ("pncp_sample", ("pncp:00000000000000:2026:1",)),
        ("offline_synthetic", ("pncp:15126437000305:2026:212",)),
        ("pncp_sample", ("garbage",)),
    ],
)
def test_reject_fake_real_keys(
    database: Path, source: str, keys: tuple[str, ...]
) -> None:
    with pytest.raises(ValueError, match="Metadados de proveniência"):
        write_provenance(
            database,
            source_type=source,
            procurement_keys=keys,
            result_count=3,
            observation_count=2,
        )
    assert read_provenance(database)["source_type"] == "unknown"


def test_reject_observation_mismatch(database: Path) -> None:
    with pytest.raises(ValueError, match="Contagem de observações"):
        write_provenance(
            database,
            source_type="pncp_sample",
            procurement_keys=("pncp:15126437000305:2026:212",),
            result_count=3,
            observation_count=200,
        )


def test_csv_contains_synthetic_source_independent_of_frontend(
    database: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_provenance(
        database,
        source_type="offline_synthetic",
        procurement_keys=("pncp:00000000000000:2026:1",),
        result_count=12,
        observation_count=2,
    )
    monkeypatch.setattr(
        "dental_procurement_intelligence.api.app.analytics_product_records_export",
        lambda *args, **kwargs: [{"award_key": "a1"}],
    )
    response = TestClient(create_app(database)).get(
        f"/api/v1/products/{'a' * 32}/records.csv"
    )
    assert response.status_code == 200
    assert "data_source_type,award_key" in response.text
    assert "offline_synthetic,a1" in response.text
    assert response.headers["x-atlas-provenance"] == "offline_synthetic"
    assert "offline_synthetic" in response.headers["content-disposition"]
    assert response.headers["cache-control"] == "no-store"
