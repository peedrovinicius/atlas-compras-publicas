import json
from collections.abc import Iterable
from dataclasses import dataclass
from time import sleep
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
                "User-Agent": "atlas-compras-publicas/1.53",
            },
        )

    def __enter__(self) -> "PNCPClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def _get_raw(
        self,
        path: str,
        *,
        params: dict[str, int] | None = None,
    ) -> PNCPRawResponse:
        last_error: httpx.TransportError | None = None
        for attempt in range(1, self.settings.pncp_max_attempts + 1):
            try:
                response = self._client.get(path, params=params)
                response.raise_for_status()
                return PNCPRawResponse(
                    url=str(response.url),
                    status_code=response.status_code,
                    content_type=response.headers.get("content-type"),
                    content=response.content,
                )
            except httpx.TransportError as exc:
                last_error = exc
                if attempt == self.settings.pncp_max_attempts:
                    raise
                sleep(
                    self.settings.pncp_retry_backoff_seconds
                    * attempt
                )

        assert last_error is not None
        raise last_error

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
        *,
        page: int | None = None,
        page_size: int | None = None,
    ) -> PNCPRawResponse:
        path = f"/v1/orgaos/{_normalize_cnpj(cnpj)}/compras/{year}/{sequence}/itens"
        params = None
        if page is not None or page_size is not None:
            params = {
                "pagina": page or 1,
                "tamanhoPagina": page_size or 100,
            }
        return self._get_raw(path, params=params)

    def get_item_pages_raw(
        self,
        cnpj: str,
        year: int,
        sequence: int,
        *,
        page_size: int = 100,
        max_pages: int = 1000,
    ) -> list[PNCPRawResponse]:
        if page_size < 1:
            raise ValueError("page_size must be positive")
        if max_pages < 1:
            raise ValueError("max_pages must be positive")

        pages: list[PNCPRawResponse] = []
        seen_payloads: set[bytes] = set()

        for page in range(1, max_pages + 1):
            raw = self.get_items_raw(
                cnpj,
                year,
                sequence,
                page=page,
                page_size=page_size,
            )
            payload = json.loads(raw.content)
            records = list(self._ensure_list(payload))

            if not records:
                if page == 1:
                    pages.append(raw)
                break
            if raw.content in seen_payloads:
                raise ValueError("PNCP item pagination did not advance")

            pages.append(raw)
            seen_payloads.add(raw.content)

            if len(records) < page_size:
                break
        else:
            raise ValueError("PNCP item pagination exceeded max_pages")

        return pages

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
        items: list[PNCPItem] = []
        for raw in self.get_item_pages_raw(cnpj, year, sequence):
            payload = json.loads(raw.content)
            items.extend(
                PNCPItem.model_validate(item)
                for item in self._ensure_list(payload)
            )
        return items

    def item_results(
        self,
        cnpj: str,
        year: int,
        sequence: int,
        item_number: int,
    ) -> list[PNCPItemResult]:
        raw = self.get_item_results_raw(cnpj, year, sequence, item_number)
        if not raw.content.strip():
            return []
        payload = json.loads(raw.content)
        if isinstance(payload, dict):
            payload = payload.get("listaResultados")
        return [
            PNCPItemResult.model_validate(item)
            for item in self._ensure_list(payload)
        ]
