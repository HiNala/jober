# Mission 08 — Pro waitlist mechanism

**Date:** 2026-06-11

## Decision

Chose a dedicated `pro_waitlist_entries` table + public `POST /api/waitlist/pro` over analytics events because:

- Email capture requires explicit contact consent, independent of analytics opt-in.
- Waitlist is operational data (launch comms), not product analytics.
- Dedupe by normalized email is trivial with a unique constraint.

## Storage

| Field | Type | Notes |
|-------|------|-------|
| `email` | `varchar(320)` unique | Lowercased on insert |
| `source` | `varchar(64)` | Default `pricing` |
| `consent_contact` | `boolean` | Required `true` on submit |
| `created_at` / `updated_at` | timestamptz | Standard mixins |

Migration: `q9r0s1t32u63_pack08_pro_waitlist.py`

## API

- `POST /api/waitlist/pro` — public (in `PUBLIC_API_PREFIXES`), rate-limited per IP via Redis (`waitlist:{ip}` bucket).
- Body: `{ email, consent_contact, source? }`
- Response: `{ status: "created" | "already_registered" }` — duplicates return 200 with `already_registered` (idempotent UX).

## Retrieval

No admin UI in this mission. Operators can query Postgres:

```sql
SELECT email, source, created_at FROM pro_waitlist_entries ORDER BY created_at DESC;
```

Future: Mission 11/30 may add admin export or Resend integration for launch email.

## Privacy

- Waitlist emails are stored for one purpose: Pro billing launch notification.
- Form links to `/privacy`; consent checkbox is required.
- Not mixed with `analytics_events` or shared with third parties.

## Web

- `ProWaitlistForm` on `/pricing` Pro card — states: loading, success, duplicate, error.
- Client: `lib/api/waitlist.ts`
