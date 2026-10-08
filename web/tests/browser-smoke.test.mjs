import assert from "node:assert/strict";
import { after, before, test } from "node:test";
import { chromium } from "playwright";

let browser;
before(async () => { browser = await chromium.launch({ headless: true }); });
after(async () => { await browser?.close(); });

async function openAtlas(viewport) {
  const context = await browser.newContext({ viewport, reducedMotion: "reduce" });
  const page = await context.newPage();
  await page.route("https://atlas-compras-publicas-analytics.onrender.com/**", route => {
    const url = route.request().url();
    const body = url.includes("/parser/categories") ? [] :
      url.includes("/health") ? { ok: true, version: "test" } :
      url.includes("/products/discovery") ? { items: [] } : { items: [] };
    return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
  });
  await page.goto("http://127.0.0.1:4173/", { waitUntil: "domcontentloaded" });
  return { page, context };
}

test("desktop: navigation switches between prices and laboratory", async () => {
  const { page, context } = await openAtlas({ width: 1280, height: 800 });
  try {
    assert.equal(await page.getByRole("button", { name: "Preços", exact: true }).getAttribute("aria-pressed"), "true");
    await page.getByRole("button", { name: "Laboratório" }).click();
    assert.equal(await page.getByRole("button", { name: "Laboratório" }).getAttribute("aria-pressed"), "true");
    assert.equal(await page.locator("#descriptions").count(), 1);
    await page.getByRole("button", { name: "Preços", exact: true }).click();
    assert.equal(await page.getByRole("button", { name: "Preços", exact: true }).getAttribute("aria-pressed"), "true");
  } finally { await context.close(); }
});

test("keyboard: skip link reaches main content", async () => {
  const { page, context } = await openAtlas({ width: 1280, height: 800 });
  try {
    await page.keyboard.press("Tab");
    assert.equal(await page.evaluate(() => document.activeElement?.textContent?.trim()), "Ir para o conteúdo");
    await page.keyboard.press("Enter");
    assert.equal(new URL(page.url()).hash, "#main-content");
  } finally { await context.close(); }
});

for (const width of [320, 375, 390, 768]) {
  test(`mobile ${width}px: navigation works without horizontal document overflow`, async () => {
    const { page, context } = await openAtlas({ width, height: 812 });
    try {
      await page.getByRole("button", { name: "Laboratório" }).click();
      assert.equal(await page.locator("#descriptions").count(), 1);
      const measurements = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        viewportWidth: document.documentElement.clientWidth,
      }));
      assert.ok(measurements.scrollWidth <= measurements.viewportWidth + 2,
        `Horizontal overflow: ${JSON.stringify(measurements)}`);
    } finally { await context.close(); }
  });
}
