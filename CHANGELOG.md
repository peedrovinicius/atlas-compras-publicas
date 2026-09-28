# Changelog

Este arquivo registra mudanças públicas relevantes do Atlas de Compras Públicas. Benchmarks e auditorias detalhadas permanecem documentados em `docs/`.

## Em desenvolvimento

- busca pública por produtos comparáveis na base analítica;
- resumo de preços com mediana, percentis, dispersão e controle de suficiência da amostra;
- histórico temporal e comparação por região e UF;
- visões de fornecedores e órgãos compradores;
- sinais estatísticos com aviso interpretativo;
- rastreabilidade dos registros até hashes de origem e PNCP;
- interface React reorganizada em Explorar preços e Laboratório;
- documentação da API atualizada para refletir as novas rotas públicas.

## 1.49.0

- congelamento do holdout independente de medicamentos v4 com 48 exemplos e 192 campos;
- baseline independente v4 preservada em 189/192 campos corretos, equivalente a 98,44% de micro accuracy;
- regressão pós-tuning v1.49 registrada separadamente em 192/192 campos corretos;
- snapshot de qualidade consolidado para medicamentos v1-v4;
- consolidação técnica atualizada para v1-v12, com 548 exemplos e 984 campos;
- integridade dos holdouts de medicamentos v1-v4 protegida por hashes;
- documentação pública, templates de colaboração e governança do repositório ampliados.

Detalhes: [release v1.49.0](docs/release-v1.49.0.md) e [auditoria v1.49.0](docs/audit-v1.49.0.md).
