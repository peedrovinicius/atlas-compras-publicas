# Documentação do Atlas de Compras Públicas

Este diretório reúne arquitetura, metodologia, benchmarks e registros de release. Os documentos históricos são preservados para rastreabilidade, mas os pontos de entrada atuais estão organizados abaixo.

## Visão geral

- [Arquitetura](architecture.md)
- [Arquitetura multidomínio](multidomain-architecture.md)
- [API e dashboard](api-dashboard.md)
- [Dataset multi-contratação](multi-contratacao.md)
- [Qualidade do normalizador](qualidade-normalizador.md)

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

O agrupamento histórico `medications` é usado para testar generalização além da odontologia e está em revisão arquitetural na [issue #30](https://github.com/peedrovinicius/atlas-compras-publicas/issues/30).

- [Consolidação histórica v1-v4](benchmark-medications-consolidated-v1-v4.md)
- [Benchmark independente v4](benchmark-medications-v4.md)
- [Pós-tuning v4](benchmark-medications-v4-post-tuning.md)
- [Congelamento do holdout v4](medications-v4-freeze.md)

## Release atual

- [Changelog](../CHANGELOG.md)
- [Release v1.49.0](release-v1.49.0.md)
- [Auditoria v1.49.0](audit-v1.49.0.md)
- [Revisão do README v1.49.0](readme-review-v1.49.0.md)

## Histórico

Os demais arquivos deste diretório registram ciclos anteriores de benchmark, tuning, arquitetura e validação. Eles são mantidos para reprodução dos resultados e não substituem os documentos consolidados acima.
