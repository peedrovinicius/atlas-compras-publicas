"""Proteção contra uso acidental do smoke em serviços públicos de produção."""

from pathlib import Path
from runpy import run_path

import pytest

# Os testes rodam com pythonpath=src no pytest; carregar o CLI por caminho
# sem depender da raiz do repositorio constar no sys.path.
_smoke = run_path(str(Path(__file__).resolve().parents[1] / "scripts/smoke_proxy_staging.py"))
cf_rejection_observed = _smoke["cf_rejection_observed"]
quota_a_passed = _smoke["quota_a_passed"]
validate_target = _smoke["validate_target"]


@pytest.mark.parametrize(
    "target",
    [
        "https://atlas-compras-publicas-analytics.onrender.com",
        "https://atlas-compras-publicas-web.onrender.com",
        "https://example.com",
        "http://atlas-compras-publicas-proxy-staging.onrender.com",
        "https://atlas-compras-publicas-proxy-staging.onrender.com:8443",
        "https://person@atlas-compras-publicas-proxy-staging.onrender.com",
        "https://atlas-compras-publicas-proxy-staging.onrender.com/x",
        "https://atlas-compras-publicas-proxy-staging.onrender.com/?token=abc",
        "https://atlas-compras-publicas-proxy-staging.onrender.com.evil.example",
        "https://127.0.0.1",
    ],
)
def test_refuse_unsafe_target(target: str) -> None:
    with pytest.raises(ValueError, match="staging"):
        validate_target(target)


def test_allow_only_atlas_dedicated_staging() -> None:
    assert (
        validate_target("https://atlas-compras-publicas-proxy-staging.onrender.com/")
        == "https://atlas-compras-publicas-proxy-staging.onrender.com"
    )


def test_quota_is_exact_and_bounded() -> None:
    assert quota_a_passed([200] * 60 + [429])
    assert not quota_a_passed([200] * 61)
    assert not quota_a_passed([200] * 59 + [429])
    assert not quota_a_passed([429])


def test_cf_response_rejection_is_not_equivalent_to_edge_proof() -> None:
    assert cf_rejection_observed(403)
    assert cf_rejection_observed(400)
    assert not cf_rejection_observed(200)
    assert not cf_rejection_observed(502)
