from dataclasses import dataclass
from pathlib import Path

import httpx

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


@dataclass(frozen=True, slots=True)
class DemoProcurement:
    cnpj: str
    year: int
    sequence: int
    label: str


DEMO_PROCUREMENTS = (
    DemoProcurement(
        cnpj="15126437000305",
        year=2026,
        sequence=212,
        label="CHC/UFPR - insumos odontológicos",
    ),
    DemoProcurement(
        cnpj="18277947000100",
        year=2026,
        sequence=259,
        label="Guarda-Mor/MG - insumos odontológicos",
    ),
    DemoProcurement(
        cnpj="39485412000102",
        year=2026,
        sequence=4,
        label="Queimados/RJ - insumos odontológicos",
    ),
)

# Compatibilidade com integrações e scripts que ainda importam as constantes antigas.
DEMO_CNPJ = DEMO_PROCUREMENTS[0].cnpj
DEMO_YEAR = DEMO_PROCUREMENTS[0].year
DEMO_SEQUENCE = DEMO_PROCUREMENTS[0].sequence


@dataclass(frozen=True, slots=True)
class DemoDataBuildResult:
    procurement_count: int
    procurement_keys: tuple[str, ...]
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
    cnpj: str | None = None,
    year: int | None = None,
    sequence: int | None = None,
    procurements: tuple[DemoProcurement, ...] | None = None,
    max_result_requests_per_procurement: int | None = None,
) -> DemoDataBuildResult:
    """Reconstrói a amostra analítica pública a partir do PNCP."""

    if procurements is not None and any(
        value is not None for value in (cnpj, year, sequence)
    ):
        raise ValueError(
            "Use procurements ou cnpj/year/sequence, não os dois formatos."
        )

    if procurements is None:
        explicit = (cnpj, year, sequence)
        if all(value is None for value in explicit):
            procurements = DEMO_PROCUREMENTS
        elif any(value is None for value in explicit):
            raise ValueError(
                "cnpj, year e sequence precisam ser informados em conjunto."
            )
        else:
            procurements = (
                DemoProcurement(
                    cnpj=str(cnpj),
                    year=int(year),
                    sequence=int(sequence),
                    label="contratação informada pela CLI",
                ),
            )

    if not procurements:
        raise ValueError("Informe pelo menos uma contratação para a amostra.")

    root = Path(output_root)
    raw_root = root / "raw"
    items_parquet = root / "silver" / "items.parquet"
    awards_parquet = root / "silver" / "awards.parquet"
    database = root / "atlas-demo.duckdb"

    store = EvidenceStore(raw_root)
    captures = []
    for procurement in procurements:
        try:
            capture = capture_contract(
                client,
                store,
                cnpj=procurement.cnpj,
                year=procurement.year,
                sequence=procurement.sequence,
                skip_result_transport_errors=True,
                max_result_requests=max_result_requests_per_procurement,
            )
        except httpx.HTTPError:
            continue
        captures.append(capture)

    if not captures:
        raise RuntimeError(
            "Nenhuma contratação da amostra pôde ser capturada no PNCP."
        )
    if sum(capture.result_count for capture in captures) == 0:
        raise RuntimeError(
            "A amostra foi capturada, mas não retornou resultados homologados."
        )

    item_paths: list[str] = []
    procurement_key_by_path: dict[str, str] = {}

    for capture in captures:
        for evidence in capture.all_item_evidence:
            path = Path(evidence.object_path).as_posix()
            item_paths.append(path)
            procurement_key_by_path[path] = capture.procurement_key

    items = build_analytics_dataset(
        item_paths,
        items_parquet,
        database,
        procurement_key_by_path=procurement_key_by_path,
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
        procurement_count=len(captures),
        procurement_keys=tuple(
            capture.procurement_key for capture in captures
        ),
        item_count=sum(capture.item_count for capture in captures),
        result_count=sum(capture.result_count for capture in captures),
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
