# Release v1.73.0

A v1.73.0 adiciona uma leitura objetiva da tendência recente observada no histórico de preços.

## Tendência recente

Na seção `Histórico de preços`, o Atlas passa a destacar os dois períodos mais recentes com mediana disponível.

A interface mostra:

- mediana do último período;
- quantidade de observações do último período;
- mediana do período anterior;
- quantidade de observações do período anterior;
- diferença absoluta entre as medianas;
- diferença percentual entre as medianas.

## Interpretação

A comparação é estritamente histórica.

Ela não produz previsão de preço futuro, recomendação de compra ou conclusão sobre adequação do valor.

Quando existe apenas um período com mediana disponível, o Atlas mostra o último período, mas não calcula variação.

## Relatório

O relatório imprimível/PDF passa a incluir uma seção `Tendência recente observada` quando existem pelo menos dois períodos comparáveis.

Essa seção registra os dois períodos, as medianas, a diferença absoluta e a variação percentual.

## Implementação

A v1.73.0 reutiliza a série mensal já exposta pela API.

Nenhum endpoint novo é necessário e nenhuma metodologia de agrupamento ou normalização de preços é alterada.
