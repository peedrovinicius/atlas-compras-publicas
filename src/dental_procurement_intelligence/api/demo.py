"""Página pública simples da demo do Atlas."""

from html import escape
import json

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
      content="Teste simples do normalizador do Atlas de Compras Públicas.">
<title>Atlas | Teste do parser</title>
<style>
:root {
  color-scheme: dark;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
  --bg: #0d1117;
  --panel: #161b22;
  --border: #30363d;
  --text: #e6edf3;
  --muted: #9da7b3;
  --link: #58a6ff;
  --ok: #7ee787;
  --error: #ff7b72;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); }
main {
  width: min(760px, 92vw);
  margin: 0 auto;
  padding: 48px 0 64px;
}
h1 { margin: 0 0 12px; font-size: clamp(34px, 7vw, 56px); line-height: 1; }
h2 { margin: 0 0 12px; font-size: 20px; }
p { color: var(--muted); line-height: 1.6; }
.card {
  margin-top: 28px;
  padding: 22px;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: var(--panel);
}
label { display: block; margin-bottom: 10px; font-weight: 700; }
textarea {
  width: 100%;
  min-height: 100px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--bg);
  color: var(--text);
  padding: 14px;
  resize: vertical;
  font: inherit;
}
button {
  margin-top: 12px;
  border: 0;
  border-radius: 10px;
  background: var(--text);
  color: var(--bg);
  padding: 11px 18px;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}
button[disabled] { opacity: .65; cursor: wait; }
.status {
  min-height: 22px;
  margin-top: 12px;
  color: var(--muted);
  font-size: 14px;
}
.status[data-kind="ok"] { color: var(--ok); }
.status[data-kind="error"] { color: var(--error); }
.result {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--bg);
  font-size: 18px;
  line-height: 1.55;
}
.supported {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}
.supported span {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 7px 10px;
  font-size: 13px;
}
.supported span[data-unknown="true"] {
  color: var(--muted);
  border-style: dashed;
}
details {
  margin-top: 18px;
  border-top: 1px solid var(--border);
  padding-top: 14px;
}
summary { cursor: pointer; color: var(--link); }
.examples {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}
.examples button {
  margin: 0;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--bg);
  color: var(--text);
  padding: 7px 10px;
  font-size: 13px;
}
dl {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 18px;
}
dt { color: var(--muted); font-size: 12px; }
dd { margin: 4px 0 0; overflow-wrap: anywhere; }
.links {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
  font-size: 14px;
}
a { color: var(--link); }
footer {
  margin-top: 32px;
  color: var(--muted);
  font-size: 12px;
}
@media (max-width: 620px) {
  main { padding-top: 32px; }
  dl { grid-template-columns: 1fr; }
  button#run { width: 100%; }
}
</style>
</head>
<body>
<main>
  <h1>Teste o Atlas</h1>
  <p>
    Cole uma descrição de item do PNCP e veja o que o parser consegue identificar.
  </p>

  <section class="card">
    <label for="description">Descrição do item</label>
    <textarea id="description" maxlength="2000">RES FOTOP A2 C/2 SERINGAS 4G</textarea>
    <button id="run" type="button">Testar</button>

    <div id="status" class="status" role="status" aria-live="polite">
      Testando o exemplo inicial...
    </div>

    <div id="result" class="result">Carregando...</div>
  </section>

  <section class="card">
    <h2>Tudo que o parser reconhece hoje</h2>
    <p>
      Use esta lista para escolher o que testar. Se a descrição não corresponder a
      nenhuma categoria suportada, o Atlas retorna “Não reconhecido”.
    </p>
    <div class="supported" aria-label="Categorias suportadas">
      __SUPPORTED_CATEGORIES__
    </div>

    <details>
      <summary>Usar exemplos prontos</summary>
      <div class="examples">
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
        <button type="button"
                data-description="FIXADOR RADIOGRAFICO PRONTO PARA USO LIQUIDO 475ML">
          Fixador
        </button>
        <button type="button" data-description="PRIME ADESIVO FRASCO 4ML">
          Adesivo
        </button>
        <button type="button" data-description="CIMENTO ODONTOLOGICO">
          Caso difícil
        </button>
      </div>
    </details>
  </section>

  <section class="card">
    <details>
      <summary>Ver detalhes técnicos do resultado</summary>
      <dl>
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

  <div class="links">
    <a href="/docs">Swagger / OpenAPI</a>
    <a href="https://github.com/peedrovinicius/atlas-compras-publicas">
      Repositório
    </a>
  </div>

  <footer>
    Atlas de Compras Públicas v__ATLAS_VERSION__.
    Limite da demo: 60 normalizações por minuto por IP.
  </footer>
</main>

<script>
"use strict";

const input = document.getElementById("description");
const button = document.getElementById("run");
const statusNode = document.getElementById("status");

const labels = __CATEGORY_LABELS__;

const presentationLabels = {
  syringe: "seringa",
  tube: "tubo",
  bottle: "frasco",
  jar: "pote",
  kit: "kit"
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

function attributes(value) {
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
  const pieces = [category];

  if (data.shade) pieces.push("cor " + data.shade);
  if (data.concentration_percent) {
    pieces.push(data.concentration_percent + "%");
  }
  if (presentation) pieces.push(presentation);
  if (data.package_count) pieces.push(data.package_count + " un");
  if (data.unit_quantity) pieces.push(quantity(data.unit_quantity) + "/un");
  if (data.total_quantity) pieces.push(quantity(data.total_quantity) + " total");

  document.getElementById("result").textContent = pieces.join(" | ");

  text("category", data.category);
  text("presentation", presentation);
  text("shade", data.shade);
  text("concentration", data.concentration_percent);
  text("unit-quantity", quantity(data.unit_quantity));
  text("package-count", data.package_count);
  text("total-quantity", quantity(data.total_quantity));
  text("measurement-resolution", data.measurement_resolution);
  text("matched-terms", (data.matched_terms || []).join(", ") || "Nenhum");
  text("technical-attributes", attributes(data.technical_attributes));
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
  button.textContent = "Testando...";
  status("Consultando o parser...", "");

  try {
    const endpoint = "/api/v1/normalize?description=";
    const response = await fetch(endpoint + encodeURIComponent(description));
    const data = await response.json();

    if (!response.ok) {
      const detail = data.detail || "Não foi possível testar essa descrição.";
      throw new Error(typeof detail === "string" ? detail : "Entrada inválida.");
    }

    render(data);
    status("Pronto.", "ok");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Falha ao consultar a API.";
    status(message, "error");
  } finally {
    button.disabled = false;
    button.textContent = "Testar";
  }
}

document.querySelectorAll(".examples button").forEach(function (example) {
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
            '<span data-unknown="true">'
            if item["fallback"]
            else "<span>"
        )
        + escape(str(item["label"]))
        + "</span>"
        for item in parser_categories()
    )
    return (
        DEMO_HTML.replace("__ATLAS_VERSION__", version)
        .replace("__CATEGORY_LABELS__", labels_json)
        .replace("__SUPPORTED_CATEGORIES__", supported)
    )
