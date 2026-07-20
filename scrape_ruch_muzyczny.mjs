#!/usr/bin/env node

import { chromium } from "playwright-core";
import { mkdir, readFile, writeFile, appendFile } from "node:fs/promises";
import path from "node:path";

const DEFAULT_CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const BASE_URL = "https://ruchmuzyczny.pl";

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
}

const fromId = Number(arg("from", "1"));
const toId = Number(arg("to", "6500"));
const delayMs = Number(arg("delay", "350"));
const outputDir = path.resolve(arg("output", "input_html/RuchMuzyczny"));
const chromePath = arg("chrome", DEFAULT_CHROME);
const headless = !process.argv.includes("--show-browser");

if (!Number.isInteger(fromId) || !Number.isInteger(toId) || fromId < 1 || toId < fromId) {
  throw new Error("Nieprawidłowy zakres. Użyj np. --from 1 --to 6500");
}

const textDir = path.join(outputDir, "txt");
const stateFile = path.join(outputDir, "state.json");
const indexFile = path.join(outputDir, "index.ndjson");
const errorsFile = path.join(outputDir, "errors.ndjson");
await mkdir(textDir, { recursive: true });

async function loadState() {
  try { return JSON.parse(await readFile(stateFile, "utf8")); }
  catch { return { lastCheckedId: fromId - 1, saved: 0, missing: 0, errors: 0 }; }
}

function safeName(id, title) {
  const slug = title.normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
    .toLowerCase().replace(/ł/g, "l").replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "").slice(0, 100);
  return `${String(id).padStart(5, "0")}-${slug || "artykul"}`;
}

const browser = await chromium.launch({ executablePath: chromePath, headless });
const context = await browser.newContext({
  locale: "pl-PL",
  userAgent: "RuchMuzycznyResearchArchive/1.0 (authorized research)",
});
const page = await context.newPage();
page.setDefaultTimeout(12_000);

let state = await loadState();
const startId = Math.max(fromId, state.lastCheckedId + 1);
console.log(`Zakres: ${startId}–${toId}; katalog: ${outputDir}`);

try {
  for (let id = startId; id <= toId; id++) {
    const url = `${BASE_URL}/article/${id}`;
    try {
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30_000 });
      const article = page.locator("#article-view");
      // Odpowiedź HTML jest tylko szkieletem Reacta; aplikacja potrzebuje chwili
      // na pobranie danych artykułu i zbudowanie właściwego DOM.
      await page.waitForTimeout(1_500);
      if (await article.count() !== 1) {
        state.missing++;
        process.stdout.write(`\rSprawdzono ${id}/${toId}; zapisano ${state.saved}`);
      } else {
        await article.waitFor({ state: "visible", timeout: 12_000 });
        const data = await article.evaluate((section) => {
          const title = section.querySelector("h1,h2")?.textContent?.trim() || "Artykuł";
          const text = section.innerText.replace(/\n{3,}/g, "\n\n").trim();
          return { title, text, canonicalUrl: location.href };
        });

        const filename = safeName(id, data.title);
        const textFile = path.join(textDir, `${filename}.txt`);
        await writeFile(textFile, `${data.title}\n${data.canonicalUrl}\n\n${data.text}\n`, "utf8");
        await appendFile(indexFile, JSON.stringify({ id, title: data.title, url: data.canonicalUrl, txt: path.basename(textFile) }) + "\n", "utf8");
        state.saved++;
        console.log(`\n[${id}] ${data.title}`);
      }
    } catch (error) {
      state.errors++;
      await appendFile(errorsFile, JSON.stringify({ id, url, error: String(error.message || error), at: new Date().toISOString() }) + "\n", "utf8");
      console.error(`\nBłąd ${id}: ${error.message}`);
    }
    state.lastCheckedId = id;
    await writeFile(stateFile, JSON.stringify(state, null, 2), "utf8");
    if (delayMs > 0) await page.waitForTimeout(delayMs);
  }
} finally {
  await browser.close();
}

console.log(`\nGotowe. Zapisano: ${state.saved}; brak ID: ${state.missing}; błędy: ${state.errors}.`);
