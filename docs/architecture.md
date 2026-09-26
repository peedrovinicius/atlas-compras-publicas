# Arquitetura

## Objetivo

Produzir inteligência de preços sem perder a cadeia de evidências que conecta um resultado analítico ao registro original do PNCP.

## Fonte oficial

A contratação é consultada pelo endpoint:

`/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}`

Esse registro fornece o contexto institucional, temporal e geográfico utilizado na v0.7.0.

Itens e resultados permanecem coletados em endpoints próprios.

## Raw

São armazenadas separadamente:

- resposta da contratação;
- resposta dos itens;
- resposta de resultados de cada item.

Cada objeto possui SHA-256 e manifesto de coleta.

## Bronze

Modelos tipados representam:

- contratação;
- órgão;
- unidade administrativa;
- item;
- resultado homologado.

## Silver

A tabela `silver_awards` reúne:

- atributos canônicos do produto;
- preços estimados e homologados;
- preço por unidade física;
- fornecedor e marca;
- resultado e situação;
- data de publicação;
- data do resultado;
- data de análise;
- ano e trimestre;
- município e código IBGE;
- UF e macrorregião;
- esfera;
- modalidade;
- três hashes de proveniência.

A macrorregião é uma derivação determinística da UF; ela não substitui os campos originais do PNCP.

## Gold

A tabela `gold_price_signals` seleciona, para cada resultado elegível, o grupo geográfico-temporal mais específico com amostra suficiente.

Hierarquia:

`UF/trimestre → região/trimestre → Brasil/trimestre → região/ano → Brasil/ano`

A escolha do grupo permanece armazenada na própria linha analítica.

## Estatística

MAD com modified z-score é o método principal.

IQR é utilizado quando o MAD é zero e ainda existe dispersão.

Grupos com amostra insuficiente ou sem variação não geram sinal.

## Rastreabilidade

A cadeia é:

`sinal → grupo → homologação → item → contratação → evidências SHA-256 → PNCP`

## Salvaguarda

Sinal estatístico não equivale a irregularidade.

O sistema deve sempre apresentar:

- grupo utilizado;
- período;
- geografia;
- tamanho da amostra;
- estatística;
- proveniência;
- limitações.
