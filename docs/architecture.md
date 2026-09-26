# Arquitetura

## Objetivo

O sistema deve produzir inteligência de preços sem perder a cadeia de evidências que conecta cada resultado analítico ao registro original do PNCP.

## Contrato de dados

Cada registro percorre quatro camadas lógicas.

### Raw

Conteúdo original da fonte acompanhado dos metadados de coleta. Depois de persistido, o objeto bruto é tratado como imutável.

Metadados de proveniência:

- URL de origem;
- data e hora da coleta em UTC;
- status HTTP;
- SHA-256 do conteúdo;
- versão do pipeline.

Itens e resultados homologados são capturados como evidências independentes.

### Bronze

Registros do PNCP tipados e estruturalmente validados. Nesta camada os campos são organizados, mas valores semânticos não são corrigidos ou inferidos.

### Silver

Camada de normalização de domínio. Contém:

- descrição normalizada;
- medidas extraídas;
- quantidade por embalagem;
- apresentação;
- cor;
- categoria odontológica;
- preço normalizado por unidade física;
- resultado homologado;
- fornecedor e marca quando informados;
- valor estimado equivalente;
- valor homologado;
- economia absoluta e percentual;
- referências SHA-256 das evidências de item e resultado.

Resultados com situação cancelada são excluídos das métricas de homologação por padrão.

Os datasets são persistidos em Parquet para permitir leitura eficiente, portabilidade e análise colunar.

### Gold

Somente grupos de comparação defensáveis chegam a esta camada.

A camada deverá conter:

- produtos comparáveis;
- estatísticas robustas;
- sinais de preço atípico;
- tamanho da população comparada;
- referências de evidência;
- justificativa metodológica.

## DuckDB

DuckDB funciona como catálogo analítico local sobre os datasets em Parquet.

As estruturas atuais incluem:

- `silver_items` — itens normalizados;
- `category_price_summary` — resumo de preços estimados;
- `silver_awards` — resultados homologados cruzados com os itens;
- `award_savings_summary` — resumo de estimado, homologado e economia por categoria.

A arquitetura mantém Parquet como formato de intercâmbio e DuckDB como mecanismo SQL, evitando dependência prematura de infraestrutura externa.

## Estratégia de identidade de produto

Identidade de produto é deliberadamente separada de similaridade textual.

O mecanismo deverá combinar:

1. extração determinística de unidades, quantidade por embalagem e atributos clínicos;
2. vocabulário odontológico controlado;
3. regras de compatibilidade capazes de rejeitar correspondências inválidas;
4. similaridade semântica para variações residuais de linguagem;
5. objeto de explicação com evidências favoráveis, conflitos e informações ausentes.

Uma pontuação alta de similaridade nunca poderá ignorar incompatibilidade de unidade, apresentação ou atributo clinicamente relevante.

## Preço comparável

Sempre que houver informação suficiente, o sistema calcula:

`preço do item / quantidade física total normalizada`

Exemplo:

`R$ 80,00 / 8 g = R$ 10,00/g`

Massa e volume permanecem dimensões distintas.

## Estimado x homologado

Para uma quantidade homologada `q`:

`valor estimado equivalente = valor unitário estimado × q`

`economia = valor estimado equivalente - valor total homologado`

`economia percentual = economia / valor estimado equivalente × 100`

Quando o PNCP não fornece valor total homologado, o pipeline pode reconstruí-lo a partir de valor unitário homologado e quantidade homologada.

## Rastreabilidade

Cada registro de homologação mantém:

- SHA-256 da resposta bruta que originou o item;
- SHA-256 da resposta bruta que originou o resultado.

Isso impede que o cruzamento analítico apague a proveniência de qualquer lado da relação.

## Salvaguarda analítica

Economia não é sinônimo automático de eficiência.

Detecção de anomalias é mecanismo de priorização, não acusação.

Todo futuro sinal deverá expor:

- população utilizada na comparação;
- método estatístico;
- tamanho da amostra;
- registros subjacentes;
- proveniência dos dados.
