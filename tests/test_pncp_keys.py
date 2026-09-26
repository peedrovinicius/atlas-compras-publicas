from decimal import Decimal

from dental_procurement_intelligence.pncp import (
    PNCPItemResult,
    award_key,
    procurement_key,
)


def test_procurement_key_normalizes_cnpj() -> None:
    assert (
        procurement_key("01.612.541/0001-33", 2026, 47)
        == "pncp:01612541000133:2026:47"
    )


def test_award_key_prefers_result_sequence() -> None:
    result = PNCPItemResult(
        numeroItem=7,
        sequencialResultado=3,
        valorUnitarioHomologado=Decimal("18.50"),
    )

    assert (
        award_key("pncp:01612541000133:2026:47", result)
        == "pncp:01612541000133:2026:47:item:7:result:3"
    )


def test_award_key_without_sequence_is_deterministic() -> None:
    first = PNCPItemResult(
        numeroItem=7,
        quantidadeHomologada=Decimal("2"),
        valorUnitarioHomologado=Decimal("18.50"),
        niFornecedor="12345678000199",
        nomeRazaoSocialFornecedor="Fornecedor Teste",
    )
    second = PNCPItemResult(
        numeroItem=7,
        quantidadeHomologada=Decimal("2.0"),
        valorUnitarioHomologado=Decimal("18.500"),
        niFornecedor="12345678000199",
        nomeRazaoSocialFornecedor="Fornecedor Teste",
    )

    assert award_key("pncp:01612541000133:2026:47", first) == award_key(
        "pncp:01612541000133:2026:47",
        second,
    )
