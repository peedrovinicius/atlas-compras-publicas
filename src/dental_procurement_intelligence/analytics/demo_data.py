import json
from dataclasses import dataclass
from pathlib import Path

import httpx

from dental_procurement_intelligence.analytics.anomalies import build_price_signals
from dental_procurement_intelligence.analytics.awards import (
    build_award_dataset,
    build_awards,
)
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


_OFFLINE_DEMO_PRICES = (
    ("Fornecedor demonstrativo A", "00000000000001", "2026-01-15", "78.90"),
    ("Fornecedor demonstrativo B", "00000000000002", "2026-01-28", "81.50"),
    ("Fornecedor demonstrativo C", "00000000000003", "2026-02-12", "84.00"),
    ("Fornecedor demonstrativo D", "00000000000004", "2026-02-27", "86.40"),
    ("Fornecedor demonstrativo E", "00000000000005", "2026-03-10", "88.90"),
    ("Fornecedor demonstrativo F", "00000000000006", "2026-03-24", "91.20"),
    ("Fornecedor demonstrativo G", "00000000000007", "2026-04-08", "93.80"),
    ("Fornecedor demonstrativo H", "00000000000008", "2026-04-22", "96.10"),
    ("Fornecedor demonstrativo I", "00000000000009", "2026-05-07", "98.70"),
    ("Fornecedor demonstrativo J", "00000000000010", "2026-05-21", "101.30"),
    ("Fornecedor demonstrativo K", "00000000000011", "2026-06-05", "104.00"),
    ("Fornecedor demonstrativo L", "00000000000012", "2026-06-19", "107.50"),
)


def _write_demo_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _build_offline_demo_data(root: Path) -> DemoDataBuildResult:
    """Gera uma amostra demonstrativa local sem depender de rede externa."""

    seed_root = root / "offline-seed"
    contract_path = seed_root / "contract.json"
    items_path = seed_root / "items.json"
    results_path = seed_root / "results.json"
    items_parquet = root / "silver" / "items.parquet"
    awards_parquet = root / "silver" / "awards.parquet"
    database = root / "atlas-demo.duckdb"
    procurement_key = "pncp:00000000000000:2026:1"

    contract = {
        "numeroControlePNCP": "00000000000000-1-000001/2026",
        "anoCompra": 2026,
        "sequencialCompra": 1,
        "modalidadeNome": "Pregão - Eletrônico",
        "situacaoCompraNome": "Amostra demonstrativa offline",
        "dataPublicacaoPncp": "2026-01-10",
        "valorTotalEstimado": "12000.00",
        "valorTotalHomologado": "11000.00",
        "orgaoEntidade": {
            "cnpj": "00000000000000",
            "razaoSocial": "Amostra demonstrativa Atlas e Preços",
            "poderId": "E",
            "esferaId": "M",
        },
        "unidadeOrgao": {
            "codigoUnidade": "DEMO-CE",
            "nomeUnidade": "Unidade demonstrativa",
            "municipioId": 2304400,
            "municipioNome": "Fortaleza",
            "ufSigla": "CE",
            "ufNome": "Ceará",
        },
    }
    items_payload = [
        {
            "numeroItem": 1,
            "descricao": "RESINA COMPOSTA NANOHÍBRIDA A2 SERINGA 4 G",
            "quantidade": "120",
            "unidadeMedida": "UNIDADE",
            "valorUnitarioEstimado": "100.00",
            "valorTotal": "12000.00",
            "temResultado": True,
        }
    ]
    results_payload = [
        {
            "numeroItem": 1,
            "sequencialResultado": index,
            "quantidadeHomologada": "10",
            "valorUnitarioHomologado": price,
            "valorTotalHomologado": f"{float(price) * 10:.2f}",
            "percentualDesconto": None,
            "nomeRazaoSocialFornecedor": supplier,
            "niFornecedor": document,
            "marca": "Marca demonstrativa",
            "dataResultado": result_date,
            "situacaoCompraItemResultadoId": 1,
            "situacaoCompraItemResultadoNome": "Homologado",
        }
        for index, (supplier, document, result_date, price)
        in enumerate(_OFFLINE_DEMO_PRICES, start=1)
    ]

    _write_demo_json(contract_path, contract)
    _write_demo_json(items_path, items_payload)
    _write_demo_json(results_path, results_payload)

    items = build_analytics_dataset(
        [items_path],
        items_parquet,
        database,
        procurement_key_by_path={items_path.as_posix(): procurement_key},
    )
    awards = build_awards(
        items_path,
        [results_path],
        awards_parquet,
        database,
        contract_raw_path=contract_path,
    )
    signals = build_price_signals(database)
    build_quality_views(database)

    return DemoDataBuildResult(
        procurement_count=1,
        procurement_keys=(procurement_key,),
        item_count=1,
        result_count=len(results_payload),
        silver_item_count=items.row_count,
        silver_award_count=awards.row_count,
        eligible_signal_rows=signals.eligible_row_count,
        signal_count=signals.signal_count,
        comparison_group_count=signals.comparison_group_count,
        raw_root=seed_root.as_posix(),
        items_parquet_path=items_parquet.as_posix(),
        awards_parquet_path=awards_parquet.as_posix(),
        database_path=database.as_posix(),
    )


def build_demo_data(
    client: PNCPClient,
    output_root: str | Path = "data/demo",
    *,
    cnpj: str | None = None,
    year: int | None = None,
    sequence: int | None = None,
    procurements: tuple[DemoProcurement, ...] | None = None,
    max_result_requests_per_procurement: int | None = None,
    allow_offline_seed: bool = False,
) -> DemoDataBuildResult:
    """Reconstrói a amostra analítica pública com fallback determinístico da demo padrão."""

    if procurements is not None and any(
        value is not None for value in (cnpj, year, sequence)
    ):
        raise ValueError(
            "Use procurements ou cnpj/year/sequence, não os dois formatos."
        )

    explicit = (cnpj, year, sequence)
    uses_default_procurements = (
        procurements is None and all(value is None for value in explicit)
    )

    if procurements is None:
        if uses_default_procurements:
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
        if allow_offline_seed or uses_default_procurements:
            return _build_offline_demo_data(root)
        raise RuntimeError(
            "Nenhuma contratação da amostra pôde ser capturada no PNCP."
        )
    if sum(capture.result_count for capture in captures) == 0:
        if allow_offline_seed or uses_default_procurements:
            return _build_offline_demo_data(root)
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
