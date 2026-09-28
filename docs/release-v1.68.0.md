# Release v1.68.0

A v1.68.0 melhora a qualidade da busca no Explorador de preços.

## Relevância estruturada

`Mais relevantes` passa a ser a ordenação padrão.

O score considera sinais estruturados que já existem na identidade do produto:

- categoria interpretada;
- cor;
- apresentação;
- correspondência textual na descrição pública.

Cobertura de preços e número de compras continuam sendo usados como critérios de desempate.

As ordenações anteriores permanecem disponíveis.

## Apresentações em linguagem natural

A busca passa a reconhecer termos comuns usados no dia a dia e conectá-los à apresentação normalizada.

Exemplos:

- `seringa` -> `syringe`;
- `frasco` -> `bottle`;
- `tubo` -> `tube`;
- `pote` -> `jar`;
- `tubete` ou `carpule` -> `cartridge`;
- `ampola` -> `ampoule`.

Isso permite localizar identidades estruturadas mesmo quando o termo digitado não aparece literalmente em todos os registros públicos.

## Por que o resultado apareceu

Cada resultado pode exibir até três motivos estruturados de correspondência, por exemplo:

- `Categoria: Resina composta`;
- `Cor A2`;
- `Apresentação: Seringa`.

Quando não existe um match estruturado específico, o Atlas informa `Descrição compatível`.

## Autocomplete

O autocomplete usa relevância em vez de somente cobertura.

Ao abrir diretamente uma sugestão, facets da pesquisa anterior são limpas para evitar refinamentos visualmente incorretos.

## Validação

O gate funcional anterior à consolidação registrou:

- Ruff aprovado;
- 238 testes aprovados;
- build React/TypeScript aprovado;
- Vite concluído em 818 ms.


## Contratos da release

A versão 1.68.0 está sincronizada entre pacote Python, API, cliente PNCP e frontend. A ordenação padrão pública passa a ser `relevance`, preservando `coverage`, `procurements`, `latest` e `name` como alternativas explícitas.
