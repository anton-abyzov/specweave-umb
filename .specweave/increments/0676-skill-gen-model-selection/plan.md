# 0676 — Implementation Plan

## Source of Truth

Design rationale lives in ADR `.specweave/docs/internal/architecture/adr/0676-01-skill-gen-model-selection.md`. User stories and ACs are in `spec.md` alongside this file. Original approved plan (scoping + alternatives): `/Users/antonabyzov/.claude/plans/compiled-tumbling-lecun.md`.

## Architecture

```
caller (eval pipeline)
        │
        ▼
createClaudeAdapter(apiKey)             ← src/lib/eval/claude-adapter.ts
        │
        ├─ resolveModel(SKILL_EVAL_MODEL)  ← src/lib/eval/model-registry.ts
        │      ├─ alias ("opus"/"sonnet"/"haiku") → current tier entry
        │      ├─ full ID (known/BYO) → pass-through
        │      └─ undefined → default Opus
        │
        └─ new Anthropic({ apiKey, baseURL: ANTHROPIC_BASE_URL? })
                ├─ baseURL unset → api.anthropic.com (default)
                └─ baseURL set   → AnyModel proxy → any backend
                                   (GPT-5, Gemini 3, OpenRouter,
                                    LM Studio, Ollama, ...)

Regression guard (runs in Playwright):
  validateSkillMarkdown(md)              ← src/lib/skills/skill-validator.ts
        ├─ frontmatter parse + name/description checks
        ├─ body ## heading required
        └─ no HTML inside mermaid blocks (Docusaurus regression)

Operator self-check endpoint:
  GET /api/v1/models/default             ← src/app/api/v1/models/default/route.ts
        → { modelId, tier, defaultOpus, envOverride, baseURLOverride }
```

## Files Touched

| File | Action | Purpose |
|------|--------|---------|
| `repositories/anton-abyzov/vskill-platform/src/lib/eval/model-registry.ts` | NEW | Priority-ordered registry + resolver functions |
| `repositories/anton-abyzov/vskill-platform/src/lib/eval/claude-adapter.ts` | EDIT | Use resolver, thread `ANTHROPIC_BASE_URL` |
| `repositories/anton-abyzov/vskill-platform/src/lib/skills/skill-validator.ts` | NEW | SKILL.md structural + auto-activation-quality validator |
| `repositories/anton-abyzov/vskill-platform/src/app/api/v1/models/default/route.ts` | NEW | Read-only debug/meta endpoint — asserts resolver state from outside |
| `repositories/anton-abyzov/vskill-platform/src/lib/eval/__tests__/model-registry.test.ts` | NEW | 14 Vitest cases |
| `repositories/anton-abyzov/vskill-platform/src/lib/eval/__tests__/claude-adapter.test.ts` | NEW | 7 Vitest cases (mock `@anthropic-ai/sdk`) |
| `repositories/anton-abyzov/vskill-platform/src/lib/skills/__tests__/skill-validator.test.ts` | NEW | 18 Vitest cases |
| `repositories/anton-abyzov/vskill-platform/tests/e2e/skill-creation.spec.ts` | NEW | 11 Playwright cases covering AC-US4-01..04 |
| `repositories/anton-abyzov/specweave/plugins/specweave/skills/skill-gen/SKILL.md` | EDIT | Add "Model Selection" section |
| `.claude/skills/skill-creator/SKILL.md` | EDIT | Add "Model Recommendations" note |
| `.specweave/docs/internal/architecture/adr/0676-01-skill-gen-model-selection.md` | NEW | ADR capturing the decision |
| `.specweave/increments/0670-skill-builder-universal/plan.md` | EDIT | Seed cross-increment guidance so 0670 doesn't invent a second resolver |

## TDD Order (RED → GREEN → REFACTOR)

1. Write `model-registry.test.ts` (RED) — 14 cases covering AC-US1-01/03, AC-US2-01/03.
2. Implement `model-registry.ts` (GREEN) — registry data + two pure functions.
3. Write `claude-adapter.test.ts` (RED) — 7 cases covering AC-US1-02 (source-level check) + AC-US2-02 (baseURL threading, mocked SDK).
4. Edit `claude-adapter.ts` (GREEN) — import resolver, thread baseURL.
5. Write `skill-validator.test.ts` (RED) — 18 cases covering AC-US3-01..05.
6. Implement `skill-validator.ts` (GREEN) — zero-dep frontmatter parser + checks.
7. Add `GET /api/v1/models/default` route — simple wrapper over resolver.
8. Write Playwright `skill-creation.spec.ts` — 11 cases covering AC-US4-01..04. Runs in the `chromium` project (unauth) since the endpoint is public metadata and validator tests are pure imports.
9. Update SKILL.md files + ADR + 0670 plan cross-reference.

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Hardcoded model string creeps back into adapter | Source-scan assertion in `claude-adapter.test.ts` (`expect(src).not.toContain("claude-sonnet-4-6")`) |
| Registry ordering bug (legacy before current) | Invariant test iterates per tier — once a legacy entry appears, current entries must not follow |
| AnyModel baseURL silently ignored | `claude-adapter.test.ts` mocks the SDK constructor and asserts `baseURL` is passed through |
| Validator rejects real SKILL.md from production | Action-verb list is conservative (removed prepositions `to`, `for`); expanded to 29 common verbs |
| 0670 duplicates the resolver | Cross-increment note inserted in `0670-skill-builder-universal/plan.md` |
| Playwright dev server collision (port 3000) | Spec works under unauth `chromium` project; run with `E2E_BASE_URL=http://localhost:<free-port>` if default port is taken |

## Verification

- `npx vitest run src/lib/eval/__tests__/model-registry.test.ts src/lib/eval/__tests__/claude-adapter.test.ts src/lib/skills/__tests__/skill-validator.test.ts` → 39/39 passing
- `E2E_BASE_URL=http://localhost:3077 npx playwright test tests/e2e/skill-creation.spec.ts --project=chromium` → 11/11 passing
- Operator self-check (manual): `curl http://localhost:<port>/api/v1/models/default` → `{"modelId":"claude-opus-4-7","tier":"opus",...}`
- BYO smoke (manual): start `npx anymodel proxy --model openrouter/deepseek/deepseek-chat-v3.2 --port 8787` in another shell, re-curl the endpoint with `ANTHROPIC_BASE_URL=http://localhost:8787 SKILL_EVAL_MODEL=openrouter/deepseek/deepseek-chat-v3.2` — `baseURLOverride` and `envOverride` fields should surface the values.

## Definition of Done

- All 15 ACs across US-001..US-004 marked `[x]` in `spec.md`.
- 39 unit tests + 11 Playwright tests passing.
- ADR `0676-01` committed; 0670 plan.md cross-reference in place.
- `sw:done` closure gates pass (code-review, simplify, grill, judge-llm, PM gates).
