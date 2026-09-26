# Local data layers

Generated datasets are intentionally not versioned in Git.

The pipeline will use the following local folders:

- `raw/` — immutable PNCP responses and provenance metadata;
- `bronze/` — typed source records;
- `silver/` — normalized product attributes and units;
- `gold/` — analytical tables and explainable anomaly outputs.

Only documentation, schemas and small test fixtures belong in the repository. Real bulk datasets should be reproducible from public sources rather than committed as opaque artifacts.
