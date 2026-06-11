function slugPart(value: string): string {
  return value
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-")
    .slice(0, 48);
}

export function coverLetterDownloadFilename(
  company: string,
  role: string,
  ext: "pdf" | "docx",
): string {
  const companyPart = slugPart(company) || "company";
  const rolePart = slugPart(role) || "role";
  return `cover-letter-${companyPart}-${rolePart}.${ext}`;
}
