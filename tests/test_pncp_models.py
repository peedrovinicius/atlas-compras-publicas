from datetime import date

from dental_procurement_intelligence.pncp.models import PNCPContract, PNCPItemResult


def test_contract_publication_datetime_is_reduced_to_date() -> None:
    contract = PNCPContract.model_validate(
        {
            "numeroControlePNCP": "01612541000133-1-000047/2026",
            "dataPublicacaoPncp": "2026-07-20T16:17:50",
        }
    )

    assert contract.publication_date == date(2026, 7, 20)


def test_contract_publication_date_still_accepts_plain_date() -> None:
    contract = PNCPContract.model_validate(
        {
            "dataPublicacaoPncp": "2026-07-20",
        }
    )

    assert contract.publication_date == date(2026, 7, 20)


def test_result_datetime_is_reduced_to_date() -> None:
    result = PNCPItemResult.model_validate(
        {
            "numeroItem": 1,
            "dataResultado": "2026-07-21T09:10:11",
        }
    )

    assert result.result_date == date(2026, 7, 21)
