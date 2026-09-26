import argparse
import json
from collections.abc import Sequence
from typing import Any

from dental_procurement_intelligence.pncp import PNCPClient


def _serialize(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dpi", description="Inspect public PNCP procurement data")
    subparsers = parser.add_subparsers(dest="command", required=True)

    items = subparsers.add_parser("items", help="Fetch the items of a PNCP procurement")
    items.add_argument("--cnpj", required=True)
    items.add_argument("--year", required=True, type=int)
    items.add_argument("--sequence", required=True, type=int)

    results = subparsers.add_parser("results", help="Fetch awarded results for one PNCP item")
    results.add_argument("--cnpj", required=True)
    results.add_argument("--year", required=True, type=int)
    results.add_argument("--sequence", required=True, type=int)
    results.add_argument("--item", required=True, type=int)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    with PNCPClient() as client:
        if args.command == "items":
            records = client.get_items(args.cnpj, args.year, args.sequence)
        else:
            records = client.get_item_results(args.cnpj, args.year, args.sequence, args.item)

    print(_serialize([record.model_dump(by_alias=True) for record in records]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
