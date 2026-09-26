# Architecture

## Objective

The system must produce price intelligence without losing the chain of evidence that connects an analytical result to the original PNCP record.

## Data contract

Each acquisition record will move through four logical layers.

### Raw

Exact source payload plus retrieval metadata. A raw object is immutable once persisted.

Required provenance metadata will include:

- source URL;
- retrieval timestamp in UTC;
- HTTP status;
- response content hash;
- pipeline version.

### Bronze

Typed and structurally validated PNCP records. Field names are standardized, but semantic values are not corrected or inferred.

### Silver

Domain normalization is applied here. Expected outputs include normalized text, extracted measurements, package attributes, dental category candidates and explicit uncertainty flags.

### Gold

Only defensible comparison groups reach this layer. It will contain normalized prices, robust descriptive statistics, anomaly signals and evidence references.

## Product identity strategy

Product identity is deliberately separated from raw text similarity.

The planned scorer will combine:

1. deterministic extraction of units, package counts and clinical attributes;
2. controlled dental vocabulary;
3. compatibility rules that can reject impossible matches;
4. semantic similarity for residual language variation;
5. an explanation object describing supporting and conflicting evidence.

A high similarity score must not override an incompatible unit, presentation or clinically relevant attribute.

## Analytical guardrail

Anomaly detection is a prioritization mechanism, not an accusation. Every signal must expose its comparison population, method, sample size and underlying records.
