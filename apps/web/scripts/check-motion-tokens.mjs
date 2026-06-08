#!/usr/bin/env node
/**
 * CI guard: feature components must not hard-code motion durations.
 * Primitives (ui/) and the motion module are exempt.
 */
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(fileURLToPath(new URL(".", import.meta.url)), "..");
const src = join(root, "src");

const SKIP_DIRS = new Set(["ui", "node_modules", ".next"]);
const SKIP_FILES = new Set([
  join(src, "lib", "design", "motion.ts"),
  join(src, "app", "globals.css"),
]);

const DURATION = /\bduration-(?:\d{2,3})\b/g;
const ANIMATE_MS = /animate-\[[^\]]*\d+ms/g;

function walk(dir, files = []) {
  for (const name of readdirSync(dir)) {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) {
      if (!SKIP_DIRS.has(name)) {
        walk(path, files);
      }
      continue;
    }
    if (/\.(tsx|ts)$/.test(name) && !SKIP_FILES.has(path)) {
      files.push(path);
    }
  }
  return files;
}

const violations = [];

for (const file of walk(src)) {
  const rel = relative(root, file).replaceAll("\\", "/");
  if (rel.includes("/ui/") || rel.includes("/marketing/")) {
    continue;
  }
  const text = readFileSync(file, "utf8");
  for (const re of [DURATION, ANIMATE_MS]) {
    re.lastIndex = 0;
    let match;
    while ((match = re.exec(text)) !== null) {
      violations.push(`${rel}: ${match[0]}`);
    }
  }
}

if (violations.length > 0) {
  console.error("Motion token violations (use @/lib/design/motion):\n");
  for (const v of violations) {
    console.error(`  ${v}`);
  }
  process.exit(1);
}

console.log("check-motion-tokens: OK");
