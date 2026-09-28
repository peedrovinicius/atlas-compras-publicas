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
| Integridade dos holdouts v1-v4 | protegida por SHA |
| Consolidação técnica v1-v12 | criada |
| Links locais do README | 27 de 27 válidos |
| Branch `release/v1.49.0` | sincronizada com a `main` auditada |
| Reexecução do CI | mesma falha antes dos steps |
| Guia local de qualidade | alinhado ao CI |
| LICENSE | ausente, decisão do mantenedor |
| SECURITY.md | ausente, melhoria futura |

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

### 7. Check-run possui annotations inacessíveis pelo conector

A consulta direta ao check-run do GitHub Actions confirmou que o job `quality` registrou duas annotations.

O endpoint das annotations não é exposto pelo conector usado nesta auditoria. Portanto, a existência das duas annotations foi confirmada, mas o conteúdo delas não pôde ser lido de forma segura por esta integração.

No mesmo commit também existe uma check suite separada do Render. Ela não deve ser confundida com o check-run `quality` do GitHub Actions.

### 8. Integridade dos holdouts de medicamentos ampliada

O teste `tests/test_release_integrity.py` protegia por Git blob SHA apenas o dataset e a baseline de medicamentos v1.

A auditoria ampliou a trava para incluir:

- `medications-v2.jsonl`;
- `medications-v2-baseline.json`;
- `medications-v3.jsonl`;
- `medications-v3-baseline.json`;
- `medications-v4.jsonl`;
- `medications-v4-baseline.json`.

Assim, alterações acidentais nos quatro holdouts independentes passam a ser detectáveis pela suíte de integridade.

### 9. Consolidação técnica atualizada para v1-v12

O README já apresentava o snapshot técnico com v1-v12, mas apontava para a consolidação v1-v11.

Foi criado:

- `docs/benchmark-technical-consolidated-v1-v12.md`

O novo consolidado registra:

- 548 exemplos;
- 984 campos técnicos;
- 899 campos corretos;
- 91,36% de micro accuracy ponderada;
- 485 categorias corretas em 548 exemplos;
- 88,50% de acurácia de categoria combinada.

A consolidação v1-v11 foi preservada como corte histórico.

### 10. Links locais do README validados

Foram verificados os 27 destinos locais referenciados pelo README, incluindo documentos, snapshot HTML, snapshot JSON e SVG.

Resultado: 27 de 27 destinos existem no repositório.

### 11. Branch de release sincronizada

A branch `release/v1.49.0` estava 20 commits atrás da `main` durante a auditoria.

Ela foi atualizada por fast-forward para o estado auditado da `main`.

### 12. Falha do CI reproduzida em nova tentativa

O job mais recente foi reexecutado para descartar falha transitória.

Resultado da nova tentativa:

| Campo | Valor |
| --- | --- |
| Run | `36412652497` |
| Job | `quality` |
| Status | completed |
| Conclusão | failure |
| Duração aproximada | 3 segundos |
| Steps | nenhum |
| Annotations | 2 |

O padrão é o mesmo da execução anterior. A falha ocorre antes de qualquer step do workflow e não fornece evidência de erro em `ruff`, `pytest` ou código do projeto.

### 13. CONTRIBUTING alinhado ao CI

O guia local usava:

`ruff check src tests`

O CI oficial usa:

`ruff check .`

A auditoria alinhou o `CONTRIBUTING.md` ao comando real do workflow para evitar diferença entre validação local e CI.

### 14. Arquivos de governança pública

`LICENSE` e `SECURITY.md` não existem atualmente.

Nenhuma licença foi escolhida automaticamente nesta auditoria, pois essa decisão pertence ao mantenedor do projeto. `SECURITY.md` fica registrado como melhoria futura caso o repositório passe a receber contribuições externas ou seja tornado público.

### 15. Auditoria textual inicial concluída

A revisão textual inicial não encontrou motivo para ampliar o README. A decisão editorial é manter a página principal enxuta e deixar o histórico técnico nos documentos especializados.

Pontos mantidos:

- linguagem técnica e direta;
- sem simular painel de preços ou homologações;
- sem substituir baseline por pós-tuning;
- sem inserir promessa de estabilidade plena do domínio de medicamentos;
- sem aumentar a lista de documentos na página principal.

### 16. Release notes sincronizadas

`docs/release-v1.49.0.md` foi sincronizado com a auditoria para registrar:

- revisão editorial do README;
- ampliação do workflow de CI;
- limitação real do Actions sem logs úteis;
- status da auditoria textual inicial.

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
- [x] Confirmar annotations no check-run.
- [x] Ampliar proteção SHA dos holdouts de medicamentos v1-v4.
- [x] Criar consolidação técnica v1-v12.
- [x] Validar os 27 links locais do README.
- [x] Sincronizar a branch `release/v1.49.0` com a `main` auditada.
- [x] Reexecutar o CI para descartar falha transitória.
- [x] Confirmar que a reexecução falha antes dos steps.
- [x] Alinhar o comando Ruff do CONTRIBUTING com o CI.
- [x] Verificar presença de LICENSE e SECURITY.md.
- [ ] Conferir Actions manualmente na interface.
- [ ] Rodar suíte local ou em ambiente conectado.
- [x] Conferir existência dos links locais do README.
- [ ] Conferir a renderização visual dos links no GitHub.
- [ ] Conferir visual do snapshot SVG no GitHub renderizado.

## Próxima etapa da auditoria

A próxima etapa depende de ambiente de execução ou interface visual:

1. abrir a aba Actions e ler a causa da falha do run `36411056152`;
2. executar localmente `ruff check .` e `pytest -q`;
3. conferir visualmente README e snapshot renderizados no GitHub.
