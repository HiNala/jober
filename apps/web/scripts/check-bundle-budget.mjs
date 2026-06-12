#!/usr/bin/env node
/**
 * CI smoke gate — client JS chunk size + marketing import hygiene after `next build`.
 * Mission 22: tightened from 2800 → 2650 KB total (measured ~2560 KB post-fix).
 * Not a substitute for Lighthouse; catches large accidental imports early.
 */
import { readdir, readFile, stat } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(fileURLToPath(new URL(".", import.meta.url)), "..");
const chunksDir = join(root, ".next", "static", "chunks");
/** Post Mission 22 provider split — headroom above measured ~2560 KB. */
const MAX_TOTAL_KB = Number(process.env.JOBER_MAX_CLIENT_JS_KB ?? "2650");

const MARKETING_SOURCE_DIRS = [
  "src/app/page.tsx",
  "src/app/features",
  "src/app/pricing",
  "src/app/how-it-works",
  "src/app/faq",
  "src/app/blog",
  "src/app/privacy",
  "src/app/terms",
  "src/app/acceptable-use",
  "src/app/(auth)",
  "src/components/marketing",
];

const FORBIDDEN_MARKETING_IMPORTS = [
  { label: "recharts", pattern: /from\s+["']recharts["']/ },
  { label: "react-resizable-panels", pattern: /from\s+["']react-resizable-panels["']/ },
  { label: "cmdk", pattern: /from\s+["']cmdk["']/ },
];

async function jsChunkBytes(dir) {
  let total = 0;
  let entries;
  try {
    entries = await readdir(dir);
  } catch {
    console.error(`Missing build output at ${chunksDir}. Run pnpm build first.`);
    process.exit(1);
  }
  for (const name of entries) {
    if (!name.endsWith(".js")) {
      continue;
    }
    const info = await stat(join(dir, name));
    total += info.size;
  }
  return total;
}

async function collectSourceFiles(relPath) {
  const abs = join(root, relPath);
  const files = [];
  try {
    const info = await stat(abs);
    if (info.isFile() && /\.(tsx?|jsx?)$/.test(relPath)) {
      return [abs];
    }
    if (!info.isDirectory()) {
      return [];
    }
  } catch {
    return [];
  }
  async function walk(dir) {
    for (const name of await readdir(dir)) {
      const child = join(dir, name);
      const childInfo = await stat(child);
      if (childInfo.isDirectory()) {
        await walk(child);
      } else if (/\.(tsx?|jsx?)$/.test(name)) {
        files.push(child);
      }
    }
  }
  await walk(abs);
  return files;
}

async function checkMarketingImportLeaks() {
  const violations = [];
  for (const rel of MARKETING_SOURCE_DIRS) {
    for (const file of await collectSourceFiles(rel)) {
      const source = await readFile(file, "utf8");
      for (const rule of FORBIDDEN_MARKETING_IMPORTS) {
        if (rule.pattern.test(source)) {
          violations.push(`${file}: imports ${rule.label}`);
        }
      }
    }
  }
  if (violations.length) {
    console.error("Marketing/auth surfaces must not statically import app-only heavy deps:");
    for (const line of violations) {
      console.error(`  ${line}`);
    }
    process.exit(1);
  }
  console.log("Marketing import guard: no recharts / resizable-panels / cmdk in marketing trees");
}

const bytes = await jsChunkBytes(chunksDir);
const kb = Math.round(bytes / 1024);
if (kb > MAX_TOTAL_KB) {
  console.error(`Client JS chunks ${kb} KB exceed budget ${MAX_TOTAL_KB} KB`);
  process.exit(1);
}
console.log(`Client JS chunks ${kb} KB (budget ${MAX_TOTAL_KB} KB)`);

await checkMarketingImportLeaks();
