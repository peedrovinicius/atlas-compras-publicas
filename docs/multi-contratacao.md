# Dataset multi-contratação

## Objetivo

Permitir análise geográfica e temporal sobre várias contratações do PNCP sem duplicar resultados e sem apagar contratações já incorporadas.

## Identidade da contratação

Cada contratação recebe uma chave estável:

~~~text
pncp:<cnpj>:<ano>:<sequencial>
~~~

A chave usa apenas a identidade do registro no PNCP. Descrição, órgão exibido, fornecedor e valores não participam dessa identidade.

## Identidade da homologação

Quando o PNCP fornece `sequencialResultado`, a chave segue:

~~~text
<procurement_key>:item:<numero_item>:result:<sequencial_resultado>
~~~

Quando esse campo não existe, o sistema usa SHA-256 sobre uma representação canônica dos campos estáveis do resultado. Valores decimais equivalentes são normalizados antes do hash.

## Manifesto por contratação

`capture-contract` preserva as respostas brutas como objetos imutáveis e grava um manifesto estável em:

~~~text
data/raw/contracts/<cnpj>/<ano>/<sequencial>.json
~~~

O manifesto aponta para:

- metadados da contratação;
- itens;
- resultados de cada item;
- SHA-256 de cada evidência;
- instante da captura.

Uma nova captura da mesma contratação atualiza o manifesto de referência, mas não altera os objetos brutos já armazenados.

## Reconstrução consolidada

O comando:

~~~bash
dpi build-award-dataset --bundles-root data/raw/contracts
~~~

executa uma reconstrução completa e determinística:

1. descobre os manifestos disponíveis;
2. seleciona a captura mais recente para cada `procurement_key`;
3. verifica o SHA-256 das evidências;
4. reconstrói as linhas de homologação;
5. deduplica por `award_key`;
6. publica Parquet e `silver_awards` no DuckDB.

## Garantias

O desenho busca garantir:

- duas contratações diferentes coexistem no mesmo dataset;
- repetir o mesmo manifesto não cria linhas extras;
- atualizar uma contratação não remove as demais quando o rebuild usa o diretório consolidado;
- a mesma identidade PNCP produz a mesma chave;
- a proveniência continua rastreável até os objetos brutos.

O comando legado `build-awards` permanece disponível para construção isolada de uma contratação. O fluxo consolidado recomendado para análises multi-contratação é `build-award-dataset`.
