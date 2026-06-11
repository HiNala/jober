import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

import colorPlugin from "./eslint-rules/no-raw-color-literal.mjs";
import motionPlugin from "./eslint-rules/no-raw-motion-duration.mjs";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
  {
    files: ["src/**/*.{ts,tsx}"],
    ignores: [
      "src/components/ui/**",
      "src/components/marketing/**",
      "src/lib/design/motion.ts",
      "src/app/globals.css",
    ],
    plugins: { joberMotion: motionPlugin, joberColor: colorPlugin },
    rules: {
      "joberMotion/no-raw-motion-duration": "error",
      "joberColor/no-raw-color-literal": "error",
    },
  },
]);

export default eslintConfig;
