from pathlib import Path
from types import SimpleNamespace

import httpx

from dental_procurement_intelligence.analytics import demo_data
from dental_procurement_intelligence.cli import (
    _demo_result_request_limit,
    build_parser,
)


def test_demo_data_cli_defaults_are_explicit() -> None:
    args = build_parser().parse_args(["build-demo-data"])

    assert args.cnpj is None
    assert args.year is None
    assert args.sequence is None
    assert args.output_root == "data/demo"
    assert args.max_result_requests_per_procurement is None
    assert args.offline_fallback is False


def test_build_demo_data_orchestrates_existing_pipeline(
    tmp_path: Path,
    monkeypatch,
) -> None:
    calls: list[tuple[str, object]] = []

    capture = SimpleNamespace(
        procurement_key="pncp:01612541000133:2026:47",
        item_count=3,
        result_count=2,
        all_item_evidence=(
            SimpleNamespace(object_path="items-page-1.json"),
            SimpleNamespace(object_path="items-page-2.json"),
        ),
    )

    monkeypatch.setattr(
        demo_data,
        "capture_contract",
        lambda *args, **kwargs: capture,
    )
    monkeypatch.setattr(
        demo_data,
        "build_analytics_dataset",
        lambda raw, parquet, database, **kwargs: (
            calls.append(("items", (raw, parquet, database, kwargs)))
            or SimpleNamespace(row_count=3)
        ),
    )
    monkeypatch.setattr(
        demo_data,
        "discover_contract_bundles",
        lambda root: [Path(root) / "47.json"],
    )
    monkeypatch.setattr(
        demo_data,
        "build_award_dataset",
        lambda manifests, parquet, database: (
            calls.append(("awards", (manifests, parquet, database)))
            or SimpleNamespace(row_count=2)
        ),
    )
    monkeypatch.setattr(
        demo_data,
        "build_price_signals",
        lambda database: (
            calls.append(("signals", database))
            or SimpleNamespace(
                eligible_row_count=2,
                signal_count=1,
                comparison_group_count=1,
            )
        ),
    )
    monkeypatch.setattr(
        demo_data,
        "build_quality_views",
        lambda database: calls.append(("quality", database)),
    )

    procurement = demo_data.DemoProcurement(
        cnpj=demo_data.DEMO_CNPJ,
        year=demo_data.DEMO_YEAR,
        sequence=demo_data.DEMO_SEQUENCE,
        label="test",
    )
    result = demo_data.build_demo_data(
        object(),
        tmp_path / "demo",
        procurements=(procurement,),
    )

    assert result.procurement_count == 1
    assert result.procurement_keys == (capture.procurement_key,)
    assert result.item_count == 3
    assert result.result_count == 2
    assert result.silver_item_count == 3
    assert result.silver_award_count == 2
    assert result.eligible_signal_rows == 2
    assert result.signal_count == 1
    assert result.comparison_group_count == 1
    assert result.database_path.endswith("atlas-demo.duckdb")
    assert [name for name, _ in calls] == [
        "items",
        "awards",
        "signals",
        "quality",
    ]



def test_build_demo_data_skips_failed_procurement(
    tmp_path: Path,
    monkeypatch,
) -> None:
    calls = 0
    capture = SimpleNamespace(
        procurement_key="pncp:22222222222222:2026:2",
        item_count=2,
        result_count=1,
        all_item_evidence=(
            SimpleNamespace(object_path="items-page-1.json"),
        ),
    )

    def capture_stub(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            request = httpx.Request("GET", "https://example.test")
            raise httpx.ReadTimeout("temporary", request=request)
        return capture

    monkeypatch.setattr(demo_data, "capture_contract", capture_stub)
    monkeypatch.setattr(
        demo_data,
        "build_analytics_dataset",
        lambda *args, **kwargs: SimpleNamespace(row_count=2),
    )
    monkeypatch.setattr(
        demo_data,
        "discover_contract_bundles",
        lambda root: [Path(root) / "2.json"],
    )
    monkeypatch.setattr(
        demo_data,
        "build_award_dataset",
        lambda *args, **kwargs: SimpleNamespace(row_count=1),
    )
    monkeypatch.setattr(
        demo_data,
        "build_price_signals",
        lambda database: SimpleNamespace(
            eligible_row_count=1,
            signal_count=0,
            comparison_group_count=1,
        ),
    )
    monkeypatch.setattr(demo_data, "build_quality_views", lambda database: None)

    procurements = (
        demo_data.DemoProcurement("11111111111111", 2026, 1, "falha"),
        demo_data.DemoProcurement("22222222222222", 2026, 2, "válida"),
    )

    result = demo_data.build_demo_data(
        object(),
        tmp_path / "demo",
        procurements=procurements,
    )

    assert result.procurement_count == 1
    assert result.procurement_keys == (capture.procurement_key,)
    assert result.silver_award_count == 1



def test_demo_result_request_limit_uses_environment(monkeypatch) -> None:
    monkeypatch.setenv("ATLAS_DEMO_MAX_RESULT_REQUESTS", "8")
    assert _demo_result_request_limit(None) == 8


def test_demo_result_request_limit_argument_wins_over_environment(
    monkeypatch,
) -> None:
    monkeypatch.setenv("ATLAS_DEMO_MAX_RESULT_REQUESTS", "8")
    assert _demo_result_request_limit(3) == 3



def test_build_demo_data_uses_offline_seed_when_pncp_is_unavailable(
    tmp_path: Path,
    monkeypatch,
) -> None:
    request = httpx.Request("GET", "https://pncp.example.test")

    def unavailable(*args, **kwargs):
        raise httpx.ReadTimeout("temporary", request=request)

    monkeypatch.setattr(demo_data, "capture_contract", unavailable)

    procurement = demo_data.DemoProcurement(
        cnpj=demo_data.DEMO_CNPJ,
        year=demo_data.DEMO_YEAR,
        sequence=demo_data.DEMO_SEQUENCE,
        label="indisponível",
    )
    result = demo_data.build_demo_data(
        object(),
        tmp_path / "demo",
        procurements=(procurement,),
        allow_offline_seed=True,
    )

    assert result.procurement_count == 1
    assert result.result_count == 12
    assert result.silver_item_count == 1
    assert result.silver_award_count == 12
    assert Path(result.database_path).is_file()
