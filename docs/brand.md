# Identidade Atlas e Preços

Este documento define o uso da identidade pública do projeto.

## Nome público

Use **Atlas e Preços** em:

- cabeçalho da aplicação;
- título da página;
- metadados sociais;
- materiais públicos de apresentação;
- README como nome principal.

## Nome técnico

**Atlas de Compras Públicas** permanece como nome técnico e descritivo do projeto, especialmente em documentação de arquitetura, histórico e contexto do repositório.

## Assinatura

Subtítulo preferencial:

`Inteligência em compras públicas`

Descrição curta preferencial:

`Inteligência de preços em compras públicas com dados do PNCP, histórico, comparação e rastreabilidade.`

## Símbolo

O símbolo oficial é o `A` metálico usado no cabeçalho da aplicação.

Regras:

- manter as proporções;
- não distorcer;
- não girar;
- não aplicar contorno;
- não adicionar brilho colorido;
- não recolorir arbitrariamente;
- preservar contraste e legibilidade;
- usar o mesmo ativo no favicon e na aplicação quando possível.

## Tipografia

O nome deve ser renderizado como texto HTML no produto sempre que possível.

Tratamento atual:

- `Atlas`: peso forte;
- `e Preços`: peso mais leve;
- cores neutras em grafite/cinza;
- sem efeitos decorativos no texto.

Isso preserva nitidez em telas de diferentes densidades e melhora acessibilidade.

## Uso no produto

No frontend:

- marca principal: `Atlas e Preços`;
- subtítulo: `Inteligência em compras públicas`;
- símbolo decorativo com `alt=""`;
- link da marca com `aria-label="Atlas e Preços"`.

## Consistência

A suíte `tests/test_release_integrity.py` valida automaticamente os principais pontos da identidade pública.
