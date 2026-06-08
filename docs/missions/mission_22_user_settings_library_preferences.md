# Mission 22 — User Settings, Library & Preferences

## Task list
- [x] Unified Library: resumes, cover letters, job lists, runs
- [x] Settings sections: vault, application defaults, AI/BYOK, appearance, account, notifications
- [x] Server-side `user_preferences` JSONB per user
- [x] BYOK provider keys encrypted (`user_provider_keys`); never returned to client
- [x] Global Library search (`/search`) from nav
- [x] Export-my-data and delete-account in Settings (Mission 14/15 APIs)
- [x] Resume activate endpoint; cover letter lock-template patch
- [x] Job lists CRUD + reorder API

## Acceptance criteria
- [x] Library lists and opens asset types; resume active-version switching
- [x] Settings persist server-side and apply immediately (theme, reduced-motion)
- [x] BYOK keys encrypted; gateway uses user key when env key absent
- [x] Export/delete wired in privacy settings section
- [x] Design Council ≥18/20 on Library + Settings

## API routes

| Route | Purpose |
|-------|---------|
| `GET/PATCH /api/settings/preferences` | User appearance, notifications, defaults, AI prefs |
| `GET/PUT/DELETE /api/settings/provider-keys/{provider}` | BYOK (openai, anthropic) |
| `GET /api/library/resumes` | Resume assets for tenant |
| `GET /api/library/cover-letters` | Generated letters |
| `GET /api/library/runs` | Past application runs |
| `GET /api/library/search?q=` | Cross-library search |
| `GET/POST/PATCH/DELETE /api/job-lists/*` | Named target lists |
| `POST /api/resumes/{id}/activate` | Set active resume |

## Web routes

| Route | Purpose |
|-------|---------|
| `/library` | Tabbed library (resumes, letters, jobs, runs) |
| `/search` | Global library search |
| `/settings` | Vault + all preference sections |
| `/documents`, `/vault` | Redirect to library/settings |

## Notes
- Delete account confirm phrase: `DELETE ALL MY DATA`
- Partial UI: resume version history preview, 2FA setup stub (job list archive/reorder UI added in M99)
- Iteration clause: global search — done

## Mission 99 (post–Mission 22)
- [x] Search lint fix; BYOK gateway wiring; API tests for prefs/BYOK
- [x] Design review 20/20 logged
- [x] Job list archive/reorder UI; library search + archive API tests
- [x] Provider-key PUT never returns full secret (test)
- [x] README updated for `/library`, `/search`, Mission 22 prefs/BYOK
