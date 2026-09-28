from decimal import Decimal
from pathlib import Path

import duckdb
import pytest

from dental_procurement_intelligence.api import service


def test_analytics_overview_uses_shared_analytics_layer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "analytics.duckdb"
    database.write_bytes(b"duckdb-placeholder")

    monkeypatch.setattr(
        service.DuckDBWarehouse,
        "summary",
        lambda self: [{"product_category": "composite_resin", "item_count": 3}],
    )
    monkeypatch.setattr(
        service,
        "quality_summary",
        lambda path: {"total_items": 3, "category_identified_items": 3},
    )
    monkeypatch.setattr(
        service,
        "quality_by_category",
        lambda path: [{"product_category": "composite_resin"}],
    )
    monkeypatch.setattr(service, "award_summary", lambda path: [])
    monkeypatch.setattr(service, "anomaly_summary", lambda path: [])

    result = service.analytics_overview(database)

    assert result["database"] == "analytics.duckdb"
    assert result["quality"]["total_items"] == 3
    assert result["category_prices"][0]["item_count"] == 3
    assert any(domain["id"] == "dental" for domain in result["domains"])
    assert any(domain["id"] == "medications" for domain in result["domains"])


def test_analytics_overview_requires_existing_database(tmp_path: Path) -> None:
    missing = tmp_path / "missing.duckdb"

    with pytest.raises(FileNotFoundError, match="Banco analítico não encontrado"):
        service.analytics_overview(missing)


