"""Página pública da demo do Atlas."""

DEMO_HTML = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description"
      content="Demo pública do Atlas de Compras Públicas para normalização de itens do PNCP.">
<title>Atlas de Compras Públicas | Demo</title>
<style>
:root {
  color-scheme: dark;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
  --bg: #0d1117;
  --panel: #161b22;
  --panel-2: #0d1117;
  --border: #30363d;
  --text: #e6edf3;
  --muted: #9da7b3;
  --link: #58a6ff;
  --success: #3fb950;
  --warning: #d29922;
  --danger: #f85149;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
}
a { color: var(--link); }
button,
textarea {
  font: inherit;
}
button:focus-visible,
textarea:focus-visible,
a:focus-visible {
  outline: 3px solid var(--link);
  outline-offset: 3px;
}
.notice {
  border-bottom: 1px solid var(--border);
  background: #11161d;
  color: var(--muted);
  padding: 10px 20px;
  font-size: 13px;
  text-align: center;
}
main {
  width: min(1040px, 92vw);
  margin: 0 auto;
  padding: 46px 0 72px;
}
.eyebrow {
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: .14em;
  font-size: 12px;
}
h1 {
  font-size: clamp(36px, 7vw, 66px);
  line-height: 1;
  margin: 10px 0 16px;
}
h2 {
  margin: 0 0 12px;
  font-size: 22px;
}
.lead {
  color: var(--muted);
  line-height: 1.65;
  max-width: 780px;
}
.links,
.examples {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.links {
  margin-top: 20px;
}
.card {
  margin-top: 28px;
  padding: 22px;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: var(--panel);
}
.problem {
  display: grid;
  gap: 16px;
  grid-template-columns: 1.4fr 1fr;
}
.metric {
  border-left: 3px solid var(--link);
  padding-left: 16px;
}
.metric strong {
  display: block;
  font-size: 28px;
}
.metric span {
  color: var(--muted);
  font-size: 13px;
}
.examples {
  margin: 12px 0 18px;
}
.example {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 8px 12px;
  background: var(--panel-2);
  color: var(--text);
  cursor: pointer;
}
.example:hover {
  border-color: #6e7681;
}
.example[data-limit="true"] {
  border-style: dashed;
}
label {
  display: block;
  font-weight: 700;
  margin-bottom: 10px;
}
textarea {
  width: 100%;
  min-height: 104px;
  resize: vertical;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--panel-2);
  color: var(--text);
  padding: 14px;
}
.form-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 8px;
}
.counter,
.helper,
.note {
  color: var(--muted);
  font-size: 13px;
  line-height: 1.55;
}
.action {
  border: 0;
  border-radius: 10px;
  padding: 11px 16px;
  font-weight: 700;
  cursor: pointer;
  background: var(--text);
  color: var(--bg);
}
.action[disabled] {
  cursor: wait;
  opacity: .65;
}
.status {
  min-height: 24px;
  margin-top: 14px;
  color: var(--muted);
}
.status[data-kind="error"] { color: #ff7b72; }
.status[data-kind="ok"] { color: #7ee787; }
.result-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 14px;
}
.field {
  min-width: 0;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--panel-2);
  padding: 14px;
}
.field dt {
  color: var(--muted);
  font-size: 12px;
  margin-bottom: 6px;
}
.field dd {
  margin: 0;
  overflow-wrap: anywhere;
}
.field.wide {
  grid-column: 1 / -1;
}
.tag-list {
  display: flex;
  gap: 7px;
  flex-wrap: wrap;
  margin-top: 8px;
}
.tag {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 5px 9px;
  color: var(--muted);
  font-size: 12px;
}
.error-box {
  border-left: 3px solid var(--danger);
}
footer {
  margin-top: 34px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 13px;
  line-height: 1.6;
}
@media (max-width: 760px) {
  main { padding-top: 32px; }
  .problem,
  .result-grid {
    grid-template-columns: 1fr;
  }
  .field.wide {
    grid-column: auto;
  }
  .form-row {
    align-items: stretch;
    flex-direction: column;
  }
  .action {
    width: 100%;
  }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
}
</style>
</head>
<body>
<div class="notice">
  Demo pública com parser real do Atlas. Não é ferramenta oficial de compras públicas.
</div>

