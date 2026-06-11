/** @type {import('eslint').ESLint.Plugin} */
const plugin = {
  rules: {
    "no-raw-color-literal": {
      meta: {
        type: "problem",
        docs: {
          description:
            "Disallow raw #hex / #rgb color literals in feature components — use design tokens",
        },
        messages: {
          raw: "Raw color literal '{{snippet}}' — use tokens from globals.css / @/lib/design/tokens",
        },
        schema: [],
      },
      create(context) {
        const HEX = /#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b/;

        function inspect(value, node) {
          if (!value || typeof value !== "string") {
            return;
          }
          const match = value.match(HEX);
          if (match) {
            context.report({
              node,
              messageId: "raw",
              data: { snippet: match[0] },
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
