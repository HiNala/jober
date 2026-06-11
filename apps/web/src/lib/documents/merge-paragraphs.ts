/** Mirror of API `letter_editor.merge_paragraphs` — locked indices stay on regen. */
export function mergeParagraphs(
  original: string[],
  updated: string[],
  lockedIndices: ReadonlySet<number>,
): string[] {
  const merged: string[] = [];
  const count = Math.max(original.length, updated.length);
  for (let index = 0; index < count; index += 1) {
    if (lockedIndices.has(index) && index < original.length) {
      merged.push(original[index]!);
    } else if (index < updated.length) {
      merged.push(updated[index]!);
    } else if (index < original.length) {
      merged.push(original[index]!);
    }
  }
  return merged;
}

export function splitParagraphs(body: string): string[] {
  return body.split("\n\n").map((part) => part.trim()).filter(Boolean);
}
