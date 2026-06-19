# Analytics Event Taxonomy

All events are tracked via `track()` from `src/lib/analytics/events.ts`.  
Events fire only when the user has accepted the `jober_analytics_consent` cookie and DNT is off.

## Rules

- Never include passwords, tokens, API keys, raw LLM prompts/completions, or any PII in event properties.
- Use the typed `track()` wrapper — never call `trackEvent()` directly from feature code.
- All event names use `domain.action` dot notation (past tense where possible).

---

## Event Reference

### Page

| Event | When | Properties |
|---|---|---|
| `page.view` | Every route change | `path`, `title` |

Fired automatically by `AnalyticsProvider` — do not call manually.

---

### CTA

| Event | When | Properties |
|---|---|---|
| `cta.click` | Marketing CTA button clicked | `feature`, `href?` |

---

### Auth

| Event | When | Properties |
|---|---|---|
| `auth.signup_started` | Signup page mounts | `method: "native" \| "google"` |
| `auth.signup_completed` | `register()` succeeds | `method: "native" \| "google"` |
| `auth.signup_failed` | Signup submit fails | `reason: "validation" \| "server" \| "duplicate"` |
| `auth.signin_completed` | `login()` succeeds | `method: "native" \| "google"` |
| `auth.signin_failed` | Login submit fails | `reason: "credentials" \| "server" \| "not_found"` |

---

### Batch / Run

| Event | When | Properties |
|---|---|---|
| `batch.launched` | User opens batch preview (non-dry) | `item_count`, `policy` |
| `batch.paused` | "Pause all" clicked | — |
| `batch.resumed` | "Resume all" clicked | — |
| `run.viewed` | Run console page loads | `run_id` |
| `checkpoint.reviewed` | Checkpoint actioned | `action: "approve" \| "reject" \| "skip"` |

---

### Vault

| Event | When | Properties |
|---|---|---|
| `vault.updated` | Profile vault section saved | `section` |

---

### Discover / Library

| Event | When | Properties |
|---|---|---|
| `discover.search` | Search boards button clicked | `board`, `result_count` |
| `library.list_created` | New job list created | — |
| `library.candidates_accepted` | Candidates accepted into list | `count` |

---

### Documents

| Event | When | Properties |
|---|---|---|
| `document.generated` | Cover letter / document generated | `doc_type` |

---

### Observability

| Event | When | Properties |
|---|---|---|
| `web.vital` | Core Web Vital measured | `name` (CLS/LCP/…), `value`, `rating` |
| `client.error` | Unhandled JS error / rejected promise | `message` (≤200 chars), `path` |

These are emitted automatically by `AnalyticsProvider` — do not call manually.

---

## Adding a new event

1. Add an entry to `AnalyticsEventMap` in `src/lib/analytics/events.ts`.
2. Call `track("your.event", { ... })` from the relevant component.
3. Update this doc.
