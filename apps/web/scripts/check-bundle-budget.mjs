#!/usr/bin/env node
/**
 * CI smoke gate — total client JS chunk size after `next build`.
 * Not a substitute for Lighthouse; catches large accidental imports early.
 */
import { readdir, stat } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(fileURLToPath(new URL(".", import.meta.url)), "..");
const chunksDir = join(root, ".next", "static", "chunks");
const MAX_TOTAL_KB = Number(process.env.JOBER_MAX_CLIENT_JS_KB ?? "2800");

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

const bytes = await jsChunkBytes(chunksDir);
const kb = Math.round(bytes / 1024);
if (kb > MAX_TOTAL_KB) {
  console.error(`Client JS chunks ${kb} KB exceed budget ${MAX_TOTAL_KB} KB`);
  process.exit(1);
}
console.log(`Client JS chunks ${kb} KB (budget ${MAX_TOTAL_KB} KB)`);
