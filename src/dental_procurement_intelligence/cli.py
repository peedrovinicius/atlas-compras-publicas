import argparse
import json
from collections.abc import Sequence
from dataclasses import asdict
from typing import Any

from dental_procurement_intelligence.analytics import DuckDBWarehouse, build_analytics
from dental_procurement_intelligence.ingestion import EvidenceStore
from dental_procurement_intelligence.pncp import PNCPClient


def _serialize(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dpi",
        description="Inteligência auditável para compras públicas odontológicas",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    items = subparsers.add_parser(
        "items",
        help="Consulta os itens de uma contratação no PNCP",
    )
    items.add_argument("--cnpj", required=True)
    items.add_argument("--year", required=True, type=int)
    items.add_argument("--sequence", required=True, type=int)

    capture = subparsers.add_parser(
        "capture-items",
        help="Persiste a resposta bruta dos itens com evidência imutável",
    )
    capture.add_argument("--cnpj", required=True)
    capture.add_argument("--year", required=True, type=int)
    capture.add_argument("--sequence", required=True, type=int)
    capture.add_argument("--output", default="data/raw")

    results = subparsers.add_parser(
        "results",
        help="Consulta os resultados homologados de um item",
    )
    results.add_argument("--cnpj", required=True)
    results.add_argument("--year", required=True, type=int)
    results.add_argument("--sequence", required=True, type=int)
    results.add_argument("--item", required=True, type=int)

    analytics = subparsers.add_parser(
        "build-analytics",
        help="Transforma um arquivo bruto em Parquet e catálogo DuckDB",
    )
    analytics.add_argument("--raw", required=True)
    analytics.add_argument("--parquet", default="data/silver/items.parquet")
    analytics.add_argument("--database", default="data/analytics.duckdb")

    summary = subparsers.add_parser(
        "analytics-summary",
        help="Exibe o resumo de preços por categoria no DuckDB",
    )
    summary.add_argument("--database", default="data/analytics.duckdb")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "build-analytics":
        result = build_analytics(args.raw, args.parquet, args.database)
        print(_serialize(asdict(result)))
        return 0

    if args.command == "analytics-summary":
        print(_serialize(DuckDBWarehouse(args.database).summary()))
        return 0

    with PNCPClient() as client:
        if args.command == "capture-items":
            raw = client.get_items_raw(args.cnpj, args.year, args.sequence)
            record = EvidenceStore(args.output).capture(raw)
            print(_serialize(asdict(record)))
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

    print(
        _serialize(
            [record.model_dump(by_alias=True) for record in records]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
