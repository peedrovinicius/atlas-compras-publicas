# Release v1.52.0

A v1.52.0 melhora a exploração pública do Atlas sem alterar a metodologia de comparação de preços.

## Ordenação

A pesquisa pode ser ordenada por:

- maior cobertura de preços comparáveis;
- maior número de compras;
- atualização mais recente;
- nome do produto.

A ordenação acontece na API antes da paginação.

## Exportação CSV

A análise selecionada pode exportar os registros filtrados em CSV.

A rota `/api/v1/products/{product_id}/records.csv` percorre internamente todas as páginas do recorte, preserva os mesmos filtros da tela e entrega UTF-8 com BOM.

O arquivo inclui contexto da compra, fornecedor, órgão comprador, valores, status da normalização, hashes de origem e link para o PNCP.

## Análises compartilháveis

Pesquisa, filtros, ordenação, página e produto selecionado passam a ser representados na URL.

O botão `Copiar link` permite compartilhar um recorte específico. Ao abrir o endereço, o frontend reconstrói o estado e carrega novamente a análise do produto quando `product_id` estiver presente.

## Histórico visual

O histórico mensal ganhou uma visualização SVG nativa com:

- linha da mediana;
- faixa entre os percentis 25 e 75;
- pontos mensais com valor acessível no título;
- período inicial e final.

A tabela permanece abaixo do gráfico para manter leitura detalhada e auditável.

## Validação

A release mantém o gate:

~~~text
ruff check .
pytest -q
npm run build
~~~

Também existem testes específicos para ordenação da busca, coleta de múltiplas páginas durante a exportação e resposta CSV com cabeçalho de download e BOM UTF-8.
