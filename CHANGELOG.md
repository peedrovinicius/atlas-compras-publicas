# Changelog

Este arquivo registra mudanças públicas relevantes do Atlas de Compras Públicas. Benchmarks e auditorias detalhadas permanecem documentados em `docs/`.

## 1.50.0

- aplicação pública reorganizada com `Explorar preços` como experiência principal e `Laboratório` para o parser;
- busca por produtos comparáveis e resumo estatístico de preços homologados;
- histórico mensal e comparação geográfica por região e UF;
- visões públicas de fornecedores e órgãos compradores;
- sinais estatísticos com aviso interpretativo e registros rastreáveis até o PNCP;
- exemplo público do parser documentado a partir do holdout v5 e protegido por teste automatizado;
- documentação da API e README atualizados para refletir a camada analítica publicada;
- versão do pacote, API e cliente PNCP sincronizada em 1.50.0.

## 1.49.0

- congelamento do holdout independente de medicamentos v4 com 48 exemplos e 192 campos;
- baseline independente v4 preservada em 189/192 campos corretos, equivalente a 98,44% de micro accuracy;
- regressão pós-tuning v1.49 registrada separadamente em 192/192 campos corretos;
- snapshot de qualidade consolidado para medicamentos v1-v4;
- consolidação técnica atualizada para v1-v12, com 548 exemplos e 984 campos;
- integridade dos holdouts de medicamentos v1-v4 protegida por hashes;
- documentação pública, templates de colaboração e governança do repositório ampliados.

Detalhes: [release v1.49.0](docs/release-v1.49.0.md) e [auditoria v1.49.0](docs/audit-v1.49.0.md).
