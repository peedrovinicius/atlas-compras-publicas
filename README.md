# Dental Procurement Intelligence

Plataforma auditável de inteligência de dados para compras públicas odontológicas no Brasil.

O projeto constrói um pipeline reprodutível para coletar, normalizar, comparar e analisar itens odontológicos publicados no Portal Nacional de Contratações Públicas (PNCP). O desafio principal não é apenas calcular preços, mas determinar quando descrições pouco padronizadas representam produtos realmente comparáveis e quando um preço merece revisão estatística.

## Status atual

**v0.6.0 — captura completa e sinais robustos de preço**

O repositório já inclui:

- pacote Python tipado;
- cliente para a API pública do PNCP;
- captura de todos os itens de uma contratação;
- captura automática dos resultados de cada item;
- armazenamento bruto endereçado por conteúdo com SHA-256;
- manifesto de proveniência e verificação de integridade;
- Product Identity Engine com decisão explicável;
- normalização de embalagem e quantidade física;
- transformação analítica em Parquet;
- catálogo SQL local com DuckDB;
- integração entre itens e resultados homologados;
- cálculo de valor estimado equivalente, valor homologado e economia;
- exclusão de resultados cancelados dos indicadores por padrão;
- cálculo de preço homologado por unidade física;
- formação explícita de grupos comparáveis;
- detecção robusta de preços atípicos com MAD e IQR;
- rastreabilidade do sinal estatístico até as evidências brutas.

O GitHub Actions permanece desativado nesta fase para evitar consumo desnecessário de minutos de CI.

## Problema

Descrições de compras públicas frequentemente apresentam abreviações, erros, variações de embalagem e unidades incompatíveis.

Exemplos:

`RES FOTOP A2 C/2 SER 4G`

`RESINA COMPOSTA FOTOPOLIMERIZAVEL COR A2 SERINGA 4 G`

Uma comparação direta pelo texto ou pelo preço unitário informado pode ser enganosa.

A pergunta central do projeto é:

> Estes registros representam produtos comparáveis o suficiente para uma análise de preço, e conseguimos explicar essa decisão até a fonte pública original?

## Fonte dos dados

A fonte principal é a API pública do PNCP:

`https://pncp.gov.br/api/pncp`

O pipeline utiliza, entre outros, os endpoints oficiais para itens e resultados de itens de uma contratação.

O conteúdo bruto recebido é preservado antes de qualquer transformação.

## Arquitetura

~~~mermaid
flowchart LR
    A[API PNCP] --> B[Evidência bruta SHA-256]
    B --> C[Validação estrutural]
    C --> D[Normalização textual]
    D --> E[Product Identity Engine]
    E --> F[Normalização de unidades]
    F --> G[Parquet]
    G --> H[DuckDB]
    H --> I[Itens + homologações]
    I --> J[Grupos comparáveis]
    J --> K[MAD / IQR]
    K --> L[Sinais explicáveis]
    L --> M[API de evidências]
    M --> N[Dashboard]
~~~

### Camadas de dados

- **raw** — resposta original e imutável da fonte;
- **bronze** — registros tipados e estruturalmente validados;
- **silver** — atributos, unidades, itens e homologações normalizados;
- **gold** — grupos comparáveis e sinais estatísticos explicáveis.

## Captura completa da contratação

A v0.6.0 adiciona um fluxo único que:

1. consulta os itens da contratação;
2. preserva a resposta bruta dos itens;
3. percorre cada número de item retornado pelo PNCP;
4. consulta os resultados cadastrados daquele item;
5. preserva cada resposta de resultado separadamente;
6. retorna contagens e referências das evidências armazenadas.

Exemplo:

~~~bash
dpi capture-contract \
  --cnpj 10000000000003 \
  --year 2021 \
  --sequence 1
~~~

A captura é deliberadamente sequencial nesta fase para reduzir complexidade e evitar carga agressiva sobre a fonte pública.

## Product Identity Engine

Uma descrição como:

`RES FOTOP A2 C/2 SERINGAS 4G`

pode ser transformada em:

~~~text
categoria: composite_resin
cor: A2
apresentacao: syringe
quantidade_embalagem: 2
quantidade_unitaria: 4 g
quantidade_total: 8 g
~~~

O motor não usa apenas similaridade textual. Diferenças relevantes de categoria, apresentação, cor ou quantidade podem tornar dois itens incompatíveis mesmo quando os textos parecem semelhantes.

## Preço normalizado

Quando a descrição oferece informação suficiente, o pipeline calcula preço por unidade física.