<main>
  <div class="eyebrow">Normalizador ao vivo</div>
  <h1>Atlas de Compras Públicas</h1>
  <p class="lead">
    Descrições do PNCP chegam com abreviações, medidas e atributos em texto livre.
    O Atlas transforma esse texto em campos estruturados antes de qualquer comparação.
  </p>

  <div class="links">
    <a href="https://github.com/peedrovinicius/atlas-compras-publicas"
       rel="noopener noreferrer">README</a>
    <a href="https://github.com/peedrovinicius/atlas-compras-publicas/blob/main/docs/architecture.md"
       rel="noopener noreferrer">Arquitetura</a>
    <a href="https://github.com/peedrovinicius/atlas-compras-publicas/blob/main/docs/dashboard-quality-snapshot.html"
       rel="noopener noreferrer">Snapshot de qualidade</a>
    <a href="/docs">Swagger / OpenAPI</a>
  </div>

  <section class="card problem" aria-labelledby="quality-title">
    <div>
      <h2 id="quality-title">O problema em uma linha</h2>
      <p class="lead">
        O mesmo produto pode aparecer escrito de formas diferentes. Comparar o texto bruto
        pode separar itens equivalentes ou aproximar produtos incompatíveis.
      </p>
    </div>
    <div class="metric">
      <strong>91,36%</strong>
      <span>
        micro accuracy ponderada em 984 campos técnicos de 548 exemplos independentes.
      </span>
    </div>
  </section>

  <section class="card" aria-labelledby="demo-title">
    <h2 id="demo-title">Teste o parser</h2>
    <p class="helper">
      Os exemplos abaixo vêm do benchmark odontológico v5. O último é um limite conhecido:
      a categoria esperada no holdout é desconhecida.
    </p>

    <div class="examples" aria-label="Exemplos reais do benchmark v5">
      <button class="example" type="button"
              data-description="RES FOTOP A2 C/2 SERINGAS 4G">Resina A2</button>
      <button class="example" type="button"
              data-description="IONOMERO RESTAURADOR AUTOPOLIMERIZAVEL LIQ 8ML">
        Ionômero
      </button>
      <button class="example" type="button"
              data-description="FLUORETO DE SODIO 2% GEL NEUTRO FRASCO 200ML">
        Flúor gel
      </button>
      <button class="example" type="button"
              data-description="HIDROXIDO DE CALCIO P.A 10G">Hidróxido de cálcio</button>
      <button class="example" type="button"
              data-description="FIXADOR RADIOGRAFICO PRONTO PARA USO LIQUIDO 475ML">
        Fixador
      </button>
      <button class="example" type="button"
              data-description="PRIME ADESIVO FRASCO 4ML">Adesivo</button>
      <button class="example" type="button" data-limit="true"
              data-description="CIMENTO ODONTOLOGICO">Limite conhecido</button>
    </div>

    <label for="description">Descrição do item</label>
    <textarea id="description" maxlength="2000"
              aria-describedby="description-help char-count">RES FOTOP A2 C/2 SERINGAS 4G</textarea>
    <div class="form-row">
      <div>
        <div id="description-help" class="helper">
          Digite entre 3 e 2.000 caracteres.
        </div>
        <div id="char-count" class="counter">29 / 2.000</div>
      </div>
      <button id="run" class="action" type="button">Normalizar</button>
    </div>

    <div id="status" class="status" role="status" aria-live="polite">
      Carregando o exemplo inicial...
    </div>

    <dl id="result" class="result-grid" aria-label="Resultado estruturado">
      <div class="field">
        <dt>Produto</dt>
        <dd id="category">Carregando...</dd>
      </div>
      <div class="field">
        <dt>Cor / concentração</dt>
        <dd id="shade">Carregando...</dd>
      </div>
      <div class="field">
        <dt>Apresentação</dt>
        <dd id="presentation">Carregando...</dd>
      </div>
      <div class="field">
        <dt>Quantidade por unidade</dt>
        <dd id="unit-quantity">Carregando...</dd>
      </div>
      <div class="field">
        <dt>Embalagem</dt>
        <dd id="package-count">Carregando...</dd>
      </div>
      <div class="field">
        <dt>Total físico</dt>
        <dd id="total-quantity">Carregando...</dd>
      </div>
      <div class="field wide">
        <dt>Como foi interpretado</dt>
        <dd id="method">Regras determinísticas do parser versionado.</dd>
        <div id="matched-terms" class="tag-list" aria-label="Termos reconhecidos"></div>
      </div>
      <div class="field wide">
        <dt>Atributos técnicos reconhecidos</dt>
        <dd id="technical-attributes">Carregando...</dd>
      </div>
    </dl>

    <p class="note">
      Em hospedagem gratuita, a primeira resposta após um período de inatividade pode demorar
      mais que as seguintes. A API limita a entrada a 2.000 caracteres e aplica proteção
      básica contra excesso de chamadas.
    </p>
  </section>

  <section class="card" aria-labelledby="scope-title">
    <h2 id="scope-title">O que esta demo prova</h2>
    <p class="lead">
      A normalização acima executa o mesmo parser versionado do repositório. Ela não simula
      preços, homologações ou sinais estatísticos. Esses painéis dependem da base DuckDB
      consolidada e permanecem fora da demo enquanto essa base não estiver publicável.
    </p>
  </section>

  <footer>
    Atlas de Compras Públicas v__ATLAS_VERSION__. Código aberto no GitHub.
    Limite da demo: 60 normalizações por minuto por IP.
  </footer>
</main>

<script>
"use strict";

