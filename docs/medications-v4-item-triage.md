# Triagem de itens para medicamentos v4

## Finalidade

Registrar a seleção item a item usada no holdout independente de medicamentos v4.

A triagem foi concluída e resultou no arquivo congelado `data/evaluation/medications-v4.jsonl`.

## Regras aplicadas

- O parser não foi alterado durante a triagem.
- O JSONL só foi criado após selecionar 48 exemplos.
- Itens sem descrição verificável foram recusados.
- Campos esperados não foram preenchidos por inferência fraca.
- A prioridade foi manter descrições fiéis à fonte pública.

## Decisão metodológica

O plano inicial previa 8 contratações com 6 itens por contratação. Durante a triagem, a distribuição foi ajustada para usar apenas descrições item a item verificáveis nas fontes públicas abertas.

Distribuição final:

| Fonte | Controle PNCP | Exemplos |
| --- | --- | ---: |
| Curitiba/PR PE 93/2026 | `14814139000183-1-000142/2026` | 30 |
| Brasília/DF PE 90018/2026 | `00394411000109-1-000150/2026` | 9 |
| Curitiba/PR PE 74/2026 | `14814139000183-1-000149/2026` | 2 |
| São Paulo/SP PE 33/2026 | `46374500000194-1-007596/2026` | 1 |
| Curitiba/PR PE 1270/2026 | `24039073000155-1-001089/2026` | 1 |
| Santos/SP PE 21/2026 | `46374500000194-1-006714/2026` | 2 |
| Curitiba/PR PE 87/2026 | `14814139000183-1-000136/2026` | 2 |
| Curitiba/PR PE 84/2026 | `14814139000183-1-000132/2026` | 1 |

## Contagem final

| Situação | Quantidade |
| --- | ---: |
| Exemplos selecionados | 48 |
| Campos por exemplo | 4 |
| Campos esperados revisados | 192 |
| Fontes públicas usadas | 8 |
| Dataset congelado | sim |

## Resultado

O dataset foi congelado em:

- `data/evaluation/medications-v4.jsonl`

O documento de congelamento está em:

- `docs/medications-v4-freeze.md`

## Próxima ação

Executar o benchmark independente do parser vigente contra o dataset congelado e registrar `data/evaluation/medications-v4-baseline.json`.
