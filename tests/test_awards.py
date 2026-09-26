import json
from decimal import Decimal
from pathlib import Path

import polars as pl

from dental_procurement_intelligence.analytics.awards import (
    build_award_frame,
    load_raw_results,
)
from dental_procurement_intelligence.pncp import PNCPItem, PNCPItemResult


def test_award_frame_calculates_economy_and_normalized_price() -> None:
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
    result = PNCPItemResult.model_validate(
        {
            "numeroItem": 1,
            "sequencialResultado": 1,
            "quantidadeHomologada": "10",
            "valorUnitarioHomologado": "72.00",
            "valorTotalHomologado": "720.00",
            "nomeRazaoSocialFornecedor": "Fornecedor Teste",
            "situacaoCompraItemResultadoId": 1,
            "situacaoCompraItemResultadoNome": "Informado",
        }
    )

    frame = build_award_frame(
        [item],
        "itemhash",
        [([result], "resulthash")],
    )
    row = frame.to_dicts()[0]

    assert row["economy_total"] == Decimal("80.000000000000")
    assert row["economy_percent"] == Decimal("10.000000000000")
    assert row["estimated_price_per_base_unit"] == Decimal("10.000000000000")
    assert row["awarded_price_per_base_unit"] == Decimal("9.000000000000")
    assert frame.schema["awarded_unit_value"] == pl.Decimal(
        precision=38,
        scale=12,
    )
    assert frame.schema["awarded_price_per_base_unit"] == pl.Decimal(
        precision=38,
        scale=12,
    )
    assert row["price_normalization_status"] == "defensible"
    assert row["package_count"] == 2
    assert row["result_source_sha256"] == "resulthash"


def test_cancelled_result_is_excluded() -> None:
    item = PNCPItem(
        numeroItem=1,
        descricao="RESINA COMPOSTA A2 SERINGA 4G",
        quantidade=Decimal("1"),
        unidadeMedida="UNIDADE",
        valorUnitarioEstimado=Decimal("40"),
        valorTotal=Decimal("40"),
    )
    result = PNCPItemResult(
        numeroItem=1,
        sequencialResultado=1,
        quantidadeHomologada=Decimal("1"),
        valorUnitarioHomologado=Decimal("35"),
        situacaoCompraItemResultadoId=2,
        situacaoCompraItemResultadoNome="Cancelado",
    )

    frame = build_award_frame([item], "itemhash", [([result], "resulthash")])

    assert frame.height == 0


def test_load_raw_results_accepts_lista_resultados_wrapper(tmp_path: Path) -> None:
    payload = {
        "listaResultados": [
            {
                "numeroItem": 3,
                "sequencialResultado": 1,
                "quantidadeHomologada": 2,
                "valorUnitarioHomologado": 20,
                "valorTotalHomologado": 40,
                "situacaoCompraItemResultadoId": 1,
            }
        ]
    }
    path = tmp_path / "results.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    results, digest = load_raw_results(path)

    assert len(results) == 1
    assert results[0].item_number == 3
    assert len(digest) == 64


def test_award_frame_does_not_normalize_ambiguous_box_price() -> None:
    item = PNCPItem.model_validate(
        {
            "numeroItem": 1,
            "descricao": "RESINA COMPOSTA A2 SERINGA 4G",
            "unidadeMedida": "CAIXA",
            "valorUnitarioEstimado": "80.00",
        }
    )
    result = PNCPItemResult.model_validate(
        {
            "numeroItem": 1,
            "sequencialResultado": 1,
            "quantidadeHomologada": "1",
            "valorUnitarioHomologado": "72.00",
            "situacaoCompraItemResultadoId": 1,
        }
    )

    row = build_award_frame(
        [item],
        "itemhash",
        [([result], "resulthash")],
    ).to_dicts()[0]

    assert row["unit_quantity_value"] == 4.0
    assert row["normalized_quantity_value"] is None
    assert row["awarded_price_per_base_unit"] is None
    assert row["price_normalization_status"] == "review"


def test_award_frame_rejects_multiple_measure_price_basis() -> None:
    item = PNCPItem.model_validate(
        {
            "numeroItem": 1,
            "descricao": (
                "KIT RESINA COMPOSTA A2 SERINGA 4G "
                "MAIS ADESIVO FRASCO 5ML"
            ),
            "unidadeMedida": "KIT",
            "valorUnitarioEstimado": "120.00",
        }
    )
    result = PNCPItemResult.model_validate(
        {
            "numeroItem": 1,
            "sequencialResultado": 1,
            "quantidadeHomologada": "1",
            "valorUnitarioHomologado": "110.00",
            "situacaoCompraItemResultadoId": 1,
        }
    )

    row = build_award_frame(
        [item],
        "itemhash",
        [([result], "resulthash")],
    ).to_dicts()[0]

    assert row["measurement_candidate_count"] == 2
    assert row["measurement_resolution"] == "ambiguous"
    assert row["normalized_quantity_value"] is None
    assert row["awarded_price_per_base_unit"] is None
    assert row["price_normalization_status"] == "review"
    assert row["price_normalization_reason"] == "mixed_product_kit"
