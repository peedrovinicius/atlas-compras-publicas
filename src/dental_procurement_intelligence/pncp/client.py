import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import httpx

from dental_procurement_intelligence.config import Settings
from dental_procurement_intelligence.pncp.models import (
    PNCPContract,
    PNCPItem,
    PNCPItemResult,
)


@dataclass(frozen=True, slots=True)
class PNCPRawResponse:
    url: str
    status_code: int
    content_type: str | None
    content: bytes


def _normalize_cnpj(cnpj: str) -> str:
    normalized = "".join(
        character
        for character in cnpj.upper()
        if character.isascii() and character.isalnum()
    )
    if len(normalized) != 14:
        raise ValueError("CNPJ must contain exactly 14 alphanumeric characters")
    return normalized


class PNCPClient:
    """Small read-only client for public PNCP procurement endpoints."""

    def __init__(
        self,
        settings: Settings | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.settings = settings or Settings()
        self._client = httpx.Client(
            base_url=self.settings.pncp_base_url.rstrip("/"),
            timeout=self.settings.pncp_timeout_seconds,
            follow_redirects=True,
            transport=transport,
            headers={
                "Accept": "application/json",
                "User-Agent": "atlas-compras-publicas/1.49",
            },
        )

    def __enter__(self) -> "PNCPClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def _get_raw(self, path: str) -> PNCPRawResponse:
        response = self._client.get(path)
        response.raise_for_status()
        return PNCPRawResponse(
            url=str(response.url),
            status_code=response.status_code,
            content_type=response.headers.get("content-type"),
            content=response.content,
        )

    @staticmethod
    def _ensure_list(payload: Any) -> Iterable[dict[str, Any]]:
        if not isinstance(payload, list):
            raise ValueError("Unexpected PNCP payload: expected a JSON array")
        return payload

    def get_contract_raw(self, cnpj: str, year: int, sequence: int) -> PNCPRawResponse:
        base_url = self.settings.pncp_query_base_url.rstrip("/")
        url = (
            f"{base_url}/v1/orgaos/{_normalize_cnpj(cnpj)}"
            f"/compras/{year}/{sequence}"
        )
        return self._get_raw(url)

    def get_items_raw(
        self,
        cnpj: str,
        year: int,
        sequence: int,
    ) -> PNCPRawResponse:
        path = f"/v1/orgaos/{_normalize_cnpj(cnpj)}/compras/{year}/{sequence}/itens"
        return self._get_raw(path)

    def get_item_results_raw(
        self,
        cnpj: str,
        year: int,
        sequence: int,
        item_number: int,
    ) -> PNCPRawResponse:
        path = (
            f"/v1/orgaos/{_normalize_cnpj(cnpj)}/compras/{year}/{sequence}"
            f"/itens/{item_number}/resultados"
        )
        return self._get_raw(path)

    def contract(self, cnpj: str, year: int, sequence: int) -> PNCPContract:
        raw = self.get_contract_raw(cnpj, year, sequence)
        return PNCPContract.model_validate(json.loads(raw.content))

    def get_items(self, cnpj: str, year: int, sequence: int) -> list[PNCPItem]:
        return self.contract_items(cnpj, year, sequence)

    def contract_items(self, cnpj: str, year: int, sequence: int) -> list[PNCPItem]:
        raw = self.get_items_raw(cnpj, year, sequence)
        payload = json.loads(raw.content)
        return [
            PNCPItem.model_validate(item)
            for item in self._ensure_list(payload)
        ]

    def item_results(
        self,
        cnpj: str,
        year: int,
        sequence: int,
        item_number: int,
    ) -> list[PNCPItemResult]:
        raw = self.get_item_results_raw(cnpj, year, sequence, item_number)
        payload = json.loads(raw.content)
        if isinstance(payload, dict):
            payload = payload.get("listaResultados")
        return [
            PNCPItemResult.model_validate(item)
            for item in self._ensure_list(payload)
        ]
