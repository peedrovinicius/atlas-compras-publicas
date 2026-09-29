# Release v1.74.0

A v1.74.0 melhora a leitura geográfica dos preços homologados sem alterar a metodologia de comparação.

## Contexto regional

A aba `Mercado` passa a apresentar primeiro a referência nacional do produto no recorte atual.

São exibidos:

- mediana nacional;
- quantidade de observações;
- quantidade de compras;
- número de UFs com amostra.

## Macrorregiões

Cada macrorregião passa a mostrar:

- mediana;
- diferença percentual em relação à mediana nacional;
- quantidade de observações.

A diferença é puramente descritiva. O Atlas não classifica uma região como cara, barata, adequada ou inadequada.

## Unidades da Federação

A comparação por UF passa a mostrar:

- UF;
- macrorregião;
- mediana;
- diferença para a mediana nacional;
- observações;
- compras.

As primeiras UFs continuam priorizadas por tamanho da amostra. Quando houver mais de oito, a lista completa pode ser aberta em tabela.

## Relatório

O relatório imprimível/PDF passa a incluir:

- mediana nacional;
- observações nacionais;
- UFs com amostra;
- número de macrorregiões;
- mediana e diferença percentual de cada macrorregião.

## Identidade visual

O frontend passa a usar a identidade `Atlas e Preços` no cabeçalho:

- símbolo metálico da marca;
- nome renderizado em texto HTML para preservar nitidez;
- subtítulo `Inteligência em compras públicas`;
- comportamento responsivo em desktop e mobile;
- ativo visual otimizado e incorporado ao bundle.

## Descoberta pública

O frontend também passa a publicar metadados básicos para descoberta e indexação:

- `robots.txt`;
- `sitemap.xml`;
- `site.webmanifest`;
- diretiva explícita de indexação;
- link do manifesto no HTML.

Esses arquivos são validados automaticamente pela suíte de integridade.

## Integridade da versão

A versão exibida no cabeçalho do relatório passa a ser verificada por `tests/test_release_integrity.py`.

Isso evita que o documento mostre uma versão antiga depois de uma nova release.

## Metodologia

Nenhum endpoint novo foi criado.

A v1.74.0 reutiliza o endpoint geográfico já existente e não altera identidade de produto, filtros, normalização de preço ou regras estatísticas.
