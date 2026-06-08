# Mission 21 — Google OAuth & Account Linking

## Task list
- [x] OAuth 2.0 / OIDC with Google (authorization code + PKCE)
- [x] `AuthIdentity` table: one user → many identities; unique on (provider, provider_user_id)
- [x] Account linking: verified-email match requires password confirmation; settings link/unlink
- [x] Sign-in/sign-up Google button + linked methods in settings
- [x] Google client id/secret via env; redirect URI per environment
- [x] Edge cases: unverified Google email, returning user, cannot unlink last credential
- [x] Provider-agnostic OAuth registry (GitHub-ready)

## Acceptance criteria
- [x] Google sign-in creates user (first time) and signs in (returning) without duplicates
- [x] Linking to existing verified native account requires password confirmation
- [x] Cannot unlink last remaining sign-in method
- [x] Secrets env-only; native auth unchanged

## Configuration

| Variable | Purpose |
|----------|---------|
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret (never commit) |
| `GOOGLE_REDIRECT_URI` | Callback URL, e.g. `http://localhost:8000/api/auth/google/callback` |
| `WEB_APP_URL` | Post-auth redirect base, e.g. `http://localhost:3000` |
| `OAUTH_STATE_TTL_SECONDS` | PKCE/state Redis TTL (default 600) |

Register redirect URIs in Google Cloud Console for local, staging, and production API hosts.

## API routes

| Route | Purpose |
|-------|---------|
| `GET /api/auth/google/start` | Begin sign-in (public) |
| `GET /api/auth/google/callback` | OAuth callback (public) |
| `GET /api/auth/google/link/start` | Link Google while signed in |
| `POST /api/auth/google/confirm-link` | Confirm link with password |
| `GET /api/auth/identities` | List linked methods |
| `DELETE /api/auth/identities/{provider}` | Unlink OAuth provider |

## Mission 99 (post–Mission 21)
- [x] Document Google OAuth env vars in `.env.example`
- [x] Quality gates: ruff, mypy, web lint/typecheck; OAuth tests run in CI with Postgres + Redis
- [x] CI: retry MinIO `mc` download on transient CDN failures
- [x] Fix confirm-link token consumed before password verification
