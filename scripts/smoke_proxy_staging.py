"""Smoke controlado do rate limiting, restrito a um staging do Atlas no Render.

Nenhuma requisição é executada sem --execute e --confirm-staging.
Use fases A/B em redes externas DIFERENTES e dentro da mesma janela de 60 s.
"""

import argparse
import re
import sys
from urllib.parse import urlsplit

import httpx

_HOST_PATTERN = re.compile(
    r"atlas-compras-publicas-proxy-staging(?:-[a-z0-9]+)*\.onrender\.com"
)
_DESCRIPTION = "RESINA COMPOSTA A2 SERINGA 4G"
_QUOTA = 60


def validate_target(raw: str) -> str:
    """Rejeita produção, outros hosts, portas, credenciais, paths e redirecionamentos."""
    parsed = urlsplit(raw)
    if (
        parsed.scheme != "https"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.hostname is None
        or _HOST_PATTERN.fullmatch(parsed.hostname) is None
        or parsed.netloc != parsed.hostname
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Informe somente a raiz HTTPS do staging dedicado do Atlas.")
    return f"https://{parsed.hostname}"


def quota_a_passed(statuses: list[int]) -> bool:
    """A origem A deve ter 60 sucessos e, em seguida, 429 na mesma janela."""
    return len(statuses) == _QUOTA + 1 and (
        statuses[:_QUOTA] == [200] * _QUOTA and statuses[-1] == 429
    )


def cf_rejection_observed(status: int) -> bool:
    """Rejeição HTTP observada não prova, sozinha, que ocorreu no Cloudflare."""
    return 400 <= status <= 499


def check(client: httpx.Client, path: str, *, headers: dict[str, str] | None = None) -> int:
    response = client.get(path, headers=headers)
    return response.status_code


def run(target: str, mode: str) -> bool:
    with httpx.Client(
        base_url=target,
        timeout=8.0,
        follow_redirects=False,
        trust_env=False,
    ) as client:
        for path in ("/health", "/ready"):
            status = check(client, path)
            print(f"Pré-condição {path}: HTTP {status}")
            if status != 200:
                return False

        route = "/api/v1/normalize"
        params = {"description": _DESCRIPTION}
        if mode == "quota-a":
            statuses = []
            for attempt in range(_QUOTA + 1):
                # Somente XFF é variado; CF-Connecting-IP é preenchido pela borda.
                headers = {"X-Forwarded-For": f"198.51.100.{attempt + 1}"}
                response = client.get(route, params=params, headers=headers)
                statuses.append(response.status_code)
                if response.status_code not in (200, 429):
                    break
            print(
                f"Origem A: HTTP 200={statuses.count(200)}, "
                f"HTTP 429={statuses.count(429)}, total={len(statuses)}"
            )
            return quota_a_passed(statuses)

        if mode == "quota-b":
            # Executar imediatamente após quota-a, em OUTRA rede com IP público distinto.
            response = client.get(route, params=params)
            print(f"Origem B: HTTP {response.status_code}")
            return response.status_code == 200

        if mode == "cf-rejection":
            # Etapa separada: o Cloudflare deve barrar CF-Connecting-IP do solicitante.
            response = client.get(
                route,
                params=params,
                headers={"CF-Connecting-IP": "198.51.100.42"},
            )
            print(f"Header CF fornecido manualmente: HTTP {response.status_code}")
            print("Inspecione separadamente se a rejeição veio da borda Cloudflare.")
            return cf_rejection_observed(response.status_code)

        response = client.get(route, params=params)
        print(f"Normalização básica: HTTP {response.status_code}")
        return response.status_code == 200


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="Raiz HTTPS do staging dedicado")
    parser.add_argument(
        "--mode",
        choices=("basic", "quota-a", "quota-b", "cf-rejection"),
        default="basic",
    )
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-staging", action="store_true")
    args = parser.parse_args()

    try:
        target = validate_target(args.target)
    except ValueError as exc:
        parser.error(str(exc))

    if not (args.execute and args.confirm_staging):
        print("Modo seguro: nenhuma chamada de rede. Exige --execute --confirm-staging.")
        return 0

    try:
        success = run(target, args.mode)
    except httpx.HTTPError as exc:
        print(f"Erro HTTP/transporte no staging: {type(exc).__name__}", file=sys.stderr)
        return 1

    print(f"Resultado: {'APROVADO' if success else 'REPROVADO'} ({args.mode})")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
