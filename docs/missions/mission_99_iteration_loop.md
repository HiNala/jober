# Mission 99 — Iteration Loop (Perfection-Aware)

Run this **between every numbered mission** (including 35–45) before advancing.

## Objective

Finish leftovers, self-improve, and raise the bar on the previous mission’s deliverables — without feature creep.

## Checklist

### Close the last mission
- [ ] Re-read prior mission acceptance criteria; close gaps or record blockers with evidence
- [ ] Update task checkboxes in the prior mission file honestly
- [ ] Note deferred items in `docs/polish-pack/notes/` or mission “Deferred” section

### Quality gates
- [ ] API: `ruff check src tests` · `mypy src` · relevant `pytest`
- [ ] Worker: `ruff` · `mypy` · `pytest` when worker touched
- [ ] Web: `pnpm typecheck` · `pnpm lint:strict` · `pnpm test` · `pnpm build` when web touched
- [ ] Motion/color lint: `pnpm check:motion` when design touched
- [ ] `detect-secrets` clean when secrets surface changes

### Product & design bar
- [ ] Re-check Design Council for touched surfaces (target ≥19/20 in perfection pack)
- [ ] Reduced-motion still honored
- [ ] No fake/disabled “coming soon” controls introduced
- [ ] Mobile spot-check at 375px for any user-facing change
- [ ] Screenshots re-captured if UI changed

### Self-improvement (required)
- [ ] Fix one adjacent rough edge discovered while verifying (small, related)
- [ ] Add or extend a test for any bug fixed (fixture-for-every-bug)
- [ ] Update docs if behavior or env vars changed

### Git
- [ ] Focused commits with mission tag (`[mNN]` or `[m99]`)
- [ ] No `--no-verify`; no secrets committed
- [ ] Push at mission boundary when gates green (repo convention)

## Perfection-pack extras (M35–45)

- [ ] Align with [`design-north-star-2030.md`](../architecture/design-north-star-2030.md)
- [ ] Prefer refine/repair over new surface area
- [ ] If Stripe/Google/SMTP blocked on credentials, document exact unblock steps — do not fake UI

## Exit criteria

All prior mission acceptance criteria still pass after iteration changes; tree clean; gates green for touched packages.