const input = document.getElementById("description");
const button = document.getElementById("run");
const statusNode = document.getElementById("status");
const counter = document.getElementById("char-count");

const categoryLabels = {
  composite_resin: "Resina composta",
  flowable_resin: "Resina flow",
  dental_adhesive: "Adesivo odontológico",
  glass_ionomer: "Ionômero de vidro",
  phosphoric_acid: "Ácido fosfórico",
  alginate: "Alginato",
  fluoride_gel: "Gel fluoretado",
  prophylaxis_paste: "Pasta profilática",
  calcium_hydroxide: "Hidróxido de cálcio",
  zinc_oxide: "Óxido de zinco",
  eugenol: "Eugenol",
  radiographic_fixer: "Fixador radiográfico",
  radiographic_developer: "Revelador radiográfico",
  local_anesthetic: "Anestésico local",
  unknown: "Não reconhecido"
};

const presentationLabels = {
  syringe: "Seringa",
  tube: "Tubo",
  bottle: "Frasco",
  jar: "Pote",
  kit: "Kit"
};

function setText(id, value) {
  const node = document.getElementById(id);
  const isEmpty = value === null || value === undefined || value === "";
  node.textContent = isEmpty ? "Não identificado" : value;
}

function formatQuantity(quantity) {
  if (!quantity) return "Não identificada";
  return quantity.value + " " + quantity.unit;
}

function updateCounter() {
  counter.textContent = input.value.length.toLocaleString("pt-BR") + " / 2.000";
}

function renderTags(values) {
  const target = document.getElementById("matched-terms");
  target.replaceChildren();

  if (!values || values.length === 0) {
    const empty = document.createElement("span");
    empty.className = "tag";
    empty.textContent = "Nenhum termo registrado";
    target.appendChild(empty);
    return;
  }

  values.forEach(function (value) {
    const tag = document.createElement("span");
    tag.className = "tag";
    tag.textContent = value;
    target.appendChild(tag);
  });
}

function renderAttributes(attributes) {
  const pairs = Object.entries(attributes || {}).filter(function (entry) {
    return entry[1] !== null && entry[1] !== undefined;
  });

  if (pairs.length === 0) {
    setText("technical-attributes", "Nenhum atributo técnico adicional identificado");
    return;
  }

  const value = pairs.map(function (entry) {
    return entry[0] + ": " + entry[1];
  }).join(" | ");
  setText("technical-attributes", value);
}

function renderResult(data) {
  const category = categoryLabels[data.category] || data.category;
  const presentation = presentationLabels[data.presentation] || data.presentation;
  const shadeParts = [];

  if (data.shade) shadeParts.push("Cor " + data.shade);
  if (data.concentration_percent) {
    shadeParts.push("Concentração " + data.concentration_percent + "%");
  }

  setText("category", category);
  setText("shade", shadeParts.length ? shadeParts.join(" | ") : "Não identificada");
  setText("presentation", presentation || "Não identificada");
  setText("unit-quantity", formatQuantity(data.unit_quantity));
  setText("package-count", data.package_count ? data.package_count + " unidade(s)" : null);
  setText("total-quantity", formatQuantity(data.total_quantity));
  setText("method", "Regras determinísticas | resolução: " + data.measurement_resolution);
  renderTags(data.matched_terms);
  renderAttributes(data.technical_attributes);
}

function setStatus(message, kind) {
  statusNode.textContent = message;
  statusNode.dataset.kind = kind || "";
}

async function normalize() {
  const description = input.value.trim();

  if (description.length < 3) {
    setStatus("Digite pelo menos 3 caracteres.", "error");
    input.focus();
    return;
  }

  if (description.length > 2000) {
    setStatus("A descrição ultrapassa o limite de 2.000 caracteres.", "error");
    input.focus();
    return;
  }

  button.disabled = true;
  button.textContent = "Processando...";
  setStatus("Consultando o parser do Atlas...", "");

  try {
    const endpoint = "/api/v1/normalize?description=";
    const response = await fetch(endpoint + encodeURIComponent(description));
    const data = await response.json();

    if (!response.ok) {
      const detail = data.detail || "A API recusou a solicitação.";
      throw new Error(typeof detail === "string" ? detail : "Entrada inválida.");
    }

    renderResult(data);
    setStatus("Normalização concluída pelo parser atual.", "ok");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Falha ao consultar a API.";
    setStatus(message, "error");
  } finally {
    button.disabled = false;
    button.textContent = "Normalizar";
  }
}

document.querySelectorAll(".example").forEach(function (example) {
  example.addEventListener("click", function () {
    input.value = example.dataset.description || "";
    updateCounter();
    normalize();
  });
});

input.addEventListener("input", updateCounter);
button.addEventListener("click", normalize);
window.addEventListener("DOMContentLoaded", function () {
  updateCounter();
  normalize();
});
</script>
</body>
</html>
"""


def render_demo(version: str) -> str:
    return DEMO_HTML.replace("__ATLAS_VERSION__", version)
