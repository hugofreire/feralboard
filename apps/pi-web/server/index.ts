import "dotenv/config";
import express from "express";
import cors from "cors";
import multer from "multer";
// @ts-ignore – pdfjs-dist legacy build has no TS declarations
import { getDocument } from "pdfjs-dist/legacy/build/pdf.mjs";
import { spawn, execSync, spawnSync } from "child_process";
import path from "path";
import fs from "fs";
import net from "net";
import crypto from "crypto";
import { fileURLToPath } from "url";
import { WebSocketServer, WebSocket } from "ws";
import {
  createAgentSession,
  AuthStorage,
  ModelRegistry,
  SessionManager,
  createCodingTools,
  type AgentSession,
} from "@mariozechner/pi-coding-agent";
import { Type } from "@sinclair/typebox";

const app = express();
app.use(cors());
app.use(express.json({ limit: "20mb" }));

const PORT = 3001;
const SERVER_DIR = path.dirname(fileURLToPath(import.meta.url));
const PI_WEB_ROOT = path.resolve(SERVER_DIR, "..");
const MONOREPO_ROOT = path.resolve(PI_WEB_ROOT, "..", "..");
const DEFAULT_FERALBOARD_PATH = path.join(MONOREPO_ROOT, "apps", "workbench");
const DEV_CLIENT_URL = process.env.PI_WEB_DEV_CLIENT_URL || "http://localhost:5173";
const SERVE_DIST_CLIENT = process.env.PI_WEB_SERVE_DIST === "1";
const DISPLAY_ASSETS_DIR = path.join(PI_WEB_ROOT, ".pi", "display-assets");
const DISPLAY_SCRIPT_PATH = path.join(PI_WEB_ROOT, "server", "scripts", "setup_display.sh");
const SWAY_CONFIG_PATH = "/etc/sway/config.d/99-custom-config";
const BOOT_FW_DIR = "/boot/firmware";
const SPLASH_HORIZONTAL_PATH = path.join(BOOT_FW_DIR, "splash-horizontal.png");
const SPLASH_PNG_PATH = path.join(BOOT_FW_DIR, "splash.png");
const SPLASH_PRESETS_DIR = "/home/pi/splash-screens";
const SUPPORTED_SPLASH_CLIENTS = ["mercadona", "ramalhos"] as const;

// ── FeralBoard Configuration ────────────────────────────────────
const FERALBOARD_PATH = process.env.FERALBOARD_PATH || DEFAULT_FERALBOARD_PATH;
const KIOSK_APPS_DIR = path.join(FERALBOARD_PATH, "kiosk_apps");
const GUI_PAGES_DIR = path.join(FERALBOARD_PATH, "gui/pages");

// ── File Upload ─────────────────────────────────────────────────
const UPLOADS_DIR = path.join(PI_WEB_ROOT, "uploads");
const DOCUMENTS_DIR = path.join(UPLOADS_DIR, "documents");
const LARGE_PDF_PAGE_THRESHOLD = Number(process.env.PDF_LARGE_PAGE_THRESHOLD || 30);
const DOCUMENT_SEARCH_RESULT_LIMIT = 5;
const DOCUMENT_READ_PAGE_LIMIT = 5;
if (!fs.existsSync(UPLOADS_DIR)) fs.mkdirSync(UPLOADS_DIR, { recursive: true });
if (!fs.existsSync(DOCUMENTS_DIR)) fs.mkdirSync(DOCUMENTS_DIR, { recursive: true });

const upload = multer({
  storage: multer.diskStorage({
    destination: (_req, _file, cb) => cb(null, UPLOADS_DIR),
    filename: (_req, file, cb) => {
      const unique = `${Date.now()}-${Math.round(Math.random() * 1e4)}`;
      const ext = path.extname(file.originalname);
      const base = path.basename(file.originalname, ext).replace(/[^a-zA-Z0-9_-]/g, "_");
      cb(null, `${base}-${unique}${ext}`);
    },
  }),
  limits: { fileSize: 10 * 1024 * 1024 }, // 10 MB
});

// ── In-Process SDK Session Management ───────────────────────────

const authStorage = new AuthStorage();
if (process.env.OPENAI_API_KEY) authStorage.setRuntimeApiKey("openai", process.env.OPENAI_API_KEY);
if (process.env.ANTHROPIC_API_KEY) authStorage.setRuntimeApiKey("anthropic", process.env.ANTHROPIC_API_KEY);
const modelRegistry = new ModelRegistry(authStorage);

// ── IPC Helper ──────────────────────────────────────────────────

function sendIpc(command: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const sock = net.createConnection({ path: "/tmp/feralboard-workbench.sock" }, () => {
      sock.write(command);
    });
    let data = "";
    sock.on("data", (chunk) => { data += chunk.toString(); });
    sock.on("end", () => resolve(data.trim()));
    sock.on("error", (err) => reject(err));
    setTimeout(() => { sock.destroy(); reject(new Error("IPC timeout")); }, 5000);
  });
}

// ── Custom Agent Tools ──────────────────────────────────────────

