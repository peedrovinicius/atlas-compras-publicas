"""Identidade do cliente usada na cota de normalizacoes da API.

Nao usar X-Forwarded-For como chave em Render, pois o Uvicorn pode
redefinir request.client.host com FORWARDED_ALLOW_IPS='*'.
"""

from ipaddress import ip_address
from typing import Any


def resolve_normalization_client_identity(
    request: Any,
    *,
    render_runtime: bool,
    trust_cloudflare: bool,
) -> str | None:
    if render_runtime:
        if trust_cloudflare:
            values = request.headers.getlist("cf-connecting-ip")
            if len(values) == 1:
                raw = values[0].strip()
                # Um header de IP nao deve conter uma cadeia, porta nem escopo
                # IPv6 (%interface). ip_address aceita identificadores de
                # escopo, que criariam varias cotas para o mesmo IP.
                if "%" not in raw:
                    try:
                        address = ip_address(raw)
                    except ValueError:
                        pass
                    else:
                        if address.version == 6 and address.ipv4_mapped is not None:
                            address = address.ipv4_mapped
                        return f"cloudflare:{address}"
            # Quando a confianca foi habilitada, um header CF invalido
            # indica que a identidade nao foi autenticada pelo ingresso.
            # A rota rejeita a requisicao antes do rate limiter.
            return None

        # Sem validacao da borda, nao confiar no cliente ASGI no Render.
        return "render:unverified-shared"

    # Em desenvolvimento ou em servidores sem a topologia do Render,
    # preservar o escopo ASGI controlado pelo servidor local.
    host = request.client.host if request.client is not None else "unknown"
    return f"asgi:{host}"
