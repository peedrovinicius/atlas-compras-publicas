from pathlib import Path
from typing import Any

from dental_procurement_intelligence.api.service import (
    analytics_anomalies,
    analytics_awards,
    analytics_categories,
    analytics_overview,
    analytics_quality,
    analytics_unrecognized,
)
from dental_procurement_intelligence.identity import available_domains, parse_product


def create_app(database_path: str | Path = "data/analytics.duckdb") -> Any:
    try:
        from fastapi import FastAPI, HTTPException, Query
        from fastapi.responses import HTMLResponse
    except ImportError as exc:
        raise RuntimeError(
            'Instale o extra da API com: pip install -e ".[api]"'
        ) from exc

    app = FastAPI(
        title="Atlas de Compras Públicas API",
        version="1",
        description=(
            "API analítica para dados normalizados, qualidade, homologações "
            "e sinais estatísticos do Atlas de Compras Públicas."
        ),
    )

    def execute(callable_: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            return callable_(*args, **kwargs)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    def demo() -> str:
        return """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Atlas de Compras Públicas</title>
<style>
:root {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif;
  color-scheme: dark;
}
* { box-sizing: border-box; }
body { margin: 0; background: #0d1117; color: #e6edf3; }
main { width: min(920px, 92vw); margin: 0 auto; padding: 56px 0 72px; }
.eyebrow {
  color: #8b949e;
  text-transform: uppercase;
  letter-spacing: .14em;
  font-size: 12px;
}
h1 { font-size: clamp(36px, 7vw, 66px); line-height: 1; margin: 10px 0 16px; }
.lead { color: #aab3bd; line-height: 1.65; max-width: 760px; }
.card {
  margin-top: 30px;
  padding: 22px;
  border: 1px solid #30363d;
  border-radius: 16px;
  background: #161b22;
}
label { display: block; font-weight: 700; margin-bottom: 10px; }
textarea {
  width: 100%;
  min-height: 110px;
  resize: vertical;
  border-radius: 10px;
  border: 1px solid #30363d;
  background: #0d1117;
  color: #e6edf3;
  padding: 14px;
  font: inherit;
}
button {
  margin-top: 12px;
  border: 0;
  border-radius: 10px;
  padding: 11px 16px;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
  background: #e6edf3;
  color: #0d1117;
}
pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #0d1117; border-radius: 10px; padding: 16px; min-height: 88px; color: #c9d1d9; }
.meta { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 18px; font-size: 14px; }
a { color: #58a6ff; }
.note { color: #8b949e; font-size: 13px; line-height: 1.55; margin-top: 18px; }
</style>
</head>
<body>
<main>
  <div class="eyebrow">Demo pública</div>
  <h1>Atlas de Compras Públicas</h1>
  <p class="lead">
    Teste a normalização real de uma descrição do PNCP. A demo usa o mesmo parser
    versionado do repositório e não simula preços nem sinais estatísticos.
  </p>

  <section class="card">
    <label for="description">Descrição do item</label>
    <textarea id="description">RES FOTOP A2 C/2 SERINGAS 4G</textarea>
    <button id="run">Normalizar</button>
    <pre id="result">Clique em “Normalizar”.</pre>
  </section>

  <div class="meta">
    <a href="/docs">Swagger / OpenAPI</a>
    <a href="/api/v1/domains">Domínios</a>
    <a href="https://github.com/peedrovinicius/atlas-compras-publicas">Código-fonte</a>
  </div>

  <p class="note">
    Os painéis de preços, homologações e sinais dependem de uma base DuckDB analítica
    consolidada e ainda não são publicados nesta demo.
  </p>
</main>
<script>
const button = document.getElementById("run");
const input = document.getElementById("description");
const output = document.getElementById("result");

async function normalize() {
  const description = input.value.trim();
  if (!description) return;
  output.textContent = "Processando...";
  try {
    const endpoint = "/api/v1/normalize?description=";
    const response = await fetch(endpoint + encodeURIComponent(description));
    const data = await response.json();
    output.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    output.textContent = "Falha ao consultar a API.";
  }
}
button.addEventListener("click", normalize);
</script>
</body>
</html>"""

    @app.get("/api/v1/normalize")
    def normalize(
        description: str = Query(min_length=3, max_length=2000),
    ) -> dict[str, Any]:
        product = parse_product(description)

        def quantity(value: Any) -> dict[str, Any] | None:
            if value is None:
                return None
            return {
                "value": str(value.value),
                "unit": value.unit,
                "dimension": value.dimension.value,
            }

        attributes = product.technical_attributes
        return {
            "original_description": product.original_description,
            "normalized_description": product.normalized_description,
            "category": product.category.value,
            "presentation": product.presentation,
            "shade": product.shade,
            "concentration_percent": (
                str(product.concentration_percent)
                if product.concentration_percent is not None
                else None
            ),
            "package_count": product.package_count,
            "measurement_resolution": product.measurement_resolution,
            "unit_quantity": quantity(product.unit_quantity),
            "total_quantity": quantity(product.total_quantity),
            "technical_attributes": {
                "resin_technology": attributes.resin_technology,
                "curing_mode": attributes.curing_mode,
                "adhesive_strategy": attributes.adhesive_strategy,
                "ionomer_use": attributes.ionomer_use,
                "fluoride_formulation": attributes.fluoride_formulation,
                "anesthetic_active_ingredient": attributes.anesthetic_active_ingredient,
                "anesthetic_vasoconstrictor": attributes.anesthetic_vasoconstrictor,
            },
            "matched_terms": list(product.matched_terms),
        }

    @app.get("/api/v1/domains")
    def domains() -> list[dict[str, Any]]:
        return [
            {
                "id": descriptor.domain.value,
                "label": descriptor.label,
                "status": descriptor.status.value,
                "benchmark_required": descriptor.benchmark_required,
            }
            for descriptor in available_domains()
        ]

    @app.get("/api/v1/overview")
    def overview() -> dict[str, Any]:
        return execute(analytics_overview, database_path)

    @app.get("/api/v1/categories")
    def categories(
        category: str | None = None,
        limit: int = Query(default=50, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> dict[str, Any]:
        return execute(
            analytics_categories,
            database_path,
            category=category,
            limit=limit,
            offset=offset,
        )

    @app.get("/api/v1/quality")
    def quality() -> dict[str, Any]:
        return execute(analytics_quality, database_path)

    @app.get("/api/v1/awards")
    def awards(
        category: str | None = None,
        macroregion: str | None = None,
        year: int | None = None,
        limit: int = Query(default=50, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> dict[str, Any]:
        return execute(
            analytics_awards,
            database_path,
            category=category,
            macroregion=macroregion,
            year=year,
            limit=limit,
            offset=offset,
        )

    @app.get("/api/v1/anomalies")
    def anomalies(
        category: str | None = None,
        scope: str | None = None,
        limit: int = Query(default=50, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> dict[str, Any]:
        return execute(
            analytics_anomalies,
            database_path,
            category=category,
            scope=scope,
            limit=limit,
            offset=offset,
        )

    @app.get("/api/v1/unrecognized")
    def unrecognized(
        limit: int = Query(default=50, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> dict[str, Any]:
        return execute(
            analytics_unrecognized,
            database_path,
            limit=limit,
            offset=offset,
        )

    return app
