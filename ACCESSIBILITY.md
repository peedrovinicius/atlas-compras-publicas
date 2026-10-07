# Acessibilidade

O Atlas Compras Públicas busca manter a interface utilizável por teclado, tecnologias assistivas e pessoas com diferentes necessidades visuais e motoras.

Este documento funciona como referência para novas alterações no frontend. Ele não declara conformidade formal com um nível específico das WCAG.

## Princípios

Toda mudança de interface deve procurar preservar:

- navegação completa por teclado;
- foco visível e ordem de foco previsível;
- contraste suficiente entre texto, controles e fundo;
- rótulos claros para campos, filtros e ações;
- textos alternativos quando imagens carregarem informação;
- uso de HTML semântico antes de soluções baseadas apenas em ARIA;
- mensagens de erro compreensíveis e associadas ao campo correspondente;
- interface funcional com zoom e diferentes larguras de tela;
- ausência de dependência exclusiva de cor para comunicar estado.

## Checklist para pull requests

Antes de concluir uma mudança visual ou interativa:

- percorra a tela usando apenas Tab, Shift+Tab, Enter e Espaço;
- confirme que elementos interativos possuem nome acessível;
- verifique se o foco não fica preso em modais ou componentes;
- teste os principais fluxos com zoom aumentado;
- confira se mensagens de carregamento, vazio e erro continuam compreensíveis;
- evite remover outline de foco sem fornecer uma alternativa equivalente;
- confirme que ícones usados como botão possuem rótulo textual acessível.

## Componentes dinâmicos

Filtros, paginação, comparadores e resultados atualizados sem recarregar a página devem manter contexto e foco previsíveis. Quando uma alteração dinâmica mudar de forma relevante o conteúdo apresentado, a implementação deve considerar uma forma adequada de comunicar a mudança a tecnologias assistivas.

## Linguagem

Prefira textos diretos, consistentes e específicos. Rótulos como "Abrir", "Comparar" ou "Ver detalhes" devem deixar claro o que será aberto, comparado ou exibido quando o contexto não for evidente.

## Relatos

Problemas de acessibilidade podem ser registrados como issue com:

- página ou componente afetado;
- passos para reprodução;
- navegador e tecnologia assistiva, quando aplicável;
- comportamento esperado;
- captura de tela ou vídeo, se isso ajudar sem expor dados sensíveis.
