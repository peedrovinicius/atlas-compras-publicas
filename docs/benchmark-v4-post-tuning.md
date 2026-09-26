# Ajustes pós-v4: v1.6.0

## Contexto

O benchmark independente v4 registrou 41 acertos em 48 itens, com acurácia de 85,42%.

Os sete erros foram mantidos intactos no dataset e usados para orientar a v1.6.0.

## Correções

### Pluralização explícita

Foram adicionadas formas públicas observadas no PNCP e em portais de compras:

- `RESINAS FLUIDAS`;
- `ADESIVOS`;
- `IONOMEROS DE VIDRO`.

A decisão continua baseada em vocabulário explícito. Não foi adicionado um stemmer genérico que pudesse produzir singularizações incorretas.

### Resina fluida por contexto distribuído

A versão anterior dependia excessivamente de expressões contíguas como `RESINA COMPOSTA FLUIDA`.

Agora o parser verifica separadamente a presença de um núcleo de resina e de um atributo de fluidez.

Assim:

`RESINA COMPOSTA TIPO BULK FILL ASPECTO FISICO FLUIDA`

passa a ser `flowable_resin`.

A regra é executada antes da classificação geral de resina composta.

### Anestésico genérico

O termo `ANESTESICO` passa a ser uma evidência explícita de `local_anesthetic`.

O sistema continua distinguindo esse termo de `ANESTESIA`, que pode aparecer em descrições de agulhas e acessórios.

### Flúor ácido em gel

A variante observada `FLUOR ACIDO GEL` passa a ser reconhecida como `fluoride_gel`.

### Componente de formulação

O caso:

`ISOLANTE ... COMPOSICAO BASICA ALGINATO DE SODIO`

deixa de ser classificado como `alginate`.

A regra exige contexto de produto isolante associado a indicação de composição ou base. Assim, a simples presença do componente químico não substitui a identidade do item comprado.

### Negação

O mecanismo de negação passa a incluir também:

`NAO <termo>`

além das formas já existentes.

## Revalidação

| Benchmark | Acertos | Total | Acurácia |
| --- | ---: | ---: | ---: |
| v1 | 37 | 37 | 100,00% |
| v2 | 48 | 48 | 100,00% |
| v3 | 42 | 42 | 100,00% |
| v4 pós-tuning | 48 | 48 | 100,00% |

Total revalidado: 175 exemplos.

## Limitação metodológica

O resultado do v4 após tuning não é uma nova validação independente.

A baseline independente anterior permanece preservada em `data/evaluation/v4-baseline.json`.

O próximo teste válido de generalização deve usar novas fontes congeladas em um benchmark v5.
