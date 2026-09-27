# Benchmark independente de medicamentos v1

## Objetivo

Validar a primeira taxonomia do novo domínio de medicamentos sem misturar suas regras com odontologia.

A taxonomia avalia quatro dimensões de identidade:

- ingrediente ativo;
- concentração principal;
- forma farmacêutica;
- via.

## Dataset

O dataset foi congelado antes da primeira medição:

- 48 exemplos;
- 8 contratações públicas de 2026;
- 192 campos avaliados;
- 6 exemplos por contratação.

As fontes incluem Campinas/SP, Varginha/MG, Montividiu/GO, Botucatu/SP, Firminópolis/GO, Paudalho/PE, Paranhos/MS e Lamim/MG.

## Baseline independente

| Campo | Corretos | Acurácia |
| --- | ---: | ---: |
| Ingrediente ativo | 31/48 | 64,58% |
| Concentração | 43/48 | 89,58% |
| Forma farmacêutica | 47/48 | 97,92% |
| Via | 47/48 | 97,92% |
| **Total** | **168/192** | **87,50%** |

Erros agregados:

- 1 falso positivo;
- 2 falsos negativos;
- 21 mismatches.

## Principais lacunas

A baseline mostrou que forma farmacêutica e via já generalizam bem.

As maiores lacunas estão em ingrediente ativo, especialmente:

- associações, como ceftazidima + avibactam;
- sais e apresentações, como benzilpenicilina benzatina;
- descrições com códigos BR;
- palavras coladas, como `Aciclovir50`;
- grafias sem separação, como `Ácidofólico`;
- nomes comerciais, que não devem ser tratados automaticamente como princípio ativo.

Na concentração, os principais problemas são:

- razões com volume explícito, como `500 mg/5 ml`;
- denominador em litro;
- números com separadores de milhar em UI.

## Decisão

O domínio de medicamentos **não é ativado** nesta release.

Ele permanece com status `benchmark_required` até que uma release posterior faça tuning controlado sobre essas lacunas e preserve esta baseline independente.

## Regra metodológica

Esta baseline nunca deve ser regravada após tuning.

Qualquer melhoria deve ser registrada em artefato pós-tuning separado.
