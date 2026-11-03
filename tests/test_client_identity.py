"""Testes da resolucao defensiva da identidade do visitante."""

from types import SimpleNamespace

import pytest
from starlette.datastructures import Headers

from dental_procurement_intelligence.api.client_identity import (
    resolve_normalization_client_identity,
)


def make_request(*header_values: str, client_host: str | None = "127.0.0.1"):
    # Preserva a duplicidade real dos cabeçalhos HTTP no teste.
    headers = Headers(
        raw=[(b"cf-connecting-ip", value.encode()) for value in header_values]
    )
    client = SimpleNamespace(host=client_host) if client_host is not None else None
    return SimpleNamespace(headers=headers, client=client)


def test_render_ignores_headers_until_cloudflare_trust_is_explicit() -> None:
    request = make_request("198.51.100.42", client_host="203.0.113.50")
    assert (
        resolve_normalization_client_identity(
            request, render_runtime=True, trust_cloudflare=False
        )
        == "render:unverified-shared"
    )


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("198.51.100.42", "cloudflare:198.51.100.42"),
        (" 198.51.100.42 ", "cloudflare:198.51.100.42"),
        ("2001:DB8::1", "cloudflare:2001:db8::1"),
        ("::ffff:198.51.100.42", "cloudflare:198.51.100.42"),
    ],
)
def test_render_trusted_header_canonicalizes_single_ip(
    header: str, expected: str
) -> None:
    assert (
        resolve_normalization_client_identity(
            make_request(header, client_host="203.0.113.50"),
            render_runtime=True,
            trust_cloudflare=True,
        )
        == expected
    )


@pytest.mark.parametrize(
    "headers",
    [
        (),
        ("",),
        ("not-an-ip",),
        ("198.51.100.42, 203.0.113.50",),
        ("198.51.100.42:1234",),
        ("[2001:db8::1]:1234",),
        ("2001:db8::1%eth0",),
        ("2001:db8::1%eth1",),
        ("198.51.100.42", "198.51.100.43"),
        ("198.51.100.42", "198.51.100.42"),
    ],
)
def test_render_rejects_untrusted_or_ambiguous_header_values(
    headers: tuple[str, ...],
) -> None:
    assert (
        resolve_normalization_client_identity(
            make_request(*headers, client_host="203.0.113.50"),
            render_runtime=True,
            trust_cloudflare=True,
        )
        == "render:unverified-shared"
    )


def test_outside_render_ignores_cf_header_and_uses_asgi_client() -> None:
    assert (
        resolve_normalization_client_identity(
            make_request("198.51.100.42", client_host="127.0.0.2"),
            render_runtime=False,
            trust_cloudflare=True,
        )
        == "asgi:127.0.0.2"
    )


def test_outside_render_without_client_uses_unknown_shared_identity() -> None:
    assert (
        resolve_normalization_client_identity(
            make_request(client_host=None),
            render_runtime=False,
            trust_cloudflare=False,
        )
        == "asgi:unknown"
    )
