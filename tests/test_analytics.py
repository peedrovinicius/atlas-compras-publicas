import hashlib
import json
from decimal import Decimal
from pathlib import Path

from dental_procurement_intelligence.analytics import (
    DuckDBWarehouse,
    build_analytics,
    build_item_frame,
)
from dental_procurement_intelligence.pncp import PNCPItem


def test_build_item_frame_normalizes_price_by_total_package_mass() -> None:
    item = PNCPItem.model_validate(
        {
            "numeroItem": 1,
            "descricao": "RES FOTOP A2 C/2 SERINGAS 4G",
            "quantidade": 10,
            "unidadeMedida": "CAIXA",
            "valorUnitarioEstimado": "80.00",
            "valorTotal": "800.00",
        }
    )

    frame = build_item_frame([item], source_sha256="abc123")
    row = frame.to_dicts()[0]

    assert row["product_category"] == "composite_resin"
    assert row["normalized_total_quantity_value"] == 8.0
    assert row["normalized_total_quantity_unit"] == "g"
    assert row["normalized_price_per_base_unit"] == 10.0
    assert row["price_normalization_status"] == "defensible"
    assert row["price_normalization_reason"] == "explicit_package_count"
    assert row["source_sha256"] == "abc123"


def test_build_item_frame_preserves_decimal_text() -> None:
    item = PNCPItem(
        numeroItem=1,
        descricao="RESINA COMPOSTA A2 SERINGA 4G",
        quantidade=Decimal("3.50"),
        unidadeMedida="UNIDADE",
        valorUnitarioEstimado=Decimal("35.90"),
        valorTotal=Decimal("125.65"),
    )

    row = build_item_frame([item], source_sha256="hash").to_dicts()[0]

    assert row["procurement_quantity_decimal"] == "3.50"
    assert row["estimated_unit_value_decimal"] == "35.90"
    assert row["total_value_decimal"] == "125.65"


def test_build_analytics_creates_parquet_and_duckdb(tmp_path: Path) -> None:
    payload = [
        {
            "numeroItem": 1,
            "descricao": "RESINA COMPOSTA A2 SERINGA 4G",
            "quantidade": 10,
            "unidadeMedida": "UNIDADE",
            "valorUnitarioEstimado": 40,
            "valorTotal": 400,
        },
        {
            "numeroItem": 2,
            "descricao": "RESINA COMPOSTA A2 SERINGA 4G",
            "quantidade": 5,
            "unidadeMedida": "UNIDADE",
            "valorUnitarioEstimado": 48,
            "valorTotal": 240,
        },
    ]
    raw_path = tmp_path / "raw.json"
    raw_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    raw_path.write_bytes(raw_bytes)

    parquet_path = tmp_path / "silver" / "items.parquet"
    database_path = tmp_path / "analytics.duckdb"

    result = build_analytics(raw_path, parquet_path, database_path)

    assert result.source_sha256 == hashlib.sha256(raw_bytes).hexdigest()
    assert result.row_count == 2
    assert result.identified_row_count == 2
    assert result.priced_row_count == 2
    assert parquet_path.exists()
    assert database_path.exists()

    summary = DuckDBWarehouse(database_path).summary()

    assert summary[0]["product_category"] == "composite_resin"
    assert summary[0]["item_count"] == 2
    assert summary[0]["priced_item_count"] == 2
    assert summary[0]["median_normalized_price"] == 11.0


def test_box_without_explicit_package_count_is_not_price_normalized() -> None:
    item = PNCPItem.model_validate(
        {
            "numeroItem": 1,
            "descricao": "RESINA COMPOSTA A2 SERINGA 4G",
            "quantidade": 10,
            "unidadeMedida": "CAIXA",
            "valorUnitarioEstimado": "80.00",
        }
    )

    row = build_item_frame([item], source_sha256="hash").to_dicts()[0]

    assert row["unit_quantity_value"] == 4.0
    assert row["normalized_total_quantity_value"] is None
    assert row["normalized_price_per_base_unit"] is None
    assert row["price_normalization_status"] == "review"
    assert (
        row["price_normalization_reason"]
        == "package_count_missing_for_procurement_package"
    )
