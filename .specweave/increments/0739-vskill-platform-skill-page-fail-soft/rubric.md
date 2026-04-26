---
increment: 0739-vskill-platform-skill-page-fail-soft
title: "vskill-platform: skill page must always render — defensive fail-soft on blocklist/rejected fallback queries"
generated: 2026-04-26
source: auto-generated
version: "1.0"
status: active
---

# Quality Contract — 0739-vskill-platform-skill-page-fail-soft

## Quality Contract

This rubric defines the per-increment quality contract consumed by closure gates (`sw:code-reviewer`, `sw:simplify`, `sw:grill`, `sw:judge-llm`, PM validation).

## Mandatory gates

| Gate | Threshold | Verifier |
|------|-----------|----------|
| **Vitest unit tests** | 4 cases pass (TC-001..TC-004), exit code 0 | `npx vitest run src/lib/__tests__/data-failsoft.test.ts` from `repositories/anton-abyzov/vskill-platform/` |
| **Vitest full-suite regression** | 0 NEW failures vs. baseline | `npx vitest run` from `repositories/anton-abyzov/vskill-platform/` |
| **Playwright e2e** | TC-005 passes | `BASE_URL=https://verified-skill.com npx playwright test tests/e2e/skill-not-found.spec.ts` |
| **Code review** | No critical / high / medium findings on the data.ts diff | `sw:code-reviewer` writes `code-review-report.json` |
| **Simplify** | Diff stays at ~4 lines net + tests; no scope creep | `/simplify` runs after code-review |
| **Grill** | Reviewer accepts the data.ts/data-failsoft.test.ts/skill-not-found.spec.ts triple as a complete fix | `sw:grill` writes `grill-report.json` |

## AC-to-gate mapping

| AC | Verified by |
|----|-------------|
| AC-US1-01 (blocklist throw → null + 404) | TC-001 (vitest) |
| AC-US1-02 (rejected throw → null + 404) | TC-003 (vitest) |
| AC-US1-03 (happy paths unchanged) | TC-002 + TC-004 (vitest) |
| AC-US1-04 (warn line shape) | TC-001 + TC-003 spy assertions (vitest) |
| AC-US1-05 (Playwright soft-404 contract) | TC-005 (Playwright) |
| AC-US2-01 (single warn line, blocklist) | TC-001 spy assertion (`toHaveBeenCalledTimes(1)`) |
| AC-US2-02 (single warn line, rejected) | TC-003 spy assertion (`toHaveBeenCalledTimes(1)`) |

## Definition of done

1. All 7 ACs flipped to `[x]` in spec.md.
2. All 13 tasks flipped to `[x]` in tasks.md.
3. `metadata.json` status → `ready_for_review` (then `done` after closure gates pass).
4. Two commits — vskill-platform child repo (data.ts + tests) and umbrella (increment artifacts).
5. Both pushed to GitHub.
6. Production deploy completes; manual sample of `wrangler tail` shows zero `digest:` strings on the canonical skill route.

## Risk-of-regression checklist

Reviewer must confirm during `sw:grill` that none of these are broken:
- [ ] Real existing blocklist entries still render `<BlockedSkillView>` (TC-002 covers).
- [ ] Real existing rejected submissions still render `<RejectedSkillView>` (TC-004 covers).
- [ ] `getSkillByName` itself is NOT modified (line 237 still rethrows — preserves "could not be loaded" UX for primary-lookup failures).
- [ ] No new env var, no new dependency, no new prisma migration.
- [ ] `generateMetadata` in `page.tsx:49-86` still works — it uses the same two functions, and now they fail soft to `{ title: "Skill Not Found | verified-skill.com" }` on DB hiccup, which is also acceptable.
