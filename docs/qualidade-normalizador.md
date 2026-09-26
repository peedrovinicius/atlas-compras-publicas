# Qualidade do normalizador

## Objetivo

A camada de qualidade mede o quanto o pipeline consegue estruturar as descrições de compras públicas odontológicas.

Ela não estima uma probabilidade subjetiva de acerto.

Todas as métricas são derivadas de evidências observáveis no próprio registro.

## Score por item

O score utiliza três componentes gerais:

- categoria: peso 0,45;
- apresentação: peso 0,20;
- medida física: peso 0,25.

Para categorias sem atributo técnico crítico adicional, o score é normalizado sobre 0,90.

Quando a categoria exige um atributo crítico, acrescenta-se peso 0,10 e o denominador passa a 1,00.

## Atributos críticos atuais

### Cor

Aplicável a:

- resina composta;
- resina flow;
- ionômero de vidro.

### Concentração

Aplicável a:

- ácido fosfórico;
- flúor em gel;
- anestésico local.

## Estrutura completa

Um item é `fully_structured` quando possui:

- categoria;
- apresentação;
- medida física;
- atributo crítico, quando aplicável.

Quantidade por embalagem não é obrigatória para o score semântico, pois a ausência pode representar legitimamente uma unidade simples.

Essa ausência, porém, é tratada separadamente na normalização de preço físico. Quando a unidade de compra indica uma embalagem, como `CAIXA`, e a descrição não informa quantas unidades existem dentro dela, o preço por g/ml não é calculado automaticamente.

## Níveis

### High

Score igual ou superior a 0,80 e estrutura mínima completa.

### Medium

Score igual ou superior a 0,55, mas com alguma lacuna relevante.

Um item com score numérico alto e atributo crítico ausente permanece em `medium`.

### Low

Score inferior a 0,55.

## Métricas agregadas

A visão `normalization_quality_summary` apresenta:

- total de itens;
- cobertura de categoria;
- cobertura de apresentação;
- cobertura de medida;
- proporção totalmente estruturada;
- proporção com preço fisicamente normalizável;
- quantidade com base física `defensible`;
- quantidade em `review`;
- quantidade `unavailable`;
- score médio.

A visão `normalization_quality_by_category` apresenta a mesma lógica segmentada por categoria.

## Fila de lacunas

A visão `unrecognized_items` contém itens ainda classificados como `unknown`.

A fila preserva:

- número do item;
- descrição original;
- unidade informada;
- valor unitário estimado;
- score;
- campos ausentes;
- SHA-256 da fonte.

O objetivo é usar essa fila para orientar novas regras e medir se uma mudança de taxonomia realmente melhora a cobertura.

## Interpretação

Cobertura alta não significa necessariamente precisão alta.

Uma regra excessivamente ampla poderia elevar cobertura e simultaneamente piorar a qualidade das classificações.

Por isso, a evolução futura deverá medir separadamente:

1. cobertura;
2. precisão em amostra revisada manualmente;
3. conflitos entre regras;
4. estabilidade entre versões;
5. distribuição de itens em `review`.

## Status da validação

A taxonomia possui benchmarks manuais versionados e um holdout independente v5 preservado sem tuning. A confiança da base física de preço é medida separadamente da acurácia de categoria.
