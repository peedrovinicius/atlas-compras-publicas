# Auditoria v1.49.0

## Escopo

Auditoria inicial da release v1.49.0 do Atlas de Compras Públicas.

O foco desta etapa é verificar consistência metodológica, documentação pública, separação entre baseline independente e pós-tuning, snapshot de qualidade e estado do CI.

## Estado auditado

| Item | Estado |
| --- | --- |
| Release documentada | concluído |
| Branch `release/v1.49.0` | criada |
| README alinhado com v1.49.0 | concluído |
| Medicamentos v4 baseline independente | preservada |
| Medicamentos v4 pós-tuning | documentado separadamente |
| Snapshot v1-v4 | atualizado |
| Teste de snapshot v1-v4 | atualizado |
| CI pelo conector | inconclusivo |

## Achados iniciais

### 1. Baseline independente preservada

A baseline independente do holdout `medications-v4.jsonl` foi preservada em arquivo próprio:

- `data/evaluation/medications-v4-baseline.json`

Resultado preservado:

| Métrica | Valor |
| --- | ---: |
| Exemplos | 48 |
| Campos avaliados | 192 |
| Campos corretos | 189 |
| Micro accuracy | 98,44% |
| Mismatches | 3 |

### 2. Pós-tuning separado

O pós-tuning v1.49 foi registrado em arquivo separado:

- `data/evaluation/medications-v4-post-v1.49.json`
- `docs/benchmark-medications-v4-post-tuning.md`

Resultado:

| Métrica | Valor |
| --- | ---: |
| Campos avaliados | 192 |
| Campos corretos | 192 |
| Micro accuracy | 100,00% |

A auditoria considera correta a separação entre baseline independente e regressão pós-tuning.

### 3. README corrigido

O README tinha um texto desatualizado dizendo que o v4 ainda não possuía pós-tuning. A inconsistência foi corrigida nesta auditoria.

O README agora:

- mantém a baseline independente v4;
- mostra o pós-tuning v1.49 como regressão separada;
- aponta para o documento técnico correto;
- evita expandir demais a página principal.

### 4. Snapshot atualizado

O snapshot de qualidade foi atualizado para medicamentos v1-v4:

| Grupo | Exemplos | Campos | Corretos | Micro accuracy |
| --- | ---: | ---: | ---: | ---: |
| Medicamentos v1-v4 | 192 | 768 | 683 | 88,93% |

Arquivos atualizados:

- `docs/dashboard-quality-snapshot.json`
- `docs/dashboard-quality-snapshot.html`
- `docs/assets/dashboard-quality-snapshot.svg`

### 5. CI inconclusivo pelo conector

A API do GitHub Actions retornou um run antigo com falha no commit `95209cf`, anterior aos commits finais da release.

O job falhou sem steps e sem logs úteis disponíveis pela API. Os commits posteriores feitos pelo conector não apareceram como novo workflow executado.

Interpretação da auditoria:

- não é correto declarar CI aprovado;
- não há erro técnico concreto visível para corrigir a partir dos logs;
- a verificação final deve ser feita pela aba Actions do GitHub ou por execução local de `ruff check .` e `pytest -q`.

## Checklist de auditoria iniciado

- [x] Conferir separação baseline x pós-tuning.
- [x] Conferir documentação de release.
- [x] Conferir README de alto nível.
- [x] Conferir snapshot v1-v4.
- [x] Conferir teste de snapshot v1-v4.
- [x] Registrar limitação de CI.
- [ ] Conferir Actions manualmente na interface.
- [ ] Rodar suíte local ou em ambiente conectado.
- [ ] Conferir links do README no GitHub renderizado.
- [ ] Conferir visual do snapshot SVG no GitHub renderizado.
- [ ] Revisar documentação para termos artificiais ou promocionais.
- [ ] Revisar se há excesso de arquivos técnicos no topo da documentação.

## Próxima etapa da auditoria

A próxima etapa deve focar em três frentes:

1. sanidade visual do README e do snapshot no GitHub;
2. execução real do CI ou suíte local;
3. revisão textual para manter o projeto com aparência técnica, séria e sem excesso de documentação operacional.
