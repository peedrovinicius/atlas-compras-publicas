# Release v1.70.0

A v1.70.0 transforma a mediana isolada em uma referência de preço mais informativa no Explorador.

## Faixa de preço de referência

A busca de produtos passa a retornar, para cada grupo comparável:

- preço mínimo observado;
- percentil 25 (P25);
- mediana;
- percentil 75 (P75);
- preço máximo observado.

As cinco estatísticas usam o mesmo recorte metodológico já adotado pelo Atlas: apenas preços com normalização `defensible`, valor por unidade base disponível e valor positivo.

## Explorador

Cada resultado passa a exibir a faixa central P25–P75 logo abaixo da mediana quando existe amostra de preço.

Isso permite distinguir rapidamente o valor central da dispersão observada sem abrir a análise detalhada.

## Comparação lado a lado

O comparador passa a mostrar duas novas linhas:

- faixa central (P25–P75);
- faixa observada (mínimo–máximo).

A restrição existente continua válida: produtos só podem ser comparados quando pertencem à mesma categoria e usam a mesma unidade normalizada.

## Contrato de dados

O tipo `ProductSearchItem` do frontend foi expandido para incluir `min_price`, `percentile_25`, `percentile_75` e `max_price`.

O endpoint de busca continua compatível com os campos anteriores e apenas acrescenta as novas estatísticas.

## Validação

Foi adicionada regressão específica para conferir mínimo, P25, mediana, P75 e máximo sobre uma amostra determinística.
