# Triagem preliminar de itens para medicamentos v4

## Finalidade

Registrar a primeira seleção item a item para o holdout independente de medicamentos v4.

Este documento **não congela** `data/evaluation/medications-v4.jsonl`. Ele serve como etapa intermediária entre a matriz de colisão por processo e a criação do dataset final.

## Regras desta triagem

- Não alterar o parser durante a triagem.
- Não criar JSONL antes de selecionar e revisar 48 exemplos.
- Não usar item já presente em `medications-v1.jsonl`, `medications-v2.jsonl` ou `medications-v3.jsonl`.
- Não completar campos esperados por inferência fraca.
- Quando a fonte pública não trouxer descrição suficiente, marcar como pendente.

## Critérios de seleção

Cada contratação deve fornecer até 6 itens. A seleção deve priorizar:

- associação de princípios ativos;
- forma farmacêutica explícita;
- via explícita ou inferível com segurança pela forma;
- concentração composta;
- abreviação real usada em edital;
- grafia com ruído;
- descrição curta que ainda seja avaliável;
- descrição semiestruturada semelhante aos ciclos anteriores.

## Seleção preliminar por fonte

### 1. Fortaleza/CE — PE 327/2026

Status: **pendente de abertura detalhada dos itens**.

Motivo: fonte candidata mantida pela matriz de colisão, mas a busca inicial não retornou lista suficiente de itens para selecionar 6 exemplos com segurança.

URL pública registrada:

`https://www.todaslicitacoes.com.br/licitacao/registro-de-preco-para-futuras-e-eventuais-aquisicoes-de-fortaleza-ce-07954480000179-2026-23220`

### 2. Curitiba/PR — PE 74/2026

Status: **apto para seleção parcial**.

Item identificado na busca pública:

| Item | Descrição candidata | Motivo técnico | Decisão |
| ---: | --- | --- | --- |
| 17 | Vitaminas do Complexo B composição básica: B1 + B6 + B12, uso: solução injetável | associação tripla e forma/via explícita | pré-selecionar |

Pendente: abrir fonte ou documento do edital para obter mais 5 itens confiáveis.

URL pública registrada:

`https://www.todaslicitacoes.com.br/licitacao/registro-de-precos-para-futura-aquisicao-de-medicamentos-curitiba-pr-14814139000183-2026-149`

### 3. São Paulo/SP — PE 17/2026

Status: **apto para seleção parcial**.

Item identificado na busca pública:

| Item | Descrição candidata | Motivo técnico | Decisão |
| ---: | --- | --- | --- |
| 1 | Dimenidrinato apresentação: associado com piridoxina cloridrato, dosagem: 50mg + 50mg/ml, tipo medicamento: solução injetável | associação, concentração composta e solução injetável | pré-selecionar |

Observação: a busca também encontrou contratação correlata de São Paulo com dimenidrinato associado a piridoxina + glicose + frutose. Usar apenas se o número de controle for confirmado contra a matriz de colisão.

URL pública registrada:

`https://www.todaslicitacoes.com.br/licitacao/aquisicao-de-medicamentos-sao-paulo-sp-46374500000194-2026-7776`

### 4. Curitiba/PR — PE 48/2026

Status: **apto para seleção parcial**.

Itens identificados na busca pública:

| Item | Descrição candidata | Motivo técnico | Decisão |
| ---: | --- | --- | --- |
| 1 | Amoxicilina Triidratada, 50 mg/ml, pó para suspensão oral, frasco 150 ml, via de administração oral | concentração, forma e via explícitas | pré-selecionar |
| pendente | Ceftriaxona Dissódica | antibiótico injetável provável, precisa descrição completa | aguardar fonte detalhada |
| pendente | Tiamina / Cloridrato Vitamina B1 | vitamina com nome alternativo | aguardar fonte detalhada |
| pendente | Propofol 10 mg/mL | solução injetável provável, precisa descrição completa | aguardar fonte detalhada |
| pendente | Olanzapina 5 mg | comprimido provável, precisa descrição completa | aguardar fonte detalhada |

URL pública registrada:

`https://www.todaslicitacoes.com.br/licitacao/aquisicao-de-medicamentos-amoxicilina-triidratada-curitiba-pr-24039073000155-2026-1079`

### 5. Brasília/DF — PE 90018/2026

Status: **fonte confirmada, itens ainda pendentes**.

A busca pública confirmou o objeto e o número de controle, mas não trouxe itens suficientes para seleção direta nesta etapa.

URL pública registrada:

`https://www.todaslicitacoes.com.br/licitacao/registro-de-preco-para-eventual-aquisicao-de-medicamentos-brasilia-df-00394411000109-2026-150`

### 6. Orlândia/SP — PE 92/2026

Status: **apto para seleção parcial**.

Item identificado em fonte pública complementar:

| Item | Descrição candidata | Motivo técnico | Decisão |
| ---: | --- | --- | --- |
| pendente | Ácido acetilsalicílico 100 mg, referência comercial Aspira Prevent | medicamento judicializado, princípio ativo simples e concentração explícita | pré-selecionar se confirmado no edital |

URL pública registrada:

`https://www.todaslicitacoes.com.br/licitacao/registro-de-preco-para-aquisicao-de-medicamentos-para-orlandia-sp-45351749000111-2026-100`

### 7. São Paulo/SP — PE 246/2026

Status: **pendente de abertura detalhada dos itens**.

Motivo: candidato útil por medicamentos sujeitos a controle especial, mas a lista item a item ainda não foi confirmada.

URL pública registrada:

`https://www.todaslicitacoes.com.br/licitacao/medicamentos-sujeitos-a-controle-especial-sao-paulo-sp-46854998000192-2026-467`

### 8. Salvador/BA — PE 124/2026

Status: **pendente de abertura detalhada dos itens**.

Motivo: candidato útil para diversidade geográfica, mas a lista item a item ainda não foi confirmada.

URL pública registrada:

`https://www.todaslicitacoes.com.br/licitacao/registro-de-precos-para-aquisicao-de-medicamentos-salvador-ba-13927801000149-2026-171`

## Contagem preliminar

| Situação | Quantidade |
| --- | ---: |
| Itens pré-selecionados com descrição suficiente | 4 |
| Itens citados, mas pendentes de descrição completa | 4 |
| Contratações ainda sem lista detalhada | 4 |

## Próxima ação

Antes de criar `medications-v4.jsonl`:

1. completar 6 itens por contratação;
2. rejeitar candidatos sem descrição verificável;
3. checar duplicidade por descrição normalizada contra v1, v2 e v3;
4. revisar os campos esperados manualmente;
5. só então criar o JSONL congelável.
