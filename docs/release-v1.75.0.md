# Release v1.75.0 — Identificação de proveniência da demonstração

Esta versão prepara uma demonstração do Atlas que **não confunde preços públicos capturados do PNCP com dados inteiramente sintéticos**. O comportamento de produção só será confirmado após deploy autorizado.

## Proveniência explícita

- `pncp_sample`: amostra efetivamente obtida do PNCP, sem alegação de cobrir todo o mercado.
- `offline_synthetic`: dados inteiramente fictícios gerados quando a amostra padrão falha ou não traz resultados suficientes.
- `unknown`: dados sem metadados confiáveis; nunca devem ser apresentados como observações reais.

A tabela `atlas_demo_provenance` guarda origem, data/hora UTC e contagens no próprio DuckDB. A API expõe os metadados em `/health`, `/ready` e `/api/v1/meta`.

## Transparência no frontend e nas exportações

O aplicativo exibe aviso de proveniência nas análises. CSV exportado contém `data_source_type`, nome de arquivo rotulado e header `X-Atlas-Provenance`; descrições similares a fórmulas são neutralizadas para segurança de planilhas. O relatório para impressão/PDF conserva a mesma advertência, inclusive quando a origem for desconhecida.

## Qualidade, testes e segurança

- Cobertura de amostra PNCP, fallback sintético e origem desconhecida/incoerente;
- Testes Python, Node, compilação TypeScript/Vite e análise CodeQL;
- Testes visuais Chromium em desktop e mobile, impressão A4/PDF e CSV;
- Melhoria do CI com testes de contrato do frontend, auditoria de dependências e manutenção do Vite;
- Documentação de deploy Render e smoke de produção com validação da origem.

## Limitações e cuidados de publicação

A aprovação dos testes **não confirma a proveniência do dataset que está atualmente no Render**. O serviço anterior não contém esta implementação. Após a publicação expressamente autorizada da v1.75.0, confirmar a origem no deploy ativo, verificar o banner, relatórios e exportações, registrar o tipo e as contagens da base e executar o workflow `Production smoke test`.

Não publicar números fictícios como preços homologados. Esta release não habilita ingestão de dados privados.
