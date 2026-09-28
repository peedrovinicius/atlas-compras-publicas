"""Página pública simples e focada da demo do Atlas."""

import json
from html import escape

from dental_procurement_intelligence.identity.models import ProductCategory

_CATEGORY_LABELS = {
    ProductCategory.COMPOSITE_RESIN: "Resina composta",
    ProductCategory.FLOWABLE_RESIN: "Resina flow",
    ProductCategory.ADHESIVE: "Adesivo odontológico",
    ProductCategory.GLASS_IONOMER: "Ionômero de vidro",
    ProductCategory.PHOSPHORIC_ACID: "Ácido fosfórico",
    ProductCategory.ALGINATE: "Alginato",
    ProductCategory.FLUORIDE_GEL: "Gel fluoretado",
    ProductCategory.PROPHYLAXIS_PASTE: "Pasta profilática",
    ProductCategory.CALCIUM_HYDROXIDE: "Hidróxido de cálcio",
    ProductCategory.ZINC_OXIDE: "Óxido de zinco",
    ProductCategory.EUGENOL: "Eugenol",
    ProductCategory.RADIOGRAPHIC_FIXER: "Fixador radiográfico",
    ProductCategory.RADIOGRAPHIC_DEVELOPER: "Revelador radiográfico",
    ProductCategory.LOCAL_ANESTHETIC: "Anestésico local",
    ProductCategory.UNKNOWN: "Não reconhecido",
}

DEMO_HTML = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description"
      content="Teste o normalizador do Atlas de Compras Públicas com descrições do PNCP.">
