# Benchmark independente de medicamentos v3

## Objetivo

Medir a generalização do parser de medicamentos da v1.46 em um novo conjunto congelado antes da primeira medição.

## Conjunto

- 48 exemplos;
- 8 contratações PNCP inéditas em relação aos benchmarks anteriores;
- 192 campos avaliados;
- 4 campos por exemplo: princípio ativo, concentração, forma farmacêutica e via;
- descrições preservadas como excertos fiéis da fonte;
- dataset congelado no commit `036449c2c83588551e51dbc44567364aa4e74e26`.

## Resultado independente

| Campo | Corretos | Total | Acurácia |
| --- | ---: | ---: | ---: |
| Princípio ativo | 35 | 48 | 72,92% |
| Concentração | 47 | 48 | 97,92% |
| Forma farmacêutica | 46 | 48 | 95,83% |
| Via | 45 | 48 | 93,75% |
| **Micro total** | **173** | **192** | **90,10%** |

Erros agregados:

- falsos positivos: 0;
- falsos negativos: 5;
- mismatches: 14;
- divergências totais: 19.

## Leitura

O v3 melhora substancialmente sobre a baseline independente v2 de 79,69%, mas ainda não justifica promoção do domínio.

A principal fragilidade continua na normalização do princípio ativo, especialmente em:

- campos estruturados como `princípio ativo: sal ...`;
- associações descritas por `associada com`;
- vírgulas entre fármaco e sal;
- abreviações de forma misturadas ao nome;
- descrições com alternativas e repetição do produto.

Forma farmacêutica, via e concentração generalizaram melhor, todas acima de 93%.

Nenhuma regra foi ajustada usando o v3 nesta release. O domínio permanece em `benchmark_required`.
