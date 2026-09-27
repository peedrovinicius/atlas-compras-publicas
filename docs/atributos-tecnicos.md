# Atributos técnicos por categoria

## Objetivo

Refinar a comparabilidade entre produtos que pertencem à mesma categoria, mas possuem características técnicas diferentes.

A extração de atributos é paralela à classificação de categoria. A v1.12.0 não altera as regras de categoria nem corrige os erros conhecidos do holdout v5.

## Atributos atuais

### Resina composta e resina flow

- tecnologia: `bulk_fill`, `nanohybrid`, `microhybrid`;
- modo de cura, quando explícito.

A tecnologia da resina participa diretamente da decisão do Product Identity Engine.

### Adesivo dental

- estratégia: `universal`, `self_etch`, `etch_and_rinse`;
- modo de cura.

### Ionômero de vidro

- uso: `restorative`, `luting`, `liner_base`;
- modo de cura.

### Flúor em gel

- formulação: `neutral` ou `acidulated`.

### Anestésico local

- princípio ativo: `lidocaine`, `articaine`, `mepivacaine`, `prilocaine`;
- vasoconstritor: `epinephrine`, `felypressin`, `norepinephrine`, `phenylephrine` ou `none` quando a ausência é explícita.

O princípio ativo é obrigatório para que dois anestésicos possam chegar a `match`.

## Regras de comparabilidade

Os atributos não acrescentam pontos ao score de identidade.

Quando um atributo configurado aparece nos dois itens:

- valores iguais adicionam evidência de suporte;
- valores diferentes tornam os itens `incompatible`.

Quando o atributo aparece em apenas um lado, a decisão passa para `review`.

Para atributos obrigatórios, a ausência nos dois lados também força `review`.

## Camadas analíticas

`silver_items` e `silver_awards` preservam:

- contagem de atributos identificados;
- tecnologia de resina;
- modo de cura;
- estratégia adesiva;
- uso do ionômero;
- formulação do flúor;
- princípio ativo anestésico;
- vasoconstritor anestésico.

A chave dos grupos de preço inclui esses atributos. Assim, diferenças técnicas explícitas não são misturadas no mesmo grupo estatístico.

Anestésicos sem princípio ativo explícito são excluídos da camada de sinais.

## Holdout v5

O v5 permanece congelado e sem tuning.

Descrições que eram erros de categoria no holdout continuam erros nesta versão. A nova camada apenas extrai atributos quando a categoria já foi reconhecida pelas regras existentes.

## Limitações

A camada ainda não modela de forma completa:

- fabricante e linha comercial;
- composição detalhada;
- viscosidade além das classes já representadas;
- indicação clínica completa;
- tempo de presa;
- resistência mecânica;
- validade e condições logísticas.

Esses fatores continuam sendo motivos possíveis para variação legítima de preço.


## Validação independente

O benchmark `technical-attributes-v1` foi congelado antes da primeira medição e usa fontes separadas dos benchmarks de taxonomia v1 a v5.

Baseline:

- 33 exemplos;
- 61 campos técnicos avaliados;
- 52 campos corretos;
- micro accuracy de 85,25%;
- 9 falsos negativos;
- nenhum falso positivo;
- nenhum mismatch.

O relatório completo está em `docs/benchmark-technical-attributes-v1.md`.


## Resultado pós-tuning v1.14

As nove lacunas observadas na baseline independente foram corrigidas sem alterar o arquivo de baseline.

No mesmo conjunto congelado:

- 61 campos avaliados;
- 61 campos corretos;
- 100% de micro accuracy;
- nenhum falso positivo;
- nenhum falso negativo;
- nenhum mismatch.

Esse resultado é regressão pós-tuning e não substitui a baseline independente de 85,25%.

Detalhes: `docs/benchmark-technical-attributes-v1-post-tuning.md`.


## Benchmark técnico v2

Após o tuning do v1, um segundo conjunto independente foi congelado com novas fontes.

Resultado inicial:

- 41 exemplos;
- 77 campos técnicos avaliados;
- 72 campos corretos;
- micro accuracy de 93,51%;
- 5 falsos negativos;
- nenhum falso positivo;
- nenhum mismatch.

As cinco lacunas ainda não foram usadas para tuning nesta versão.

Detalhes: `docs/benchmark-technical-attributes-v2.md`.


## Resultado pós-tuning v1.16

As cinco lacunas observadas no benchmark técnico v2 foram corrigidas sem alterar a baseline independente.

No mesmo conjunto congelado:

- 77 campos avaliados;
- 77 campos corretos;
- 100% de micro accuracy;
- nenhum falso positivo;
- nenhum falso negativo;
- nenhum mismatch.

A referência independente continua sendo 93,51%.

Detalhes: `docs/benchmark-technical-attributes-v2-post-tuning.md`.


## Benchmark técnico v3

Um terceiro conjunto independente foi congelado após o tuning do v2.

Resultado inicial:

- 45 exemplos;
- 86 campos técnicos avaliados;
- 81 campos corretos;
- micro accuracy de 94,19%;
- 42/45 categorias corretas;
- 5 falsos negativos técnicos;
- nenhum falso positivo;
- nenhum mismatch.

As lacunas do v3 ainda não foram usadas para tuning nesta versão.

Detalhes: `docs/benchmark-technical-attributes-v3.md`.
