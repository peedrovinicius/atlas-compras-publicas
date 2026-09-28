import csv
import io
import os
from collections import defaultdict, deque
from pathlib import Path
from threading import Lock
from time import monotonic
from typing import Any

import duckdb

from dental_procurement_intelligence import __version__
from dental_procurement_intelligence.api.catalog import parser_categories
from dental_procurement_intelligence.api.service import (
    analytics_anomalies,
    analytics_awards,
    analytics_categories,
    analytics_overview,
    analytics_product_buyers,
    analytics_product_discovery,
    analytics_product_distribution,
    analytics_product_history,
    analytics_product_records,
    analytics_product_records_export,
    analytics_product_regions,
    analytics_product_search,
    analytics_product_signals,
    analytics_product_summary,
    analytics_product_suppliers,
    analytics_quality,
    analytics_unrecognized,
)
from dental_procurement_intelligence.identity import available_domains, parse_product


def _bootstrap_demo_database(path: Path) -> Path:
    if path.exists():
        return path

    enabled = os.environ.get("ATLAS_BOOTSTRAP_DEMO", "").strip().lower()
    if enabled not in {"1", "true", "yes"}:
        return path

    from dental_procurement_intelligence.analytics.demo_data import build_demo_data
    from dental_procurement_intelligence.pncp import PNCPClient

    max_results_raw = os.environ.get("ATLAS_BOOTSTRAP_MAX_RESULTS", "8").strip()
    try:
        max_results = int(max_results_raw)
    except ValueError as exc:
        raise RuntimeError(
            "ATLAS_BOOTSTRAP_MAX_RESULTS deve ser um inteiro positivo."
        ) from exc
    if max_results < 1:
        raise RuntimeError(
            "ATLAS_BOOTSTRAP_MAX_RESULTS deve ser um inteiro positivo."
        )

    with PNCPClient() as client:
        result = build_demo_data(
            client,
            path.parent,
            max_result_requests_per_procurement=max_results,
        )

    generated = Path(result.database_path)
    if generated != path:
        path.parent.mkdir(parents=True, exist_ok=True)
        generated.replace(path)

    return path


