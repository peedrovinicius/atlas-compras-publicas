import { FormEvent, useEffect, useRef, useState } from "react";

import { fetchProductAnalytics, searchProducts } from "./api";
import type {
  ProductAnalyticsBundle,
  ProductSearchItem,
} from "./types";

const DEFAULT_QUERY = "resina";
const EXAMPLES = ["resina", "ionômero", "anestésico", "flúor"];

function money(value: number | null | undefined): string {
  if (value === null || value === undefined) return "Sem amostra";
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  }).format(Number(value));
}

function number(value: number | null | undefined): string {
  return new Intl.NumberFormat("pt-BR").format(Number(value ?? 0));
}

function date(value: string | null | undefined): string {
  if (!value) return "Não informado";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return new Intl.DateTimeFormat("pt-BR", {
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(parsed);
}

function percent(value: number | null | undefined): string {
  if (value === null || value === undefined) return "Sem referência";
  const numeric = Number(value);
  return `${numeric > 0 ? "+" : ""}${numeric.toLocaleString("pt-BR", {
    maximumFractionDigits: 1,
  })}%`;
}

function Metric({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </div>
  );
}

export default function AnalyticsExplorer() {
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [results, setResults] = useState<ProductSearchItem[]>([]);
  const [total, setTotal] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [bundle, setBundle] = useState<ProductAnalyticsBundle | null>(null);
  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const detailRef = useRef<HTMLElement>(null);

  async function runSearch(nextQuery = query) {
    const cleaned = nextQuery.trim();
    if (cleaned.length < 2) {
      setError("Digite pelo menos 2 caracteres para pesquisar.");
      return;
    }

    setSearching(true);
    setError(null);
    setBundle(null);
    setSelectedId(null);

    try {
      const response = await searchProducts(cleaned);
      setResults(response.items);
      setTotal(response.total);
    } catch (requestError) {
      setResults([]);
      setTotal(0);
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Não foi possível pesquisar agora.",
      );
    } finally {
      setSearching(false);
    }
  }

  async function selectProduct(item: ProductSearchItem) {
    setSelectedId(item.product_id);
    setLoading(true);
    setError(null);

    try {
      const analytics = await fetchProductAnalytics(item.product_id);
      setBundle(analytics);
      window.requestAnimationFrame(() => {
        detailRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    } catch (requestError) {
      setBundle(null);
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Não foi possível carregar os detalhes.",
      );
    } finally {
      setLoading(false);
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void runSearch();
  }

  useEffect(() => {
    void runSearch(DEFAULT_QUERY);
  }, []);

  const summary = bundle?.summary;
  const stats = summary?.price_stats;

  return (
    <>
      <section className="hero analytics-hero">
        <span className="eyebrow">Inteligência sobre compras públicas</span>
        <h1>Pesquise um produto e descubra quanto o governo está pagando por ele.</h1>
        <p>
          Compare preços homologados, evolução temporal, diferenças regionais,
          fornecedores, órgãos compradores e sinais estatísticos com rastreabilidade até o PNCP.
        </p>
      </section>

      <section className="panel analytics-search-panel">
        <form onSubmit={submit}>
          <label htmlFor="analytics-search">Produto ou característica</label>
          <div className="analytics-search-row">
            <input
              id="analytics-search"
              value={query}
              onChange={(event: { target: { value: string } }) => setQuery(event.target.value)}
              placeholder="Ex.: resina A2, ionômero, anestésico"
              autoComplete="off"
            />
            <button className="primary-button" type="submit" disabled={searching}>
              {searching ? "Pesquisando..." : "Pesquisar"}
            </button>
          </div>
        </form>

        <div className="analytics-examples">
          <span>Exemplos</span>
          {EXAMPLES.map((example) => (
            <button
              type="button"
              key={example}
              onClick={() => {
                setQuery(example);
                void runSearch(example);
              }}
            >
              {example}
            </button>
          ))}
        </div>

        {error && <p className="analytics-error">{error}</p>}
      </section>

      <section className="analytics-results">
        <div className="results-header">
          <div>
            <span className="section-kicker">Resultados compatíveis</span>
            <h2>Produtos encontrados</h2>
          </div>
          {!searching && <span className="item-count">{number(total)} grupos</span>}
        </div>

        {searching ? (
          <div className="analytics-loading">Consultando a base analítica...</div>
        ) : results.length === 0 ? (
          <div className="empty-state">
            <strong>Nenhum produto encontrado.</strong>
            <span>Tente um termo mais amplo ou use um dos exemplos acima.</span>
          </div>
        ) : (
          <div className="analytics-result-list">
            {results.map((item) => (
              <button
                type="button"
                key={item.product_id}
                className={
                  selectedId === item.product_id
                    ? "analytics-result analytics-result-selected"
                    : "analytics-result"
                }
                onClick={() => void selectProduct(item)}
              >
                <span>
                  <strong>{item.display_name}</strong>
                  <small>{item.sample_description}</small>
                </span>
                <span className="analytics-result-meta">
                  {number(item.priced_observation_count)} preços · {number(item.procurement_count)} compras · {number(item.state_count)} UFs
                </span>
              </button>
            ))}
          </div>
        )}
      </section>

      <section ref={detailRef} className="analytics-detail">
        {loading && <div className="analytics-loading">Carregando análise completa...</div>}

        {!loading && bundle && summary && stats && (
          <>
            <div className="analytics-title-row">
              <div>
                <span className="section-kicker">Análise consolidada</span>
                <h2>{summary.display_name}</h2>
                <p>{summary.sample_description}</p>
              </div>
              <span className={summary.sample_sufficient ? "sample-status" : "sample-status sample-status-warning"}>
                {summary.sample_sufficient
                  ? `${number(summary.price_sample_count)} preços comparáveis`
                  : `Amostra pequena: ${number(summary.price_sample_count)} preços`}
              </span>
            </div>

            {!summary.sample_sufficient && (
              <p className="sample-warning">
                A amostra está abaixo do mínimo metodológico de {number(summary.minimum_sample_size)} observações de preço. Interprete as estatísticas com cautela.
              </p>
            )}

            <div className="analytics-metrics">
              <Metric label="Mediana" value={money(stats.median_price)} note={summary.price_unit ?? "preço normalizado"} />
              <Metric label="Faixa central" value={`${money(stats.percentile_25)} a ${money(stats.percentile_75)}`} note="25º ao 75º percentil" />
              <Metric label="Compras" value={number(summary.procurement_count)} note="processos distintos" />
              <Metric label="Fornecedores" value={number(summary.supplier_count)} note="documentos distintos" />
              <Metric label="UFs" value={number(summary.state_count)} note="cobertura da amostra" />
              <Metric label="Período" value={`${date(summary.period_start)} a ${date(summary.period_end)}`} note="datas observadas" />
            </div>

            <div className="analytics-grid">
              <article className="analytics-card analytics-card-wide">
                <span className="section-kicker">Evolução</span>
                <h3>Histórico de preços</h3>
                {bundle.history.points.length === 0 ? (
                  <p className="analytics-empty">Sem série temporal defensável para este produto.</p>
                ) : (
                  <div className="analytics-table-wrap">
                    <table>
                      <thead><tr><th>Mês</th><th>Mediana</th><th>Faixa central</th><th>Observações</th></tr></thead>
                      <tbody>
                        {bundle.history.points.map((point) => (
                          <tr key={point.month}>
                            <td>{date(point.month)}</td>
                            <td>{money(point.median_price)}</td>
                            <td>{money(point.percentile_25)} a {money(point.percentile_75)}</td>
                            <td>{number(point.observations)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </article>

              <article className="analytics-card">
                <span className="section-kicker">Geografia</span>
                <h3>Comparação por UF</h3>
                <div className="analytics-rank-list">
                  {bundle.regions.states.slice(0, 8).map((state) => (
                    <div key={state.state_code}>
                      <span><strong>{state.state_code}</strong><small>{state.macroregion ?? "Região não informada"}</small></span>
                      <span><strong>{money(state.median_price)}</strong><small>{percent(state.difference_from_national_percent)}</small></span>
                    </div>
                  ))}
                </div>
              </article>

              <article className="analytics-card">
                <span className="section-kicker">Mercado</span>
                <h3>Fornecedores</h3>
                <div className="analytics-rank-list">
                  {bundle.suppliers.items.map((supplier) => (
                    <div key={supplier.supplier_document}>
                      <span><strong>{supplier.supplier_name ?? "Fornecedor sem nome"}</strong><small>{number(supplier.procurement_count)} compras</small></span>
                      <span><strong>{money(supplier.median_price)}</strong><small>{percent(supplier.sample_share_percent)} da amostra</small></span>
                    </div>
                  ))}
                </div>
              </article>

              <article className="analytics-card">
                <span className="section-kicker">Demanda pública</span>
                <h3>Órgãos compradores</h3>
                <div className="analytics-rank-list">
                  {bundle.buyers.items.map((buyer, index) => (
                    <div key={`${buyer.organization_cnpj ?? "org"}-${buyer.buyer_unit_code ?? index}`}>
                      <span><strong>{buyer.organization_name ?? buyer.buyer_unit_name ?? "Órgão sem nome"}</strong><small>{buyer.state_code ?? "UF não informada"} · {number(buyer.procurement_count)} compras</small></span>
                      <span><strong>{money(buyer.median_price)}</strong><small>{money(buyer.awarded_total_value)} homologados</small></span>
                    </div>
                  ))}
                </div>
              </article>

              <article className="analytics-card analytics-card-wide">
                <span className="section-kicker">Sinais estatísticos</span>
                <h3>Preços fora da distribuição observada</h3>
                <p className="analytics-note">{bundle.signals.disclaimer}</p>
                {bundle.signals.items.length === 0 ? (
                  <p className="analytics-empty">Nenhum sinal estatístico publicado para este produto.</p>
                ) : (
                  <div className="analytics-table-wrap">
                    <table>
                      <thead><tr><th>Data</th><th>Preço</th><th>Mediana</th><th>Método</th><th>UF</th><th>Fonte</th></tr></thead>
                      <tbody>
                        {bundle.signals.items.map((signal) => (
                          <tr key={signal.award_key}>
                            <td>{date(signal.analysis_date)}</td>
                            <td>{money(signal.awarded_price_per_base_unit)}</td>
                            <td>{money(signal.median_price)}</td>
                            <td>{signal.detection_method ?? "Não informado"}</td>
                            <td>{signal.state_code ?? "Não informada"}</td>
                            <td>{signal.pncp_url ? <a href={signal.pncp_url} target="_blank" rel="noreferrer">PNCP</a> : "Sem link"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </article>

              <article className="analytics-card analytics-card-wide">
                <span className="section-kicker">Rastreabilidade</span>
                <h3>Registros que sustentam a análise</h3>
                <div className="analytics-records">
                  {bundle.records.items.map((record) => (
                    <div key={record.award_key}>
                      <span>
                        <strong>{money(record.awarded_price_per_base_unit)}</strong>
                        <small>{date(record.analysis_date)} · {record.state_code ?? "UF não informada"}</small>
                      </span>
                      <p>{record.original_description}</p>
                      <span>
                        <small>{record.supplier_name ?? "Fornecedor não informado"}</small>
                        {record.pncp_url && <a href={record.pncp_url} target="_blank" rel="noreferrer">Abrir no PNCP</a>}
                      </span>
                    </div>
                  ))}
                </div>
              </article>
            </div>
          </>
        )}
      </section>
    </>
  );
}
