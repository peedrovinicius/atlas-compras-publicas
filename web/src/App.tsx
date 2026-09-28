import { useEffect, useMemo, useRef, useState } from "react";

import AnalyticsExplorer from "./AnalyticsExplorer";

import {
  API_BASE_URL,
  checkHealth,
  fetchCategories,
  normalizeDescriptions,
} from "./api";
import type {
  NormalizationResult,
  ParserCategory,
  TechnicalAttributes,
} from "./types";

const DEFAULT_TEXT = "";

const CATEGORY_EXAMPLES: Record<string, string> = {
  flowable_resin: "RESINA FLOW A2 SERINGA 2G",
  composite_resin: "RES FOTOP A2 C/2 SERINGAS 4G",
  dental_adhesive: "ADESIVO DENTAL FRASCO 4ML",
  glass_ionomer: "IONOMERO RESTAURADOR AUTOPOLIMERIZAVEL LIQ 8ML",
  phosphoric_acid: "ACIDO FOSFORICO 37% SERINGA 2,5ML",
  alginate: "ALGINATO PARA MOLDAGEM PACOTE 410G",
  fluoride_gel: "FLUORETO DE SODIO 2% GEL NEUTRO FRASCO 200ML",
  prophylaxis_paste: "PASTA PROFILATICA TUBO 90G",
  calcium_hydroxide: "HIDROXIDO DE CALCIO P.A 10G",
  zinc_oxide: "OXIDO DE ZINCO 50G",
  eugenol: "EUGENOL FRASCO 20ML",
  radiographic_fixer: "FIXADOR RADIOGRAFICO PRONTO PARA USO LIQUIDO 475ML",
  radiographic_developer: "REVELADOR RADIOGRAFICO PRONTO PARA USO 475ML",
  local_anesthetic: "ANESTESICO LOCAL LIDOCAINA 2% COM EPINEFRINA 1:100.000",
  unknown: "CIMENTO ODONTOLOGICO",
};

const EXAMPLES = [
  {
    label: "Resina A2",
    value: "RES FOTOP A2 C/2 SERINGAS 4G",
  },
  {
    label: "Ionômero",
    value: "IONOMERO RESTAURADOR AUTOPOLIMERIZAVEL LIQ 8ML",
  },
  {
    label: "Flúor gel",
    value: "FLUORETO DE SODIO 2% GEL NEUTRO FRASCO 200ML",
  },
  {
    label: "Hidróxido de cálcio",
    value: "HIDROXIDO DE CALCIO P.A 10G",
  },
];

const PRESENTATION_LABELS: Record<string, string> = {
  syringe: "Seringa",
  tube: "Tubo",
  bottle: "Frasco",
  jar: "Pote",
  kit: "Kit",
};

const TECHNICAL_LABELS: Record<keyof TechnicalAttributes, string> = {
  resin_technology: "Tecnologia da resina",
  curing_mode: "Modo de cura",
  adhesive_strategy: "Estratégia adesiva",
  ionomer_use: "Uso do ionômero",
  fluoride_formulation: "Formulação de flúor",
  anesthetic_active_ingredient: "Princípio ativo",
  anesthetic_vasoconstrictor: "Vasoconstritor",
};

