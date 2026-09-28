from pathlib import Path
from types import SimpleNamespace

from dental_procurement_intelligence.analytics import demo_data
from dental_procurement_intelligence.cli import build_parser


def test_demo_data_cli_defaults_are_explicit() -> None:
    args = build_parser().parse_args(["build-demo-data"])

    assert args.cnpj is None
    assert args.year is None
    assert args.sequence is None
    assert args.output_root == "data/demo"


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
