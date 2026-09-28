from dental_procurement_intelligence.analytics.awards import build_award_frame
from dental_procurement_intelligence.pncp import PNCPContract, PNCPItem, PNCPItemResult


def test_award_frame_adds_geographic_and_temporal_context() -> None:
    contract = PNCPContract.model_validate(
        {
            "numeroControlePNCP": "control",
            "anoCompra": 2026,
            "sequencialCompra": 1,
            "modalidadeNome": "Pregão - Eletrônico",
            "dataPublicacaoPncp": "2026-07-01",
            "orgaoEntidade": {
                "cnpj": "12345678000190",
                "razaoSocial": "Secretaria Municipal de Saúde",
                "esferaId": "M",
            },
            "unidadeOrgao": {
                "codigoUnidade": "UASG-001",
                "nomeUnidade": "Coordenação de Saúde Bucal",
                "municipioId": 2304400,
                "municipioNome": "Fortaleza",
                "ufSigla": "CE",
                "ufNome": "Ceará",
            },
        }
    )
    item = PNCPItem.model_validate(
        {
            "numeroItem": 1,
            "descricao": "RESINA COMPOSTA A2 SERINGA 4G",
            "valorUnitarioEstimado": 40,
        }
    )
    result = PNCPItemResult.model_validate(
        {
            "numeroItem": 1,
            "sequencialResultado": 1,
            "valorUnitarioHomologado": 36,
            "quantidadeHomologada": 10,
            "dataResultado": "2026-07-15",
            "situacaoCompraItemResultadoId": 1,
        }
    )

    frame = build_award_frame(
        [item],
        "itemhash",
        [([result], "resulthash")],
        contract=contract,
        contract_source_sha256="contracthash",
    )
    row = frame.to_dicts()[0]

    assert row["contract_source_sha256"] == "contracthash"
    assert row["analysis_year"] == 2026
    assert row["analysis_quarter"] == "2026-T3"
    assert row["organization_cnpj"] == "12345678000190"
    assert row["organization_name"] == "Secretaria Municipal de Saúde"
    assert row["buyer_unit_code"] == "UASG-001"
    assert row["buyer_unit_name"] == "Coordenação de Saúde Bucal"
    assert row["municipality_ibge"] == "2304400"
    assert row["municipality_name"] == "Fortaleza"
    assert row["state_code"] == "CE"
    assert row["macroregion"] == "Nordeste"
    assert row["government_sphere"] == "M"
