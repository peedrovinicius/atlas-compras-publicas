from collections import defaultdict, deque
from pathlib import Path
from threading import Lock
from time import monotonic
from typing import Any

from dental_procurement_intelligence import __version__
from dental_procurement_intelligence.api.catalog import parser_categories
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
        from fastapi import Body, FastAPI, HTTPException, Query, Request
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import RedirectResponse
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
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/", include_in_schema=False)
    def frontend() -> RedirectResponse:
        return RedirectResponse(
            "https://atlas-compras-publicas-web.onrender.com",
            status_code=307,
        )

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
