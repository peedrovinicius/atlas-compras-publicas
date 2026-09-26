# Dental Procurement Intelligence

Auditable data intelligence for Brazilian public dental procurement.

This project builds a reproducible pipeline to collect, normalize and compare dental procurement items published by Brazil's Portal Nacional de Contratações Públicas (PNCP). The central challenge is not plotting prices: it is determining when poorly standardized procurement descriptions refer to genuinely comparable products.

## Current status

**v0.2.0 — auditable ingestion**

The repository currently includes:

- a typed Python package;
- a public PNCP API client;
- structured models for procurement items and awarded results;
- deterministic text and measurement normalization;
- unit-tested parsing rules;
- an explicit raw-to-evidence architecture;
- a CLI for inspecting PNCP items and results;
- content-addressed raw evidence storage with SHA-256 provenance manifests.

No automated GitHub Actions workflow is enabled at this stage. Validation is designed to run locally so development does not consume unnecessary CI minutes.

## Why this project exists

Public procurement descriptions are often inconsistent. The same material can appear with abbreviations, different packaging conventions, spelling variants and mixed units. Direct price comparisons can therefore be misleading.

Dental Procurement Intelligence is designed around a stricter question:

> Are these two procurement records comparable enough for a price analysis, and can that decision be explained?

The long-term system will combine deterministic parsing, domain rules, semantic similarity and robust statistics while preserving traceability to the original public record.

## Data source

The primary source is the public PNCP production API:

`https://pncp.gov.br/api/pncp`

The initial integration uses official endpoints for procurement items and item results. Raw responses are treated as source evidence and should never be overwritten by transformed data.

## Architecture

~~~mermaid
flowchart LR
    A[PNCP API] --> B[Raw evidence]
    B --> C[Schema validation]
    C --> D[Text normalization]
    D --> E[Product identity engine]
    E --> F[Unit normalization]
    F --> G[Comparable groups]
    G --> H[Robust price analytics]
    H --> I[Evidence API]
    I --> J[Dashboard]
~~~

The intended data layers are:

- **raw** — immutable source payloads;
- **bronze** — structurally validated records;
- **silver** — normalized descriptions, units and product attributes;
- **gold** — comparable products, statistics and explainable alerts.

## Product identity engine

A future record such as:

`RES FOTOP A2 C/2 SER 4G`

should become structured evidence similar to:

~~~text
category: composite_resin
shade: A2
presentation: syringe
package_count: 2
unit_mass_g: 4
package_mass_g: 8
~~~

The system must retain the original description and explain every transformation. Similar text alone will never be treated as sufficient proof of product equivalence.

## Quick start

Python 3.12 or newer is recommended.

~~~bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
~~~

On Windows PowerShell:

~~~powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
~~~

Inspect the items of a known PNCP procurement:

~~~bash
dpi items --cnpj 10000000000003 --year 2021 --sequence 1
~~~

Capture the exact raw PNCP response with a SHA-256 evidence manifest:

~~~bash
dpi capture-items --cnpj 10000000000003 --year 2021 --sequence 1
~~~

Inspect awarded results for one item:

~~~bash
dpi results --cnpj 10000000000003 --year 2021 --sequence 1 --item 1
~~~

## Repository layout

~~~text
src/dental_procurement_intelligence/
  pncp/             public PNCP client and typed payload models
  ingestion/        immutable raw evidence and provenance manifests
  normalization/    deterministic description and measurement parsing
  cli.py            command-line interface

tests/              unit tests
docs/               architecture and technical decisions
data/               local data-layer contract; generated data is ignored
~~~

## Methodological guardrail

A statistically unusual price is not evidence of fraud, corruption or illegality. Future anomaly detection will identify records that deserve review and will expose the comparison group, method and source evidence used to produce that signal.

## Roadmap

- [x] Repository architecture and package foundation
- [x] PNCP item/result client
- [x] Deterministic text normalization
- [x] Measurement extraction baseline
- [x] Reproducible raw ingestion with content hashes
- [ ] Dental vocabulary and canonical product model
- [ ] Packaging and unit-equivalence engine
- [ ] Product identity scoring with explanations
- [ ] Parquet/DuckDB analytical layer
- [ ] Robust price-outlier detection
- [ ] FastAPI evidence service
- [ ] React analytical interface
- [ ] Public methodology and data-quality report

## Principles

1. Source evidence is immutable.
2. Transformations are reproducible.
3. Product equivalence is explainable.
4. Prices are compared only inside defensible groups.
5. Missing or uncertain information remains explicit.
6. Every analytical output must be traceable to its public source.
