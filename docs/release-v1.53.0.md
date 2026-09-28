# Release v1.53.0

A v1.53.0 reduz o principal atrito de uso do Explorador de preços: o usuário não precisa mais conhecer a forma exata como um produto aparece no PNCP.

## Descoberta por categoria

O Explorador consulta `/api/v1/products/discovery` e mostra somente categorias realmente presentes na base publicada.

Cada atalho apresenta:

- nome amigável da categoria;
- quantidade de grupos comparáveis;
- quantidade de observações com preço defensável.

Ao clicar, a pesquisa é executada imediatamente.

## Busca com linguagem mais natural

A camada de busca passou a resolver nomes comuns para a taxonomia interna.

Exemplos:

~~~text
adesivo odontológico -> dental_adhesive
ionômero de vidro -> glass_ionomer
resina flow -> flowable_resin
anestésico local -> local_anesthetic
flúor -> fluoride_gel
~~~

A normalização dos aliases ignora acentos e diferenças de caixa.

Termos adicionais continuam refinando a consulta. Por exemplo, `resina composta A2` resolve a categoria e mantém `A2` como restrição textual.

Buscas genéricas permanecem abrangentes. `resina`, isoladamente, não é convertida para uma única categoria.

## Interface

O campo de pesquisa ganhou uma área `Encontre por categoria`.

Quando o usuário começa a digitar e existe uma categoria compatível, a interface troca para `Talvez você esteja procurando` e prioriza os atalhos relacionados.

Após a busca, o Atlas informa quando interpretou a consulta como uma categoria conhecida.

## Validação

A release inclui testes para:

- aliases com acentos;
- busca por `flúor` mesmo quando a descrição pública não contém a mesma palavra;
- resolução de `adesivo odontológico`;
- exclusão de `unknown` da descoberta;
- contagem das categorias realmente disponíveis.

O gate permanece:

~~~text
ruff check .
pytest -q
npm run build
~~~
