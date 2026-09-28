# Release v1.61.0

A v1.61.0 simplifica a primeira experiência no Explorador de preços.

## Home orientada à busca

O Atlas não executa mais uma pesquisa automática por `resina` ao abrir a página.

A entrada agora permanece limpa até o usuário:

- digitar uma pesquisa;
- escolher uma categoria;
- abrir uma pesquisa recente;
- acessar uma URL compartilhada com consulta.

Isso reduz ruído visual e evita que a primeira impressão pareça uma demonstração pré-carregada.

## Estados preservados

Links compartilhados continuam funcionando normalmente. Quando a URL contém `q` e, opcionalmente, `product_id`, o Atlas restaura a pesquisa e a análise correspondente.

## Controles

O botão principal e a ação de aplicar filtros só ficam disponíveis quando a consulta possui pelo menos dois caracteres.

Limpar filtros na home vazia apenas limpa os campos e não dispara uma tentativa inválida de pesquisa.

## Validação

O gate funcional executado antes da consolidação registrou:

- 226 testes aprovados;
- Ruff aprovado;
- build React/TypeScript aprovado;
- Vite concluído em 736 ms.
