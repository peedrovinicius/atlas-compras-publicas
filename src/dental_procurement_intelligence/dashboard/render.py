from html import escape
from pathlib import Path
from typing import Any

from dental_procurement_intelligence.api.service import analytics_overview


def _format_value(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return escape(str(value))


def _table(rows: list[dict[str, Any]], columns: tuple[str, ...]) -> str:
    if not rows:
        return '<p class="empty">Sem dados disponíveis para esta camada.</p>'

    head = "".join(f"<th>{escape(column)}</th>" for column in columns)
    body = []
    for row in rows:
        cells = "".join(
            f"<td>{_format_value(row.get(column))}</td>"
            for column in columns
        )
        body.append(f"<tr>{cells}</tr>")

    return (
        '<div class="table-wrap"><table><thead><tr>'
        + head
        + "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table></div>"
    )


def render_dashboard(overview: dict[str, Any]) -> str:
    quality = overview.get("quality") or {}
    categories = overview.get("category_prices") or []
    awards = overview.get("awards") or []
    anomalies = overview.get("anomalies") or []
    domains = overview.get("domains") or []

    total_items = quality.get("total_items", "—")
    recognized = quality.get("recognized_items", "—")
    fully_structured = quality.get("fully_structured_items", "—")
    avg_quality = quality.get("average_quality_score", "—")

    domain_badges = "".join(
        (
            '<span class="badge">'
            f"{escape(str(item.get('label', item.get('id', ''))))}: "
            f"{escape(str(item.get('status', '')))}"
            "</span>"
        )
        for item in domains
    )

    category_table = _table(
        categories,
        (
            "product_category",
            "item_count",
            "priced_item_count",
            "median_normalized_price",
            "min_normalized_price",
            "max_normalized_price",
        ),
    )
    award_table = _table(
        awards[:20],
        tuple(awards[0].keys()) if awards else (),
    )
    anomaly_table = _table(
        anomalies[:20],
        tuple(anomalies[0].keys()) if anomalies else (),
    )

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Atlas de Compras Públicas</title>
<style>
:root {{
  color-scheme: light dark;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: #0d1117;
  color: #e6edf3;
}}
main {{ width: min(1440px, 94vw); margin: 0 auto; padding: 48px 0 72px; }}
header {{ margin-bottom: 32px; }}
.eyebrow {{ text-transform: uppercase; letter-spacing: .14em; color: #8b949e; font-size: 12px; }}
h1 {{ font-size: clamp(34px, 5vw, 64px); margin: 8px 0 12px; line-height: 1; }}
.subtitle {{ color: #8b949e; max-width: 820px; line-height: 1.6; }}
.badges {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }}
.badge {{ border: 1px solid #30363d; border-radius: 999px; padding: 7px 11px; font-size: 12px; }}
.grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }}
.card {{ background: #161b22; border: 1px solid #30363d; border-radius: 14px; padding: 20px; }}
.card .label {{ color: #8b949e; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }}
.card .value {{ font-size: 30px; font-weight: 700; margin-top: 10px; }}
section {{ margin-top: 34px; }}
section h2 {{ font-size: 22px; margin-bottom: 14px; }}
.table-wrap {{ overflow-x: auto; border: 1px solid #30363d; border-radius: 12px; }}
table {{ width: 100%; border-collapse: collapse; min-width: 760px; }}
th, td {{ text-align: left; padding: 12px 14px; border-bottom: 1px solid #21262d; }}
th {{ color: #8b949e; font-size: 12px; text-transform: uppercase; letter-spacing: .06em; }}
td {{ font-size: 13px; }}
.empty {{ color: #8b949e; border: 1px dashed #30363d; padding: 18px; border-radius: 12px; }}
footer {{ color: #6e7681; margin-top: 42px; font-size: 12px; }}
@media (max-width: 900px) {{
  .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
}}
@media (max-width: 560px) {{
  main {{ width: min(92vw, 1440px); padding-top: 28px; }}
  .grid {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>
<main>
<header>
  <div class="eyebrow">Inteligência de dados auditável</div>
  <h1>Atlas de Compras Públicas</h1>
  <p class="subtitle">
    Visão analítica gerada diretamente do DuckDB do projeto.
    Snapshot: {_format_value(overview.get("generated_at"))}.
  </p>
  <div class="badges">{domain_badges}</div>
</header>
<div class="grid">
  <article class="card"><div class="label">Itens</div><div class="value">{_format_value(total_items)}</div></article>
  <article class="card"><div class="label">Reconhecidos</div><div class="value">{_format_value(recognized)}</div></article>
  <article class="card"><div class="label">Estruturados</div><div class="value">{_format_value(fully_structured)}</div></article>
  <article class="card"><div class="label">Qualidade média</div><div class="value">{_format_value(avg_quality)}</div></article>
</div>
<section>
  <h2>Preços normalizados por categoria</h2>
  {category_table}
</section>
<section>
  <h2>Homologações e economia</h2>
  {award_table}
</section>
<section>
  <h2>Sinais estatísticos</h2>
  {anomaly_table}
</section>
<footer>
  O dashboard apresenta sinais analíticos. Sinais estatísticos não constituem prova de irregularidade.
</footer>
</main>
</body>
</html>
"""


def build_dashboard(
    database_path: str | Path,
    output_path: str | Path,
) -> Path:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        render_dashboard(analytics_overview(database_path)),
        encoding="utf-8",
    )
    return target
