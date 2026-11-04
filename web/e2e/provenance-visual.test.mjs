import assert from "node:assert/strict";
import { mkdir, readFile } from "node:fs/promises";
import { after, before, test } from "node:test";
import { chromium } from "playwright";

const API = "https://atlas-compras-publicas-analytics.onrender.com";
const PRODUCT_ID = "f".repeat(32);
const SCREENSHOTS = "e2e/artifacts";
const labels = {
  pncp_sample: "Amostra obtida do PNCP",
  offline_synthetic: "Dados demonstrativos — preços fictícios",
  unknown: "Origem dos dados não verificada",
};

let browser;
before(async () => {
  await mkdir(SCREENSHOTS, { recursive: true });
  browser = await chromium.launch({ headless: true });
});
after(async () => { await browser?.close(); });

const product = {
  product_id: PRODUCT_ID, product_category: "composite_resin",
  presentation: "syringe", shade: "A2", normalized_quantity_unit: "un",
  award_count: 12, procurement_count: 1, supplier_count: 12, state_count: 1,
  priced_observation_count: 12, min_price: 78.90,
  percentile_25: 83.20, median_price: 88.50, percentile_75: 96.10,
  max_price: 107.50, latest_date: "2026-06-19",
  sample_description: "Resina de demonstração em seringa",
  display_name: "Resina composta A2", relevance_score: 1, match_reasons: [],
};

const summary = {
  ...product, item_count: 1, period_start: "2026-01-15",
  period_end: "2026-06-19", latest_update: "2026-06-19",
  price_sample_count: 12, minimum_sample_size: 5,
  sample_sufficient: true, price_unit: "un",
  price_stats: {
    median_price: 88.5, average_price: 91.2, min_price: 78.9, max_price: 107.5,
    percentile_25: 83.2, percentile_75: 96.1, standard_deviation: 9.3,
    total_physical_quantity: 120,
  },
};

function provenance(source) {
  if (source === "unknown") return undefined;
  return {
    source_type: source,
    captured_at: "2026-11-03T20:00:00+00:00",
    procurement_keys: [
      source === "pncp_sample"
        ? "pncp:15126437000305:2026:212"
        : "pncp:00000000000000:2026:1",
    ],
    procurement_count: 1, result_count: 12, observation_count: 12,
    notice: "Metadados de ensaio do navegador, não observações da produção.",
  };
}

function responseFor(url, source) {
  const path = new URL(url).pathname;
  if (path === "/health") return { status: "ok", version: "test" };
  if (path === "/api/v1/meta") return { version: "test", provenance: provenance(source) };
  if (path === "/api/v1/parser/categories") return [];
  if (path === "/api/v1/products/discovery") return { items: [] };
  if (path === "/api/v1/products/search") {
    return {
      query: "resina", sort: "relevance", interpreted_category: null,
      interpreted_label: null, filters: {}, items: [product], facets: {},
      total: 1, limit: 10, offset: 0,
    };
  }
  const stem = `/api/v1/products/${PRODUCT_ID}`;
  if (path === stem) return summary;
  if (path === stem + "/distribution") {
    return {
      product_id: PRODUCT_ID, observations: 12, bin_count: 5, min_price: 78.9,
      max_price: 107.5, bins: [],
    };
  }
  if (path === stem + "/history") {
    return { product_id: PRODUCT_ID, points: [], total_observations: 12 };
  }
  if (path === stem + "/regions") {
    return {
      product_id: PRODUCT_ID,
      national: { observations: 12, procurement_count: 1, state_count: 1, median_price: 88.5 },
      regions: [], states: [],
    };
  }
  for (const part of ["suppliers", "buyers", "signals", "records"]) {
    if (path === stem + "/" + part) {
      return {
        product_id: PRODUCT_ID, items: [], total: 0, limit: 12, offset: 0,
        ...(part === "signals" ? { disclaimer: "Simulação sem dados reais" } : {}),
      };
    }
  }
  return { items: [] };
}

