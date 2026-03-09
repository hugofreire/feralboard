import crypto from "node:crypto";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

if (typeof crypto.hash !== "function") {
  crypto.hash = (algorithm, data, outputEncoding = "hex") =>
    crypto.createHash(algorithm).update(data).digest(outputEncoding);
}

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const viteCliPath = path.resolve(scriptDir, "..", "node_modules", "vite", "bin", "vite.js");
await import(pathToFileURL(viteCliPath).href);