~~~text
Preço homologado: R$ 72,00
Embalagem: 2 seringas
Conteúdo por seringa: 4 g
Conteúdo total: 8 g

Preço homologado normalizado: R$ 9,00/g
~~~

## Estimado x homologado

~~~text
Valor unitário estimado:   R$ 80,00
Valor unitário homologado: R$ 72,00
Quantidade homologada:     10

Valor estimado equivalente: R$ 800,00
Valor homologado:           R$ 720,00
Economia:                   R$ 80,00
Economia percentual:        10,00%
~~~

Resultados cancelados pelo PNCP não entram nos indicadores por padrão.

## Sinais robustos de preço

A v0.6.0 introduz uma camada `gold_price_signals`.

Um grupo comparável considera, na versão atual:

- categoria odontológica;
- apresentação;
- cor, quando identificada;
- unidade física normalizada;
- quantidade física normalizada.

Um registro só pode gerar sinal quando o grupo possui pelo menos **5 resultados válidos**.

### Método principal

Quando o desvio absoluto mediano é maior que zero:

`modified z-score = 0,67448975 × (preço - mediana) / MAD`

O limite padrão é:

`|modified z-score| >= 3,5`

### Fallback

Quando o MAD é zero, mas o intervalo interquartil é maior que zero, o sistema usa limites de Tukey:

`Q1 - 1,5 × IQR`

`Q3 + 1,5 × IQR`

Quando não há amostra ou variação suficientes, nenhum sinal é produzido.

Executar:

~~~bash
dpi detect-anomalies --database data/analytics.duckdb
~~~

Consultar resumo:

~~~bash
dpi anomalies-summary --database data/analytics.duckdb
~~~

A metodologia completa está em `docs/metodologia-anomalias.md`.

## Início rápido

Recomendado: Python 3.12 ou superior.

~~~bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
~~~

No Windows PowerShell:

~~~powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
~~~

## Fluxo analítico

~~~text
capture-contract
        ↓
evidências raw
        ↓
build-analytics
        ↓
build-awards
        ↓
detect-anomalies
        ↓
anomalies-summary
~~~

## Estrutura do repositório

~~~text
src/dental_procurement_intelligence/
  pncp/             cliente PNCP e modelos tipados
  ingestion/        evidência bruta e captura completa
  identity/         identidade canônica e comparabilidade
  normalization/    normalização textual e de medidas
  analytics/        Parquet, DuckDB, homologações e sinais
  cli.py            interface de linha de comando

tests/              testes automatizados
docs/               arquitetura e metodologia
data/               contrato das camadas locais
~~~

## Princípio de auditabilidade

O objetivo é preservar a cadeia:

`sinal → grupo comparável → homologação → item → evidência bruta → PNCP`

As camadas analíticas mantêm hashes das respostas de origem.

## Salvaguarda metodológica

Um sinal estatístico significa apenas que o preço se afastou do padrão observado dentro do grupo comparado.

Ele não constitui evidência de:

- fraude;
- corrupção;
- superfaturamento juridicamente caracterizado;
- irregularidade administrativa;
- conduta ilícita do fornecedor ou órgão.

Diferenças podem decorrer de marca, especificação não capturada, região, prazo, logística, volume, momento da compra ou outras variáveis ainda não modeladas.

## Roadmap

- [x] Estrutura inicial do projeto
- [x] Cliente de itens e resultados do PNCP
- [x] Normalização textual
- [x] Extração de medidas
- [x] Ingestão bruta com hash de conteúdo
- [x] Product Identity Engine explicável — baseline
- [x] Camada analítica Parquet
- [x] DuckDB
- [x] Preço normalizado por unidade física
- [x] Resultados homologados
- [x] Estimado x homologado
- [x] Captura automática de todos os resultados de uma contratação
- [x] Detecção robusta de preços atípicos — baseline
- [ ] Expandir taxonomia odontológica validada
- [ ] Incorporar atributos técnicos adicionais por categoria
- [ ] Adicionar recuperação semântica de candidatos
- [ ] Incorporar dimensão geográfica e temporal
- [ ] FastAPI de evidências
- [ ] Interface analítica em React
- [ ] Relatório público de qualidade dos dados

## Princípios

1. A evidência de origem é imutável.
2. Toda transformação deve ser reproduzível.
3. A equivalência de produtos deve ser explicável.
4. Preços só podem ser comparados dentro de grupos defensáveis.
5. Ausência e incerteza devem permanecer explícitas.
6. Todo resultado analítico deve ser rastreável à fonte pública.
