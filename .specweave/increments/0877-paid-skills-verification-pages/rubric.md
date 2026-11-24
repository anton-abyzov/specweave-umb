# Rubric: 0877-paid-skills-verification-pages

## Quality Contract

A staff engineer (and a skeptical security engineer, for /verification) must approve this before close.

### Business truth (hard gate — corrected scope 2026-07-01)
- [ ] **Zero marketplace claims anywhere**: no selling, revenue share, platform fees, payouts, paid packs, or third-party licensing language on any page touched by this increment. The paid model is presented exclusively as private skill **storage + security + scanning**.
- [ ] Page ships at `/private-skills` with hero "Your team's skills. Stored, secured, scanned."; `/paid-skills` is a permanent redirect only.
- [ ] Design-partner CTA promises only: white-glove migration, flat founder pricing year one, direct line to founder.

### Honesty (hard gate — this increment is a trust asset)
- [ ] No claim on /verification or /private-skills overstates the implementation; verification language is "reduces risk", never "guarantees safe" (or equivalent).
- [ ] Every number (52 patterns, 9 categories, agent count 53-vs-54 resolved, 0–100 score, twice-daily) was re-verified against source files at implementation time — not copied from planning notes.
- [ ] Sample verification report mirrors the real report shape (`verify-result.json` + `ScanResult` fields) and is explicitly labeled as a sample.
- [ ] All screenshots are real product captures — zero fabricated/mocked/AI-generated UI; no secrets, tokens, or personal emails visible in any capture.

### Copy & design fidelity
- [ ] /private-skills copy is faithful to `assets/private-skills-page-draft.md` (CORRECTED 2026-07-01); only placeholder resolution and grammar-level deviations.
- [ ] Both pages are indistinguishable in styling from existing pages (inline styles + CSS vars, 960px, JetBrains Mono display, #F25F1C accents); verified visually in light AND dark themes.
- [ ] No Tailwind, no CSS modules, no new client components.

### Engineering
- [ ] TDD order respected (RED suites exist and failed before GREEN; documented in task completion notes).
- [ ] `npx vitest run` fully green; existing pricing/layout tests updated — none deleted or skipped to pass.
- [ ] E2E smoke spec passes; `<details>` FAQ works without JS enabled; /paid-skills redirect verified.
- [ ] `mailto:anton.abyzov@gmail.com` count in `src/app/pricing/page.tsx` is exactly 0; contact path defined once in `src/lib/contact.ts`.
- [ ] Metadata complete on both pages: title, description, canonical, OG (1200×630), twitter, JSON-LD — matching site conventions.
- [ ] Images ≤ 300 KB each with descriptive alt text.

### Deployment
- [ ] Deploy used the clean chain (cache purge → `build:worker` → `wrangler deploy`); queue-health 401 acknowledged as benign, not "fixed".
- [ ] Live URLs verified by curl (200 + content, redirect for /paid-skills) and recorded in completion notes.
- [ ] vskill-platform commits pushed to `main`; umbrella increment committed.

### Non-goals guard
- [ ] No paid-pack checkout/backend was built; no new contact API; /press mailto untouched (flagged as follow-up).