def _analytics_database_ready(path: Path) -> bool:
    if not path.is_file():
        return False

    try:
        with duckdb.connect(str(path), read_only=True) as connection:
            row = connection.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name = 'silver_awards'
                """
            ).fetchone()
    except duckdb.Error:
        return False

    return bool(row and row[0] > 0)


def create_app(database_path: str | Path | None = None) -> Any:
    try:
        from fastapi import Body, FastAPI, HTTPException, Query, Request
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import RedirectResponse, Response
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

    resolved_database_path = _bootstrap_demo_database(
        Path(
            database_path
            or os.environ.get("ATLAS_DATABASE_PATH", "data/analytics.duckdb")
        )
    )
    frontend_url = os.environ.get(
        "ATLAS_FRONTEND_URL",
        "https://atlas-compras-publicas-web.onrender.com",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_origin_regex=r"https://atlas-compras-publicas(?:-web)?\.onrender\.com",
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    rate_window_seconds = 60.0
    rate_limit = 60
    normalization_requests: dict[str, deque[float]] = defaultdict(deque)
    rate_lock = Lock()

    def enforce_normalization_rate_limit(request: Any) -> None:
        forwarded = request.headers.get("x-forwarded-for", "")
        client_ip = forwarded.split(",", 1)[0].strip()
        if not client_ip and request.client is not None:
            client_ip = request.client.host
        client_ip = client_ip or "unknown"

        now = monotonic()
        with rate_lock:
            bucket = normalization_requests[client_ip]
            while bucket and now - bucket[0] >= rate_window_seconds:
                bucket.popleft()
            if len(bucket) >= rate_limit:
                raise HTTPException(
                    status_code=429,
                    detail="Limite de normalizações atingido. Tente novamente em instantes.",
                    headers={"Retry-After": "60"},
                )
            bucket.append(now)

    def execute(callable_: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            return callable_(*args, **kwargs)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/ready")
    def ready() -> dict[str, str]:
        if not _analytics_database_ready(resolved_database_path):
            raise HTTPException(
                status_code=503,
                detail="Banco analítico indisponível.",
            )
        return {
            "status": "ready",
            "version": __version__,
            "database": resolved_database_path.name,
        }

    @app.get("/", include_in_schema=False)
    def frontend() -> RedirectResponse:
        return RedirectResponse(frontend_url, status_code=307)

    def serialize_description(description: str) -> dict[str, Any]:
        cleaned_description = description.strip()
        if len(cleaned_description) < 3:
            raise HTTPException(
                status_code=422,
                detail="A descrição deve ter pelo menos 3 caracteres úteis.",
            )
        if len(cleaned_description) > 2000:
            raise HTTPException(
                status_code=422,
                detail="Cada descrição deve ter no máximo 2.000 caracteres.",
            )

        product = parse_product(cleaned_description)

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
            "atlas_version": __version__,
            "classification_method": "deterministic_rules",
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

    @app.get("/api/v1/normalize")
    def normalize(
        request: Request,
        description: str = Query(min_length=3, max_length=2000),
    ) -> dict[str, Any]:
        enforce_normalization_rate_limit(request)
        return serialize_description(description)

    batch_descriptions_body = Body(min_length=1, max_length=20)

    @app.post("/api/v1/normalize/batch")
    def normalize_batch(
        request: Request,
        descriptions: list[str] = batch_descriptions_body,
    ) -> dict[str, Any]:
        enforce_normalization_rate_limit(request)
        cleaned = [description.strip() for description in descriptions if description.strip()]
        if not cleaned:
            raise HTTPException(
                status_code=422,
                detail="Informe pelo menos uma descrição.",
            )
        if len(cleaned) > 20:
            raise HTTPException(
                status_code=422,
                detail="Envie no máximo 20 descrições por lote.",
            )
        return {
            "count": len(cleaned),
            "items": [serialize_description(description) for description in cleaned],
        }

    @app.get("/api/v1/meta")
    def meta() -> dict[str, Any]:
        return {
            "version": __version__,
            "database_available": resolved_database_path.exists(),
            "database_name": resolved_database_path.name,
            "frontend_url": frontend_url,
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

    @app.get("/api/v1/parser/categories")
    def supported_parser_categories() -> list[dict[str, str | bool]]:
        return parser_categories()

    @app.get("/api/v1/overview")
    def overview() -> dict[str, Any]:
        return execute(analytics_overview, resolved_database_path)

    @app.get("/api/v1/products/discovery")
    def product_discovery() -> dict[str, Any]:
        return execute(
            analytics_product_discovery,
            resolved_database_path,
        )

    @app.get("/api/v1/products/search")
    def product_search(
        q: str = Query(min_length=2, max_length=200),
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        sort: str = Query(default="relevance"),
        state_code: str | None = None,
        macroregion: str | None = None,
        supplier: str | None = None,
        buyer: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        return execute(
            analytics_product_search,
            resolved_database_path,
            query=q,
            limit=limit,
            offset=offset,
            sort=sort,
            state_code=state_code,
            macroregion=macroregion,
            supplier=supplier,
            buyer=buyer,
            start_date=start_date,
            end_date=end_date,
        )

    @app.get("/api/v1/products/{product_id}/signals")
    def product_signals(
        product_id: str,
        limit: int = Query(default=50, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        state_code: str | None = None,
        macroregion: str | None = None,
        supplier: str | None = None,
        buyer: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        return execute(
            analytics_product_signals,
            resolved_database_path,
            product_id=product_id,
            limit=limit,
            offset=offset,
            state_code=state_code,
            macroregion=macroregion,
            supplier=supplier,
            buyer=buyer,
            start_date=start_date,
            end_date=end_date,
        )

    @app.get("/api/v1/products/{product_id}/records.csv")
    def product_records_csv(
        product_id: str,
        state_code: str | None = None,
        macroregion: str | None = None,
        supplier: str | None = None,
        buyer: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> Response:
        rows = execute(
            analytics_product_records_export,
            resolved_database_path,
            product_id=product_id,
            state_code=state_code,
            macroregion=macroregion,
            supplier=supplier,
            buyer=buyer,
            start_date=start_date,
            end_date=end_date,
        )
        columns = [
            "award_key",
            "procurement_key",
            "item_number",
            "result_sequence",
            "analysis_date",
            "original_description",
            "supplier_name",
            "supplier_document",
            "organization_name",
            "buyer_unit_name",
            "municipality_name",
            "state_code",
            "macroregion",
            "modality",
            "awarded_unit_value",
            "awarded_quantity",
            "awarded_total_value",
            "awarded_price_per_base_unit",
            "price_normalization_status",
            "price_normalization_reason",
            "contract_source_sha256",
            "item_source_sha256",
            "result_source_sha256",
            "pncp_url",
        ]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        content = "\ufeff" + output.getvalue()
        return Response(
            content=content,
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="atlas-{product_id[:8]}-registros.csv"'
                )
            },
        )

    @app.get("/api/v1/products/{product_id}/records")
    def product_records(
        product_id: str,
        limit: int = Query(default=50, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        state_code: str | None = None,
        macroregion: str | None = None,
        supplier: str | None = None,
        buyer: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        return execute(
            analytics_product_records,
            resolved_database_path,
            product_id=product_id,
            limit=limit,
            offset=offset,
            state_code=state_code,
            macroregion=macroregion,
            supplier=supplier,
            buyer=buyer,
            start_date=start_date,
            end_date=end_date,
        )

    @app.get("/api/v1/products/{product_id}/suppliers")
    def product_suppliers(
        product_id: str,
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        state_code: str | None = None,
        macroregion: str | None = None,
        supplier: str | None = None,
        buyer: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        return execute(
            analytics_product_suppliers,
            resolved_database_path,
            product_id=product_id,
            limit=limit,
            offset=offset,
            state_code=state_code,
            macroregion=macroregion,
            supplier=supplier,
            buyer=buyer,
            start_date=start_date,
            end_date=end_date,
        )

    @app.get("/api/v1/products/{product_id}/buyers")
    def product_buyers(
        product_id: str,
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        state_code: str | None = None,
        macroregion: str | None = None,
        supplier: str | None = None,
        buyer: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        return execute(
            analytics_product_buyers,
            resolved_database_path,
            product_id=product_id,
            limit=limit,
            offset=offset,
            state_code=state_code,
            macroregion=macroregion,
            supplier=supplier,
            buyer=buyer,
            start_date=start_date,
            end_date=end_date,
        )

    @app.get("/api/v1/products/{product_id}/regions")
    def product_regions(
        product_id: str,
        state_code: str | None = None,
        macroregion: str | None = None,
        supplier: str | None = None,
        buyer: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        return execute(
            analytics_product_regions,
            resolved_database_path,
            product_id=product_id,
            state_code=state_code,
            macroregion=macroregion,
            supplier=supplier,
            buyer=buyer,
            start_date=start_date,
            end_date=end_date,
        )

    @app.get("/api/v1/products/{product_id}/distribution")
    def product_distribution(
        product_id: str,
        bins: int = Query(default=10, ge=5, le=40),
        state_code: str | None = None,
        macroregion: str | None = None,
        supplier: str | None = None,
        buyer: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        return execute(
            analytics_product_distribution,
            resolved_database_path,
            product_id=product_id,
            bin_count=bins,
            state_code=state_code,
            macroregion=macroregion,
            supplier=supplier,
            buyer=buyer,
            start_date=start_date,
            end_date=end_date,
        )

    @app.get("/api/v1/products/{product_id}/history")
    def product_history(
        product_id: str,
        state_code: str | None = None,
        macroregion: str | None = None,
        supplier: str | None = None,
        buyer: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        return execute(
            analytics_product_history,
            resolved_database_path,
            product_id=product_id,
            state_code=state_code,
            macroregion=macroregion,
            supplier=supplier,
            buyer=buyer,
            start_date=start_date,
            end_date=end_date,
        )

    @app.get("/api/v1/products/{product_id}")
    def product_summary(
        product_id: str,
        state_code: str | None = None,
        macroregion: str | None = None,
        supplier: str | None = None,
        buyer: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        return execute(
            analytics_product_summary,
            resolved_database_path,
            product_id=product_id,
            state_code=state_code,
            macroregion=macroregion,
            supplier=supplier,
            buyer=buyer,
            start_date=start_date,
            end_date=end_date,
        )

    @app.get("/api/v1/categories")
    def categories(
        category: str | None = None,
        limit: int = Query(default=50, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> dict[str, Any]:
        return execute(
            analytics_categories,
            resolved_database_path,
            category=category,
            limit=limit,
            offset=offset,
        )

    @app.get("/api/v1/quality")
    def quality() -> dict[str, Any]:
        return execute(analytics_quality, resolved_database_path)

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
            resolved_database_path,
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
            resolved_database_path,
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
            resolved_database_path,
            limit=limit,
            offset=offset,
        )

    return app
