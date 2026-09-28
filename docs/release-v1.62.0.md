# Release v1.62.0

A v1.62.0 fecha a etapa de refinamento de interação do novo Explorador.

## Foco rápido na busca

A pesquisa pode ser focada sem usar o mouse:

- `/`;
- `Ctrl+K`;
- `Cmd+K` em macOS.

O atalho não interfere quando o foco já está em campos editáveis.

Em desktop, uma indicação discreta de `/` aparece dentro do campo de busca.

## Resultados mais fáceis de escanear

Descrições públicas muito longas passam a ocupar no máximo duas linhas na lista.

O nome comparável, os indicadores de cobertura e a mediana continuam visíveis, mas o cartão ganha menos altura e melhor separação visual.

O foco por teclado também ganhou destaque visível.

## Mobile

Em telas pequenas:

- os cartões usam menos espaço vertical;
- os indicadores ficam mais compactos;
- preço e ação permanecem na mesma linha;
- o texto auxiliar da unidade deixa de competir com o valor principal;
- a indicação do atalho de teclado é ocultada.

## Validação

O gate funcional da mudança passou com:

- Ruff aprovado;
- 226 testes aprovados;
- build React/TypeScript aprovado;
- GitHub Actions concluído com sucesso.

A consulta externa ao domínio público do Render continuou bloqueada na ferramenta de verificação usada nesta sessão, então esta release descreve o estado validado do `main`, não uma confirmação de propagação do deploy.
