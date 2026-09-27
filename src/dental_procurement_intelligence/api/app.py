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
from dental_procurement_intelligence.identity import available_domains


def create_app(database_path: str | Path = "data/analytics.duckdb") -> Any:
    try:
        from fastapi import FastAPI, HTTPException, Query
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
