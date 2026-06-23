"use client";

import Link from "next/link";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background text-foreground antialiased">
        <main className="mx-auto flex max-w-lg flex-col gap-4 px-6 py-24">
          <h1 className="text-xl font-semibold">Something went wrong</h1>
          <p className="text-sm text-muted-foreground">
            {error.message || "An unexpected error occurred. Try again or return to the home page."}
          </p>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => reset()}
              className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
            >
              Try again
            </button>
            <Link href="/" className="rounded-md border px-4 py-2 text-sm font-medium">
              Home
            </Link>
          </div>
        </main>
      </body>
    </html>
  );
}
