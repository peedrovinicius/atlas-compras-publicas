import hashlib
import json
from decimal import Decimal
from pathlib import Path

import duckdb
import polars as pl

from dental_procurement_intelligence.analytics import (
    DuckDBWarehouse,
    build_analytics,
    build_analytics_dataset,
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

    assert row["procurement_key"] is None
    assert row["product_category"] == "composite_resin"
    assert row["normalized_total_quantity_value"] == 8.0
    assert row["normalized_total_quantity_unit"] == "g"
    assert row["estimated_unit_value"] == Decimal("80.000000000000")
    assert row["normalized_price_per_base_unit"] == Decimal("10.000000000000")
    assert frame.schema["estimated_unit_value"] == pl.Decimal(
        precision=38,
        scale=12,
    )
    assert frame.schema["normalized_price_per_base_unit"] == pl.Decimal(
        precision=38,
        scale=12,
    )
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

    page_hash = hashlib.sha256(raw_bytes).hexdigest()
    expected_dataset_hash = hashlib.sha256(page_hash.encode("ascii")).hexdigest()
    assert result.source_sha256 == expected_dataset_hash
    assert result.row_count == 2
    assert result.identified_row_count == 2
    assert result.priced_row_count == 2
    assert parquet_path.exists()
    assert database_path.exists()

    summary = DuckDBWarehouse(database_path).summary()

    with duckdb.connect(str(database_path), read_only=True) as connection:
        duckdb_types = {
            row[1]: row[2]
            for row in connection.execute(
                "PRAGMA table_info('silver_items')"
            ).fetchall()
        }

    assert duckdb_types["estimated_unit_value"] == "DECIMAL(38,12)"
    assert duckdb_types["total_value"] == "DECIMAL(38,12)"
    assert (
        duckdb_types["normalized_price_per_base_unit"]
        == "DECIMAL(38,12)"
    )

    assert summary[0]["product_category"] == "composite_resin"
    assert summary[0]["item_count"] == 2
    assert summary[0]["priced_item_count"] == 2
    assert summary[0]["median_normalized_price"] == Decimal("11.000000000000")


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


def test_multiple_physical_measurements_are_sent_to_review() -> None:
    item = PNCPItem.model_validate(
        {
            "numeroItem": 1,
            "descricao": (
                "KIT RESINA COMPOSTA A2 SERINGA 4G "
                "MAIS ADESIVO FRASCO 5ML"
            ),
            "quantidade": 1,
            "unidadeMedida": "KIT",
            "valorUnitarioEstimado": "120.00",
        }
    )

    row = build_item_frame([item], source_sha256="hash").to_dicts()[0]

    assert row["measurement_candidate_count"] == 2
    assert row["measurement_resolution"] == "ambiguous"
    assert row["normalized_total_quantity_value"] is None
    assert row["normalized_price_per_base_unit"] is None
    assert row["price_normalization_status"] == "review"
    assert row["price_normalization_reason"] == "mixed_product_kit"


def test_explicit_total_measurement_is_used_as_price_basis() -> None:
    item = PNCPItem.model_validate(
        {
            "numeroItem": 1,
            "descricao": (
                "RESINA COMPOSTA A2 C/2 SERINGAS 4G "
                "CONTEUDO TOTAL 8G"
            ),
            "quantidade": 1,
            "unidadeMedida": "CAIXA",
            "valorUnitarioEstimado": "80.00",
        }
    )

    row = build_item_frame([item], source_sha256="hash").to_dicts()[0]

    assert row["measurement_resolution"] == "package_total_confirmed"
    assert row["normalized_total_quantity_value"] == 8.0
    assert row["normalized_price_per_base_unit"] == 10.0
    assert row["price_normalization_status"] == "defensible"
    assert (
        row["price_normalization_reason"]
        == "explicit_package_total_confirmed"
    )


def test_normalized_price_uses_decimal_rounding_not_binary_float() -> None:
    item = PNCPItem.model_validate(
        {
            "numeroItem": 1,
            "descricao": "RESINA COMPOSTA A2 SERINGA 3G",
            "quantidade": 1,
            "unidadeMedida": "UNIDADE",
            "valorUnitarioEstimado": "0.10",
        }
    )

    row = build_item_frame([item], source_sha256="hash").to_dicts()[0]

    assert row["estimated_unit_value"] == Decimal("0.100000000000")
    assert row["normalized_price_per_base_unit"] == Decimal("0.033333333333")


def test_item_frame_exposes_technical_attributes() -> None:
    item = PNCPItem.model_validate(
        {
            "numeroItem": 1,
            "descricao": (
                "RESINA COMPOSTA NANOHIBRIDA A2 "
                "FOTOPOLIMERIZAVEL SERINGA 4G"
            ),
            "quantidade": 1,
            "unidadeMedida": "UNIDADE",
            "valorUnitarioEstimado": "40.00",
        }
    )

    row = build_item_frame([item], source_sha256="hash").to_dicts()[0]

    assert row["technical_attribute_count"] == 2
    assert row["resin_technology"] == "nanohybrid"
    assert row["curing_mode"] == "light_cure"
    assert row["adhesive_strategy"] is None


def test_build_analytics_dataset_preserves_page_hash_per_item(
    tmp_path: Path,
) -> None:
    first_payload = [
        {
            "numeroItem": 1,
            "descricao": "RESINA COMPOSTA A2 SERINGA 4G",
        }
    ]
    second_payload = [
        {
            "numeroItem": 2,
            "descricao": "ADESIVO DENTAL FRASCO 5ML",
        }
    ]
    first_path = tmp_path / "page-1.json"
    second_path = tmp_path / "page-2.json"
    first_bytes = json.dumps(first_payload).encode("utf-8")
    second_bytes = json.dumps(second_payload).encode("utf-8")
    first_path.write_bytes(first_bytes)
    second_path.write_bytes(second_bytes)

    database = tmp_path / "analytics.duckdb"
    result = build_analytics_dataset(
        [first_path, second_path],
        tmp_path / "items.parquet",
        database,
    )

    assert result.row_count == 2

    with duckdb.connect(str(database), read_only=True) as connection:
        rows = connection.execute(
            """
            SELECT item_number, source_sha256
            FROM silver_items
            ORDER BY item_number
            """
        ).fetchall()

    assert rows == [
        (1, hashlib.sha256(first_bytes).hexdigest()),
        (2, hashlib.sha256(second_bytes).hexdigest()),
    ]


def test_build_analytics_dataset_allows_same_item_number_across_procurements(
    tmp_path: Path,
) -> None:
    first_path = tmp_path / "procurement-a.json"
    second_path = tmp_path / "procurement-b.json"
    first_path.write_text(
        json.dumps(
            [{"numeroItem": 1, "descricao": "RESINA COMPOSTA A2 SERINGA 4G"}]
        ),
        encoding="utf-8",
    )
    second_path.write_text(
        json.dumps(
            [{"numeroItem": 1, "descricao": "ADESIVO DENTAL FRASCO 5ML"}]
        ),
        encoding="utf-8",
    )

    database = tmp_path / "analytics.duckdb"
    result = build_analytics_dataset(
        [first_path, second_path],
        tmp_path / "items.parquet",
        database,
        procurement_key_by_path={
            first_path.as_posix(): "pncp:1:2026:1",
            second_path.as_posix(): "pncp:2:2026:1",
        },
    )

    assert result.row_count == 2

    with duckdb.connect(str(database), read_only=True) as connection:
        rows = connection.execute(
            """
            SELECT procurement_key, item_number, product_category
            FROM silver_items
            ORDER BY procurement_key
            """
        ).fetchall()

    assert rows == [
        ("pncp:1:2026:1", 1, "composite_resin"),
        ("pncp:2:2026:1", 1, "dental_adhesive"),
    ]
