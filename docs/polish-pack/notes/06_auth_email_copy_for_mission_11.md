# Auth email copy — Mission 11 handoff

**From:** Mission 06 (2026-06-11) · **Owner:** Mission 11 (email delivery)

## Current behavior

- Register → session established; **no inbox verification required** (GP-004).
- Forgot-password API creates a token but **does not send email** in production (GP-001/002).
- Dev API returns `X-Jober-Reset-Token` header when `JOBER_ENV=development`.

## UI copy (Mission 06)

| Surface | Copy intent |
|---------|-------------|
| Signup subtitle | Workspace ready immediately — no verify-first promise |
| Forgot-password subtitle | Notes reset email not live on this deployment |
| Forgot-password success | Request received; directs to sign-in / support — **no “check your inbox”** |

## When Mission 11 ships SMTP/Resend

1. Update `lib/auth/copy.ts` — `FORGOT_PASSWORD_SUBTITLE`, `FORGOT_PASSWORD_SUCCESS`.
2. Optionally add verification email sent state on signup if product enforces verify.
3. Re-capture auth screenshots `11–13` + reset-password.
4. Close GP-001/002 in `03_golden_path_findings.md`.
