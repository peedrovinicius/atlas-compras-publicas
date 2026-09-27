# Benchmark independente de atributos técnicos v5

## Objetivo

Medir a generalização das regras técnicas depois da introdução de contexto negativo na v1.20.

O dataset foi congelado antes da primeira medição.

## Amostra

- 48 descrições públicas;
- 8 contratações inéditas;
- 92 campos técnicos revisados manualmente;
- negativos contextuais;
- grafias não padronizadas;
- abreviações comerciais;
- alternativas técnicas explícitas;
- nenhuma fonte reutilizada dos benchmarks técnicos v1 a v4.

## Resultado independente

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 48 |
| Categorias corretas | 39/48 |
| Acurácia de categoria | 81,25% |
| Campos técnicos avaliados | 92 |
| Campos técnicos corretos | 80 |
| Micro accuracy | 86,96% |
| Falsos positivos | 2 |
| Falsos negativos | 10 |
| Mismatches | 0 |

## Resultado por atributo

| Atributo | Avaliados | Corretos | Acurácia |
| --- | ---: | ---: | ---: |
| Tecnologia de resina | 18 | 15 | 83,33% |
| Modo de cura | 34 | 27 | 79,41% |
| Estratégia adesiva | 9 | 9 | 100,00% |
| Uso do ionômero | 7 | 7 | 100,00% |
| Formulação do flúor | 4 | 2 | 50,00% |
| Princípio ativo anestésico | 10 | 10 | 100,00% |
| Vasoconstritor anestésico | 10 | 10 | 100,00% |

## Principais falhas

### Contexto de produto

Dois erros mostram que a classificação ainda pode seguir uma palavra subordinada em vez do produto principal:

- `DISPENSA O USO DE ADESIVO` levou um ionômero a ser classificado como adesivo;
- um selante `COMPOSTO POR RESINA FOTOPOLIMERIZÁVEL` foi classificado como resina composta.

`APLICADOR DE ADESIVO` também foi classificado como adesivo, embora o produto seja um aplicador.

### Alternativas explícitas

Em `MICRO-HIBRIDA OU NANO-HIBRIDA`, o parser escolheu `nanohybrid`.

A descrição não define uma tecnologia única, portanto o rótulo correto para `resin_technology` é `null`.

### Grafias não padronizadas

Ainda não são reconhecidas:

- `FOTOPOLIMERIZALVEL`;
- `FOTOPOLIMERIXAVE`;
- `MICROHIDRIDA`.

### Formas de categoria ainda não cobertas

Ficaram como `unknown`:

- `RESINA ODONTOLÓGICA`;
- `RESINA FORMA NANOHIBRIDA`;
- `FLUOR NEUTRO`;
- `FLUOR ACIDULADO`;
- `RESINA FOTO`.

### Abreviação de cura

`RESINA FOTO` e `RESINA FOTO ... FLOW` não geraram `light_cure`.

## Interpretação

O v5 é mais adversarial que os conjuntos anteriores e combina erros de vocabulário com erros de relação contextual.

A queda para 86,96% não invalida os ciclos anteriores. Ela mostra que o ganho obtido no v4 ainda não generaliza completamente para descrições com:

- produto principal e produto citado na mesma frase;
- negação sem a palavra `sem`;
- alternativas ligadas por `ou`;
- nomes abreviados;
- erros de digitação.

Esta baseline deve permanecer imutável. Qualquer correção posterior precisa ser registrada como resultado pós-tuning separado.

O holdout v5 da taxonomia permanece separado e não foi alterado.
