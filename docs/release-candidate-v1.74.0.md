# Release candidata v1.74.0

Este documento registra o estado da release candidata que deve ser publicada quando a infraestrutura de produção estiver liberada.

## Origem

- versão: `1.74.0`;
- branch de integração: `develop`;
- Pull Request de produção: `#36`;
- destino: `main`.

O SHA exato de produção deve ser o commit resultante do merge do PR #36. Não use um commit intermediário da `develop` para publicação manual.

## Conteúdo funcional

A release candidata reúne:

- comparação de proposta recebida com a distribuição observada;
- relatório imprimível/PDF;
- tendência recente entre os dois períodos mais recentes;
- contexto geográfico nacional, macrorregional e por UF;
- comparação de produtos compatíveis;
- exportação CSV e evidências rastreáveis ao PNCP;
- nova identidade visual `Atlas e Preços` no frontend;
- metadados de descoberta pública, sitemap, robots e manifesto web.

## Serviços canônicos

Produção deve usar somente:

- `atlas-compras-publicas-web`;
- `atlas-compras-publicas-analytics`.

Não fazem parte da arquitetura canônica:

- `atlas-compras-publicas-api`;
- `atlas-compras-publicas`.

## Gates obrigatórios

Antes do merge:

- `quality` aprovado;
- Ruff aprovado;
- pytest aprovado;
- build React/TypeScript aprovado;
- contratos de versão aprovados;
- contrato do Blueprint Render aprovado;
- `main` protegida;
- capacidade de build do Render disponível;
- serviços duplicados desativados/removidos;
- serviços canônicos alinhados com `checksPass`.

## Pós-deploy

Executar o workflow manual `Production smoke test`.

O workflow confirma:

- frontend acessível;
- versão do bundle igual à versão de `web/package.json`;
- `/health`;
- `/ready`;
- discovery;
- uma busca real.

Depois validar manualmente:

- P25, mediana e P75;
- comparador;
- `Preço que recebi`;
- tendência recente;
- contexto regional;
- CSV;
- relatório/PDF;
- evidências do PNCP.

## Estado atual

A release permanece bloqueada por infraestrutura externa. Não fazer merge do PR #36 enquanto os critérios acima não forem atendidos.
