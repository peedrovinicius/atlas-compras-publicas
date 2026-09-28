# Benchmark independente de medicamentos v2

## Resultado independente

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 48 |
| Campos avaliados | 192 |
| Campos corretos | 153 |
| Micro accuracy | 79,69% |
| Falsos positivos | 0 |
| Falsos negativos | 0 |
| Mismatches | 39 |

## Resultado por campo

| Campo | Corretos | Acurácia |
| --- | ---: | ---: |
| Ingrediente ativo | 28/48 | 58,33% |
| Concentração | 47/48 | 97,92% |
| Forma farmacêutica | 39/48 | 81,25% |
| Via | 39/48 | 81,25% |

## Principais lacunas

O v2 mostrou que a concentração generaliza melhor que os demais campos.

As divergências se concentram em:

- remoção semântica de pontuação entre ingrediente e sal;
- associações em que o sinal `+` desaparece na normalização;
- segundo princípio ativo após uma primeira concentração;
- formas ainda não reconhecidas, como elixir, suspensão oral, gel vaginal, loção oleosa e abreviação `CAPS`;
- injetáveis descritos apenas por `IV/IM`;
- via tópica explícita sem uma forma já reconhecida;
- qualificadores de sal presentes em campos estruturais como `composição` ou `apresentação`;
- descrições com palavras coladas.

## Decisão metodológica

Nenhum erro do v2 é corrigido na v1.45.

A baseline independente de **79,69%** deve permanecer imutável. Qualquer tuning posterior deve ser registrado separadamente.
