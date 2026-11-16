// Copies the held-out test metrics produced by the training pipeline into the web app,
// so every number on the page comes from models/metrics.json and is never hand-typed.
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = resolve(here, "../../models/metrics.json");
const target = resolve(here, "../src/data/metrics.json");

if (!existsSync(source)) {
  console.error(`metrics.json not found at ${source}. Train the model first (see the root README).`);
  process.exit(1);
}
mkdirSync(dirname(target), { recursive: true });
copyFileSync(source, target);
console.log("Copied models/metrics.json into web/src/data/");
