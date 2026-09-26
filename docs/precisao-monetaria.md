# Precisão monetária

## Objetivo

Evitar que preços, totais e economias sejam alterados por representação binária de ponto flutuante durante o pipeline analítico.

## Política

O Atlas utiliza:

~~~text
DECIMAL(38,12)
~~~

Isso reserva 38 dígitos de precisão total e 12 casas decimais.

Antes da persistência, valores são quantizados explicitamente com `ROUND_HALF_EVEN`.

## Campos abrangidos

Na camada de itens:

- valor unitário estimado;
- valor total;
- preço normalizado por unidade física.

Na camada de homologações:

- valor unitário estimado;
- valor unitário homologado;
- valor total homologado;
- total estimado equivalente;
- economia total;
- percentual de economia persistido;
- preços estimado e homologado por unidade física.

## O que continua em ponto flutuante

Ponto flutuante é mantido para grandezas que não representam dinheiro, como:

- quantidade de compra usada apenas como medida analítica;
- concentração;
- score de qualidade;
- modified z-score;
- parâmetros MAD e IQR derivados para detecção.

A origem financeira desses cálculos permanece decimal até a etapa estatística.

## Arredondamento

Quando uma divisão produz expansão infinita, como `0,10 / 3`, o resultado é quantizado em 12 casas:

~~~text
0.033333333333
~~~

O modo `ROUND_HALF_EVEN` torna a política explícita e reproduzível.

## Persistência

Parquet preserva o tipo decimal e DuckDB recebe as colunas financeiras como `DECIMAL(38,12)`.

O detector de sinais recusa uma `silver_awards` antiga se `awarded_price_per_base_unit` ainda estiver em `DOUBLE`. Nesse caso, o dataset deve ser reconstruído com:

~~~bash
dpi build-award-dataset --bundles-root data/raw/contracts
~~~

Essa exigência evita misturar resultados produzidos com políticas numéricas diferentes.
