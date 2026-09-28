# Segurança

## Escopo

Relatos de segurança são relevantes quando envolvem, por exemplo:

- exposição de segredos, tokens ou credenciais;
- execução indevida de código;
- comprometimento de workflows ou dependências;
- manipulação não autorizada de evidências, hashes ou artefatos analíticos;
- vulnerabilidades na API, quando utilizada;
- injeção em consultas, scripts ou processos de ingestão.

Erros de normalização, divergências metodológicas e sinais estatísticos incorretos devem ser tratados como issues de qualidade de dados, não como vulnerabilidades.

## Como relatar

Não abra uma issue pública para uma vulnerabilidade ainda não corrigida.

Prefira o mecanismo privado de reporte de vulnerabilidade do GitHub quando ele estiver disponível. Caso não esteja, entre em contato de forma privada com o mantenedor pelo perfil do GitHub.

Inclua, quando possível:

- descrição objetiva do problema;
- componente e versão afetados;
- passos mínimos para reprodução;
- impacto observado ou plausível;
- evidências sem dados pessoais ou segredos;
- sugestão de mitigação, se houver.

## Dados e segredos

Nunca envie ao repositório:

- credenciais;
- arquivos `.env`;
- tokens de API;
- chaves privadas;
- cookies ou sessões autenticadas;
- dumps privados;
- dados pessoais que não possam ser redistribuídos.

O projeto usa dados públicos do PNCP e preserva rastreabilidade sem exigir a publicação de credenciais ou informações privadas.
