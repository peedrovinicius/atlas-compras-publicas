import json
from datetime import UTC, datetime
from pathlib import Path

import duckdb

from dental_procurement_intelligence.analytics import build_award_dataset
from dental_procurement_intelligence.ingestion import (
    EvidenceStore,
    build_contract_bundle,
    discover_contract_bundles,
    write_contract_bundle,
)
from dental_procurement_intelligence.pncp import PNCPRawResponse


def _raw(url: str, payload: object) -> PNCPRawResponse:
    return PNCPRawResponse(
        url=url,
        status_code=200,
        content_type="application/json",
        content=json.dumps(payload).encode("utf-8"),
    )


def _capture_bundle(
    store: EvidenceStore,
    *,
    cnpj: str,
    year: int,
    sequence: int,
    awarded_value: float,
    captured_at: datetime,
) -> Path:
    control = f"{cnpj}-1-{sequence:06d}/{year}"
    base = f"https://example.test/{cnpj}/{year}/{sequence}"

    contract = store.capture(
        _raw(
            f"{base}/contract",
            {
                "numeroControlePNCP": control,
                "anoCompra": year,
                "sequencialCompra": sequence,
                "dataPublicacaoPncp": f"{year}-07-01",
                "orgaoEntidade": {
                    "cnpj": cnpj,
                    "esferaId": "M",
                },
                "unidadeOrgao": {
                    "municipioId": 2304400,
                    "municipioNome": "Fortaleza",
                    "ufSigla": "CE",
                },
            },
        ),
        retrieved_at=captured_at,
    )
    items = store.capture(
        _raw(
            f"{base}/items",
            [
                {
                    "numeroItem": 1,
                    "descricao": "RESINA COMPOSTA A2 SERINGA 4G",
                    "valorUnitarioEstimado": 40,
                }
            ],
        ),
        retrieved_at=captured_at,
    )
    results = store.capture(
        _raw(
            f"{base}/items/1/results",
            {
                "listaResultados": [
                    {
                        "numeroItem": 1,
                        "sequencialResultado": 1,
                        "quantidadeHomologada": 1,
                        "valorUnitarioHomologado": awarded_value,
                        "valorTotalHomologado": awarded_value,
                        "situacaoCompraItemResultadoId": 1,
                    }
                ]
            },
        ),
        retrieved_at=captured_at,
    )

    bundle = build_contract_bundle(
        cnpj=cnpj,
        year=year,
        sequence=sequence,
        contract_evidence=contract,
        item_evidence=items,
        result_evidence=(results,),
    )
    return write_contract_bundle(store, bundle)


def test_multi_contract_dataset_is_idempotent_and_preserves_other_contracts(
    tmp_path: Path,
) -> None:
    store = EvidenceStore(tmp_path / "raw")
    first_time = datetime(2026, 9, 26, 20, 0, tzinfo=UTC)

    first_path = _capture_bundle(
        store,
        cnpj="01612541000133",
        year=2026,
        sequence=47,
        awarded_value=36,
        captured_at=first_time,
    )
    second_path = _capture_bundle(
        store,
        cnpj="04394805000118",
        year=2026,
        sequence=83,
        awarded_value=32,
        captured_at=first_time,
    )

    parquet = tmp_path / "silver" / "awards.parquet"
    database = tmp_path / "analytics.duckdb"

    result = build_award_dataset(
        [first_path, second_path, first_path],
        parquet,
        database,
    )

    assert result.row_count == 2
    assert result.procurement_count == 2
    assert result.manifest_count == 3
    assert result.superseded_manifest_count == 1

    with duckdb.connect(str(database), read_only=True) as connection:
        rows = connection.execute(
            """
            SELECT procurement_key, award_key, awarded_unit_value
            FROM silver_awards
            ORDER BY procurement_key
            """
        ).fetchall()

    assert len(rows) == 2
    assert len({row[0] for row in rows}) == 2
    assert len({row[1] for row in rows}) == 2

    later = datetime(2026, 9, 26, 21, 0, tzinfo=UTC)
    updated_path = _capture_bundle(
        store,
        cnpj="01612541000133",
        year=2026,
        sequence=47,
        awarded_value=34,
        captured_at=later,
    )

    assert updated_path == first_path

    manifests = discover_contract_bundles(store.root / "contracts")
    rebuilt = build_award_dataset(manifests, parquet, database)

    assert rebuilt.row_count == 2
    assert rebuilt.procurement_count == 2

    with duckdb.connect(str(database), read_only=True) as connection:
        values = dict(
            connection.execute(
                """
                SELECT procurement_key, awarded_unit_value
                FROM silver_awards
                ORDER BY procurement_key
                """
            ).fetchall()
        )

    assert values["pncp:01612541000133:2026:47"] == 34
    assert values["pncp:04394805000118:2026:83"] == 32