const feralboardTools = [
  {
    name: "restart_kiosk_app",
    label: "Restart Kiosk App",
    description: "Restart the FeralBoard GUI and open a specific kiosk app by slug. The GUI will restart and load directly into that app. Use this after making changes to a kiosk app's code to see the result.",
    parameters: Type.Object({
      slug: Type.String({ description: "Kiosk app slug (e.g. 'expedicao', 'hello-world')" }),
    }),
    async execute(toolCallId: string, params: { slug: string }, signal: AbortSignal | undefined, onUpdate: any, ctx: any) {
      const defaultAppPath = path.join(FERALBOARD_PATH, ".default_app");
      fs.writeFileSync(defaultAppPath, params.slug + "\n");

      // Kill existing GUI
      try { execSync('pkill -f "python3.*gui/app.py"', { cwd: FERALBOARD_PATH, timeout: 5000 }); } catch {}

      // Wait for cleanup, then start GUI
      await new Promise((r) => setTimeout(r, 500));
      spawn("bash", ["scripts/run.sh"], {
        cwd: FERALBOARD_PATH,
        detached: true,
        stdio: "ignore",
      }).unref();

      // Wait for GUI to initialize
      await new Promise((r) => setTimeout(r, 3000));

      return {
        content: [{ type: "text" as const, text: `GUI restarted with app "${params.slug}". The app should now be visible on screen.` }],
        details: {},
      };
    },
  },
  {
    name: "screenshot",
    label: "Screenshot",
    description: "Take a screenshot of the FeralBoard kiosk display. Returns the current screen image. Use this to verify visual changes after restarting the GUI or clicking elements.",
    parameters: Type.Object({}),
    async execute(toolCallId: string, params: {}, signal: AbortSignal | undefined, onUpdate: any, ctx: any) {
      execSync("bash scripts/screenshot.sh", { cwd: FERALBOARD_PATH, timeout: 10000 });
      const imgPath = path.join(FERALBOARD_PATH, "screen.png");
      const base64Data = fs.readFileSync(imgPath).toString("base64");
      return {
        content: [
          { type: "image" as const, data: base64Data, mimeType: "image/png" },
          { type: "text" as const, text: "Screenshot captured successfully." },
        ],
        details: {},
      };
    },
  },
  {
    name: "gui_click",
    label: "GUI Click",
    description: "Simulate a click at pixel coordinates (x, y) on the FeralBoard GUI. Use 'gui_widgets' first to find button positions.",
    parameters: Type.Object({
      x: Type.Number({ description: "X pixel coordinate" }),
      y: Type.Number({ description: "Y pixel coordinate" }),
    }),
    async execute(toolCallId: string, params: { x: number; y: number }, signal: AbortSignal | undefined, onUpdate: any, ctx: any) {
      const response = await sendIpc(`click ${params.x} ${params.y}`);
      return {
        content: [{ type: "text" as const, text: response || `Clicked at (${params.x}, ${params.y}).` }],
        details: {},
      };
    },
  },
  {
    name: "gui_navigate",
    label: "GUI Navigate",
    description: "Navigate the FeralBoard GUI to a specific page. Static pages: home, outputs, inputs, tests, wifi, ethernet, system, kiosk, pin, apps, rfid. Dynamic pages: the slug of a loaded kiosk app.",
    parameters: Type.Object({
      page: Type.String({ description: "Page name to navigate to (e.g. 'home', 'kiosk', 'apps', or a kiosk app slug)" }),
    }),
    async execute(toolCallId: string, params: { page: string }, signal: AbortSignal | undefined, onUpdate: any, ctx: any) {
      const response = await sendIpc(`navigate ${params.page}`);
      return {
        content: [{ type: "text" as const, text: response || `Navigated to "${params.page}".` }],
        details: {},
      };
    },
  },
  {
    name: "gui_widgets",
    label: "GUI Widgets",
    description: "List all visible interactive widgets (buttons, switches, labels) in the FeralBoard GUI with their names and pixel coordinates. Use this before calling gui_click to find the right coordinates.",
    parameters: Type.Object({}),
    async execute(toolCallId: string, params: {}, signal: AbortSignal | undefined, onUpdate: any, ctx: any) {
      const response = await sendIpc("widgets");
      return {
        content: [{ type: "text" as const, text: response || "No widgets found." }],
        details: {},
      };
    },
  },
  {
    name: "document_manifest",
    label: "Document Manifest",
    description: "Inspect a large uploaded PDF before reading pages. Returns metadata, storage status, and the document page count.",
    parameters: Type.Object({
      documentId: Type.String({ description: "Large document id returned when the PDF was indexed on the server." }),
    }),
    async execute(_toolCallId: string, params: { documentId: string }) {
      const manifest = loadDocumentManifest(params.documentId);
      return {
        content: [{ type: "text" as const, text: summarizeDocumentManifest(manifest) }],
        details: {},
      };
    },
  },
  {
    name: "document_search",
    label: "Document Search",
    description: "Search a large uploaded PDF by keyword before reading pages. Use this first to find the most relevant pages.",
    parameters: Type.Object({
      documentId: Type.String({ description: "Large document id returned when the PDF was indexed on the server." }),
      query: Type.String({ description: "Keywords or a short question to search for in the document text." }),
    }),
    async execute(_toolCallId: string, params: { documentId: string; query: string }) {
      const manifest = loadDocumentManifest(params.documentId);
      const hits = searchDocumentPages(manifest, params.query);
      const lines = [
        `Search query: ${params.query}`,
        `Document: ${manifest.originalFilename} (${manifest.documentId})`,
      ];

      if (hits.length === 0) {
        lines.push("No page hits found.");
      } else {
        lines.push("Top page hits:");
        for (const hit of hits) lines.push(`- Page ${hit.page} (score ${hit.score}): ${hit.snippet}`);
      }

      return {
        content: [{ type: "text" as const, text: lines.join("\n") }],
        details: {},
      };
    },
  },
  {
    name: "document_read_pages",
    label: "Document Read Pages",
    description: "Read a small page range from a large uploaded PDF after searching. Keep reads narrow and focused.",
    parameters: Type.Object({
      documentId: Type.String({ description: "Large document id returned when the PDF was indexed on the server." }),
      startPage: Type.Number({ description: "First page to read, 1-based." }),
      endPage: Type.Optional(Type.Number({ description: "Last page to read, inclusive. Defaults to startPage." })),
    }),
    async execute(_toolCallId: string, params: { documentId: string; startPage: number; endPage?: number }) {
      const manifest = loadDocumentManifest(params.documentId);
      const startPage = Math.max(1, Math.floor(params.startPage));
      const endPage = Math.max(startPage, Math.floor(params.endPage ?? params.startPage));
      if (endPage - startPage + 1 > DOCUMENT_READ_PAGE_LIMIT) {
        throw new Error(`Read at most ${DOCUMENT_READ_PAGE_LIMIT} pages at a time`);
      }

      const pages: string[] = [];
      for (let page = startPage; page <= endPage; page++) {
        pages.push(`Page ${page}\n${readDocumentPage(manifest, page) || "(empty page)"}`);
      }

      return {
        content: [{ type: "text" as const, text: pages.join("\n\n") }],
        details: {},
      };
    },
  },
];

const sessions = new Map<string, AgentSession>();
let activeInstanceCwd: string = FERALBOARD_PATH;

async function getOrCreateSession(cwd: string): Promise<AgentSession> {
  const existing = sessions.get(cwd);
  if (existing) { activeInstanceCwd = cwd; return existing; }

  console.log(`[sdk] Creating agent session for ${cwd}`);

  const { session } = await createAgentSession({
    cwd,
    tools: createCodingTools(cwd),
    customTools: feralboardTools,
    sessionManager: SessionManager.create(cwd),
    authStorage,
    modelRegistry,
  });

  sessions.set(cwd, session);
  activeInstanceCwd = cwd;
  return session;
}

function getActiveSession(): AgentSession | undefined {
  return sessions.get(activeInstanceCwd);
}

function disposeSession(cwd: string) {
  const s = sessions.get(cwd);
  if (s) { s.dispose(); sessions.delete(cwd); }
}

