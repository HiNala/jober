/** @type {import('eslint').ESLint.Plugin} */
const plugin = {
  rules: {
    "no-raw-motion-duration": {
      meta: {
        type: "problem",
        docs: {
          description:
            "Disallow hard-coded Tailwind duration-* / animate-[…ms] in feature components",
        },
        messages: {
          raw: "Hard-coded motion '{{snippet}}' — use tokens from @/lib/design/motion",
        },
        schema: [],
      },
      create(context) {
        const DURATION = /\bduration-(?:\d{2,3})\b/;
        const ANIMATE_MS = /animate-\[[^\]]*\d+ms/;

        function inspect(value, node) {
          if (!value || typeof value !== "string") {
            return;
          }
          const durationMatch = value.match(DURATION);
          if (durationMatch) {
            context.report({
              node,
              messageId: "raw",
              data: { snippet: durationMatch[0] },
            });
            return;
          }
          const animateMatch = value.match(ANIMATE_MS);
          if (animateMatch) {
            context.report({
              node,
              messageId: "raw",
              data: { snippet: animateMatch[0].slice(0, 40) },
            });
          }
        }

        return {
          Literal(node) {
            if (typeof node.value === "string") {
              inspect(node.value, node);
            }
          },
          TemplateElement(node) {
            inspect(node.value.raw, node);
          },
        };
      },
    },
  },
};

export default plugin;
