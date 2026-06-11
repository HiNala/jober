/** Client-side consent helpers — shared by the consent sheet and settings. */

export const CONSENT_COOKIE = "jober_analytics_consent";
export const CONSENT_PROMPTED_KEY = "jober_analytics_consent_prompted";

/** True when the user has chosen Accept or Decline (cookie is set to 0 or 1). */
export function hasConsentDecision(): boolean {
  if (typeof document === "undefined") return false;
  return new RegExp(`(?:^|;\\s*)${CONSENT_COOKIE}=`).test(document.cookie);
}

/** True when the one-time consent sheet should open (no decision yet). */
export function shouldPromptConsent(): boolean {
  return !hasConsentDecision();
}

export function markConsentPrompted(): void {
  if (typeof localStorage === "undefined") return;
  localStorage.setItem(CONSENT_PROMPTED_KEY, "1");
}
