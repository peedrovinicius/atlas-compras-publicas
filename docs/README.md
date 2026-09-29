# Documentação do Atlas de Compras Públicas

Este diretório reúne arquitetura, metodologia, benchmarks e registros de release. Os documentos históricos são preservados para rastreabilidade, mas os pontos de entrada atuais estão organizados abaixo.

## Visão geral

- [Arquitetura](architecture.md)
- [Arquitetura multidomínio](multidomain-architecture.md)
- [Fronteiras dos domínios de saúde](architecture-health-domains.md)
- [API e aplicação analítica](api-dashboard.md)
- [Exemplo real e reproduzível do parser](exemplo-parser-real.md)
- [Contrato do warehouse v1](warehouse-v1.md)
- [Dataset multi-contratação](multi-contratacao.md)
- [Qualidade do normalizador](qualidade-normalizador.md)
- [Exemplos de SQL no DuckDB](sql-examples.md)

## Metodologia

- [Metodologia de sinais de preço](metodologia-anomalias.md)
- [Precisão monetária](precisao-monetaria.md)
- [Revisão do motor de regras](architecture-rules-review.md)

## Qualidade e benchmarks

- [Snapshot de qualidade](dashboard-quality-snapshot.html)
- [Dados do snapshot](dashboard-quality-snapshot.json)
- [Consolidação técnica v1-v12](benchmark-technical-consolidated-v1-v12.md)
- [Benchmark técnico v12](benchmark-technical-attributes-v12.md)
- [Pós-tuning técnico v12](benchmark-technical-attributes-v12-post-tuning.md)

### Domínio experimental de saúde

O domínio histórico `medications` testa a generalização além da odontologia. A auditoria da issue #30 concluiu que os holdouts v1-v4 são farmacêuticos e devem permanecer separados de materiais, dispositivos e outros produtos de saúde.

- [Consolidação histórica v1-v4](benchmark-medications-consolidated-v1-v4.md)
- [Benchmark independente v4](benchmark-medications-v4.md)
- [Pós-tuning v4](benchmark-medications-v4-post-tuning.md)
- [Congelamento do holdout v4](medications-v4-freeze.md)

## Release atual

- [Changelog](../CHANGELOG.md)
- [Release v1.72.0](release-v1.72.0.md)
- [Release v1.71.0](release-v1.71.0.md)
- [Release v1.70.0](release-v1.70.0.md)
- [Release v1.69.0](release-v1.69.0.md)
- [Release v1.68.0](release-v1.68.0.md)
- [Release v1.67.0](release-v1.67.0.md)
- [Release v1.66.0](release-v1.66.0.md)
- [Release v1.65.0](release-v1.65.0.md)
- [Release v1.64.0](release-v1.64.0.md)
- [Release v1.63.0](release-v1.63.0.md)
- [Release v1.62.0](release-v1.62.0.md)
- [Release v1.61.0](release-v1.61.0.md)
- [Release v1.60.0](release-v1.60.0.md)
- [Release v1.59.0](release-v1.59.0.md)
- [Release v1.58.0](release-v1.58.0.md)
- [Release v1.57.0](release-v1.57.0.md)
- [Release v1.56.0](release-v1.56.0.md)
- [Release v1.55.0](release-v1.55.0.md)
- [Release v1.54.0](release-v1.54.0.md)
- [Release v1.53.0](release-v1.53.0.md)
- [Release v1.52.0](release-v1.52.0.md)
- [Release v1.51.0](release-v1.51.0.md)
- [Release v1.50.0](release-v1.50.0.md)
- [Release v1.49.0](release-v1.49.0.md)
- [Auditoria v1.49.0](audit-v1.49.0.md)
- [Revisão do README v1.49.0](readme-review-v1.49.0.md)

## Histórico

Os demais arquivos deste diretório registram ciclos anteriores de benchmark, tuning, arquitetura e validação. Eles são mantidos para reprodução dos resultados e não substituem os documentos consolidados acima.
