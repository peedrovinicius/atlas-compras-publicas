# Release v1.49.0

## Resumo

A release v1.49.0 fecha o ciclo de medicamentos v4 com baseline independente, pós-tuning pontual, snapshot atualizado, documentação consolidada e auditoria inicial registrada.

## Entregas principais

- Holdout independente `medications-v4.jsonl` congelado com 48 exemplos e 192 campos.
- Baseline independente v4 preservada com 189/192 campos corretos e 98,44% de micro accuracy.
- Pós-tuning v1.49 registrado separadamente com 192/192 campos corretos.
- Correção pontual do parser para dois padrões residuais:
  - `geléia` como forma farmacêutica tópica;
  - prefixos numéricos compostos antes do princípio ativo.
- Snapshot de qualidade atualizado para medicamentos v1-v4.
- Testes de baseline, pós-tuning e snapshot atualizados.
- README alinhado com a consolidação de medicamentos v1-v4 e com o pós-tuning v1.49.
- Revisão editorial do README atualizada em `docs/readme-review-v1.49.0.md`.
- Workflow de CI ampliado para cobrir README e snapshot visual.
- Auditoria inicial registrada em `docs/audit-v1.49.0.md`.

## Arquivos novos

- `data/evaluation/medications-v4-post-v1.49.json`
- `docs/benchmark-medications-v4-post-tuning.md`
- `docs/release-v1.49.0.md`
- `docs/audit-v1.49.0.md`

## Arquivos atualizados

- `.github/workflows/ci.yml`
- `README.md`
- `src/dental_procurement_intelligence/identity/medications.py`
- `tests/test_medication_evaluation.py`
- `tests/test_release_integrity.py`
- `docs/dashboard-quality-snapshot.json`
- `docs/dashboard-quality-snapshot.html`
- `docs/assets/dashboard-quality-snapshot.svg`
- `docs/benchmark-medications-consolidated-v1-v4.md`
- `docs/readme-review-v1.49.0.md`
- `pyproject.toml`
- `src/dental_procurement_intelligence/__init__.py`
- `src/dental_procurement_intelligence/pncp/client.py`

## Métricas preservadas

| Marco | Campos corretos | Micro accuracy | Observação |
| --- | ---: | ---: | --- |
| Baseline independente v4 | 189/192 | 98,44% | preservada |
| Pós-tuning v1.49 | 192/192 | 100,00% | regressão separada |
| Consolidado independente v1-v4 | 683/768 | 88,93% | snapshot |

## Decisão metodológica

A baseline independente não foi substituída pelo resultado pós-tuning. O domínio de medicamentos permanece em `benchmark_required` na documentação consolidada porque a promoção de domínio deve considerar estabilidade histórica e não apenas regressões perfeitas.

## Validação esperada

A suíte deve validar:

- consistência de versão entre `pyproject.toml`, `__version__` e `User-Agent`;
- integridade dos artefatos congelados antigos;
- snapshot técnico e de medicamentos v1-v4;
- baseline independente v4 preservada;
- regressão pós-tuning v4 com 192/192 campos corretos.

## Estado do CI

A auditoria disparou um novo run do GitHub Actions depois de ampliar os paths do workflow. O run falhou antes de retornar steps ou logs úteis pela API.

Portanto, esta release fica tecnicamente documentada e preparada, mas o CI ainda precisa de uma das verificações abaixo:

- conferência visual na aba Actions do GitHub;
- execução local de `ruff check .` e `pytest -q`;
- nova execução do Actions quando o runner estiver disponível.
