import httpx

from dental_procurement_intelligence.config import Settings
from dental_procurement_intelligence.pncp.client import PNCPClient


def test_get_items_maps_public_pncp_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/orgaos/10000000000003/compras/2021/1/itens"
        return httpx.Response(
            200,
            json=[
                {
                    "numeroItem": 1,
                    "descricao": "RESINA COMPOSTA A2 4G",
                    "quantidade": 10,
                    "unidadeMedida": "UNIDADE",
                    "valorUnitarioEstimado": 35.9,
                    "valorTotal": 359,
                }
            ],
        )

    client = PNCPClient(
        settings=Settings(pncp_base_url="https://example.test"),
        transport=httpx.MockTransport(handler),
    )
    try:
        items = client.get_items("10.000.000/0000-03", 2021, 1)
    finally:
        client.close()

    assert len(items) == 1
    assert items[0].description == "RESINA COMPOSTA A2 4G"
    assert str(items[0].estimated_unit_value) == "35.9"


def test_invalid_cnpj_is_rejected_before_network_call() -> None:
    client = PNCPClient(settings=Settings(pncp_base_url="https://example.test"))
    try:
        try:
            client.get_items("123", 2021, 1)
        except ValueError as exc:
            assert str(exc) == "CNPJ must contain exactly 14 digits"
        else:
            raise AssertionError("Expected ValueError")
    finally:
        client.close()
