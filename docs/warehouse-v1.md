# Warehouse analítico v1

## Objetivo

Formalizar o contrato analítico atual do Atlas sem alterar as tabelas já usadas pelo pipeline.

O warehouse v1 possui três camadas principais:

1. `silver_items`: itens normalizados da contratação;
2. `silver_awards`: resultados homologados enriquecidos com identidade, contexto e preços;
3. `gold_price_signals`: linhas elegíveis para comparação, estatísticas de grupo e sinais explicáveis.

## silver_items

Granularidade: um item de contratação.

Principais grupos de campos:

- evidência: `source_sha256`;
- origem: `item_number`, `original_description`;
- normalização: `normalized_description`, `product_category`, `presentation`;
- atributos: cor, concentração e atributos técnicos;
- quantidade: unidade, quantidade por unidade e quantidade total normalizada;
- preço: valor estimado e preço normalizado por unidade-base;
- qualidade: cobertura de categoria, apresentação, medida e atributos críticos.

A tabela é construída em `analytics/lakehouse.py`.

## silver_awards

Granularidade: um resultado homologado ativo.

Chaves:

- `procurement_key`: identidade estável da contratação;
- `award_key`: identidade estável do resultado homologado.

Rastreabilidade:

- `contract_source_sha256`;
- `item_source_sha256`;
- `result_source_sha256`.

Contexto disponível:

- categoria e atributos técnicos;
- apresentação e quantidade física;
- fornecedor e marca;
- data, ano e trimestre;
- município, UF e macrorregião;
- esfera e modalidade;
- preço estimado, homologado e preço por unidade-base.

A tabela é construída em `analytics/awards.py`.

## gold_price_signals

Granularidade: uma homologação elegível para análise de preço.

A tabela é derivada de `silver_awards` e inclui:

- `product_key`: identidade técnica usada na comparação;
- `comparison_scope`: recorte geográfico e temporal selecionado;
- `scope_group_key`: chave do grupo comparável;
- `group_size`;
- mediana, quartis, IQR e MAD;
- `modified_z_score`;
- `detection_method`;
- `is_price_signal`.

O Atlas seleciona o escopo comparável mais específico com amostra suficiente e usa MAD ou IQR conforme a variação disponível.

Sinal estatístico não é tratado como prova de irregularidade.

## SQL versionado

As consultas públicas de portfólio estão em `sql/`:

1. evolução mensal de preço;
2. dispersão por grupo comparável;
3. diferença regional para a mediana nacional;
4. cobertura da normalização;
5. rastreabilidade completa de um sinal.

Essas consultas são testadas no CI contra um schema DuckDB mínimo compatível com o warehouse v1.

## Regra de evolução

Mudanças incompatíveis de coluna, tipo ou granularidade exigem uma nova versão deste contrato. A versão v1 não deve ser reescrita silenciosamente após publicação.
