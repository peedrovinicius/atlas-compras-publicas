import argparse
import json
from collections.abc import Sequence
from dataclasses import asdict
from typing import Any

from dental_procurement_intelligence.analytics import (
    DEMO_CNPJ,
    DEMO_SEQUENCE,
    DEMO_YEAR,
    DuckDBWarehouse,
    anomaly_summary,
    award_summary,
    build_analytics,
    build_award_dataset,
    build_awards,
    build_demo_data,
    build_price_signals,
    quality_by_category,
    quality_summary,
    unrecognized_items,
)
from dental_procurement_intelligence.evaluation import (
    evaluate_dataset,
    evaluate_technical_attributes,
    evaluation_errors,
    technical_attribute_errors,
)
from dental_procurement_intelligence.ingestion import (
    EvidenceStore,
    capture_contract,
    discover_contract_bundles,
)
from dental_procurement_intelligence.pncp import PNCPClient


def _serialize(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dpi",
        description="Atlas de Compras Públicas, inteligência de dados auditável",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    contract = subparsers.add_parser(
        "contract",
        help="Consulta metadados de uma contratação no PNCP",
    )
    contract.add_argument("--cnpj", required=True)
    contract.add_argument("--year", required=True, type=int)
    contract.add_argument("--sequence", required=True, type=int)

    items = subparsers.add_parser("items", help="Consulta itens de uma contratação")
    items.add_argument("--cnpj", required=True)
    items.add_argument("--year", required=True, type=int)
    items.add_argument("--sequence", required=True, type=int)

    capture = subparsers.add_parser(
        "capture-items",
        help="Persiste itens brutos como evidência imutável",
    )
    capture.add_argument("--cnpj", required=True)
    capture.add_argument("--year", required=True, type=int)
    capture.add_argument("--sequence", required=True, type=int)
    capture.add_argument("--output", default="data/raw")

    capture_all = subparsers.add_parser(
        "capture-contract",
        help="Captura contratação, itens e resultados de todos os itens",
    )
    capture_all.add_argument("--cnpj", required=True)
    capture_all.add_argument("--year", required=True, type=int)
    capture_all.add_argument("--sequence", required=True, type=int)
    capture_all.add_argument("--output", default="data/raw")

    results = subparsers.add_parser(
        "results",
        help="Consulta resultados homologados de um item",
    )
    results.add_argument("--cnpj", required=True)
    results.add_argument("--year", required=True, type=int)
    results.add_argument("--sequence", required=True, type=int)
    results.add_argument("--item", required=True, type=int)

    capture_results = subparsers.add_parser(
        "capture-results",
        help="Persiste resultados homologados brutos com SHA-256",
    )
    capture_results.add_argument("--cnpj", required=True)
    capture_results.add_argument("--year", required=True, type=int)
    capture_results.add_argument("--sequence", required=True, type=int)
    capture_results.add_argument("--item", required=True, type=int)
    capture_results.add_argument("--output", default="data/raw")

    analytics = subparsers.add_parser(
        "build-analytics",
        help="Transforma itens brutos em Parquet e DuckDB",
    )
    analytics.add_argument("--raw", required=True)
    analytics.add_argument("--parquet", default="data/silver/items.parquet")
    analytics.add_argument("--database", default="data/analytics.duckdb")

    awards = subparsers.add_parser(
        "build-awards",
        help="Cruza contratação, itens e resultados homologados",
    )
    awards.add_argument("--contract-raw")
    awards.add_argument("--items-raw", required=True)
    awards.add_argument("--results-raw", required=True, nargs="+")
    awards.add_argument("--parquet", default="data/silver/awards.parquet")
    awards.add_argument("--database", default="data/analytics.duckdb")

    award_dataset = subparsers.add_parser(
        "build-award-dataset",
        help="Reconstrói homologações consolidadas de múltiplas contratações",
    )
    award_dataset.add_argument(
        "--bundles-root",
        default="data/raw/contracts",
        help="Diretório com manifestos de contratação",
    )
    award_dataset.add_argument(
        "--parquet",
        default="data/silver/awards.parquet",
    )
    award_dataset.add_argument(
        "--database",
        default="data/analytics.duckdb",
    )

    demo_data = subparsers.add_parser(
        "build-demo-data",
        help="Reconstrói a amostra analítica reproduzível usada na demonstração",
    )
    demo_data.add_argument("--cnpj")
    demo_data.add_argument("--year", type=int)
    demo_data.add_argument("--sequence", type=int)
    demo_data.add_argument("--output-root", default="data/demo")

    signals = subparsers.add_parser(
        "detect-anomalies",
        help="Gera sinais estatísticos com contexto temporal e geográfico",
    )
    signals.add_argument("--database", default="data/analytics.duckdb")
    signals.add_argument("--minimum-group-size", type=int, default=5)
    signals.add_argument("--modified-z-threshold", type=float, default=3.5)
    signals.add_argument("--iqr-multiplier", type=float, default=1.5)

    summary = subparsers.add_parser(
        "analytics-summary",
        help="Exibe o resumo de preços estimados por categoria",
    )
    summary.add_argument("--database", default="data/analytics.duckdb")

    awards_summary = subparsers.add_parser(
        "awards-summary",
        help="Exibe economia por categoria, região e ano",
    )
    awards_summary.add_argument("--database", default="data/analytics.duckdb")

    anomalies_summary = subparsers.add_parser(
        "anomalies-summary",
        help="Exibe resumo dos sinais por escopo de comparação",
    )
    anomalies_summary.add_argument("--database", default="data/analytics.duckdb")

    quality = subparsers.add_parser(
        "normalization-quality",
        help="Exibe métricas de cobertura e qualidade do normalizador",
    )
    quality.add_argument("--database", default="data/analytics.duckdb")
    quality.add_argument("--by-category", action="store_true")

    unknown = subparsers.add_parser(
        "unrecognized-items",
        help="Lista itens cuja categoria ainda não foi reconhecida",
    )
    unknown.add_argument("--database", default="data/analytics.duckdb")
    unknown.add_argument("--limit", type=int, default=50)

    dashboard = subparsers.add_parser(
        "build-dashboard",
        help="Gera dashboard HTML a partir do DuckDB analítico",
    )
    dashboard.add_argument("--database", default="data/analytics.duckdb")
    dashboard.add_argument("--output", default="docs/dashboard.html")

    api = subparsers.add_parser(
        "serve-api",
        help="Inicia a API HTTP analítica do Atlas",
    )
    api.add_argument("--database", default="data/analytics.duckdb")
    api.add_argument("--host", default="127.0.0.1")
    api.add_argument("--port", type=int, default=8000)

    evaluate = subparsers.add_parser(
        "evaluate-taxonomy",
        help="Avalia a taxonomia contra um dataset manual versionado",
    )
    evaluate.add_argument("--dataset", default="data/evaluation/v1.jsonl")

    technical_evaluate = subparsers.add_parser(
        "evaluate-technical-attributes",
        help="Avalia atributos técnicos contra dataset manual versionado",
    )
    technical_evaluate.add_argument(
        "--dataset",
        default="data/evaluation/technical-attributes-v1.jsonl",
    )

    technical_errors = subparsers.add_parser(
        "technical-attribute-errors",
        help="Lista divergências dos atributos técnicos avaliados",
    )
    technical_errors.add_argument(
        "--dataset",
        default="data/evaluation/technical-attributes-v1.jsonl",
    )
    technical_errors.add_argument("--limit", type=int, default=50)

    medications_evaluate = subparsers.add_parser(
        "evaluate-medications",
        help="Avalia a taxonomia de medicamentos contra dataset versionado",
    )
    medications_evaluate.add_argument(
        "--dataset",
        default="data/evaluation/medications-v1.jsonl",
    )

    medications_errors = subparsers.add_parser(
        "medication-errors",
        help="Lista divergências do benchmark de medicamentos",
    )
    medications_errors.add_argument(
        "--dataset",
        default="data/evaluation/medications-v1.jsonl",
    )
    medications_errors.add_argument("--limit", type=int, default=50)

    errors = subparsers.add_parser(
        "evaluation-errors",
        help="Lista divergências entre rótulo manual e categoria prevista",
    )
    errors.add_argument("--dataset", default="data/evaluation/v1.jsonl")
    errors.add_argument("--limit", type=int, default=50)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "build-analytics":
        result = build_analytics(args.raw, args.parquet, args.database)
        print(_serialize(asdict(result)))
        return 0

    if args.command == "build-awards":
        result = build_awards(
            args.items_raw,
            args.results_raw,
            args.parquet,
            args.database,
            contract_raw_path=args.contract_raw,
        )
        print(_serialize(asdict(result)))
        return 0

    if args.command == "build-award-dataset":
        manifests = discover_contract_bundles(args.bundles_root)
        result = build_award_dataset(
            manifests,
            args.parquet,
            args.database,
        )
        print(_serialize(asdict(result)))
        return 0

    if args.command == "build-demo-data":
        with PNCPClient() as client:
            result = build_demo_data(
                client,
                args.output_root,
                cnpj=args.cnpj,
                year=args.year,
                sequence=args.sequence,
            )
        print(_serialize(asdict(result)))
        return 0

    if args.command == "detect-anomalies":
        result = build_price_signals(
            args.database,
            minimum_group_size=args.minimum_group_size,
            modified_z_threshold=args.modified_z_threshold,
            iqr_multiplier=args.iqr_multiplier,
        )
        print(_serialize(asdict(result)))
        return 0

    if args.command == "analytics-summary":
        print(_serialize(DuckDBWarehouse(args.database).summary()))
        return 0

    if args.command == "awards-summary":
        print(_serialize(award_summary(args.database)))
        return 0

    if args.command == "anomalies-summary":
        print(_serialize(anomaly_summary(args.database)))
        return 0

    if args.command == "normalization-quality":
        if args.by_category:
            print(_serialize(quality_by_category(args.database)))
        else:
            print(_serialize(quality_summary(args.database)))
        return 0

    if args.command == "unrecognized-items":
        print(
            _serialize(
                unrecognized_items(
                    args.database,
                    limit=args.limit,
                )
            )
        )
        return 0

    if args.command == "build-dashboard":
        from dental_procurement_intelligence.dashboard import build_dashboard

        output = build_dashboard(args.database, args.output)
        print(_serialize({"output": str(output)}))
        return 0

    if args.command == "serve-api":
        try:
            import uvicorn
        except ImportError as exc:
            raise RuntimeError(
                'Instale o extra da API com: pip install -e ".[api]"'
            ) from exc

        from dental_procurement_intelligence.api.app import create_app

        uvicorn.run(
            create_app(args.database),
            host=args.host,
            port=args.port,
        )
        return 0

    if args.command == "evaluate-taxonomy":
        print(_serialize(asdict(evaluate_dataset(args.dataset))))
        return 0

    if args.command == "evaluate-technical-attributes":
        print(_serialize(asdict(evaluate_technical_attributes(args.dataset))))
        return 0

    if args.command == "technical-attribute-errors":
        if args.limit < 1:
            raise ValueError("--limit deve ser pelo menos 1")
        print(
            _serialize(
                technical_attribute_errors(args.dataset)[: args.limit]
            )
        )
        return 0

    if args.command == "evaluate-medications":
        from dental_procurement_intelligence.evaluation import (
            evaluate_medications,
        )

        print(_serialize(asdict(evaluate_medications(args.dataset))))
        return 0

    if args.command == "medication-errors":
        from dental_procurement_intelligence.evaluation import medication_errors

        if args.limit < 1:
            raise ValueError("--limit deve ser pelo menos 1")
        print(_serialize(medication_errors(args.dataset)[: args.limit]))
        return 0

    if args.command == "evaluation-errors":
        if args.limit < 1:
            raise ValueError("--limit deve ser pelo menos 1")
        print(_serialize(evaluation_errors(args.dataset)[: args.limit]))
        return 0

    with PNCPClient() as client:
        store = EvidenceStore(args.output) if hasattr(args, "output") else None

        if args.command == "capture-contract":
            result = capture_contract(
                client,
                store,
                cnpj=args.cnpj,
                year=args.year,
                sequence=args.sequence,
            )
            print(_serialize(asdict(result)))
            return 0

        if args.command == "capture-items":
            raw = client.get_items_raw(args.cnpj, args.year, args.sequence)
            record = store.capture(raw)
            print(_serialize(asdict(record)))
            return 0

        if args.command == "capture-results":
            raw = client.get_item_results_raw(
                args.cnpj,
                args.year,
                args.sequence,
                args.item,
            )
            record = store.capture(raw)
            print(_serialize(asdict(record)))
            return 0

        if args.command == "contract":
            record = client.get_contract(args.cnpj, args.year, args.sequence)
            print(_serialize(record.model_dump(by_alias=True)))
            return 0

        if args.command == "items":
            records = client.get_items(args.cnpj, args.year, args.sequence)
        else:
            records = client.get_item_results(
                args.cnpj,
                args.year,
                args.sequence,
                args.item,
            )

    print(_serialize([record.model_dump(by_alias=True) for record in records]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