process.on("SIGTERM", () => {
  for (const cwd of sessions.keys()) disposeSession(cwd);
  process.exit(0);
});

// ── Helpers ─────────────────────────────────────────────────────

function slugify(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

function createDocumentId() {
  return `doc_${Date.now().toString(36)}_${crypto.randomBytes(4).toString("hex")}`;
}

function normalizePdfText(text: string) {
  return text.replace(/\s+/g, " ").trim();
}

async function extractPdfPages(filePath: string): Promise<PdfExtractionResult> {
  const data = new Uint8Array(fs.readFileSync(filePath));
  const doc = await getDocument({ data, useSystemFonts: true }).promise;
  const pageTexts: string[] = [];

  for (let i = 1; i <= doc.numPages; i++) {
    const page = await doc.getPage(i);
    const content = await page.getTextContent();
    const pageText = normalizePdfText(
      (content.items as any[])
        .filter((item) => "str" in item)
        .map((item) => item.str)
        .join(" ")
    );
    pageTexts.push(pageText);
  }

  return { pageCount: doc.numPages, pageTexts };
}

function summarizeDocumentManifest(manifest: StoredDocumentManifest) {
  return [
    `Document ID: ${manifest.documentId}`,
    `Filename: ${manifest.originalFilename}`,
    `Pages: ${manifest.pageCount}`,
    `Status: ${manifest.extractionStatus}`,
    `Manifest: ${manifest.manifestPath}`,
    `Stored PDF: ${manifest.originalPath}`,
    `Page text directory: ${manifest.pagesDir}`,
    manifest.extractionError ? `Extraction error: ${manifest.extractionError}` : null,
  ].filter(Boolean).join("\n");
}

function documentDir(documentId: string) {
  return path.join(DOCUMENTS_DIR, path.basename(documentId));
}

function manifestPathFor(documentId: string) {
  return path.join(documentDir(documentId), "manifest.json");
}

function loadDocumentManifest(documentId: string): StoredDocumentManifest {
  const manifestPath = manifestPathFor(documentId);
  if (!fs.existsSync(manifestPath)) throw new Error(`Document "${documentId}" not found`);
  return JSON.parse(fs.readFileSync(manifestPath, "utf-8"));
}

function writeDocumentManifest(manifest: StoredDocumentManifest) {
  fs.writeFileSync(manifest.manifestPath, JSON.stringify(manifest, null, 2) + "\n", "utf-8");
}

function readDocumentPage(manifest: StoredDocumentManifest, pageNumber: number) {
  if (!Number.isInteger(pageNumber) || pageNumber < 1 || pageNumber > manifest.pageCount) {
    throw new Error(`Page ${pageNumber} is out of range for document "${manifest.documentId}"`);
  }
  const pageFile = manifest.pageFiles[pageNumber - 1];
  return fs.existsSync(pageFile) ? fs.readFileSync(pageFile, "utf-8") : "";
}

function queryTerms(query: string) {
  return query.toLowerCase().split(/\s+/).map((term) => term.trim()).filter(Boolean);
}

function countTermHits(text: string, terms: string[]) {
  const haystack = text.toLowerCase();
  return terms.reduce((score, term) => score + (haystack.split(term).length - 1), 0);
}

function buildSnippet(text: string, terms: string[]) {
  if (!text.trim()) return "(empty page)";
  const lower = text.toLowerCase();
  const firstHit = terms.map((term) => lower.indexOf(term)).filter((idx) => idx >= 0).sort((a, b) => a - b)[0];
  const center = firstHit >= 0 ? firstHit : 0;
  const start = Math.max(0, center - 90);
  const snippet = text.slice(start, start + 220).trim();
  return `${start > 0 ? "..." : ""}${snippet}${start + 220 < text.length ? "..." : ""}`;
}

function searchDocumentPages(manifest: StoredDocumentManifest, query: string) {
  const terms = queryTerms(query);
  if (terms.length === 0) throw new Error("query is required");

  return manifest.pageFiles
    .map((pageFile, index) => {
      const text = fs.readFileSync(pageFile, "utf-8");
      const score = countTermHits(text, terms);
      return score > 0 ? {
        page: index + 1,
        score,
        snippet: buildSnippet(text, terms),
      } : null;
    })
    .filter((result): result is { page: number; score: number; snippet: string } => Boolean(result))
    .sort((a, b) => b.score - a.score || a.page - b.page)
    .slice(0, DOCUMENT_SEARCH_RESULT_LIMIT);
}

function deleteUploadedArtifact(filename: string) {
  const filePath = path.join(UPLOADS_DIR, path.basename(filename));
  if (!fs.existsSync(filePath)) return false;
  fs.unlinkSync(filePath);

  const ext = path.extname(filePath);
  if (/\.pdf$/i.test(ext)) {
    const textPath = filePath.replace(/\.pdf$/i, ".txt");
    if (fs.existsSync(textPath)) fs.unlinkSync(textPath);
  }

  return true;
}

async function createLargePdfDocument(originalname: string, filePath: string, size: number, extracted: PdfExtractionResult) {
  const documentId = createDocumentId();
  const docDir = documentDir(documentId);
  const pagesDir = path.join(docDir, "pages");
  ensureDir(pagesDir);

  const originalPath = path.join(docDir, "original.pdf");
  fs.renameSync(filePath, originalPath);

  const pageFiles = extracted.pageTexts.map((_pageText, index) => path.join(pagesDir, `${String(index + 1).padStart(4, "0")}.txt`));
  for (let i = 0; i < extracted.pageTexts.length; i++) {
    fs.writeFileSync(pageFiles[i], extracted.pageTexts[i], "utf-8");
  }

  const manifest: StoredDocumentManifest = {
    documentId,
    originalFilename: originalname,
    originalPath,
    manifestPath: path.join(docDir, "manifest.json"),
    pagesDir,
    pageCount: extracted.pageCount,
    pageFiles,
    extractionStatus: "indexed",
    createdAt: new Date().toISOString(),
    storageBytes: size + pageFiles.reduce((total, pageFile) => total + fs.statSync(pageFile).size, 0),
  };
  writeDocumentManifest(manifest);
  return manifest;
}

function discoverApps(): any[] {
  if (!fs.existsSync(KIOSK_APPS_DIR)) return [];
  const apps: any[] = [];
  for (const entry of fs.readdirSync(KIOSK_APPS_DIR).sort()) {
    const manifestPath = path.join(KIOSK_APPS_DIR, entry, "app.json");
    if (!fs.existsSync(manifestPath)) continue;
    try {
      const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf-8"));
      const envPath = path.join(KIOSK_APPS_DIR, entry, ".env");
      const pageFile = manifest.page ? path.join(GUI_PAGES_DIR, `${manifest.page}.py`) : null;
      apps.push({
        slug: entry,
        ...manifest,
        type: manifest.page ? "custom" : "greeting",
        hasEnv: fs.existsSync(envPath),
        hasPageFile: pageFile ? fs.existsSync(pageFile) : false,
        manifestPath,
      });
    } catch {}
  }
  return apps;
}

function parseEnvFile(filePath: string): Record<string, string> {
  if (!fs.existsSync(filePath)) return {};
  const vars: Record<string, string> = {};
  for (const line of fs.readFileSync(filePath, "utf-8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eq = trimmed.indexOf("=");
    if (eq > 0) {
      vars[trimmed.slice(0, eq).trim()] = trimmed.slice(eq + 1).trim();
    }
  }
  return vars;
}

function writeEnvFile(filePath: string, vars: Record<string, string>) {
  const lines = Object.entries(vars).map(([k, v]) => `${k}=${v}`);
  fs.writeFileSync(filePath, lines.join("\n") + "\n");
}

function ensureDir(dirPath: string) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function readSwaySetting(pattern: RegExp): string | null {
  if (!fs.existsSync(SWAY_CONFIG_PATH)) return null;
  const config = fs.readFileSync(SWAY_CONFIG_PATH, "utf-8");
  const match = config.match(pattern);
  return match?.[1] ?? null;
}

function getDisplaySettings() {
  const rotationValue = readSwaySetting(/^output HDMI-A-1 transform (.+)$/m);
  const backgroundPath = readSwaySetting(/^output \* bg (.+) fill$/m);

  return {
    rotation: ["0", "90", "180", "270"].includes(rotationValue || "") ? Number(rotationValue) : 0,
    backgroundPath: backgroundPath || SPLASH_HORIZONTAL_PATH,
    splashPath: SPLASH_PNG_PATH,
    horizontalSplashPath: SPLASH_HORIZONTAL_PATH,
    splashPreset: null as string | null,
    supportedSplashClients: [...SUPPORTED_SPLASH_CLIENTS],
    customAssets: {
      splash: path.join(DISPLAY_ASSETS_DIR, "splash.png"),
      background: path.join(DISPLAY_ASSETS_DIR, "splash-horizontal.png"),
    },
  };
}

function writeBase64Image(targetPath: string, dataUrl: string) {
  const match = dataUrl.match(/^data:(image\/[a-zA-Z0-9.+-]+);base64,(.+)$/);
  if (!match) throw new Error(`Invalid image payload for ${path.basename(targetPath)}`);
  ensureDir(path.dirname(targetPath));
  fs.writeFileSync(targetPath, Buffer.from(match[2], "base64"));
}

function runPrivileged(command: string, args: string[], options?: { cwd?: string }) {
  const finalCommand = process.getuid?.() === 0 ? command : "sudo";
  const finalArgs = process.getuid?.() === 0 ? args : [command, ...args];
  const result = spawnSync(finalCommand, finalArgs, {
    cwd: options?.cwd,
    encoding: "utf-8",
  });

  if (result.status !== 0) {
    throw new Error(result.stderr?.trim() || result.stdout?.trim() || `${command} failed`);
  }

  return {
    stdout: result.stdout?.trim() || "",
    stderr: result.stderr?.trim() || "",
  };
}

type DisplaySettingsApplyBody = {
  rotation?: number;
  splashMode?: "unchanged" | "preset" | "custom";
  splashClient?: string;
  customSplashDataUrl?: string;
  customBackgroundDataUrl?: string;
  backgroundMode?: "default" | "custom" | "path";
  backgroundPath?: string;
};

type StoredDocumentManifest = {
  documentId: string;
  originalFilename: string;
  originalPath: string;
  manifestPath: string;
  pagesDir: string;
  pageCount: number;
  pageFiles: string[];
  extractionStatus: "indexed" | "failed";
  extractionError?: string;
  createdAt: string;
  storageBytes: number;
};

type PdfExtractionResult = {
  pageCount: number;
  pageTexts: string[];
};

function buildDisplayScriptArgs(body: DisplaySettingsApplyBody) {
  const rotation = Number(body.rotation);
  if (![0, 90, 180, 270].includes(rotation)) throw new Error("rotation must be 0, 90, 180, or 270");

  let backgroundPath = SPLASH_HORIZONTAL_PATH;
  let clientArg = "";

  if (body.splashMode === "preset") {
    if (!body.splashClient || !SUPPORTED_SPLASH_CLIENTS.includes(body.splashClient as any)) {
      throw new Error(`splashClient must be one of: ${SUPPORTED_SPLASH_CLIENTS.join(", ")}`);
    }
    clientArg = body.splashClient;
  }

  if (body.splashMode === "custom") {
    if (!body.customSplashDataUrl) throw new Error("customSplashDataUrl is required for custom splash mode");
    const customSplashPath = path.join(DISPLAY_ASSETS_DIR, "splash.png");
    writeBase64Image(customSplashPath, body.customSplashDataUrl);

    if (body.customBackgroundDataUrl) {
      const customBackgroundPath = path.join(DISPLAY_ASSETS_DIR, "splash-horizontal.png");
      writeBase64Image(customBackgroundPath, body.customBackgroundDataUrl);
      backgroundPath = customBackgroundPath;
    } else {
      const fallbackBackgroundPath = path.join(DISPLAY_ASSETS_DIR, "splash-horizontal.png");
      writeBase64Image(fallbackBackgroundPath, body.customSplashDataUrl);
      backgroundPath = fallbackBackgroundPath;
    }

    clientArg = "custom";
  }

  if (body.backgroundMode === "custom") {
    if (!body.customBackgroundDataUrl) throw new Error("customBackgroundDataUrl is required for custom background mode");
    const customBackgroundPath = path.join(DISPLAY_ASSETS_DIR, "splash-horizontal.png");
    writeBase64Image(customBackgroundPath, body.customBackgroundDataUrl);
    backgroundPath = customBackgroundPath;
  } else if (body.backgroundMode === "path") {
    if (!body.backgroundPath?.trim()) throw new Error("backgroundPath is required when backgroundMode is path");
    backgroundPath = body.backgroundPath.trim();
  }

  const args = [DISPLAY_SCRIPT_PATH, "-r", String(rotation), "-b", backgroundPath];
  if (clientArg) args.push("-c", clientArg);

  return { rotation, backgroundPath, clientArg, args };
}

function canReadDisplayImage(targetPath: string) {
  const resolved = path.resolve(targetPath);
  const allowedRoots = [BOOT_FW_DIR, SPLASH_PRESETS_DIR, DISPLAY_ASSETS_DIR];
  return allowedRoots.some((root) => resolved.startsWith(path.resolve(root) + path.sep) || resolved === path.resolve(root));
}

function generatePageBoilerplate(slug: string, name: string): string {
  const className = slug.split(/[-_]/).map(w => w.charAt(0).toUpperCase() + w.slice(1)).join("");
  return `"""${name} kiosk app."""

import os
import sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class ${className}Page(Gtk.Box):
    """${name} — custom kiosk page."""

    def __init__(self, on_unlock=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.get_style_context().add_class("kiosk-page")
        self._on_unlock = on_unlock
        self._press_timer = None

        self._build_ui()

    def _build_ui(self):
        # Title with long-press to unlock
        event_box = Gtk.EventBox()
        event_box.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK
        )
        event_box.connect("button-press-event", self._on_press)
        event_box.connect("button-release-event", self._on_release)

        title = Gtk.Label()
        title.set_markup(
            '<span size="20000" weight="bold" foreground="white">'
            '${name}</span>'
        )
        title.set_margin_top(16)
        title.set_margin_bottom(8)
        event_box.add(title)
        self.pack_start(event_box, False, False, 0)

        # ── Your UI below ──
        content = Gtk.Label()
        content.set_markup(
            '<span size="14000" foreground="#8b949e">'
            'Edit gui/pages/${slug}.py to build your app</span>'
        )
        content.set_vexpand(True)
        content.set_valign(Gtk.Align.CENTER)
        self.pack_start(content, True, True, 0)

    def load_app(self, app_info):
        """Receive the full app.json dict. Use it to configure your page."""
        pass

    def cleanup(self):
        """Stop any background tasks, timers, threads, connections."""
        pass

    def update_from_rx(self, rx_buffer):
        """Optional: receive serial RX data when this page is visible."""
        pass

    # ── Long-press unlock ──

    def _on_press(self, widget, event):
        if event.button == 1:
            self._cancel_timer()
            self._press_timer = GLib.timeout_add(2000, self._timer_fired)
        return False

    def _on_release(self, widget, event):
        if event.button == 1:
            self._cancel_timer()
        return False

    def _timer_fired(self):
        self._press_timer = None
        if self._on_unlock:
            self._on_unlock()
        return False

    def _cancel_timer(self):
        if self._press_timer is not None:
            GLib.source_remove(self._press_timer)
            self._press_timer = None
`;
}

// ── Kiosk App CRUD Routes ───────────────────────────────────────

// List all apps
app.get("/api/apps", (_req, res) => {
  try {
    res.json(discoverApps());
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

// Get single app
app.get("/api/apps/:slug", (req, res) => {
  try {
    const slug = req.params.slug;
    const manifestPath = path.join(KIOSK_APPS_DIR, slug, "app.json");
    if (!fs.existsSync(manifestPath)) { res.status(404).json({ error: "App not found" }); return; }
    const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf-8"));
    const envPath = path.join(KIOSK_APPS_DIR, slug, ".env");
    const pageFile = manifest.page ? path.join(GUI_PAGES_DIR, `${manifest.page}.py`) : null;
    res.json({
      slug,
      ...manifest,
      type: manifest.page ? "custom" : "greeting",
      hasEnv: fs.existsSync(envPath),
      hasPageFile: pageFile ? fs.existsSync(pageFile) : false,
    });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

// Create new app
app.post("/api/apps", (req, res) => {
  const { name, description, type, greeting } = req.body;
  if (!name) { res.status(400).json({ error: "name is required" }); return; }

  const slug = slugify(name);
  const appDir = path.join(KIOSK_APPS_DIR, slug);
  if (fs.existsSync(appDir)) { res.status(409).json({ error: `App "${slug}" already exists` }); return; }

  try {
    fs.mkdirSync(appDir, { recursive: true });

    const manifest: any = { name, description: description || "" };
    if (type === "custom") {
      manifest.page = slug;
    } else {
      manifest.greeting = greeting || name;
    }
    fs.writeFileSync(path.join(appDir, "app.json"), JSON.stringify(manifest, null, 4) + "\n");

    // Generate page boilerplate for custom apps
    if (type === "custom") {
      const pageFilePath = path.join(GUI_PAGES_DIR, `${slug}.py`);
      if (!fs.existsSync(pageFilePath)) {
        fs.writeFileSync(pageFilePath, generatePageBoilerplate(slug, name));
      }
    }

    // Create empty .env
    fs.writeFileSync(path.join(appDir, ".env"), "");

    res.json({ success: true, slug, path: appDir });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

// Update app manifest
app.put("/api/apps/:slug", (req, res) => {
  const slug = req.params.slug;
  const manifestPath = path.join(KIOSK_APPS_DIR, slug, "app.json");
  if (!fs.existsSync(manifestPath)) { res.status(404).json({ error: "App not found" }); return; }

  try {
    const manifest = req.body;
    fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 4) + "\n");
    res.json({ success: true });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

// Delete app
app.delete("/api/apps/:slug", (req, res) => {
  const slug = req.params.slug;
  const appDir = path.join(KIOSK_APPS_DIR, slug);
  if (!fs.existsSync(appDir)) { res.status(404).json({ error: "App not found" }); return; }

  try {
    // Read manifest to check for page file
    const manifestPath = path.join(appDir, "app.json");
    if (fs.existsSync(manifestPath)) {
      const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf-8"));
      if (manifest.page) {
        const pageFile = path.join(GUI_PAGES_DIR, `${manifest.page}.py`);
        if (fs.existsSync(pageFile)) fs.unlinkSync(pageFile);
      }
    }
    fs.rmSync(appDir, { recursive: true });
    res.json({ success: true });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

// ── Per-App Env Routes ──────────────────────────────────────────

app.get("/api/apps/:slug/env", (req, res) => {
  const envPath = path.join(KIOSK_APPS_DIR, req.params.slug, ".env");
  try {
    res.json(parseEnvFile(envPath));
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.put("/api/apps/:slug/env", (req, res) => {
  const appDir = path.join(KIOSK_APPS_DIR, req.params.slug);
  if (!fs.existsSync(appDir)) { res.status(404).json({ error: "App not found" }); return; }
  try {
    writeEnvFile(path.join(appDir, ".env"), req.body);
    res.json({ success: true });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

// ── Per-App File Explorer ────────────────────────────────────────

function listDirRecursive(dir: string, base: string): { name: string; path: string; relativePath: string; size: number; isDir: boolean }[] {
  const results: any[] = [];
  if (!fs.existsSync(dir)) return results;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith(".") || entry.name === "__pycache__" || entry.name === "node_modules") continue;
    const full = path.join(dir, entry.name);
    const rel = path.relative(base, full);
    if (entry.isDirectory()) {
      results.push({ name: entry.name, path: full, relativePath: rel, size: 0, isDir: true });
      results.push(...listDirRecursive(full, base));
    } else {
      const stat = fs.statSync(full);
      results.push({ name: entry.name, path: full, relativePath: rel, size: stat.size, isDir: false });
    }
  }
  return results;
}

app.get("/api/apps/:slug/files", (req, res) => {
  const slug = req.params.slug;
  const appDir = path.join(KIOSK_APPS_DIR, slug);
  if (!fs.existsSync(appDir)) { res.status(404).json({ error: "App not found" }); return; }

  try {
    // Gather files from kiosk_apps/<slug>/
    const appFiles = listDirRecursive(appDir, FERALBOARD_PATH);

    // Check for page file in gui/pages/
    const manifestPath = path.join(appDir, "app.json");
    if (fs.existsSync(manifestPath)) {
      const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf-8"));
      if (manifest.page) {
        const pageFile = path.join(GUI_PAGES_DIR, `${manifest.page}.py`);
        if (fs.existsSync(pageFile)) {
          const stat = fs.statSync(pageFile);
          appFiles.push({
            name: `${manifest.page}.py`,
            path: pageFile,
            relativePath: path.relative(FERALBOARD_PATH, pageFile),
            size: stat.size,
            isDir: false,
          });
        }
      }
    }

    res.json(appFiles);
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.get("/api/files/read", (req, res) => {
  const filePath = req.query.path as string;
  if (!filePath) { res.status(400).json({ error: "path is required" }); return; }
  // Security: only allow reading within FERALBOARD_PATH
  const resolved = path.resolve(filePath);
  if (!resolved.startsWith(FERALBOARD_PATH)) { res.status(403).json({ error: "Access denied" }); return; }
  if (!fs.existsSync(resolved) || fs.statSync(resolved).isDirectory()) { res.status(404).json({ error: "File not found" }); return; }
  try {
    const content = fs.readFileSync(resolved, "utf-8");
    res.json({ path: resolved, relativePath: path.relative(FERALBOARD_PATH, resolved), content });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

// ── File Upload ─────────────────────────────────────────────────

app.post("/api/upload", upload.single("file"), async (req, res) => {
  if (!req.file) { res.status(400).json({ error: "No file provided" }); return; }
  const { originalname, filename, size } = req.file;
  const filePath = path.join(UPLOADS_DIR, filename);

  const result: Record<string, any> = { kind: "file", originalName: originalname, filename, size, path: filePath };

  // Auto-extract text from PDFs
  if (/\.pdf$/i.test(originalname)) {
    try {
      const extracted = await extractPdfPages(filePath);
      result.pages = extracted.pageCount;

      if (extracted.pageCount > LARGE_PDF_PAGE_THRESHOLD) {
        const manifest = await createLargePdfDocument(originalname, filePath, size, extracted);
        result.kind = "large_document";
        result.path = manifest.originalPath;
        result.documentId = manifest.documentId;
        result.manifestPath = manifest.manifestPath;
        result.indexedOnServer = true;
        result.threshold = LARGE_PDF_PAGE_THRESHOLD;
      } else {
        const textFilename = filename.replace(/\.pdf$/i, ".txt");
        const textPath = path.join(UPLOADS_DIR, textFilename);
        fs.writeFileSync(textPath, extracted.pageTexts.filter(Boolean).join("\n\n"), "utf-8");
        result.extractedText = textFilename;
        result.extractedTextPath = textPath;
      }
    } catch (err: any) {
      result.extractionError = err.message;
    }
  }

  res.json(result);
});

app.get("/api/uploads", (_req, res) => {
  try {
    const files = fs.readdirSync(UPLOADS_DIR)
      .filter((f) => !f.startsWith("."))
      .map((f) => {
        const stat = fs.statSync(path.join(UPLOADS_DIR, f));
        return stat.isFile() ? { filename: f, size: stat.size, createdAt: stat.birthtime } : null;
      })
      .filter((file): file is { filename: string; size: number; createdAt: Date } => Boolean(file))
      .sort((a, b) => +b.createdAt - +a.createdAt);
    res.json(files);
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.delete("/api/uploads/:filename", (req, res) => {
  const deleted = deleteUploadedArtifact(req.params.filename);
  if (!deleted) { res.status(404).json({ error: "Not found" }); return; }
  res.json({ ok: true });
});

app.get("/api/documents/:id/manifest", (req, res) => {
  try {
    res.json(loadDocumentManifest(req.params.id));
  } catch (err: any) {
    res.status(404).json({ error: err.message });
  }
});

app.get("/api/documents/:id/search", (req, res) => {
  try {
    const query = String(req.query.q || "").trim();
    const manifest = loadDocumentManifest(req.params.id);
    res.json({
      documentId: manifest.documentId,
      originalFilename: manifest.originalFilename,
      results: searchDocumentPages(manifest, query),
    });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/api/documents/:id/pages", (req, res) => {
  try {
    const manifest = loadDocumentManifest(req.params.id);
    const startPage = Math.max(1, Number(req.query.startPage || req.query.page || 1));
    const endPage = Math.max(startPage, Number(req.query.endPage || startPage));
    if (endPage - startPage + 1 > DOCUMENT_READ_PAGE_LIMIT) {
      res.status(400).json({ error: `Read at most ${DOCUMENT_READ_PAGE_LIMIT} pages at a time` });
      return;
    }

    res.json({
      documentId: manifest.documentId,
      pages: Array.from({ length: endPage - startPage + 1 }, (_, index) => {
        const pageNumber = startPage + index;
        return { page: pageNumber, text: readDocumentPage(manifest, pageNumber) };
      }),
    });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.delete("/api/documents/:id", (req, res) => {
  const targetDir = documentDir(req.params.id);
  if (!fs.existsSync(targetDir)) {
    res.status(404).json({ error: "Not found" });
    return;
  }
  fs.rmSync(targetDir, { recursive: true, force: true });
  res.json({ ok: true });
});

// ── System Actions ──────────────────────────────────────────────

app.post("/api/system/restart-gui", (req, res) => {
  try {
    const slug = typeof req.body?.slug === "string" ? req.body.slug.trim() : "";
    if (slug) {
      const manifestPath = path.join(KIOSK_APPS_DIR, slug, "app.json");
      if (!fs.existsSync(manifestPath)) {
        res.status(404).json({ error: "App not found" });
        return;
      }
      fs.writeFileSync(path.join(FERALBOARD_PATH, ".default_app"), `${slug}\n`);
    }
    // Kill existing GUI process
    try { execSync('pkill -f "python3.*gui/app.py"', { cwd: FERALBOARD_PATH, timeout: 5000 }); } catch {}
    // Wait a moment for cleanup
    setTimeout(() => {
      spawn("bash", ["scripts/run.sh"], {
        cwd: FERALBOARD_PATH,
        detached: true,
        stdio: "ignore",
      }).unref();
    }, 500);
    res.json({ success: true, slug: slug || null });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.post("/api/system/screenshot", (_req, res) => {
  try {
    execSync("bash scripts/screenshot.sh", { cwd: FERALBOARD_PATH, timeout: 10000 });
    res.json({ success: true, path: path.join(FERALBOARD_PATH, "screen.png") });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.get("/api/system/screenshot", (_req, res) => {
  const imgPath = path.join(FERALBOARD_PATH, "screen.png");
  if (!fs.existsSync(imgPath)) { res.status(404).json({ error: "No screenshot available" }); return; }
  res.sendFile(imgPath);
});

app.get("/api/system/config", (_req, res) => {
  const session = getActiveSession();
  const model = session?.model;
  res.json({
    feralboardPath: FERALBOARD_PATH,
    provider: model?.provider || process.env.PI_PROVIDER || "openai",
    model: model?.id || process.env.PI_MODEL || "o3-mini",
  });
});

app.get("/api/system/display-settings", (_req, res) => {
  try {
    res.json(getDisplaySettings());
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/api/system/display-image", (req, res) => {
  try {
    const targetPath = String(req.query.path || "");
    if (!targetPath) {
      res.status(400).json({ error: "path is required" });
      return;
    }
    if (!canReadDisplayImage(targetPath)) {
      res.status(403).json({ error: "Access denied" });
      return;
    }
    if (!fs.existsSync(targetPath) || fs.statSync(targetPath).isDirectory()) {
      res.status(404).json({ error: "Image not found" });
      return;
    }
    res.sendFile(path.resolve(targetPath));
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/system/display-settings", (req, res) => {
  try {
    const scriptRun = buildDisplayScriptArgs(req.body);
    const result = runPrivileged("bash", scriptRun.args, { cwd: PI_WEB_ROOT });
    res.json({
      success: true,
      rotation: scriptRun.rotation,
      backgroundPath: scriptRun.backgroundPath,
      rebootRecommended: true,
      output: result.stdout,
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/system/reboot", (_req, res) => {
  try {
    runPrivileged("reboot", []);
    res.json({ success: true });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// ── Chat / Agent SDK Routes ─────────────────────────────────────

// SSE streaming endpoint
app.post("/api/chat/stream", async (req, res) => {
  const { message, cwd } = req.body;
  if (!message) { res.status(400).json({ error: "message is required" }); return; }

  const targetCwd = cwd || activeInstanceCwd;
  console.log(`[stream] [${targetCwd}] "${message.slice(0, 80)}"`);

  res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache", Connection: "keep-alive" });

  let session: AgentSession;
  try { session = await getOrCreateSession(targetCwd); } catch (err: any) {
    res.write(`data: ${JSON.stringify({ type: "error", error: err.message })}\n\n`); res.end(); return;
  }

  let done = false;
  const cleanup = () => { done = true; unsubscribe(); clearTimeout(timeout); };

  const unsubscribe = session.subscribe((event: any) => {
    if (done) return;
    if (event.type === "message_update" && event.assistantMessageEvent) {
      const ae = event.assistantMessageEvent;
      if (ae.type === "text_delta") res.write(`data: ${JSON.stringify({ type: "delta", text: ae.delta })}\n\n`);
      else if (ae.type === "thinking_delta") res.write(`data: ${JSON.stringify({ type: "thinking", text: ae.delta })}\n\n`);
    }
    if (event.type === "tool_execution_start") res.write(`data: ${JSON.stringify({ type: "tool_start", tool: event.toolName, args: event.args })}\n\n`);
    if (event.type === "tool_execution_end") res.write(`data: ${JSON.stringify({ type: "tool_end", tool: event.toolName, isError: event.isError })}\n\n`);
    if (event.type === "agent_end") {
      const lastMsg = event.messages?.findLast?.((m: any) => m.role === "assistant");
      if (lastMsg?.errorMessage) {
        res.write(`data: ${JSON.stringify({ type: "error", error: lastMsg.errorMessage })}\n\n`);
      }
      res.write(`data: ${JSON.stringify({ type: "done" })}\n\n`);
      cleanup(); res.end();
    }
  });

  const timeout = setTimeout(() => {
    if (!done) { cleanup(); res.write(`data: ${JSON.stringify({ type: "error", error: "Timeout" })}\n\n`); res.end(); }
  }, 120_000);

  req.on("close", () => { if (!done) cleanup(); });

  session.prompt(message).catch((err) => {
    if (!done) { cleanup(); res.write(`data: ${JSON.stringify({ type: "error", error: err.message })}\n\n`); res.end(); }
  });
});

app.post("/api/chat", async (req, res) => {
  const { message, cwd } = req.body;
  if (!message) { res.status(400).json({ error: "message is required" }); return; }

  try {
    const session = await getOrCreateSession(cwd || activeInstanceCwd);
    let text = "";

    const unsubscribe = session.subscribe((event: any) => {
      if (event.type === "message_update" && event.assistantMessageEvent?.type === "text_delta") {
        text += event.assistantMessageEvent.delta;
      }
    });

    try { await session.prompt(message); }
    finally { unsubscribe(); }
    res.json({ response: text });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.get("/api/folders", async (req, res) => {
  const dir = (req.query.path as string) || process.env.HOME || "/";
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true })
      .filter((e) => e.isDirectory() && !e.name.startsWith("."))
      .map((e) => ({ name: e.name, path: path.join(dir, e.name) }))
      .sort((a, b) => a.name.localeCompare(b.name));
    res.json({ current: dir, parent: path.dirname(dir), folders: entries });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.post("/api/folders", async (req, res) => {
  const { parentPath, name } = req.body;
  if (!parentPath || !name) { res.status(400).json({ error: "parentPath and name are required" }); return; }
  const newPath = path.join(parentPath, name);
  try {
    fs.mkdirSync(newPath, { recursive: true });
    res.json({ success: true, path: newPath });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.post("/api/workspace", async (req, res) => {
  const { cwd } = req.body;
  if (!cwd) { res.status(400).json({ error: "cwd is required" }); return; }
  try {
    await getOrCreateSession(cwd);
    res.json({ success: true, cwd });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.post("/api/model", async (req, res) => {
  const { provider, modelId } = req.body;
  try {
    const session = await getOrCreateSession(activeInstanceCwd);
    const model = session.modelRegistry.find(provider, modelId);
    if (!model) { res.status(404).json({ error: `Model ${provider}/${modelId} not found` }); return; }
    await session.setModel(model);
    res.json({ success: true, data: { provider: model.provider, id: model.id, name: model.name } });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.get("/api/models", async (_req, res) => {
  try {
    const session = await getOrCreateSession(activeInstanceCwd);
    const models = session.modelRegistry.getAvailable();
    res.json(models.map((m: any) => ({
      provider: m.provider,
      id: m.id,
      name: m.name,
      reasoning: m.reasoning,
    })));
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.post("/api/thinking", async (req, res) => {
  try {
    const session = await getOrCreateSession(activeInstanceCwd);
    session.setThinkingLevel(req.body.level);
    res.json({ success: true });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.get("/api/state", async (_req, res) => {
  try {
    const session = getActiveSession();
    if (!session) {
      res.json({ cwd: activeInstanceCwd, isStreaming: false });
      return;
    }
    const model = session.model;
    res.json({
      model: model ? { provider: model.provider, id: model.id, name: model.name } : null,
      isStreaming: session.isStreaming,
      sessionId: session.sessionId,
      sessionFile: session.sessionFile,
      thinkingLevel: session.thinkingLevel,
      cwd: activeInstanceCwd,
    });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.get("/api/stats", async (_req, res) => {
  try {
    const session = await getOrCreateSession(activeInstanceCwd);
    res.json(session.getSessionStats());
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.post("/api/abort", async (_req, res) => {
  try {
    const session = getActiveSession();
    if (session) await session.abort();
    res.json({ success: true });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.post("/api/new-session", async (req, res) => {
  const cwd = req.body?.cwd || activeInstanceCwd;
  try {
    const session = await getOrCreateSession(cwd);
    await session.newSession();
    res.json({ success: true });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.post("/api/compact", async (_req, res) => {
  try {
    const session = await getOrCreateSession(activeInstanceCwd);
    const result = await session.compact();
    res.json({ success: true, data: result });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

// ── Session Management ──────────────────────────────────────────

app.get("/api/sessions", async (_req, res) => {
  try {
    const allSessions = await SessionManager.listAll();
    const mapped = allSessions.map((s: any) => ({
      id: s.id,
      timestamp: s.modified?.toISOString?.() || s.created?.toISOString?.() || new Date().toISOString(),
      cwd: s.cwd,
      name: s.name || s.firstMessage?.slice(0, 80) || "Untitled",
      preview: s.firstMessage?.slice(0, 80) || "",
      messageCount: s.messageCount,
      filePath: s.path,
      isCoding: s.cwd !== process.cwd(),
    }));
    mapped.sort((a: any, b: any) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    res.json(mapped);
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.post("/api/sessions/switch", async (req, res) => {
  const { sessionPath, cwd } = req.body;
  if (!sessionPath) { res.status(400).json({ error: "sessionPath is required" }); return; }
  try {
    const targetCwd = cwd || activeInstanceCwd;
    const session = await getOrCreateSession(targetCwd);
    await session.switchSession(sessionPath);
    res.json({ success: true });
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.get("/api/sessions/messages", async (_req, res) => {
  try {
    const session = await getOrCreateSession(activeInstanceCwd);
    const messages = session.messages
      .filter((m: any) => m.role === "user" || m.role === "assistant")
      .map((m: any) => {
        const content = m.content;
        let text = "";
        if (typeof content === "string") text = content;
        else if (Array.isArray(content)) text = content.filter((c: any) => c.type === "text").map((c: any) => c.text).join("");
        return { role: m.role, content: text };
      });
    res.json(messages);
  } catch (err: any) { res.status(500).json({ error: err.message }); }
});

app.get("/api/health", (_req, res) => {
  res.json({
    status: "ok",
    instances: sessions.size,
    activeWorkspace: activeInstanceCwd,
    feralboardPath: FERALBOARD_PATH,
  });
});

const CLIENT_DIST_DIR = path.join(PI_WEB_ROOT, "dist");

if (!SERVE_DIST_CLIENT) {
  app.get(/^(?!\/api|\/vnc-ws).*/, (req, res) => {
    const target = new URL(req.originalUrl || "/", DEV_CLIENT_URL);
    res.redirect(target.toString());
  });
} else if (fs.existsSync(CLIENT_DIST_DIR)) {
  app.use(express.static(CLIENT_DIST_DIR));
  app.get(/^(?!\/api|\/vnc-ws).*/, (_req, res) => {
    res.sendFile(path.join(CLIENT_DIST_DIR, "index.html"));
  });
}

// ── VNC WebSocket Proxy ──────────────────────────────────────────

const VNC_HOST = "127.0.0.1";
const VNC_PORT = 5900;

const server = app.listen(PORT, () => {
  console.log(`FeralBoard Developer Portal running on http://localhost:${PORT}`);
  console.log(`  Workbench: ${FERALBOARD_PATH}`);
  console.log(`  VNC proxy: ws://localhost:${PORT}/vnc-ws -> ${VNC_HOST}:${VNC_PORT}`);
});

const wss = new WebSocketServer({ noServer: true });

server.on("upgrade", (req, socket, head) => {
  if (req.url === "/vnc-ws") {
    wss.handleUpgrade(req, socket, head, (ws) => wss.emit("connection", ws, req));
  } else {
    socket.destroy();
  }
});

wss.on("connection", (ws: WebSocket) => {
  console.log("[vnc-proxy] Browser connected");

  const tcp = net.createConnection({ host: VNC_HOST, port: VNC_PORT }, () => {
    console.log("[vnc-proxy] Connected to VNC server");
  });

  // TCP -> WebSocket
  tcp.on("data", (data) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(data);
    }
  });

  // WebSocket -> TCP
  ws.on("message", (data: Buffer) => {
    if (!tcp.destroyed) {
      tcp.write(data);
    }
  });

  tcp.on("error", (err) => {
    console.error("[vnc-proxy] TCP error:", err.message);
    ws.close();
  });

  tcp.on("close", () => {
    console.log("[vnc-proxy] TCP connection closed");
    ws.close();
  });

  ws.on("close", () => {
    console.log("[vnc-proxy] Browser disconnected");
    tcp.destroy();
  });

  ws.on("error", (err) => {
    console.error("[vnc-proxy] WebSocket error:", err.message);
    tcp.destroy();
  });
});
