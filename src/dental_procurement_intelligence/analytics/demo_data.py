from dataclasses import dataclass
from pathlib import Path

from dental_procurement_intelligence.analytics.anomalies import build_price_signals
from dental_procurement_intelligence.analytics.awards import build_award_dataset
from dental_procurement_intelligence.analytics.lakehouse import build_analytics_dataset
from dental_procurement_intelligence.analytics.quality import build_quality_views
from dental_procurement_intelligence.ingestion import (
    EvidenceStore,
    capture_contract,
    discover_contract_bundles,
)
from dental_procurement_intelligence.pncp import PNCPClient

DEMO_CNPJ = "15126437000305"
DEMO_YEAR = 2026
DEMO_SEQUENCE = 212


@dataclass(frozen=True, slots=True)
class DemoDataBuildResult:
    procurement_key: str
    item_count: int
    result_count: int
    silver_item_count: int
    silver_award_count: int
    eligible_signal_rows: int
    signal_count: int
    comparison_group_count: int
    raw_root: str
    items_parquet_path: str
    awards_parquet_path: str
    database_path: str


def build_demo_data(
    client: PNCPClient,
    output_root: str | Path = "data/demo",
    *,
    cnpj: str = DEMO_CNPJ,
    year: int = DEMO_YEAR,
    sequence: int = DEMO_SEQUENCE,
) -> DemoDataBuildResult:
    """Reconstrói a amostra analítica pública a partir do PNCP."""

    root = Path(output_root)
    raw_root = root / "raw"
    items_parquet = root / "silver" / "items.parquet"
    awards_parquet = root / "silver" / "awards.parquet"
    database = root / "atlas-demo.duckdb"

    capture = capture_contract(
        client,
        EvidenceStore(raw_root),
        cnpj=cnpj,
        year=year,
        sequence=sequence,
    )

    items = build_analytics_dataset(
        [
            evidence.object_path
            for evidence in capture.all_item_evidence
        ],
        items_parquet,
        database,
    )

    manifests = discover_contract_bundles(raw_root / "contracts")
    awards = build_award_dataset(
        manifests,
        awards_parquet,
        database,
    )

    signals = build_price_signals(database)
    build_quality_views(database)

    return DemoDataBuildResult(
        procurement_key=capture.procurement_key,
        item_count=capture.item_count,
        result_count=capture.result_count,
        silver_item_count=items.row_count,
        silver_award_count=awards.row_count,
        eligible_signal_rows=signals.eligible_row_count,
        signal_count=signals.signal_count,
        comparison_group_count=signals.comparison_group_count,
        raw_root=raw_root.as_posix(),
        items_parquet_path=items_parquet.as_posix(),
        awards_parquet_path=awards_parquet.as_posix(),
        database_path=database.as_posix(),
    )
