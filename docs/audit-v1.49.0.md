# Auditoria v1.49.0

## Escopo

Auditoria da release v1.49.0 do Atlas de Compras Públicas.

O foco desta etapa é verificar consistência metodológica, documentação pública, separação entre baseline independente e pós-tuning, snapshot de qualidade e estado real do CI.

## Estado auditado

| Item | Estado |
| --- | --- |
| Release documentada | concluído |
| Branch `release/v1.49.0` | criada |
| README alinhado com v1.49.0 | concluído |
| Revisão do README | atualizada |
| Medicamentos v4 baseline independente | preservada |
| Medicamentos v4 pós-tuning | documentado separadamente |
| Snapshot v1-v4 | atualizado |
| Teste de snapshot v1-v4 | atualizado |
| CI | falhou sem logs úteis |
| Auditoria textual inicial | concluída |
| Release notes sincronizadas | concluído |

## Achados

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

O pós-tuning v1.49 foi registrado em arquivos separados:

- `data/evaluation/medications-v4-post-v1.49.json`
- `docs/benchmark-medications-v4-post-tuning.md`

Resultado:

| Métrica | Valor |
| --- | ---: |
| Campos avaliados | 192 |
| Campos corretos | 192 |
| Micro accuracy | 100,00% |

A auditoria considera correta a separação entre baseline independente e regressão pós-tuning.

### 3. README corrigido, reduzido e revisado

O README tinha um texto desatualizado dizendo que o v4 ainda não possuía pós-tuning. A inconsistência foi corrigida nesta auditoria.

Também foi atualizada a revisão editorial em:

- `docs/readme-review-v1.49.0.md`

O README agora:

- mantém a baseline independente v4;
- mostra o pós-tuning v1.49 como regressão separada;
- aponta para o documento técnico correto;
- reduz excesso operacional na página principal;
- usa `->` na cadeia de rastreabilidade para evitar travessões em texto público.

### 4. Snapshot atualizado

O snapshot de qualidade foi atualizado para medicamentos v1-v4:

| Grupo | Exemplos | Campos | Corretos | Micro accuracy |
| --- | ---: | ---: | ---: | ---: |
| Medicamentos v1-v4 | 192 | 768 | 683 | 88,93% |

Arquivos atualizados:

- `docs/dashboard-quality-snapshot.json`
- `docs/dashboard-quality-snapshot.html`
- `docs/assets/dashboard-quality-snapshot.svg`

### 5. CI passou a cobrir README e snapshot visual

O workflow `.github/workflows/ci.yml` foi ampliado para disparar também quando houver alteração em:

- `README.md`;
- `docs/dashboard-quality-snapshot.html`;
- `docs/assets/dashboard-quality-snapshot.svg`.

Antes, o CI cobria o JSON do snapshot, mas não cobria o HTML e o SVG do snapshot nem o README.

### 6. CI executou, mas falhou sem logs úteis

Após a correção do workflow, houve novo run do GitHub Actions:

| Campo | Valor |
| --- | --- |
| Run | `36411056152` |
| Commit | `57ac5b0d1eea06238443ec1bd00ae4b9aa760758` |
| Job | `quality` |
| Status | completed |
| Conclusão | failure |
| Steps retornados pela API | nenhum |
| Logs pela API | indisponíveis, BlobNotFound |

Interpretação da auditoria:

- não é correto declarar CI aprovado;
- a falha ocorreu sem etapas visíveis de `Install`, `Ruff` ou `Tests`;
- sem logs, não há erro concreto de código para corrigir pela API;
- o padrão é compatível com falha operacional antes da execução do runner, limite de minutos, fila, permissão, quota ou problema de infraestrutura do Actions;
- a próxima verificação precisa ser feita visualmente na aba Actions ou por execução local de `ruff check .` e `pytest -q`.

### 7. Auditoria textual inicial concluída

A revisão textual inicial não encontrou motivo para ampliar o README. A decisão editorial é manter a página principal enxuta e deixar o histórico técnico nos documentos especializados.

Pontos mantidos:

- linguagem técnica e direta;
- sem simular painel de preços ou homologações;
- sem substituir baseline por pós-tuning;
- sem inserir promessa de estabilidade plena do domínio de medicamentos;
- sem aumentar a lista de documentos na página principal.

### 8. Release notes sincronizadas

`docs/release-v1.49.0.md` foi sincronizado com a auditoria para registrar:

- revisão editorial do README;
- ampliação do workflow de CI;
- limitação real do Actions sem logs úteis;
- status da auditoria textual inicial;
- link de referência para esta auditoria final.

## Checklist de auditoria

- [x] Conferir separação baseline x pós-tuning.
- [x] Conferir documentação de release.
- [x] Conferir README de alto nível.
- [x] Corrigir README desatualizado.
- [x] Atualizar revisão editorial do README.
- [x] Conferir snapshot v1-v4.
- [x] Conferir teste de snapshot v1-v4.
- [x] Ampliar cobertura de path do CI para README e snapshot visual.
- [x] Disparar novo CI via commit no workflow.
- [x] Registrar falha do CI sem logs úteis.
- [x] Concluir auditoria textual inicial.
- [x] Sincronizar release notes.
- [ ] Conferir Actions manualmente na interface.
- [ ] Rodar suíte local ou em ambiente conectado.
- [ ] Conferir links do README no GitHub renderizado.
- [ ] Conferir visual do snapshot SVG no GitHub renderizado.

## Próxima etapa da auditoria

A próxima etapa depende de ambiente de execução ou interface visual:

1. abrir a aba Actions e ler a causa da falha do run `36411056152`;
2. executar localmente `ruff check .` e `pytest -q`;
3. conferir visualmente README e snapshot renderizados no GitHub.
