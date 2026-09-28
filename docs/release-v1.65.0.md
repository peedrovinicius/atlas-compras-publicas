# Release v1.65.0

A v1.65.0 melhora acessibilidade e continuidade de navegação sem alterar a aparência principal do Atlas.

## Navegação por teclado

Foi adicionado um skip link `Ir para o conteúdo`, visível ao receber foco.

A alternância entre Preços e Laboratório passa a expor o estado ativo por `aria-pressed`.

Inputs, selects, links e regiões interativas passam a usar foco visível consistente.

## Resultados e análise

Depois de abrir um produto, a análise detalhada recebe foco programaticamente após a rolagem.

No Laboratório, o foco também é movido para os resultados quando uma normalização termina.

Isso evita que usuários de teclado precisem percorrer novamente toda a página depois de uma ação principal.

## Leitores de tela

A release adiciona:

- status acessível da API;
- anúncio da quantidade de grupos encontrados;
- `role="alert"` para erros;
- `aria-busy` em resultados e análise durante carregamento;
- rótulos explícitos para regiões de resultados e análise.

## Movimento reduzido

Quando o sistema indica `prefers-reduced-motion`, o Atlas reduz transições, animações e rolagem suave.

## Validação

O gate funcional registrou:

- Ruff aprovado;
- 226 testes aprovados;
- build React/TypeScript aprovado;
- Vite concluído em 726 ms;
- GitHub Actions concluído com sucesso.