<title>Atlas | Testar normalização</title>
<style>
:root {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
  color: #171717;
  background: #f7f7f5;
  --bg: #f7f7f5;
  --surface: #ffffff;
  --text: #171717;
  --muted: #6b6b6b;
  --line: #deded9;
  --soft: #f1f1ee;
  --accent: #171717;
  --ok: #237a3b;
  --error: #b42318;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
}
button,
textarea {
  font: inherit;
}
a { color: inherit; }
.shell {
  width: min(1120px, calc(100vw - 32px));
  margin: 0 auto;
  padding: 28px 0 56px;
}
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 62px;
}
.brand {
  font-weight: 750;
  letter-spacing: -.02em;
}
.toplinks {
  display: flex;
  gap: 18px;
  font-size: 14px;
  color: var(--muted);
}
.toplinks a {
  text-decoration: none;
}
.toplinks a:hover {
  color: var(--text);
}
.hero {
  max-width: 760px;
  margin-bottom: 34px;
}
.eyebrow {
  color: var(--muted);
  font-size: 13px;
  margin-bottom: 10px;
}
h1 {
  margin: 0;
  font-size: clamp(38px, 7vw, 68px);
  line-height: .98;
  letter-spacing: -.055em;
  font-weight: 760;
}
.hero p {
  margin: 20px 0 0;
  color: var(--muted);
  font-size: 18px;
  line-height: 1.55;
  max-width: 660px;
}
.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(280px, .85fr);
  gap: 18px;
  align-items: start;
}
.panel {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 18px;
}
.test-panel {
  padding: 26px;
}
.list-panel {
  padding: 22px;
}
.panel-title {
  margin: 0 0 6px;
  font-size: 18px;
  letter-spacing: -.02em;
}
.panel-copy {
  margin: 0 0 20px;
  color: var(--muted);
  line-height: 1.5;
  font-size: 14px;
}
label {
  display: block;
  margin-bottom: 9px;
  font-size: 14px;
  font-weight: 650;
}
textarea {
  width: 100%;
  min-height: 122px;
  resize: vertical;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: #fbfbfa;
  color: var(--text);
  padding: 14px 15px;
  line-height: 1.45;
}
textarea:focus {
  outline: 3px solid #e7e7e3;
  border-color: #a5a5a0;
}
.actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}
.primary {
  border: 0;
  border-radius: 10px;
  background: var(--accent);
  color: white;
  padding: 11px 18px;
  font-weight: 700;
  cursor: pointer;
}
.primary[disabled] {
  opacity: .55;
  cursor: wait;
}
.status {
  color: var(--muted);
  font-size: 13px;
}
.status[data-kind="ok"] { color: var(--ok); }
.status[data-kind="error"] { color: var(--error); }
.result {
  margin-top: 26px;
  padding-top: 22px;
  border-top: 1px solid var(--line);
}
.result-label {
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: .08em;
  margin-bottom: 8px;
}
.result-main {
  font-size: 23px;
  line-height: 1.35;
  letter-spacing: -.025em;
  font-weight: 700;
}
.result-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 14px;
}
.meta {
  background: var(--soft);
  border-radius: 999px;
  padding: 7px 10px;
  font-size: 12px;
  color: #494949;
}
.categories {
  list-style: none;
  padding: 0;
  margin: 0;
}
.categories li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #ecece8;
  font-size: 14px;
}
.categories li:last-child {
  border-bottom: 0;
}
.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #92928c;
  flex: 0 0 auto;
}
.categories li[data-fallback="true"] {
  color: var(--muted);
}
.examples {
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid var(--line);
}
.examples-title {
  color: var(--muted);
  font-size: 12px;
  margin-bottom: 10px;
}
.example-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}
.example-buttons button {
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--surface);
  color: var(--text);
  padding: 7px 10px;
  font-size: 12px;
  cursor: pointer;
}
.example-buttons button:hover {
  background: var(--soft);
}
details {
  margin-top: 18px;
}
summary {
  cursor: pointer;
  color: var(--muted);
  font-size: 13px;
}
.technical {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 20px;
  margin-top: 16px;
}
.technical dt {
  color: var(--muted);
  font-size: 11px;
}
.technical dd {
  margin: 3px 0 0;
  font-size: 13px;
  overflow-wrap: anywhere;
}
footer {
  margin-top: 28px;
  color: var(--muted);
  font-size: 12px;
  display: flex;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
}
footer a {
  color: var(--muted);
  text-decoration: none;
}
footer a:hover {
  color: var(--text);
}
@media (max-width: 820px) {
  .topbar {
    margin-bottom: 42px;
  }
  .workspace {
    grid-template-columns: 1fr;
  }
  .list-panel {
    order: 2;
  }
}
@media (max-width: 560px) {
  .shell {
    width: min(100% - 20px, 1120px);
    padding-top: 18px;
  }
  .toplinks {
    gap: 10px;
  }
  .toplinks .optional {
    display: none;
  }
  .test-panel,
  .list-panel {
    padding: 18px;
  }
  h1 {
    font-size: 42px;
  }
  .hero p {
    font-size: 16px;
  }
  .actions {
    align-items: stretch;
    flex-direction: column;
  }
  .primary {
    width: 100%;
  }
  .technical {
    grid-template-columns: 1fr;
  }
}
</style>
</head>
<body>
<div class="shell">
  <header class="topbar">
    <div class="brand">Atlas</div>
    <nav class="toplinks" aria-label="Links principais">
      <a href="/docs">API</a>
      <a class="optional"
         href="https://github.com/peedrovinicius/atlas-compras-publicas">GitHub</a>
    </nav>
  </header>

  <section class="hero">
    <div class="eyebrow">Normalizador de descrições do PNCP</div>
    <h1>Teste uma descrição.</h1>
    <p>
      Cole o texto exatamente como aparece na compra pública. O Atlas mostra o que
      conseguiu identificar e deixa explícito quando não reconhece o produto.
    </p>
  </section>

  <div class="workspace">
    <section class="panel test-panel" aria-labelledby="test-title">
      <h2 id="test-title" class="panel-title">Testar agora</h2>
      <p class="panel-copy">
        Você pode apagar o exemplo e escrever qualquer outra descrição.
      </p>

      <label for="description">Descrição</label>
      <textarea id="description" maxlength="2000">RES FOTOP A2 C/2 SERINGAS 4G</textarea>

      <div class="actions">
        <button id="run" class="primary" type="button">Analisar</button>
        <div id="status" class="status" role="status" aria-live="polite">
          Analisando o exemplo...
        </div>
      </div>

      <div class="result">
        <div class="result-label">Resultado</div>
        <div id="result-main" class="result-main">Carregando...</div>
        <div id="result-meta" class="result-meta"></div>
      </div>

      <div class="examples">
        <div class="examples-title">Exemplos rápidos</div>
        <div class="example-buttons">
          <button type="button" data-description="RES FOTOP A2 C/2 SERINGAS 4G">
            Resina A2
          </button>
          <button type="button"
                  data-description="IONOMERO RESTAURADOR AUTOPOLIMERIZAVEL LIQ 8ML">
            Ionômero
          </button>
          <button type="button"
                  data-description="FLUORETO DE SODIO 2% GEL NEUTRO FRASCO 200ML">
            Flúor gel
          </button>
          <button type="button" data-description="HIDROXIDO DE CALCIO P.A 10G">
            Hidróxido de cálcio
          </button>
          <button type="button" data-description="CIMENTO ODONTOLOGICO">
            Caso difícil
          </button>
        </div>
      </div>

      <details>
        <summary>Ver detalhes técnicos</summary>
        <dl class="technical">
          <div>
            <dt>Categoria interna</dt>
            <dd id="category">...</dd>
          </div>
          <div>
            <dt>Apresentação</dt>
            <dd id="presentation">...</dd>
          </div>
          <div>
            <dt>Cor</dt>
            <dd id="shade">...</dd>
          </div>
          <div>
            <dt>Concentração</dt>
            <dd id="concentration">...</dd>
          </div>
          <div>
            <dt>Quantidade por unidade</dt>
            <dd id="unit-quantity">...</dd>
          </div>
          <div>
            <dt>Embalagem</dt>
            <dd id="package-count">...</dd>
          </div>
          <div>
            <dt>Total físico</dt>
            <dd id="total-quantity">...</dd>
          </div>
          <div>
            <dt>Resolução da medida</dt>
            <dd id="measurement-resolution">...</dd>
          </div>
          <div>
            <dt>Termos reconhecidos</dt>
            <dd id="matched-terms">...</dd>
          </div>
          <div>
            <dt>Atributos técnicos</dt>
            <dd id="technical-attributes">...</dd>
          </div>
        </dl>
      </details>
    </section>

    <aside class="panel list-panel" aria-labelledby="list-title">
      <h2 id="list-title" class="panel-title">O que reconhece hoje</h2>
      <p class="panel-copy">
        Esta lista vem diretamente do parser atual.
      </p>
      <ul class="categories">
        __SUPPORTED_CATEGORIES__
      </ul>
    </aside>
  </div>

  <footer>
    <span>Atlas de Compras Públicas v__ATLAS_VERSION__</span>
    <span>60 análises/minuto por IP · até 2.000 caracteres</span>
  </footer>
