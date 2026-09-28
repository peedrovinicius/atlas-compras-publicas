# Release v1.64.0

A v1.64.0 reduz o ruído visual da análise detalhada sem remover informação.

## Ações

Copiar link e exportar CSV passam a ficar agrupados em um menu `Ações`.

O cabeçalho da análise mantém visíveis apenas:

- suficiência da amostra;
- data de atualização;
- acesso ao menu de ações.

## Histórico

O gráfico de histórico permanece visível como leitura principal.

A tabela mensal detalhada passa a ficar recolhida em `Ver tabela detalhada`, com a quantidade de períodos indicada no próprio controle.

## Sinais estatísticos

A explicação metodológica continua visível.

Quando existem sinais, a tabela completa passa a ficar recolhida em `Ver sinais detectados`, com a quantidade de registros indicada no resumo.

## Evidências

A seção de rastreabilidade agora informa quantos registros estão sendo exibidos em relação ao total do recorte.

Descrições longas ficam limitadas na visualização fechada e são expandidas quando a evidência é aberta.

No mobile:

- o resumo de cada evidência passa a uma coluna;
- o grid interno vira uma coluna;
- hashes e link do PNCP ficam empilhados;
- o menu de ações deixa de usar popover flutuante.

## Validação

O gate funcional registrou:

- Ruff aprovado;
- 226 testes aprovados;
- build React/TypeScript aprovado;
- Vite concluído em 783 ms;
- GitHub Actions concluído com sucesso.
