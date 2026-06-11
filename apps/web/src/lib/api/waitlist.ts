import { apiFetch } from "@/lib/api/client";

export type ProWaitlistStatus = "created" | "already_registered";

export async function joinProWaitlist(input: {
  email: string;
  consentContact: boolean;
  source?: string;
}): Promise<{ status: ProWaitlistStatus }> {
  return apiFetch<{ status: ProWaitlistStatus }>("/api/waitlist/pro", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: input.email,
      consent_contact: input.consentContact,
      source: input.source ?? "pricing",
    }),
  });
}
