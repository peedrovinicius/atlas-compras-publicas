# Exemplo real e reproduzível do parser

Este exemplo usa um item público já congelado no dataset `data/evaluation/v5.jsonl`.

## Origem

- dataset: `data/evaluation/v5.jsonl`;
- id no holdout: `lr-350`;
- item: `350`;
- controle PNCP: `01612541000133-1-000047/2026`;
- descrição registrada: `PRIME ADESIVO FRASCO 4ML`;
- fonte pública registrada no dataset: https://www.todaslicitacoes.com.br/licitacao/registro-de-precos-para-eventual-e-futura-contratacao-de-lago-dos-rodrigues-ma-01612541000133-2026-47

O dataset permanece congelado. Este documento não altera o rótulo nem a lógica do parser.

## Entrada

~~~text
PRIME ADESIVO FRASCO 4ML
~~~

## Saída do parser atual

~~~text
categoria: dental_adhesive
apresentação: bottle
quantidade por unidade: 4 ml
resolução da medida: single
quantidade na embalagem: não identificada
quantidade total: não derivada
cor: não identificada
concentração: não identificada
termos reconhecidos: ADESIVO
atributos técnicos adicionais: nenhum
~~~

## Como interpretar

`dental_adhesive` indica que as regras classificaram a descrição como adesivo odontológico.

`bottle` vem do termo `FRASCO`.

`4 ml` é a única medida física explícita na descrição. Como não há quantidade de frascos informada, o parser mantém `package_count = null` e não calcula uma quantidade total.

`single` registra que existe uma única medida física não ambígua.

Nenhum atributo técnico adicional é inferido porque a descrição não informa estratégia adesiva nem modo de cura.

## Reproduzir

Em Python:

~~~python
from dental_procurement_intelligence.identity import parse_product

product = parse_product("PRIME ADESIVO FRASCO 4ML")
print(product)
~~~

Pela API:

~~~text
GET /api/v1/normalize?description=PRIME%20ADESIVO%20FRASCO%204ML
~~~

O teste `tests/test_documented_parser_example.py` protege os campos publicados acima contra divergência acidental entre documentação e implementação.
