# Arquitetura

## Objetivo

O sistema deve produzir inteligência de preços sem perder a cadeia de evidências que conecta cada resultado analítico ao registro original do PNCP.

## Fluxo

`API PNCP → raw → bronze → silver → gold → API analítica → dashboard`

## Raw

Conteúdo original da fonte acompanhado de:

- URL;
- data e hora da coleta;
- status HTTP;
- SHA-256;
- quantidade de bytes;
- manifesto de proveniência.

Itens e resultados são armazenados como evidências independentes.

A v0.6.0 adiciona captura completa de uma contratação. O pipeline consulta primeiro os itens e, em seguida, o endpoint de resultados de cada item retornado.

## Bronze

Registros tipados do PNCP.

Nenhuma inferência semântica deve ser misturada à validação estrutural.

## Silver

Nesta camada são produzidos:

- texto normalizado;
- categoria;
- apresentação;
- cor;
- quantidade por embalagem;
- quantidade física;
- preço estimado normalizado;
- preço homologado normalizado;
- fornecedor;
- marca;
- economia;
- referências às evidências de origem.

As tabelas principais atuais são:

- `silver_items`;
- `silver_awards`.

## Gold

A camada gold contém sinais analíticos derivados apenas de registros que atendem aos critérios mínimos de comparabilidade.

A tabela atual é:

- `gold_price_signals`.

A visão:

- `price_anomalies`

contém somente registros sinalizados pelo método robusto.

## Grupo comparável

A chave baseline combina:

- categoria;
- apresentação;
- cor;
- unidade física;
- quantidade física.

A chave é explícita no dataset para permitir auditoria do agrupamento.

## Estatística robusta

Grupos com menos de cinco observações não produzem sinais.

Quando MAD é maior que zero, utiliza-se modified z-score.

Quando MAD é zero e IQR é maior que zero, utiliza-se IQR.

Quando não existe variação suficiente, o sistema registra a condição sem gerar sinal.

## Rastreabilidade

A cadeia desejada é:

`sinal → grupo → homologação → item → SHA-256 → resposta original → PNCP`

O processamento não deve remover os identificadores de proveniência.

## Salvaguarda

Sinal estatístico não equivale a irregularidade.

A camada gold serve para priorização analítica e deve sempre expor método, grupo, tamanho da amostra e limitações.
