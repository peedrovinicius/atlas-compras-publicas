# Benchmark independente v3

## Objetivo

O v3 mede a generalização da taxonomia após as correções orientadas pelo v2.

O dataset foi congelado antes da avaliação e não foi alterado para favorecer o resultado.

## Fontes

A amostra usa cinco fontes novas de 2026:

1. Crisólita/MG, PNCP `01614283000124-1-000014/2026`;
2. Serra/ES, PNCP `27174093000127-1-000260/2026`;
3. São Luís/MA, Pregão Eletrônico `90057/2026`;
4. Itaipulândia/PR, PNCP `95725057000164-1-000297/2026`;
5. Pojuca/BA, PNCP `13806237000106-1-000153/2026`.

## Resultado

| Métrica | Resultado |
| --- | ---: |
| Amostras | 42 |
| Categorias corretas | 38 |
| Erros | 4 |
| Acurácia | 90,48% |
| Macro precision | 0,6598 |
| Macro recall | 0,6931 |
| Macro F1 | 0,6731 |
| Cor | 1/1 |
| Concentração | 6/6 |

## Correção do avaliador

Antes da publicação desta baseline foi identificada uma falha no cálculo macro.

A implementação anterior criava a lista de classes apenas a partir dos rótulos esperados. Se o classificador produzisse uma categoria que não existia entre os rótulos da amostra, essa categoria prevista indevidamente não entrava no macro precision, recall ou F1.

A v1.3.0 passa a usar a união entre:

- categorias esperadas;
- categorias previstas.

Assim, falsos positivos em classes sem suporte também são contabilizados.

Essa correção altera somente o avaliador. A taxonomia permaneceu congelada durante a medição do v3.

## Quatro erros encontrados

### Óxido de zinco

`OXIDO ZINCO` foi previsto como `unknown`.

A regra atual exige a forma `OXIDO DE ZINCO`.

### Fixador radiológico

`FIXADOR RADIOLOGICO` foi previsto como `unknown`.

A taxonomia cobre `FIXADOR RADIOGRAFICO`, mas ainda não a variante observada.

### Negação de eugenol

`CIMENTO ODONTOLOGICO ENDODONTICO SEM EUGENOL` foi previsto como `eugenol`.

O caso prova que ocorrência lexical positiva não é suficiente quando existe uma negação explícita.

### Kit misto

`KIT 3 RESINAS MAIS ADESIVO UNIVERSAL` foi previsto como `dental_adhesive`.

O registro representa um conjunto misto e não deve ser reduzido automaticamente a um único produto canônico.

## Interpretação

O salto entre a baseline independente do v2 e a baseline independente do v3 sugere melhora de generalização, mas as amostras têm composição diferente e não devem ser tratadas como experimento controlado equivalente.

O valor principal do v3 é revelar novas classes de erro que não estavam presentes no conjunto usado para o tuning anterior.

## Próximo passo

As quatro falhas podem orientar a próxima versão sem modificar os rótulos do v3.

Depois disso, um v4 com fontes novas deve ser congelado antes de qualquer nova adaptação.