function parseDescriptions(value: string): string[] {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function formatQuantity(
  value: NormalizationResult["unit_quantity"],
): string | null {
  if (!value) return null;
  return `${value.value} ${value.unit}`;
}

function ResultCard({
  result,
  index,
  total,
  categoryLabels,
}: {
  result: NormalizationResult;
  index: number;
  total: number;
  categoryLabels: Map<string, string>;
}) {
  const category =
    categoryLabels.get(result.category) ??
    (result.category === "unknown" ? "Não reconhecido" : result.category);

  const technicalEntries = Object.entries(result.technical_attributes).filter(
    ([, value]) => value !== null,
  ) as [keyof TechnicalAttributes, string][];

  const chips = [
    result.shade ? `Cor ${result.shade}` : null,
    result.concentration_percent
      ? `${result.concentration_percent}%`
      : null,
    result.presentation
      ? PRESENTATION_LABELS[result.presentation] ?? result.presentation
      : null,
    result.package_count ? `${result.package_count} un` : null,
    result.unit_quantity
      ? `${formatQuantity(result.unit_quantity)}/un`
      : null,
    result.total_quantity
      ? `${formatQuantity(result.total_quantity)} total`
      : null,
  ].filter(Boolean) as string[];

  return (
    <article className="result-card">
      <div className="result-heading">
        <div>
          <span className="result-kicker">
            {total > 1 ? `Resultado ${index} de ${total}` : "Resultado"}
          </span>
          <h3>{category}</h3>
        </div>
        <span
          className={
            result.category === "unknown"
              ? "confidence confidence-review"
              : "confidence"
          }
        >
          {result.category === "unknown" ? "Requer revisão" : "Reconhecido"}
        </span>
      </div>

      <p className="source-description">{result.original_description}</p>

      {chips.length > 0 && (
        <div className="chip-row">
          {chips.map((chip) => (
            <span className="chip" key={chip}>
              {chip}
            </span>
          ))}
        </div>
      )}

      <div className="technical-grid">
        <Detail label="Categoria interna" value={result.category} />
        <Detail
          label="Apresentação"
          value={
            result.presentation
              ? PRESENTATION_LABELS[result.presentation] ?? result.presentation
              : null
          }
        />
        <Detail label="Cor" value={result.shade} />
        <Detail
          label="Concentração"
          value={
            result.concentration_percent
              ? `${result.concentration_percent}%`
              : null
          }
        />
        <Detail
          label="Quantidade por unidade"
          value={formatQuantity(result.unit_quantity)}
        />
        <Detail
          label="Embalagem"
          value={
            result.package_count ? `${result.package_count} unidade(s)` : null
          }
        />
        <Detail
          label="Total físico"
          value={formatQuantity(result.total_quantity)}
        />
        <Detail
          label="Resolução da medida"
          value={result.measurement_resolution}
        />
        <Detail
          label="Termos reconhecidos"
          value={
            result.matched_terms.length
              ? result.matched_terms.join(", ")
              : "Nenhum"
          }
          wide
        />
        <Detail
          label="Atributos técnicos"
          value={
            technicalEntries.length
              ? technicalEntries
                  .map(([key, value]) => `${TECHNICAL_LABELS[key]}: ${value}`)
                  .join(" · ")
              : "Nenhum atributo adicional"
          }
          wide
        />
      </div>
    </article>
  );
}

function Detail({
  label,
  value,
  wide = false,
}: {
  label: string;
  value: string | number | null | undefined;
  wide?: boolean;
}) {
  return (
    <div className={wide ? "detail detail-wide" : "detail"}>
      <dt>{label}</dt>
      <dd>{value ?? "Não identificado"}</dd>
    </div>
  );
}

export default function App() {
  const [mode, setMode] = useState<"analytics" | "laboratory">("analytics");
  const [input, setInput] = useState(DEFAULT_TEXT);
  const [results, setResults] = useState<NormalizationResult[]>([]);
  const [categories, setCategories] = useState<ParserCategory[]>([]);
  const [loading, setLoading] = useState(false);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [apiVersion, setApiVersion] = useState<string | null>(null);
  const [message, setMessage] = useState(
    "Cole uma descrição do PNCP ou escolha um exemplo rápido.",
  );
  const [hasAnalyzed, setHasAnalyzed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const resultsRef = useRef<HTMLElement>(null);

  const descriptions = useMemo(() => parseDescriptions(input), [input]);
  const categoryLabels = useMemo(
    () => new Map(categories.map((item) => [item.id, item.label])),
    [categories],
  );

  async function analyze(nextInput = input) {
    const items = parseDescriptions(nextInput);

    if (!items.length) {
      setError("Digite pelo menos uma descrição.");
      inputRef.current?.focus();
      return;
    }

    if (items.length > 20) {
      setError("Use no máximo 20 descrições por análise.");
      inputRef.current?.focus();
      return;
    }

    setHasAnalyzed(true);
    setLoading(true);
    setError(null);
    setMessage(
      items.length === 1
        ? "Analisando a descrição."
        : `Analisando ${items.length} descrições.`,
    );

    try {
      const nextResults = await normalizeDescriptions(items);
      setResults(nextResults);
      setMessage(
        nextResults.length === 1
          ? "1 resultado processado."
          : `${nextResults.length} resultados processados.`,
      );
      setApiOnline(true);
      window.requestAnimationFrame(() => {
        resultsRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
        resultsRef.current?.focus({ preventScroll: true });
      });
    } catch (requestError) {
      setResults([]);
      setApiOnline(false);
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Não foi possível consultar a API.",
      );
      setMessage("A análise não foi concluída.");
    } finally {
      setLoading(false);
    }
  }

  function useExample(value: string) {
    setInput(value);
    inputRef.current?.focus();
    void analyze(value);
  }

  async function runCategoryExample(category: ParserCategory) {
    const example = CATEGORY_EXAMPLES[category.id];

    if (!example) {
      setError(`Ainda não há exemplo configurado para ${category.label}.`);
      return;
    }

    setInput(example);
    await analyze(example);

    window.requestAnimationFrame(() => {
      resultsRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  }

  useEffect(() => {
    let active = true;

    Promise.all([fetchCategories(), checkHealth()])
      .then(([nextCategories, health]) => {
        if (!active) return;
        setCategories(nextCategories);
        setApiOnline(health.ok);
        setApiVersion(health.version);
      })
      .catch(() => {
        if (!active) return;
        setApiOnline(false);
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (mode !== "laboratory") return;

    window.requestAnimationFrame(() => {
      inputRef.current?.focus();
    });
  }, [mode]);

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Ir para o conteúdo
      </a>
      <header className="site-header">
        <a className="brand" href="/" aria-label="Atlas de Compras Públicas">
          <span className="brand-mark">A</span>
          <span className="brand-copy">
            <strong>Atlas</strong>
            <small>Compras públicas</small>
          </span>
        </a>

        <nav className="header-actions" aria-label="Links principais">
          <div className="mode-switch" aria-label="Áreas do Atlas">
            <button
              type="button"
              className={mode === "analytics" ? "active" : ""}
              aria-pressed={mode === "analytics"}
              onClick={() => setMode("analytics")}
            >
              Preços
            </button>
            <button
              type="button"
              className={mode === "laboratory" ? "active" : ""}
              aria-pressed={mode === "laboratory"}
              onClick={() => setMode("laboratory")}
            >
              Laboratório
            </button>
          </div>
          <span
            role="status"
            aria-live="polite"
            className={
              apiOnline === false
                ? "api-state api-state-offline"
                : "api-state"
            }
            title={
              apiOnline === null
                ? "Verificando disponibilidade da API"
                : apiOnline
                  ? "API disponível"
                  : "API indisponível"
            }
          >
            <span className="status-dot" />
            <span className="api-state-label">
              {apiOnline === null
                ? "Verificando"
                : apiOnline
                  ? "Online"
                  : "Offline"}
            </span>
          </span>
          <a
            className="header-link"
            href="https://github.com/peedrovinicius/atlas-compras-publicas"
            target="_blank"
            rel="noreferrer"
          >
            Código
          </a>
        </nav>
      </header>

      <main id="main-content" tabIndex={-1}>
        {mode === "analytics" ? (
          <AnalyticsExplorer />
        ) : (
          <>
        <section className="hero laboratory-hero">
          <span className="eyebrow">Laboratório técnico</span>
          <h1>Veja como o Atlas entende uma descrição do PNCP.</h1>
          <p>
            Cole uma ou mais descrições para inspecionar a normalização,
            medidas e atributos usados na inteligência de preços.
          </p>
        </section>

        <section className="workspace laboratory-workspace">
          <div className="panel composer-panel">
            <div className="section-heading">
              <div>
                <span className="section-kicker">Entrada</span>
                <h2>Descrição da compra</h2>
              </div>
              <span className="item-count">
                {descriptions.length}/20 {descriptions.length === 1 ? "item" : "itens"}
              </span>
            </div>

            <label className="field-label" htmlFor="descriptions">
              Uma descrição por linha
            </label>
            <textarea
              id="descriptions"
              ref={inputRef}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ex.: RESINA FOTOPOLIMERIZÁVEL A2 SERINGA 4G"
              spellCheck={false}
            />

            <div className="composer-footer">
              <div>
                <p
                  className={error ? "feedback feedback-error" : "feedback"}
                  role={error ? "alert" : "status"}
                  aria-live="polite"
                >
                  {error ?? message}
                </p>
              </div>

              <button
                className="primary-button"
                type="button"
                disabled={
                  loading
                  || descriptions.length === 0
                  || descriptions.length > 20
                }
                onClick={() => void analyze()}
              >
                {loading ? "Analisando..." : "Analisar descrição"}
              </button>
            </div>

            <div className="examples-block">
              <span>Exemplos rápidos</span>
              <div className="example-row">
                {EXAMPLES.map((example) => (
                  <button
                    type="button"
                    key={example.label}
                    onClick={() => useExample(example.value)}
                  >
                    {example.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <aside className="panel categories-panel">
            <div className="section-heading compact">
              <div>
                <span className="section-kicker">Vocabulário</span>
                <h2>Categorias reconhecidas</h2>
              </div>
            </div>
            <p className="aside-copy">
              Escolha uma categoria para preencher e analisar um exemplo real.
            </p>

            <div className="category-list">
              {categories.map((category) => (
                <button
                  type="button"
                  key={category.id}
                  className={
                    category.fallback
                      ? "category-row category-row-fallback"
                      : "category-row"
                  }
                  disabled={loading}
                  onClick={() => void runCategoryExample(category)}
                >
                  <span className="category-dot" />
                  <span>{category.label}</span>
                </button>
              ))}
            </div>
          </aside>
        </section>

        {(hasAnalyzed || loading) && (
        <section
          ref={resultsRef}
          className="results-section laboratory-results"
          tabIndex={-1}
          aria-live="polite"
          aria-busy={loading}
          aria-label="Resultados da normalização"
        >
          <div className="results-header">
            <div>
              <span className="section-kicker">Saída estruturada</span>
              <h2>Resultados</h2>
            </div>
            {results.length > 0 && (
              <span className="item-count">
                {results.length} {results.length === 1 ? "resultado" : "resultados"}
              </span>
            )}
          </div>

          {results.length === 0 && !loading ? (
            <div className="empty-state">
              <strong>Nenhum resultado para mostrar.</strong>
              <span>
                Clique em uma categoria ou exemplo acima, ou digite uma descrição.
              </span>
            </div>
          ) : (
            <div className="result-list">
              {results.map((result, index) => (
                <ResultCard
                  key={`${result.original_description}-${index}`}
                  result={result}
                  index={index + 1}
                  total={results.length}
                  categoryLabels={categoryLabels}
                />
              ))}
            </div>
          )}
        </section>
        )}
          </>
        )}
      </main>

      <footer className="site-footer">
        <span>
          Atlas de Compras Públicas
          {apiVersion ? ` v${apiVersion}` : ""}
        </span>
        <span className="footer-links">
          <a href={`${API_BASE_URL}/docs`} target="_blank" rel="noreferrer">
            API
          </a>
          <span>Dados públicos · PNCP · rastreabilidade</span>
        </span>
      </footer>
    </div>
  );
}
