# Integração contínua

## Objetivo

Executar os guardrails do Atlas automaticamente sem criar uma matriz cara de jobs.

## Workflow

Arquivo: `.github/workflows/ci.yml`.

O CI usa:

- Ubuntu;
- Python 3.12;
- cache de pip;
- um único job;
- limite de 10 minutos;
- cancelamento automático de execução antiga da mesma branch.

## Gatilhos

O workflow roda em pull requests e pushes no `main` somente quando mudam:

- `src/**`;
- `tests/**`;
- `data/evaluation/**`;
- `pyproject.toml`;
- o próprio workflow;
- o JSON de origem do snapshot.

Mudanças somente em documentação comum não consomem uma execução automática.

Também existe `workflow_dispatch` para execução manual.

## Guardrails

O CI executa:

~~~bash
ruff check .
pytest -q
~~~

Os testes incluem:

- consistência entre `pyproject.toml`, `__version__` e User-Agent;
- SHA Git blob dos principais datasets/baselines congelados;
- consistência do snapshot real com as baselines v1–v12;
- regressões técnicas;
- API;
- dashboard;
- domínio de medicamentos.

## Uso de minutos

A configuração evita matriz de versões e múltiplos jobs.

O cache de dependências, os filtros de caminho e o cancelamento por concorrência reduzem execuções e tempo consumido.
