# Release v1.63.0

A v1.63.0 conclui a unificação visual e comportamental do Laboratório com o novo Explorador.

## Entrada limpa

O Laboratório não executa mais uma normalização automática quando o site é aberto.

A área técnica começa vazia e só processa uma descrição quando o usuário:

- digita ou cola uma descrição;
- escolhe um exemplo rápido;
- seleciona uma categoria reconhecida.

Isso reduz chamadas desnecessárias à API e evita que o Laboratório pareça uma demonstração pré-carregada.

## Interface

O Laboratório ganhou:

- hero mais compacto;
- painel de entrada sem altura fixa;
- categorias reconhecidas mais compactas;
- textarea e ações alinhadas ao sistema visual do Explorador;
- resultados técnicos com menos sombra, menos espaçamento e maior densidade;
- comportamento mobile simplificado.

## Controles

O botão de análise fica indisponível quando:

- não há descrições;
- existem mais de 20 descrições;
- uma análise já está em execução.

A seção de resultados só é exibida depois que uma análise foi iniciada.

## Limpeza de apresentação

O texto sobre cold start e plano gratuito foi removido da interface pública. A disponibilidade da API continua indicada no cabeçalho.

## Validação

O gate funcional da mudança registrou:

- Ruff aprovado;
- 226 testes aprovados;
- build React/TypeScript aprovado;
- Vite concluído em 893 ms;
- GitHub Actions concluído com sucesso.