async function openAtlas(source, viewport) {
  const context = await browser.newContext({
    viewport, reducedMotion: "reduce", acceptDownloads: true,
  });
  const page = await context.newPage();
  const pageErrors = [];
  page.on("pageerror", error => pageErrors.push(error.message));

  await page.route(`${API}/**`, route => {
    const url = route.request().url();
    const path = new URL(url).pathname;
    if (path.endsWith("/records.csv")) {
      return route.fulfill({
        status: 200,
        headers: {
          "Content-Type": "text/csv; charset=utf-8",
          "X-Atlas-Provenance": source,
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Expose-Headers": "X-Atlas-Provenance",
        },
        body: `data_source_type,award_key\n${source},a1\n`,
      });
    }
    return route.fulfill({
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
      body: JSON.stringify(responseFor(url, source)),
    });
  });
  await page.goto("http://127.0.0.1:4173/", { waitUntil: "domcontentloaded" });
  await page.getByRole("status", { name: "Proveniência dos dados" })
    .getByText(labels[source], { exact: true }).waitFor();
  return { page, context, pageErrors };
}

for (const source of ["pncp_sample", "offline_synthetic", "unknown"]) {
  for (const width of [1280, 375]) {
    test(`provenance ${source}: visible at ${width}px without horizontal overflow`, async () => {
      const { page, context, pageErrors } = await openAtlas(source, { width, height: 850 });
      try {
        const banner = page.getByRole("status", { name: "Proveniência dos dados" });
        assert.equal(await banner.count(), 1);
        const message = await banner.innerText();
        assert.ok(message.includes(labels[source]));
        if (source !== "pncp_sample") {
          assert.match(message, /fictíci|não verificada/i);
          assert.ok(!(await page.locator(".analytics-hero").innerText()).includes("preços homologados"));
        }
        const overflow = await page.evaluate(() => ({
          body: document.documentElement.scrollWidth,
          viewport: document.documentElement.clientWidth,
        }));
        assert.ok(overflow.body <= overflow.viewport + 2, JSON.stringify(overflow));
        assert.deepEqual(pageErrors, []);
        await page.screenshot({
          path: `${SCREENSHOTS}/${source}-${width}.png`, fullPage: true,
        });
      } finally {
        await context.close();
      }
    });
  }
}

for (const source of ["pncp_sample", "offline_synthetic", "unknown"]) {
  test(`report PDF and CSV preserve ${source} label`, async () => {
    const { page, context, pageErrors } = await openAtlas(source, { width: 1280, height: 900 });
    try {
      await page.locator("#analytics-search").fill("resina");
      await page.getByRole("button", { name: "Pesquisar", exact: true }).click();
      await page.locator(".analytics-result-main").first().click();
      await page.locator("#analytics-detail-title").waitFor();

      const report = page.locator(".analytics-print-report");
      assert.ok((await report.innerText()).includes(labels[source]));
      const sourceText = await report.locator(".analytics-print-report-footer").innerText();
      if (source === "pncp_sample") {
        assert.match(sourceText, /PNCP/i);
      } else {
        assert.match(sourceText, /não verificada|sintéticos/i);
      }

      // A prova print usa exatamente a folha A4 e o CSS de produção.
      await page.emulateMedia({ media: "print" });
      assert.equal(await page.locator(".analytics-print-provenance").isVisible(), true);
      const pdf = await page.pdf({
        path: `${SCREENSHOTS}/report-${source}.pdf`,
        format: "A4", printBackground: true,
      });
      assert.ok(pdf.byteLength > 3000);
      // Evita regressão: elementos invisíveis não podem gerar folhas vazias.
      const pages = pdf.toString("latin1").match(/\\/Type\\s*\\/Page\\b/g) ?? [];
      assert.equal(pages.length, 1, "Relatório de teste gerou folhas adicionais");
      await page.emulateMedia({ media: "screen" });

      await page.locator(".analytics-actions-menu summary").click();
      const event = page.waitForEvent("download");
      await page.getByRole("button", { name: "Exportar CSV" }).click();
      const download = await event;
      const name = download.suggestedFilename();
      const label = source === "pncp_sample"
        ? "pncp"
        : source === "offline_synthetic" ? "sintetico" : "origem-desconhecida";
      assert.ok(name.includes(label), name);
      const csv = await readFile(await download.path(), "utf8");
      assert.match(csv, new RegExp(`^${source},a1$`, "m"));
      assert.deepEqual(pageErrors, []);
    } finally {
      await context.close();
    }
  });
}
