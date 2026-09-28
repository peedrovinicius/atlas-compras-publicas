# Release v1.54.0

A v1.54.0 reduz ainda mais o esforço necessário para encontrar um produto no Explorador de preços.

## Autocomplete

A partir de dois caracteres, o campo de pesquisa consulta produtos reais da base e mostra até seis sugestões.

As sugestões:

- respeitam os filtros já selecionados;
- priorizam produtos com maior cobertura de preços comparáveis;
- exibem nome amigável, descrição pública de exemplo e quantidade de preços;
- podem ser selecionadas diretamente para abrir a análise.

A consulta usa debounce de 250 ms para evitar chamadas desnecessárias enquanto o usuário digita.

## Pequenos erros de digitação

O resolvedor de categorias agora aceita pequenas diferenças de escrita em nomes conhecidos.

Exemplo:

~~~text
ionomero de vidor A2
~~~

é interpretado como `Ionômero de vidro`, mantendo `A2` como termo residual de refinamento.

A aproximação não é aplicada livremente sobre qualquer descrição. Ela é limitada ao vocabulário conhecido de categorias e exige similaridade alta, reduzindo o risco de classificar um produto incorretamente.

Quando uma expressão curta exata e uma expressão mais longa aproximada competem, o Atlas prefere a expressão mais específica quando a similaridade é suficiente.

## Segurança da busca

Termos não relacionados continuam sem categoria inferida. Por exemplo, uma consulta como `escova dental` permanece como busca textual normal.

Buscas genéricas como `resina` também continuam amplas.

## Validação

A release inclui testes para:

- aliases com e sem acento;
- pequenos erros de digitação;
- preservação de termos residuais;
- manutenção de buscas genéricas;
- rejeição de inferência em termos não relacionados.

O gate permanece:

~~~text
ruff check .
pytest -q
npm run build
~~~
