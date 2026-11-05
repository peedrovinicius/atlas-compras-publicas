"""Exercita o limitador com Uvicorn real em HTTP local, sem usar o Render."""

from collections.abc import Iterator
from contextlib import contextmanager
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
from time import monotonic, sleep

import httpx
import pytest
import uvicorn
from fastapi import Request

from dental_procurement_intelligence.api.app import create_app

PARAMS = {"description": "RESINA COMPOSTA A2 SERINGA 4G"}


@contextmanager
def local_uvicorn(trusted_proxies: str) -> Iterator[httpx.Client]:
    """Inicia Uvicorn em uma porta efemera acessivel somente por loopback."""
    app = create_app("data/analytics.duckdb")

    # A rota adicional existe apenas no objeto de teste, nunca na producao.
    @app.get("/__test_asgi_client")
    def show_client(request: Request) -> dict[str, str]:
        return {"host": request.client.host if request.client else "unknown"}

    listener = socket(AF_INET, SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(128)
    port = listener.getsockname()[1]
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        proxy_headers=True,
        forwarded_allow_ips=trusted_proxies,
        lifespan="off",
        log_level="critical",
        access_log=False,
    )
    server = uvicorn.Server(config)
    worker = Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
    worker.start()
    try:
        deadline = monotonic() + 5.0
        while not server.started and monotonic() < deadline:
            sleep(0.02)
        assert server.started, "Uvicorn local nao iniciou"

        with httpx.Client(
            base_url=f"http://127.0.0.1:{port}",
            timeout=5.0,
            trust_env=False,
        ) as client:
            yield client
    finally:
        server.should_exit = True
        worker.join(timeout=5)
        listener.close()
        assert not worker.is_alive(), "Uvicorn local nao encerrou"


def test_http_untrusted_peer_cannot_change_rate_limit_identity() -> None:
    # O socket local 127.0.0.1 NAO esta na lista de proxies confiaveis.
    with local_uvicorn("10.0.0.10") as client:
        for attempt in range(60):
            response = client.get(
                "/api/v1/normalize",
                params=PARAMS,
                headers={"X-Forwarded-For": f"203.0.113.{attempt + 1}"},
            )
            assert response.status_code == 200

        blocked = client.get(
            "/api/v1/normalize",
            params=PARAMS,
            headers={"X-Forwarded-For": "198.51.100.250"},
        )
        assert blocked.status_code == 429


def test_http_known_proxy_chain_discards_spoofed_prefix() -> None:
    # 127.0.0.1 representa o balanceador; 10.0.0.10, o hop intermediario.
    # O cliente 198.51.100.42 e o ultimo endereco nao confiavel da direita.
    with local_uvicorn("127.0.0.1,10.0.0.10") as client:
        for attempt in range(60):
            response = client.get(
                "/api/v1/normalize",
                params=PARAMS,
                headers={
                    "X-Forwarded-For": (
                        f"203.0.113.{attempt + 1}, 198.51.100.42, 10.0.0.10"
                    )
                },
            )
            assert response.status_code == 200

        blocked = client.get(
            "/api/v1/normalize",
            params=PARAMS,
            headers={"X-Forwarded-For": "203.0.113.250, 198.51.100.42, 10.0.0.10"},
        )
        assert blocked.status_code == 429

        distinct_client = client.get(
            "/api/v1/normalize",
            params=PARAMS,
            headers={"X-Forwarded-For": "203.0.113.250, 198.51.100.43, 10.0.0.10"},
        )
        assert distinct_client.status_code == 200


def test_http_trust_everything_exposes_spoofed_address() -> None:
    # Contraprova: uma configuracao '*' interpreta o prefixo falsificavel.
    # Este comportamento e um risco documentado, nao uma configuracao recomendada.
    with local_uvicorn("*") as client:
        response = client.get(
            "/__test_asgi_client",
            headers={"X-Forwarded-For": "203.0.113.42, 198.51.100.42, 10.0.0.10"},
        )
        assert response.status_code == 200
        assert response.json() == {"host": "203.0.113.42"}



def test_http_render_without_cf_trust_cannot_bypass_through_xff(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Simula env padrao do Render com Uvicorn confiando em qualquer proxy.
    # Sem permitir explicitamente Cloudflare, nao usa ASGI host falsificado.
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.delenv("ATLAS_TRUST_CF_CONNECTING_IP", raising=False)
    with local_uvicorn("*") as client:
        for attempt in range(60):
            r = client.get(
                "/api/v1/normalize",
                params=PARAMS,
                headers={
                    "X-Forwarded-For": f"203.0.113.{attempt + 1}",
                    "CF-Connecting-IP": f"198.51.100.{attempt + 1}",
                },
            )
            assert r.status_code == 200

        blocked = client.get(
            "/api/v1/normalize",
            params=PARAMS,
            headers={
                "X-Forwarded-For": "203.0.113.250",
                "CF-Connecting-IP": "198.51.100.250",
            },
        )
        assert blocked.status_code == 429


def test_http_render_cf_trust_opt_in_separates_clients_and_ignores_xff(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Simulacao somente: nao demonstra que Render sanitiza esse header.
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.setenv("ATLAS_TRUST_CF_CONNECTING_IP", "true")
    with local_uvicorn("*") as client:
        for attempt in range(60):
            r = client.get(
                "/api/v1/normalize",
                params=PARAMS,
                headers={
                    "X-Forwarded-For": f"203.0.113.{attempt + 1}",
                    "CF-Connecting-IP": "198.51.100.42",
                },
            )
            assert r.status_code == 200

        blocked = client.get(
            "/api/v1/normalize",
            params=PARAMS,
            headers={"X-Forwarded-For": "203.0.113.251", "CF-Connecting-IP": "198.51.100.42"},
        )
        assert blocked.status_code == 429

        other = client.get(
            "/api/v1/normalize",
            params=PARAMS,
            headers={"X-Forwarded-For": "203.0.113.251", "CF-Connecting-IP": "198.51.100.43"},
        )
        assert other.status_code == 200


def test_http_render_trusted_cf_rejects_invalid_headers_without_consuming_quota(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Se houver garantia explicita sobre o proxy Cloudflare, header malformado
    # nao deve ocupar um bucket compartilhado e prejudicar outras origens.
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.setenv("ATLAS_TRUST_CF_CONNECTING_IP", "true")
    with local_uvicorn("*") as client:
        for i in range(80):
            invalid = client.get(
                "/api/v1/normalize",
                params=PARAMS,
                headers={
                    "X-Forwarded-For": f"203.0.113.{i + 1}",
                    "CF-Connecting-IP": "198.51.100.1, 198.51.100.2",
                },
            )
            assert invalid.status_code == 400
            assert invalid.headers.get("retry-after") is None

        missing = client.get("/api/v1/normalize", params=PARAMS)
        assert missing.status_code == 400

        invalid_single = client.get(
            "/api/v1/normalize",
            params=PARAMS,
            headers={"CF-Connecting-IP": "not-an-ip"},
        )
        assert invalid_single.status_code == 400

        valid = client.get(
            "/api/v1/normalize",
            params=PARAMS,
            headers={"CF-Connecting-IP": "2001:db8::1"},
        )
        assert valid.status_code == 200
