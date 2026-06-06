import { FileUpload } from "@/components/import/file-upload";
import { PageEmpty } from "@/components/states/page-states";

export default function VaultPage() {
  return (
    <div className="space-y-8 p-4 md:p-6">
      <section className="max-w-xl space-y-2">
        <h2 className="text-sm font-medium">Import spreadsheet</h2>
        <p className="text-sm text-muted-foreground">
          Full XLSX import lands in Mission 03. Dropzone is wired for early UX testing.
        </p>
        <FileUpload />
      </section>
      <PageEmpty
        title="Profile vault"
        description="Resume assets and encrypted EEO answers are managed here starting Mission 04."
      />
    </div>
  );
}
