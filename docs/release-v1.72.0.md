# Release v1.72.0

A v1.72.0 transforma a análise detalhada do Atlas em um relatório reutilizável para consulta, registro e compartilhamento.

## Gerar relatório / PDF

A área de ações da análise passa a oferecer `Gerar relatório / PDF`.

A ação abre a impressão do navegador com um layout A4 dedicado. O usuário pode imprimir ou salvar o documento como PDF sem dependência externa e sem novo endpoint.

## Conteúdo do relatório

O relatório reúne:

- produto analisado e descrição de referência;
- consulta executada;
- unidade de preço;
- período observado;
- quantidade de preços comparáveis;
- mínimo, P25, mediana, P75 e máximo;
- compras, fornecedores, UFs e quantidade de registros;
- filtros ativos;
- metodologia e orientação de interpretação.

Quando o campo `Preço que recebi` estiver preenchido com um valor válido, o relatório também inclui:

- valor da proposta;
- diferença absoluta e percentual para a mediana;
- posição em relação à distribuição;
- percentil aproximado.

## Metodologia

O relatório explicita que as estatísticas usam apenas observações com normalização de preço classificada como defensável, valor por unidade base disponível e valor positivo.

O documento não classifica preços como justos, abusivos, corretos ou irregulares. Ele descreve a posição dos valores dentro da amostra pública observada.

## Impressão

O layout de impressão usa página A4 e remove da saída os elementos de navegação e interação da aplicação, preservando somente o relatório.

## Integridade da release

A v1.71.0 expôs uma inconsistência no contrato de versão do cliente PNCP: o pacote estava em 1.71.0, mas o User-Agent permanecia em 1.69.

A v1.72.0 corrige esse contrato e sincroniza pacote, cliente PNCP e frontend.
