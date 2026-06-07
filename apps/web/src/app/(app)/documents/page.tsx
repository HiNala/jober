"use client";

import { DocumentStudio } from "@/components/documents/document-studio";

export default function DocumentsPage() {
  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Document Studio</h1>
        <p className="text-sm text-muted-foreground">
          Generate grounded cover letters with ATS coverage — no fabricated claims.
        </p>
      </div>
      <DocumentStudio />
    </div>
  );
}
