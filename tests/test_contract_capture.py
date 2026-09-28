import json
from pathlib import Path

import httpx

from dental_procurement_intelligence.config import Settings
from dental_procurement_intelligence.ingestion import EvidenceStore, capture_contract
from dental_procurement_intelligence.pncp import PNCPClient


def test_capture_contract_collects_metadata_items_and_results(
    tmp_path: Path,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path

        if path.endswith("/compras/2021/1"):
            return httpx.Response(
                200,
                json={
                    "numeroControlePNCP": "example",
                    "anoCompra": 2021,
                    "sequencialCompra": 1,
                    "dataPublicacaoPncp": "2021-08-01",
                    "unidadeOrgao": {
                        "municipioId": 2304400,
                        "municipioNome": "Fortaleza",
                        "ufSigla": "CE",
                        "ufNome": "Ceará",
                    },
                },
            )

        if path.endswith("/itens"):
            return httpx.Response(
                200,
                json=[
                    {
                        "numeroItem": 1,
                        "descricao": "RESINA COMPOSTA A2 SERINGA 4G",
                        "temResultado": True,
                    },
                    {
                        "numeroItem": 2,
                        "descricao": "ADESIVO DENTAL FRASCO 5ML",
                        "temResultado": False,
                    },
                ],
            )

        if path.endswith("/itens/1/resultados"):
            return httpx.Response(
                200,
                content=json.dumps(
                    {
                        "listaResultados": [
                            {
                                "numeroItem": 1,
                                "sequencialResultado": 1,
                                "quantidadeHomologada": 2,
                                "valorUnitarioHomologado": 30,
                            }
                        ]
                    }
                ).encode(),
            )

        raise AssertionError(f"Rota inesperada: {path}")

    client = PNCPClient(
        settings=Settings(pncp_base_url="https://example.test"),
        transport=httpx.MockTransport(handler),
    )

    try:
        result = capture_contract(
            client,
            EvidenceStore(tmp_path),
            cnpj="10.000.000/0000-03",
            year=2021,
            sequence=1,
        )
    finally:
        client.close()

    assert result.procurement_key == "pncp:10000000000003:2021:1"
    assert Path(result.bundle_manifest_path).exists()
    assert result.item_count == 2
    assert result.result_response_count == 1
    assert result.result_count == 1
    assert len(result.result_evidence) == 1
    assert result.item_page_evidence == ()
    assert Path(result.contract_evidence.object_path).exists()
    assert Path(result.item_evidence.object_path).exists()



def test_capture_contract_can_skip_transient_result_timeout(
    tmp_path: Path,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path

        if path.endswith("/compras/2021/1"):
            return httpx.Response(
                200,
                json={
                    "numeroControlePNCP": "example",
                    "anoCompra": 2021,
                    "sequencialCompra": 1,
                },
            )

        if path.endswith("/itens"):
            return httpx.Response(
                200,
                json=[
                    {
                        "numeroItem": 1,
                        "descricao": "RESINA COMPOSTA A2 SERINGA 4G",
                        "temResultado": True,
                    },
                    {
                        "numeroItem": 2,
                        "descricao": "ADESIVO DENTAL FRASCO 5ML",
                        "temResultado": True,
                    },
                ],
            )

        if path.endswith("/itens/1/resultados"):
            raise httpx.ReadTimeout("temporary timeout", request=request)

        if path.endswith("/itens/2/resultados"):
            return httpx.Response(
                200,
                json={
                    "listaResultados": [
                        {
                            "numeroItem": 2,
                            "sequencialResultado": 1,
                            "quantidadeHomologada": 1,
                            "valorUnitarioHomologado": 12,
                        }
                    ]
                },
            )

        raise AssertionError(f"Rota inesperada: {path}")

    client = PNCPClient(
        settings=Settings(
            pncp_base_url="https://example.test",
            pncp_max_attempts=1,
        ),
        transport=httpx.MockTransport(handler),
    )

    try:
        result = capture_contract(
            client,
            EvidenceStore(tmp_path),
            cnpj="10.000.000/0000-03",
            year=2021,
            sequence=1,
            skip_result_transport_errors=True,
        )
    finally:
        client.close()

    assert result.item_count == 2
    assert result.result_response_count == 1
    assert result.result_count == 1



def test_capture_contract_limits_result_requests(
    tmp_path: Path,
) -> None:
    requested_results: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path

        if path.endswith("/compras/2021/1"):
            return httpx.Response(
                200,
                json={
                    "numeroControlePNCP": "example",
                    "anoCompra": 2021,
                    "sequencialCompra": 1,
                },
            )

        if path.endswith("/itens"):
            return httpx.Response(
                200,
                json=[
                    {
                        "numeroItem": 1,
                        "descricao": "RESINA COMPOSTA A2 SERINGA 4G",
                        "temResultado": True,
                    },
                    {
                        "numeroItem": 2,
                        "descricao": "ADESIVO DENTAL FRASCO 5ML",
                        "temResultado": True,
                    },
                ],
            )

        if "/resultados" in path:
            item_number = int(path.split("/itens/")[1].split("/")[0])
            requested_results.append(item_number)
            return httpx.Response(
                200,
                json={
                    "listaResultados": [
                        {
                            "numeroItem": item_number,
                            "sequencialResultado": 1,
                            "quantidadeHomologada": 1,
                            "valorUnitarioHomologado": 10,
                        }
                    ]
                },
            )

        raise AssertionError(f"Rota inesperada: {path}")

    client = PNCPClient(
        settings=Settings(pncp_base_url="https://example.test"),
        transport=httpx.MockTransport(handler),
    )

    try:
        result = capture_contract(
            client,
            EvidenceStore(tmp_path),
            cnpj="10.000.000/0000-03",
            year=2021,
            sequence=1,
            max_result_requests=1,
        )
    finally:
        client.close()

    assert requested_results == [1]
    assert result.result_response_count == 1
    assert result.result_count == 1
