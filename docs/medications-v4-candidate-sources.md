# Pré-candidatos de fontes para medicamentos v4

## Finalidade

Registrar fontes candidatas para o holdout independente de medicamentos v4 antes de qualquer criação de dataset.

Este arquivo **não congela** o v4. Ele apenas organiza contratações públicas candidatas para checagem posterior de colisão, diversidade e qualidade dos itens.

## Regras de uso

- Não copiar itens para `data/evaluation/medications-v4.jsonl` antes da checagem de colisão.
- Confirmar o número de controle diretamente na fonte pública antes do congelamento.
- Conferir se a contratação não aparece em `medications-v1.jsonl`, `medications-v2.jsonl` ou `medications-v3.jsonl`.
- Selecionar no máximo 6 itens por contratação.
- Priorizar descrições reais com ruído suficiente para medir generalização.

## Pré-candidatos levantados

| Prioridade | Local | Objeto resumido | Sinal útil para o v4 | URL pública |
| --- | --- | --- | --- | --- |
| Alta | Fortaleza/CE | Registro de preço de medicamentos, PE 327/2026 | Associação com quatro componentes em solução injetável | https://www.todaslicitacoes.com.br/licitacao/registro-de-preco-para-futuras-e-eventuais-aquisicoes-de-fortaleza-ce-07954480000179-2026-23220 |
| Alta | Curitiba/PR | Registro de preços de medicamentos, PE 74/2026 | Vitaminas do complexo B com B1 + B6 + B12 em solução injetável | https://www.todaslicitacoes.com.br/licitacao/registro-de-precos-para-futura-aquisicao-de-medicamentos-curitiba-pr-14814139000183-2026-149 |
| Alta | São Paulo/SP | Aquisição de medicamentos, PE 17/2026 | Dimenidrinato associado com piridoxina e concentração composta | https://www.todaslicitacoes.com.br/licitacao/aquisicao-de-medicamentos-sao-paulo-sp-46374500000194-2026-7776 |
| Alta | Curitiba/PR | Aquisição de medicamentos, PE 48/2026 | Mistura de antibiótico, vitamina, anestésico e antipsicótico no mesmo processo | https://www.todaslicitacoes.com.br/licitacao/aquisicao-de-medicamentos-amoxicilina-triidratada-curitiba-pr-24039073000155-2026-1079 |
| Média | Brasília/DF | Registro de preço para eventual aquisição de medicamentos, PE 90018/2026 | Fonte federal diferente das amostras v2/v3 | https://www.todaslicitacoes.com.br/licitacao/registro-de-preco-para-eventual-aquisicao-de-medicamentos-brasilia-df-00394411000109-2026-150 |
| Média | Orlândia/SP | Registro de preço para aquisição de medicamentos, PE 92/2026 | Possível foco em demandas judiciais | https://www.todaslicitacoes.com.br/licitacao/registro-de-preco-para-aquisicao-de-medicamentos-para-orlandia-sp-45351749000111-2026-100 |
| Média | São Paulo/SP | Medicamentos sujeitos a controle especial, PE 246/2026 | Classe controlada e descrições potencialmente mais específicas | https://www.todaslicitacoes.com.br/licitacao/medicamentos-sujeitos-a-controle-especial-sao-paulo-sp-46854998000192-2026-467 |
| Média | Curitiba/PR | Aquisição de medicamentos por registro de preços, PE 10/2026 | Item com grafia problemática: `INFLIMABE`, caneta SC | https://www.todaslicitacoes.com.br/licitacao/aquisicao-de-medicamentos-atraves-do-sistema-de-registro-de-curitiba-pr-03518900000113-2026-10 |
| Média | Salvador/BA | Registro de preços para aquisição de medicamentos, PE 124/2026 | Fonte municipal/estadual fora dos polos já usados | https://www.todaslicitacoes.com.br/licitacao/registro-de-precos-para-aquisicao-de-medicamentos-salvador-ba-13927801000149-2026-171 |
| Baixa | Fortaleza/CE | Registro de preço de medicamento, PE 202621567/2026 | Mesmo ente de v2, mas processo novo; usar só se faltar diversidade | https://www.todaslicitacoes.com.br/licitacao/registro-de-preco-medicamento-fortaleza-ce-07954480000179-2026-22607 |
| Baixa | Brasília/DF | Medicamentos para determinações judiciais, PE 90052/2026 | Pode ser útil para itens especializados, mas precisa checar colisão com Brasília v3 | https://www.todaslicitacoes.com.br/licitacao/registro-de-precos-para-aquisicao-de-medicamentos-para-brasilia-df-00394544000185-2026-1239 |
| Baixa | Fortaleza/CE | Registro de preço para medicamentos, PE 475/2026 | Metronidazol injetável; usar apenas se houver itens não redundantes | https://www.todaslicitacoes.com.br/licitacao/registro-de-preco-para-futuras-e-eventuais-aquisicoes-de-fortaleza-ce-07954480000179-2026-24203 |

## Seleção recomendada inicial

Para reduzir repetição geográfica e institucional, a primeira tentativa de v4 deve partir destes 8 grupos:

1. Fortaleza/CE — PE 327/2026;
2. Curitiba/PR — PE 74/2026;
3. São Paulo/SP — PE 17/2026;
4. Curitiba/PR — PE 48/2026;
5. Brasília/DF — PE 90018/2026;
6. Orlândia/SP — PE 92/2026;
7. São Paulo/SP — PE 246/2026;
8. Salvador/BA — PE 124/2026.

## Próxima ação

Antes de criar `medications-v4.jsonl`, executar uma checagem objetiva:

- extrair todos os `pncp_control_number` de v1, v2 e v3;
- comparar os candidatos contra essa lista;
- abrir cada fonte candidata e selecionar 6 itens com ruído real;
- registrar quais itens foram recusados e por quê.

Somente depois disso o dataset v4 deve ser criado em `data/evaluation/`.
