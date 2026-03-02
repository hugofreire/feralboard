/**
 * Post-build prerender script.
 * Starts a local server on dist/, renders the page with Puppeteer,
 * scrolls the entire page to trigger whileInView animations,
 * then strips any remaining opacity:0 styles and writes index.html.
 */
import { createServer } from "http";
import { readFileSync, writeFileSync } from "fs";
import { resolve, extname, join } from "path";
import puppeteer from "puppeteer";

const DIST = resolve("dist");
const PORT = 4567;

if (process.env.SKIP_PRERENDER === "1") {
  console.log("[prerender] Skipped because SKIP_PRERENDER=1");
  process.exit(0);
}

const MIME = {
  ".html": "text/html",
  ".js": "application/javascript",
  ".css": "text/css",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".json": "application/json",
};

// Simple static file server
const server = createServer((req, res) => {
  let filePath = join(DIST, req.url === "/" ? "index.html" : req.url);
  try {
    const data = readFileSync(filePath);
    const ext = extname(filePath);
    res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
    res.end(data);
  } catch {
    // SPA fallback
    const html = readFileSync(join(DIST, "index.html"));
    res.writeHead(200, { "Content-Type": "text/html" });
    res.end(html);
  }
});

server.listen(PORT, async () => {
  console.log(`[prerender] Serving dist/ on http://localhost:${PORT}`);

  try {
    const browser = await puppeteer.launch({ headless: "new", args: ["--no-sandbox"] });
    const page = await browser.newPage();

    // Force English locale so prerendered HTML is in the default/SEO language
    await page.goto(`http://localhost:${PORT}/?lang=en`, { waitUntil: "networkidle0" });

    // Scroll the entire page to trigger all framer-motion whileInView animations
    await page.evaluate(async () => {
      const delay = (ms) => new Promise((r) => setTimeout(r, ms));
      const scrollHeight = document.body.scrollHeight;
      const step = window.innerHeight;
      for (let y = 0; y <= scrollHeight; y += step) {
        window.scrollTo(0, y);
        await delay(200);
      }
      // Scroll to very bottom to catch any remaining elements
      window.scrollTo(0, document.body.scrollHeight);
      await delay(500);
    });

    // Wait for animations to fully settle
    await new Promise((r) => setTimeout(r, 1500));

    let html = await page.content();
    await browser.close();

    // Strip any remaining opacity:0 / transform styles from framer-motion
    // so crawlers don't treat content as hidden
    html = html.replace(/\s*style="opacity:\s*0[^"]*"/g, "");
    html = html.replace(/\s*style="[^"]*opacity:\s*0[^"]*"/g, "");

    // Write prerendered HTML
    writeFileSync(join(DIST, "index.html"), html, "utf-8");
    console.log(`[prerender] Wrote prerendered index.html (${(html.length / 1024).toFixed(1)} KB)`);
  } catch (error) {
    console.warn("[prerender] Skipped because browser launch failed.");
    console.warn(error instanceof Error ? error.message : String(error));
  } finally {
    server.close();
  }
});