</div>

<script>
"use strict";

const input = document.getElementById("description");
const button = document.getElementById("run");
const statusNode = document.getElementById("status");
const resultMain = document.getElementById("result-main");
const resultMeta = document.getElementById("result-meta");
const labels = __CATEGORY_LABELS__;

const presentationLabels = {
  syringe: "Seringa",
  tube: "Tubo",
  bottle: "Frasco",
  jar: "Pote",
  kit: "Kit"
};

function text(id, value) {
  const node = document.getElementById(id);
  const empty = value === null || value === undefined || value === "";
  node.textContent = empty ? "Não identificado" : value;
}

function quantity(value) {
  if (!value) return null;
  return value.value + " " + value.unit;
}

function addMeta(value) {
  if (!value) return;
  const item = document.createElement("span");
  item.className = "meta";
  item.textContent = value;
  resultMeta.appendChild(item);
}

function technicalAttributes(value) {
  const pairs = Object.entries(value || {}).filter(function (entry) {
    return entry[1] !== null && entry[1] !== undefined;
  });
  if (!pairs.length) return "Nenhum";
  return pairs.map(function (entry) {
    return entry[0] + ": " + entry[1];
  }).join(" | ");
}

function render(data) {
  const category = labels[data.category] || data.category;
  const presentation = presentationLabels[data.presentation] || data.presentation;

  resultMain.textContent = category;
  resultMeta.replaceChildren();

  if (data.shade) addMeta("Cor " + data.shade);
  if (data.concentration_percent) {
    addMeta(data.concentration_percent + "%");
  }
  if (presentation) addMeta(presentation);
  if (data.package_count) addMeta(data.package_count + " un");
  if (data.unit_quantity) addMeta(quantity(data.unit_quantity) + "/un");
  if (data.total_quantity) addMeta(quantity(data.total_quantity) + " total");

  text("category", data.category);
  text("presentation", presentation);
  text("shade", data.shade);
  text("concentration", data.concentration_percent);
  text("unit-quantity", quantity(data.unit_quantity));
  text("package-count", data.package_count);
  text("total-quantity", quantity(data.total_quantity));
  text("measurement-resolution", data.measurement_resolution);
  text("matched-terms", (data.matched_terms || []).join(", ") || "Nenhum");
  text("technical-attributes", technicalAttributes(data.technical_attributes));
}

function status(message, kind) {
  statusNode.textContent = message;
  statusNode.dataset.kind = kind || "";
}

async function normalize() {
  const description = input.value.trim();

  if (description.length < 3) {
    status("Digite pelo menos 3 caracteres.", "error");
    input.focus();
    return;
  }

  button.disabled = true;
  button.textContent = "Analisando...";
  status("Consultando o parser...", "");

  try {
    const endpoint = "/api/v1/normalize?description=";
    const response = await fetch(endpoint + encodeURIComponent(description));
    const data = await response.json();

    if (!response.ok) {
      const detail = data.detail || "Não foi possível analisar essa descrição.";
      throw new Error(typeof detail === "string" ? detail : "Entrada inválida.");
    }

    render(data);
    status("Pronto.", "ok");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Falha ao consultar a API.";
    status(message, "error");
  } finally {
    button.disabled = false;
    button.textContent = "Analisar";
  }
}

document.querySelectorAll(".example-buttons button").forEach(function (example) {
  example.addEventListener("click", function () {
    input.value = example.dataset.description || "";
    normalize();
  });
});

button.addEventListener("click", normalize);
window.addEventListener("DOMContentLoaded", normalize);
</script>
</body>
</html>
"""


def parser_categories() -> list[dict[str, str | bool]]:
    return [
        {
            "id": category.value,
            "label": _CATEGORY_LABELS[category],
            "fallback": category is ProductCategory.UNKNOWN,
        }
        for category in ProductCategory
    ]


def render_demo(version: str) -> str:
    labels = {
        category.value: label
        for category, label in _CATEGORY_LABELS.items()
    }
    labels_json = json.dumps(labels, ensure_ascii=False)
    supported = "\n".join(
        (
            f'<li data-fallback="{str(item["fallback"]).lower()}">'
            '<span class="dot" aria-hidden="true"></span>'
            + escape(str(item["label"]))
            + "</li>"
        )
        for item in parser_categories()
    )
    return (
        DEMO_HTML.replace("__ATLAS_VERSION__", version)
        .replace("__CATEGORY_LABELS__", labels_json)
        .replace("__SUPPORTED_CATEGORIES__", supported)
    )