def test_categories_support_filter_and_pagination(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "analytics.duckdb"
    database.write_bytes(b"duckdb-placeholder")
    rows = [
        {"product_category": "composite_resin", "item_count": 8},
        {"product_category": "glass_ionomer", "item_count": 5},
        {"product_category": "fluoride_gel", "item_count": 3},
    ]
    monkeypatch.setattr(
        service.DuckDBWarehouse,
        "summary",
        lambda self: rows,
    )

    page = service.analytics_categories(
        database,
        category="glass_ionomer",
        limit=10,
        offset=0,
    )

    assert page == {
        "items": [{"product_category": "glass_ionomer", "item_count": 5}],
        "total": 1,
        "limit": 10,
        "offset": 0,
    }


def test_awards_support_combined_filters(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "analytics.duckdb"
    database.write_bytes(b"duckdb-placeholder")
    rows = [
        {
            "product_category": "composite_resin",
            "macroregion": "Nordeste",
            "analysis_year": 2026,
        },
        {
            "product_category": "composite_resin",
            "macroregion": "Sudeste",
            "analysis_year": 2026,
        },
    ]
    monkeypatch.setattr(service, "award_summary", lambda path: rows)

    page = service.analytics_awards(
        database,
        category="composite_resin",
        macroregion="Nordeste",
        year=2026,
        limit=20,
        offset=0,
    )

    assert page["total"] == 1
    assert page["items"][0]["macroregion"] == "Nordeste"


def test_anomalies_support_scope_filter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "analytics.duckdb"
    database.write_bytes(b"duckdb-placeholder")
    rows = [
        {
            "comparison_scope": "state",
            "product_category": "glass_ionomer",
        },
        {
            "comparison_scope": "national",
            "product_category": "glass_ionomer",
        },
    ]
    monkeypatch.setattr(service, "anomaly_summary", lambda path: rows)

    page = service.analytics_anomalies(
        database,
        category="glass_ionomer",
        scope="state",
        limit=20,
        offset=0,
    )

    assert page["total"] == 1
    assert page["items"][0]["comparison_scope"] == "state"


def test_unrecognized_pagination_uses_total_count(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "analytics.duckdb"
    database.write_bytes(b"duckdb-placeholder")

    monkeypatch.setattr(
        service,
        "unrecognized_items",
        lambda path, limit, offset: [{"item_number": offset + 1}],
    )
    monkeypatch.setattr(service, "unrecognized_count", lambda path: 37)

    page = service.analytics_unrecognized(
        database,
        limit=10,
        offset=20,
    )

    assert page == {
        "items": [{"item_number": 21}],
        "total": 37,
        "limit": 10,
        "offset": 20,
    }


def test_pagination_rejects_invalid_bounds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "analytics.duckdb"
    database.write_bytes(b"duckdb-placeholder")
    monkeypatch.setattr(service.DuckDBWarehouse, "summary", lambda self: [])

    with pytest.raises(ValueError, match="limit"):
        service.analytics_categories(database, limit=0)

    with pytest.raises(ValueError, match="offset"):
        service.analytics_categories(database, offset=-1)



def test_product_search_groups_awards_by_technical_identity(
    tmp_path: Path,
) -> None:
    database = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards AS
            SELECT * FROM (
                VALUES
                    (
                        'p1', 'a1', 1, 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '111', 'CE', DATE '2026-05-10', 10.0,
                        'defensible', 10.00
                    ),
                    (
                        'p2', 'a2', 1, 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '222', 'MG', DATE '2026-06-10', 20.0,
                        'defensible', 12.00
                    ),
                    (
                        'p3', 'a3', 2, 'IONOMERO DE VIDRO 10G',
                        'glass_ionomer', 'powder', NULL, NULL,
                        NULL, NULL, NULL, NULL, NULL,
                        NULL, NULL, 1, 10.0, 'g', NULL, NULL,
                        '333', 'PR', DATE '2026-06-11', 5.0,
                        'review', NULL
                    )
            ) AS t(
                procurement_key,
                award_key,
                item_number,
                original_description,
                product_category,
                presentation,
                shade,
                concentration_percent,
                resin_technology,
                curing_mode,
                adhesive_strategy,
                ionomer_use,
                fluoride_formulation,
                anesthetic_active_ingredient,
                anesthetic_vasoconstrictor,
                package_count,
                unit_quantity_value,
                unit_quantity_unit,
                normalized_quantity_value,
                normalized_quantity_unit,
                supplier_document,
                state_code,
                analysis_date,
                awarded_quantity,
                price_normalization_status,
                awarded_price_per_base_unit
            )
            """
        )

    result = service.analytics_product_search(
        database,
        query="resina composta A2",
        limit=20,
        offset=0,
    )

    assert result["query"] == "resina composta A2"
    assert result["total"] == 1
    item = result["items"][0]
    assert item["product_category"] == "composite_resin"
    assert item["display_name"].startswith("Resina composta")
    assert item["award_count"] == 2
    assert item["procurement_count"] == 2
    assert item["supplier_count"] == 2
    assert item["state_count"] == 2
    assert item["priced_observation_count"] == 2


def test_product_search_rejects_short_query(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"
    database.touch()

    with pytest.raises(ValueError, match="pelo menos 2"):
        service.analytics_product_search(database, query="a")



def test_product_summary_prioritizes_median_and_marks_small_sample(
    tmp_path: Path,
) -> None:
    database = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards AS
            SELECT * FROM (
                VALUES
                    (
                        'p1', 'a1', 1, 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '111', 'CE', DATE '2026-05-10', 10.0,
                        'defensible', 10.00
                    ),
                    (
                        'p2', 'a2', 1, 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '222', 'MG', DATE '2026-06-10', 20.0,
                        'defensible', 12.00
                    )
            ) AS t(
                procurement_key,
                award_key,
                item_number,
                original_description,
                product_category,
                presentation,
                shade,
                concentration_percent,
                resin_technology,
                curing_mode,
                adhesive_strategy,
                ionomer_use,
                fluoride_formulation,
                anesthetic_active_ingredient,
                anesthetic_vasoconstrictor,
                package_count,
                unit_quantity_value,
                unit_quantity_unit,
                normalized_quantity_value,
                normalized_quantity_unit,
                supplier_document,
                state_code,
                analysis_date,
                awarded_quantity,
                price_normalization_status,
                awarded_price_per_base_unit
            )
            """
        )

    search = service.analytics_product_search(
        database,
        query="resina composta A2",
    )
    product_id = search["items"][0]["product_id"]

    summary = service.analytics_product_summary(
        database,
        product_id=product_id,
    )

    assert summary["display_name"].startswith("Resina composta")
    assert summary["award_count"] == 2
    assert summary["procurement_count"] == 2
    assert summary["item_count"] == 2
    assert summary["supplier_count"] == 2
    assert summary["state_count"] == 2
    assert summary["price_sample_count"] == 2
    assert summary["minimum_sample_size"] == 5
    assert summary["sample_sufficient"] is False
    assert summary["price_unit"] == "R$/g"
    assert summary["price_stats"]["median_price"] == Decimal("11.000")
    assert summary["price_stats"]["min_price"] == Decimal("10.000")
    assert summary["price_stats"]["max_price"] == Decimal("12.000")
    assert float(summary["price_stats"]["total_physical_quantity"]) == 120.0


def test_product_summary_rejects_unknown_product(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards (
                product_category VARCHAR,
                presentation VARCHAR,
                shade VARCHAR,
                concentration_percent DOUBLE,
                resin_technology VARCHAR,
                curing_mode VARCHAR,
                adhesive_strategy VARCHAR,
                ionomer_use VARCHAR,
                fluoride_formulation VARCHAR,
                anesthetic_active_ingredient VARCHAR,
                anesthetic_vasoconstrictor VARCHAR,
                package_count BIGINT,
                unit_quantity_value DOUBLE,
                unit_quantity_unit VARCHAR,
                normalized_quantity_value DOUBLE,
                normalized_quantity_unit VARCHAR,
                procurement_key VARCHAR,
                item_number BIGINT,
                supplier_document VARCHAR,
                state_code VARCHAR,
                analysis_date DATE,
                original_description VARCHAR,
                awarded_quantity DOUBLE,
                price_normalization_status VARCHAR,
                awarded_price_per_base_unit DECIMAL(38,12)
            )
            """
        )

    with pytest.raises(LookupError, match="não encontrado"):
        service.analytics_product_summary(
            database,
            product_id="0" * 32,
        )



def test_product_history_aggregates_monthly_prices(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards AS
            SELECT * FROM (
                VALUES
                    (
                        'p1', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '111', 'CE', DATE '2026-05-10', 'defensible', 10.00
                    ),
                    (
                        'p2', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '222', 'MG', DATE '2026-05-20', 'defensible', 14.00
                    ),
                    (
                        'p3', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '333', 'PR', DATE '2026-06-05', 'defensible', 12.00
                    )
            ) AS t(
                procurement_key,
                original_description,
                product_category,
                presentation,
                shade,
                concentration_percent,
                resin_technology,
                curing_mode,
                adhesive_strategy,
                ionomer_use,
                fluoride_formulation,
                anesthetic_active_ingredient,
                anesthetic_vasoconstrictor,
                package_count,
                unit_quantity_value,
                unit_quantity_unit,
                normalized_quantity_value,
                normalized_quantity_unit,
                supplier_document,
                state_code,
                analysis_date,
                price_normalization_status,
                awarded_price_per_base_unit
            )
            """
        )

    search = service.analytics_product_search(
        database,
        query="resina composta A2",
    )
    product_id = search["items"][0]["product_id"]

    history = service.analytics_product_history(
        database,
        product_id=product_id,
    )

    assert history["total_observations"] == 3
    assert len(history["points"]) == 2
    may = history["points"][0]
    assert may["observations"] == 2
    assert float(may["median_price"]) == 12.0
    assert float(may["percentile_25"]) == 11.0
    assert float(may["percentile_75"]) == 13.0
    june = history["points"][1]
    assert june["observations"] == 1
    assert float(june["median_price"]) == 12.0



def test_product_regions_compare_states_to_national_median(
    tmp_path: Path,
) -> None:
    database = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards AS
            SELECT * FROM (
                VALUES
                    (
                        'p1', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '111', 'CE', 'Nordeste', 'defensible', 10.00
                    ),
                    (
                        'p2', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '222', 'MG', 'Sudeste', 'defensible', 20.00
                    ),
                    (
                        'p3', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '333', 'MG', 'Sudeste', 'defensible', 30.00
                    )
            ) AS t(
                procurement_key,
                original_description,
                product_category,
                presentation,
                shade,
                concentration_percent,
                resin_technology,
                curing_mode,
                adhesive_strategy,
                ionomer_use,
                fluoride_formulation,
                anesthetic_active_ingredient,
                anesthetic_vasoconstrictor,
                package_count,
                unit_quantity_value,
                unit_quantity_unit,
                normalized_quantity_value,
                normalized_quantity_unit,
                supplier_document,
                state_code,
                macroregion,
                price_normalization_status,
                awarded_price_per_base_unit
            )
            """
        )

    search = service.analytics_product_search(
        database,
        query="resina composta A2",
    )
    product_id = search["items"][0]["product_id"]

    result = service.analytics_product_regions(
        database,
        product_id=product_id,
    )

    assert result["national"]["observations"] == 3
    assert float(result["national"]["median_price"]) == 20.0
    assert len(result["regions"]) == 2
    states = {row["state_code"]: row for row in result["states"]}
    assert states["CE"]["observations"] == 1
    assert states["CE"]["difference_from_national_percent"] == -50.0
    assert states["MG"]["observations"] == 2
    assert states["MG"]["difference_from_national_percent"] == 25.0



def test_product_suppliers_and_buyers_use_public_award_context(
    tmp_path: Path,
) -> None:
    database = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards AS
            SELECT * FROM (
                VALUES
                    (
                        'p1', 1, 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '111', 'Fornecedor Alfa',
                        '10000000000100', 'Órgão Alfa', 'U1', 'Unidade Alfa',
                        'CE', 'Nordeste', 100.0, 'defensible', 10.00
                    ),
                    (
                        'p2', 1, 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '111', 'Fornecedor Alfa',
                        '20000000000100', 'Órgão Beta', 'U2', 'Unidade Beta',
                        'MG', 'Sudeste', 240.0, 'defensible', 12.00
                    ),
                    (
                        'p3', 1, 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '222', 'Fornecedor Beta',
                        '20000000000100', 'Órgão Beta', 'U2', 'Unidade Beta',
                        'MG', 'Sudeste', 130.0, 'defensible', 13.00
                    )
            ) AS t(
                procurement_key,
                item_number,
                original_description,
                product_category,
                presentation,
                shade,
                concentration_percent,
                resin_technology,
                curing_mode,
                adhesive_strategy,
                ionomer_use,
                fluoride_formulation,
                anesthetic_active_ingredient,
                anesthetic_vasoconstrictor,
                package_count,
                unit_quantity_value,
                unit_quantity_unit,
                normalized_quantity_value,
                normalized_quantity_unit,
                supplier_document,
                supplier_name,
                organization_cnpj,
                organization_name,
                buyer_unit_code,
                buyer_unit_name,
                state_code,
                macroregion,
                awarded_total_value,
                price_normalization_status,
                awarded_price_per_base_unit
            )
            """
        )

    search = service.analytics_product_search(
        database,
        query="resina composta A2",
    )
    product_id = search["items"][0]["product_id"]

    suppliers = service.analytics_product_suppliers(
        database,
        product_id=product_id,
    )
    buyers = service.analytics_product_buyers(
        database,
        product_id=product_id,
    )

    assert suppliers["total"] == 2
    assert suppliers["items"][0]["supplier_name"] == "Fornecedor Alfa"
    assert suppliers["items"][0]["award_count"] == 2
    assert suppliers["items"][0]["sample_share_percent"] == 66.67
    assert float(suppliers["items"][0]["median_price"]) == 11.0

    assert buyers["total"] == 2
    beta = next(
        row for row in buyers["items"]
        if row["organization_name"] == "Órgão Beta"
    )
    assert beta["buyer_unit_name"] == "Unidade Beta"
    assert beta["award_count"] == 2
    assert beta["procurement_count"] == 2
    assert float(beta["awarded_total_value"]) == 370.0
    assert float(beta["median_price"]) == 12.5



def test_product_signals_and_records_preserve_traceability(
    tmp_path: Path,
) -> None:
    database = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards AS
            SELECT * FROM (
                VALUES (
                    'pncp:15126437000305:2026:212',
                    'award-1',
                    'contract-hash',
                    'item-hash',
                    'result-hash',
                    1,
                    1,
                    'RESINA COMPOSTA A2 SERINGA 4G',
                    'composite_resin',
                    'syringe',
                    'A2',
                    NULL,
                    'nanohybrid',
                    'light_cure',
                    NULL,
                    NULL,
                    NULL,
                    NULL,
                    NULL,
                    'UNIDADE',
                    1,
                    4.0,
                    'g',
                    4.0,
                    'g',
                    'Fornecedor Alfa',
                    '111',
                    'Marca X',
                    '15126437000305',
                    'Órgão Alfa',
                    'U1',
                    'Unidade Alfa',
                    'Curitiba',
                    'PR',
                    'Sul',
                    'Pregão',
                    DATE '2026-06-10',
                    10.00,
                    10.0,
                    100.00,
                    10.00,
                    'defensible',
                    'base física identificada'
                )
            ) AS t(
                procurement_key,
                award_key,
                contract_source_sha256,
                item_source_sha256,
                result_source_sha256,
                item_number,
                result_sequence,
                original_description,
                product_category,
                presentation,
                shade,
                concentration_percent,
                resin_technology,
                curing_mode,
                adhesive_strategy,
                ionomer_use,
                fluoride_formulation,
                anesthetic_active_ingredient,
                anesthetic_vasoconstrictor,
                procurement_unit,
                package_count,
                unit_quantity_value,
                unit_quantity_unit,
                normalized_quantity_value,
                normalized_quantity_unit,
                supplier_name,
                supplier_document,
                brand,
                organization_cnpj,
                organization_name,
                buyer_unit_code,
                buyer_unit_name,
                municipality_name,
                state_code,
                macroregion,
                modality,
                analysis_date,
                awarded_unit_value,
                awarded_quantity,
                awarded_total_value,
                awarded_price_per_base_unit,
                price_normalization_status,
                price_normalization_reason
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE gold_price_signals AS
            SELECT
                silver_awards.*,
                'brasil_ano' AS comparison_scope,
                'Brasil' AS comparison_geography,
                '2026' AS comparison_period,
                'group-1' AS scope_group_key,
                8 AS group_size,
                CAST(8.0 AS DECIMAL(38,12)) AS median_price,
                CAST(7.0 AS DECIMAL(38,12)) AS q1_price,
                CAST(9.0 AS DECIMAL(38,12)) AS q3_price,
                CAST(0.5 AS DECIMAL(38,12)) AS mad_price,
                4.2 AS modified_z_score,
                'modified_z_score' AS detection_method,
                TRUE AS is_price_signal
            FROM silver_awards
            """
        )

    search = service.analytics_product_search(
        database,
        query="resina composta A2",
    )
    product_id = search["items"][0]["product_id"]

    signals = service.analytics_product_signals(
        database,
        product_id=product_id,
    )
    records = service.analytics_product_records(
        database,
        product_id=product_id,
    )

    assert signals["total"] == 1
    assert signals["items"][0]["award_key"] == "award-1"
    assert signals["items"][0]["detection_method"] == "modified_z_score"
    assert signals["items"][0]["contract_source_sha256"] == "contract-hash"
    assert "prova de irregularidade" in signals["disclaimer"]
    assert signals["items"][0]["pncp_url"] == (
        "https://pncp.gov.br/app/editais/15126437000305/2026/212"
    )

    assert records["total"] == 1
    record = records["items"][0]
    assert record["original_description"] == "RESINA COMPOSTA A2 SERINGA 4G"
    assert record["supplier_name"] == "Fornecedor Alfa"
    assert record["organization_name"] == "Órgão Alfa"
    assert record["item_source_sha256"] == "item-hash"
    assert record["result_source_sha256"] == "result-hash"
    assert record["pncp_url"] == (
        "https://pncp.gov.br/app/editais/15126437000305/2026/212"
    )



def test_product_distribution_bins_defensible_prices(
    tmp_path: Path,
) -> None:
    database = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards AS
            SELECT * FROM (
                VALUES
                    (
                        'p1', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '111', 'CE', 'defensible', 10.0
                    ),
                    (
                        'p2', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '222', 'MG', 'defensible', 12.0
                    ),
                    (
                        'p3', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '333', 'PR', 'defensible', 30.0
                    ),
                    (
                        'p4', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '444', 'SP', 'review', 999.0
                    )
            ) AS t(
                procurement_key,
                original_description,
                product_category,
                presentation,
                shade,
                concentration_percent,
                resin_technology,
                curing_mode,
                adhesive_strategy,
                ionomer_use,
                fluoride_formulation,
                anesthetic_active_ingredient,
                anesthetic_vasoconstrictor,
                package_count,
                unit_quantity_value,
                unit_quantity_unit,
                normalized_quantity_value,
                normalized_quantity_unit,
                supplier_document,
                state_code,
                price_normalization_status,
                awarded_price_per_base_unit
            )
            """
        )

    search = service.analytics_product_search(
        database,
        query="resina composta A2",
    )
    product_id = search["items"][0]["product_id"]

    result = service.analytics_product_distribution(
        database,
        product_id=product_id,
        bin_count=5,
    )

    assert result["observations"] == 3
    assert result["bin_count"] == 5
    assert result["min_price"] == 10.0
    assert result["max_price"] == 30.0
    assert len(result["bins"]) == 5
    assert sum(item["count"] for item in result["bins"]) == 3
    assert result["bins"][0]["count"] == 2
    assert result["bins"][-1]["count"] == 1



def test_product_search_filters_and_paginates(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards AS
            SELECT * FROM (
                VALUES
                    (
                        'p1', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '111', 'Fornecedor Alfa', 'CE', 'Nordeste',
                        '100', 'Hospital Alfa', 'U1', 'Unidade Central',
                        DATE '2026-05-10', 'defensible', 10.0
                    ),
                    (
                        'p2', 'RESINA COMPOSTA A3 SERINGA 4G',
                        'composite_resin', 'syringe', 'A3', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '222', 'Fornecedor Beta', 'MG', 'Sudeste',
                        '200', 'Hospital Beta', 'U2', 'Unidade Sul',
                        DATE '2026-06-10', 'defensible', 20.0
                    ),
                    (
                        'p3', 'RESINA COMPOSTA B1 SERINGA 4G',
                        'composite_resin', 'syringe', 'B1', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '333', 'Fornecedor Gama', 'PR', 'Sul',
                        '300', 'Clínica Escola', 'U3', 'Odontologia',
                        DATE '2026-07-10', 'defensible', 30.0
                    )
            ) AS t(
                procurement_key,
                original_description,
                product_category,
                presentation,
                shade,
                concentration_percent,
                resin_technology,
                curing_mode,
                adhesive_strategy,
                ionomer_use,
                fluoride_formulation,
                anesthetic_active_ingredient,
                anesthetic_vasoconstrictor,
                package_count,
                unit_quantity_value,
                unit_quantity_unit,
                normalized_quantity_value,
                normalized_quantity_unit,
                supplier_document,
                supplier_name,
                state_code,
                macroregion,
                organization_cnpj,
                organization_name,
                buyer_unit_code,
                buyer_unit_name,
                analysis_date,
                price_normalization_status,
                awarded_price_per_base_unit
            )
            """
        )

    filtered = service.analytics_product_search(
        database,
        query="resina",
        state_code="CE",
        macroregion="Nordeste",
        supplier="alfa",
        buyer="hospital",
        start_date="2026-05-01",
        end_date="2026-05-31",
        limit=10,
        offset=0,
    )

    assert filtered["total"] == 1
    assert filtered["items"][0]["shade"] == "A2"
    assert filtered["filters"]["state_code"] == "CE"
    assert filtered["filters"]["supplier"] == "alfa"

    page = service.analytics_product_search(
        database,
        query="resina",
        limit=1,
        offset=1,
    )

    assert page["total"] == 3
    assert page["limit"] == 1
    assert page["offset"] == 1
    assert len(page["items"]) == 1

    latest = service.analytics_product_search(
        database,
        query="resina",
        sort="latest",
        limit=10,
        offset=0,
    )
    assert [item["shade"] for item in latest["items"]] == ["B1", "A3", "A2"]
    assert latest["sort"] == "latest"

    with pytest.raises(ValueError, match="sort"):
        service.analytics_product_search(
            database,
            query="resina",
            sort="invalid",
        )


def test_product_filters_apply_to_summary_and_records(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards AS
            SELECT * FROM (
                VALUES
                    (
                        'p1', 'a1', 1, 1,
                        'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 'UNIDADE', 1, 4.0, 'g', 4.0, 'g',
                        'Fornecedor Alfa', '111', 'Marca A',
                        '100', 'Hospital Alfa', 'U1', 'Unidade Central',
                        'Fortaleza', 'CE', 'Nordeste', 'Pregão',
                        DATE '2026-05-10', 10.0, 1.0, 10.0, 10.0,
                        'defensible', 'base física identificada',
                        'contract-1', 'item-1', 'result-1'
                    ),
                    (
                        'p2', 'a2', 1, 1,
                        'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 'UNIDADE', 1, 4.0, 'g', 4.0, 'g',
                        'Fornecedor Beta', '222', 'Marca B',
                        '200', 'Hospital Beta', 'U2', 'Unidade Sul',
                        'Belo Horizonte', 'MG', 'Sudeste', 'Pregão',
                        DATE '2026-06-10', 30.0, 1.0, 30.0, 30.0,
                        'defensible', 'base física identificada',
                        'contract-2', 'item-2', 'result-2'
                    )
            ) AS t(
                procurement_key,
                award_key,
                item_number,
                result_sequence,
                original_description,
                product_category,
                presentation,
                shade,
                concentration_percent,
                resin_technology,
                curing_mode,
                adhesive_strategy,
                ionomer_use,
                fluoride_formulation,
                anesthetic_active_ingredient,
                anesthetic_vasoconstrictor,
                procurement_unit,
                package_count,
                unit_quantity_value,
                unit_quantity_unit,
                normalized_quantity_value,
                normalized_quantity_unit,
                supplier_name,
                supplier_document,
                brand,
                organization_cnpj,
                organization_name,
                buyer_unit_code,
                buyer_unit_name,
                municipality_name,
                state_code,
                macroregion,
                modality,
                analysis_date,
                awarded_unit_value,
                awarded_quantity,
                awarded_total_value,
                awarded_price_per_base_unit,
                price_normalization_status,
                price_normalization_reason,
                contract_source_sha256,
                item_source_sha256,
                result_source_sha256
            )
            """
        )

    search = service.analytics_product_search(
        database,
        query="resina composta A2",
    )
    product_id = search["items"][0]["product_id"]

    summary = service.analytics_product_summary(
        database,
        product_id=product_id,
        state_code="CE",
    )
    records = service.analytics_product_records(
        database,
        product_id=product_id,
        state_code="CE",
    )
    distribution = service.analytics_product_distribution(
        database,
        product_id=product_id,
        state_code="CE",
        bin_count=5,
    )

    assert summary["award_count"] == 1
    assert float(summary["price_stats"]["median_price"]) == 10.0
    assert records["total"] == 1
    assert records["items"][0]["state_code"] == "CE"
    assert distribution["observations"] == 1
    assert distribution["min_price"] == 10.0
    assert distribution["max_price"] == 10.0



def test_product_records_export_collects_all_pages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []

    def fake_records(
        database_path: str | Path,
        *,
        product_id: str,
        limit: int,
        offset: int,
        **_: object,
    ) -> dict[str, object]:
        calls.append(offset)
        total = 205
        remaining = max(0, total - offset)
        size = min(limit, remaining)
        return {
            "product_id": product_id,
            "items": [
                {"award_key": f"award-{index}"}
                for index in range(offset, offset + size)
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    monkeypatch.setattr(service, "analytics_product_records", fake_records)

    rows = service.analytics_product_records_export(
        "unused.duckdb",
        product_id="a" * 32,
        state_code="CE",
    )

    assert len(rows) == 205
    assert rows[0]["award_key"] == "award-0"
    assert rows[-1]["award_key"] == "award-204"
    assert calls == [0, 100, 200]
