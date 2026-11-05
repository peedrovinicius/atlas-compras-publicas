"""Proveniência da amostra, persistida junto às estatísticas no DuckDB."""

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import duckdb

SourceType = Literal["pncp_sample", "offline_synthetic"]
_KEY = re.compile(r"pncp:\d{14}:\d{4}:\d+\Z")
_SYNTHETIC = "pncp:00000000000000:2026:1"
_NOTICES = {
    "pncp_sample": "Amostra obtida do PNCP; não representa todas as contratações.",
    "offline_synthetic": (
        "Amostra 100% sintética: fornecedores e preços fictícios; "
        "não representa compras públicas homologadas."
    ),
    "unknown": "Origem não verificada. Não interprete valores como preços reais.",
}


def _unknown() -> dict[str, Any]:
    return {
        "source_type": "unknown",
        "captured_at": None,
        "procurement_keys": [],
        "procurement_count": None,
        "result_count": None,
        "observation_count": None,
        "notice": _NOTICES["unknown"],
    }


def _valid_keys(source: str, keys: list[str]) -> bool:
    if not keys or len(keys) > 1000:
        return False
    if any(not isinstance(k, str) or not _KEY.fullmatch(k) for k in keys):
        return False
    if len(set(keys)) != len(keys):
        return False
    if source == "offline_synthetic":
        return keys == [_SYNTHETIC]
    return source == "pncp_sample" and _SYNTHETIC not in keys


def write_provenance(
    database_path: str | Path,
    *,
    source_type: SourceType,
    procurement_keys: tuple[str, ...],
    result_count: int,
    observation_count: int,
) -> None:
    """Após o pipeline, grava origem e contagens verificáveis no próprio DB."""
    keys = list(procurement_keys)
    if (
        source_type not in ("pncp_sample", "offline_synthetic")
        or not _valid_keys(source_type, keys)
        or result_count < 1
        or observation_count < 1
    ):
        raise ValueError("Metadados de proveniência inválidos.")

    with duckdb.connect(str(database_path)) as connection:
        actual = connection.execute("SELECT COUNT(*) FROM silver_awards").fetchone()[0]
        if actual != observation_count:
            raise ValueError("Contagem de observações diverge do banco.")
        connection.execute("BEGIN TRANSACTION")
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS atlas_demo_provenance (
                    schema_version INTEGER NOT NULL,
                    source_type VARCHAR NOT NULL,
                    captured_at VARCHAR NOT NULL,
                    procurement_keys VARCHAR NOT NULL,
                    procurement_count INTEGER NOT NULL,
                    result_count INTEGER NOT NULL,
                    observation_count INTEGER NOT NULL
                )
                """
            )
            connection.execute("DELETE FROM atlas_demo_provenance")
            connection.execute(
                "INSERT INTO atlas_demo_provenance VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    1, source_type, datetime.now(UTC).isoformat(),
                    json.dumps(keys), len(keys), result_count, observation_count,
                ],
            )
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise


def read_provenance(database_path: str | Path) -> dict[str, Any]:
    """Fail-closed: bases antigas, ausentes ou incoerentes nunca parecem reais."""
    path = Path(database_path)
    if not path.is_file():
        return _unknown()
    try:
        with duckdb.connect(str(path), read_only=True) as connection:
            rows = connection.execute(
                """
                SELECT schema_version, source_type, captured_at, procurement_keys,
                       procurement_count, result_count, observation_count
                FROM atlas_demo_provenance
                """
            ).fetchall()
            if len(rows) != 1:
                return _unknown()
            ver, source, captured, keys_json, count, results, obs = rows[0]
            keys = json.loads(keys_json)
            actual = connection.execute("SELECT COUNT(*) FROM silver_awards").fetchone()[0]
        instant = datetime.fromisoformat(captured)
    except (duckdb.Error, ValueError, TypeError, OSError):
        return _unknown()

    if (
        ver != 1
        or source not in ("pncp_sample", "offline_synthetic")
        or not isinstance(keys, list)
        or not _valid_keys(source, keys)
        or count != len(keys)
        or not isinstance(results, int)
        or results < 1
        or not isinstance(obs, int)
        or obs < 1
        or actual != obs
        or instant.tzinfo is None
    ):
        return _unknown()
    return {
        "source_type": source,
        "captured_at": captured,
        "procurement_keys": keys,
        "procurement_count": count,
        "result_count": results,
        "observation_count": obs,
        "notice": _NOTICES[source],
    }
