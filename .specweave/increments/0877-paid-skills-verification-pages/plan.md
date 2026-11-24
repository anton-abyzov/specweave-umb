# Implementation Plan: Private Skills & Verification Marketing Pages

> **Corrected scope (2026-07-01)**: no paid-skills marketplace exists. Paid model = private skill **storage + security + scanning**. Route is `/private-skills`; `/paid-skills` is a permanent redirect only.

## Overview

Two static, server-rendered marketing pages in `repositories/anton-abyzov/vskill-platform` (Next.js App Router on Cloudflare via OpenNext), plus pricing-page CTA rework, chrome links, real screenshot capture, and a production deploy. No new backend, no schema changes, no new client components.

**Working directory note**: all implementation happens in the main checkout `repositories/anton-abyzov/vskill-platform` (its own git repo, branch `main`) — `repositories/` is gitignored in the umbrella and does not exist in Claude worktrees.

## Design

### Components & files

| Change | File | Notes |
|---|---|---|
| /private-skills page | `src/app/private-skills/page.tsx` (new) | Async server component; copy from `assets/private-skills-page-draft.md` (corrected 2026-07-01) |
| /paid-skills redirect | `next.config.ts` `redirects()` | `{ source: '/paid-skills', destination: '/private-skills', permanent: true }` — check existing redirects config first |
| /verification page | `src/app/verification/page.tsx` (new) | Async server component; facts per table below; sample report section |
| Sample report data | `src/app/verification/sample-report.ts` (new) | Typed constant mirroring real report shape; keeps page.tsx readable |
| Contact path constants | `src/lib/contact.ts` (new) | `ENTERPRISE_CONTACT_PATH = '/pricing#enterprise-contact'`, `DESIGN_PARTNER_CONTACT_PATH` (same until a calendar URL exists) |
| Enterprise CTA + hero link | `src/app/pricing/page.tsx` | Delete `ENTERPRISE_MAILTO` (~line 65); CTA → `ENTERPRISE_CONTACT_PATH`; add `id="enterprise-contact"` on waitlist form section + retitle to contact/talk-to-sales framing; hero gets `/private-skills` link |
| Docs hub cards | `src/app/docs/page.tsx` | DocCard for /private-skills + DocCard for /verification (Security section) |
| Footer links | `src/app/layout.tsx` | `footerLink`-styled anchors for both pages |
| Screenshots | `public/images/private-skills/*.png`, `public/images/verification/*.png` | Real captures only; optimized ≤300KB |
| OG images | `public/og/private-skills.*`, `public/og/verification.*` | Follow existing `/public/og/` convention (check what `/og/pricing.png` actually serves — SVGs exist on disk; match whatever works live) |
| Unit tests | `src/app/private-skills/__tests__/page.test.tsx`, `src/app/verification/__tests__/page.test.tsx` (new); update `src/app/pricing/__tests__/page.test.tsx`, `src/app/__tests__/layout.nav.test.tsx` | Existing patterns: `renderToString` for pages, string-grep for layout |
| E2E smoke | `e2e/0877-marketing-pages.spec.ts` (new) | Route 200s, redirect, H1s, CTA hrefs, details toggle |

### Page architecture — /private-skills

Section order = corrected-draft order: Hero ("Your team's skills. Stored, secured, scanned.") → problem strip (unscanned skill sharing over Slack/gists/git + Snyk stat) → 4-step how-it-works (Create & test → Publish privately w/ 3-tier scan → **We store and secure it** (isolated tenant, default-deny, audit log) → one-command install; each step: number, heading, copy, screenshot) → "Why not just a git repo?" table → "What the scan covers" trust strip (links `/verification`) → pricing recap (Pro = private skill storage) → FAQ (`<details>`) → final design-partner CTA (white-glove migration, flat founder pricing — **no marketplace promises**). All sections `maxWidth: 960`, `padding: '3rem 2rem'`, `borderTop: '1px solid var(--border)'` separators; pill badges `rgba(242,95,28,0.08)` bg + `#F25F1C` text.

**Deleted from the original plan**: two-path selector, "Path B: selling skills", revenue-split/payout FAQ, "0% platform fee" — the marketplace does not exist.

### Page architecture — /verification

Hero ("What 'verified' actually means" + honest one-liner) → pipeline overview (numbered 5-stage walk-through with a simple stage diagram built from styled divs, no image) → Tier 1 patterns section (9 category chips + counts) → Tier 2 intent analysis → prompt-injection probes → runtime execution (units/fixtures/invariants) → per-version transcript fields → re-verification schedule → **full sample verification report** (styled: summary header verdict PASS, Tier 1/Tier 2 summary cards, unit/fixture/check tree with `invariant.*` rows; collapsible `<details>` with raw JSON) → honesty note ("what verification does NOT prove") → CTA row (`/private-skills`, `/pricing`, GitHub).

The "what it does NOT prove" section is deliberate: it makes the trust asset credible to security reviewers — the exact audience of cold outreach.

### Fact sources for /verification (verify at implementation time)

| Claim | Source of truth |
|---|---|
| 52 Tier-1 patterns, 9 categories (CI/DE/PE/CT/PI/FS/NA/CE/DCI) | `vskill-platform/crawl-worker/lib/scanner-patterns.js` |
| Tier 2: intent/scope/concerns, 0–100 score, LLM models | `ScanResult` model, `prisma/schema.prisma` (~lines 760–820) |
| Verdicts PASS/CONCERNS/FAIL; severity counts; contentHash; commitSha; scannerVersion; durationMs | same `ScanResult` model |
| Submission states incl. `RESCAN_REQUIRED`, `AUTO_APPROVED`, `BLOCKED` | `SubmissionState` enum, `prisma/schema.prisma` (~lines 15–29) |
| Blocklist gate | `BlocklistEntry` model (~lines 988–1013) |
| Runtime verify report shape (`units[]/fixtures[]/checks[]`, `invariant.*`, `surface`, BLOCKED verdict, probe fixtures) | `vskill/test/verify/reports/verify-result.json` + 0853/0857 specs |
| Re-verification cadence (twice-daily CI stub lane + real-model lane; loud-skip; per-version rescan) | 0858 spec + `matrix.test.mjs` assertion |
| Agent count (**draft says 53, vskill README badge says 54 known — confirm before hardcoding**) | `vskill` README badge / agents registry |
| Semver + per-version cert (`certTier`, `treeHash`, yank/deprecate) | `SkillVersion` model (~lines 635–714) |
| Snyk prompt-injection stat (problem strip) | As worded in approved copy draft — external stat, keep the draft's wording/attribution |

### Screenshot capture plan (US-003)

1. **Studio UI** (drawer/PrivacyChooser, PaywallModal, sidebar grouping, My Queue; audit-log view bonus): run Studio locally (`vskill studio` from `repositories/anton-abyzov/vskill`; platform stack per memory `vskill-platform-local-stack` if Studio needs the platform API — vault creds → `.env.local`, `prisma db push`, `E2E_BYPASS=1`). Drive with Playwright CLI (preferred per config `testing.playwright.preferCli`) at 1440×900, capture element-cropped PNGs. PaywallModal requires a Free-tier context at the private-skill limit (`VSKILL_FREE_PRIVATE_SKILL_LIMIT`; seed or toggle locally). My Queue needs at least one submission in a non-terminal state — reuse the 0862 lifecycle-demo seeding approach if available.
2. **CLI verified-install**: run a real `vskill install <org/skill>` against a verified skill, capture terminal output (freeze/termshot screenshot, or preserve exact text and render as a styled terminal block — decide at implementation by what looks better against site style).
3. Optimize: `sips`/`pngquant` to ≤300KB, verify no secrets/tokens/emails visible in captures.
4. Copies of final assets also land in `assets/screenshots/studio/` in this increment (provenance).

### Deploy (US-006)

From `repositories/anton-abyzov/vskill-platform`:

```bash
rm -rf .next .open-next .turbo node_modules/.cache   # stale-cache guard (known false "pages/500" error otherwise)
npm run build:worker                                  # opennextjs-cloudflare build + worker entry
npx wrangler deploy                                   # worker: verified-skill-com (OAuth-authed)
```

Postdeploy `queue-health` smoke returns 401 locally — benign (script lacks internal key). Verify via `Current Version ID` output + curl of the two new URLs, the /paid-skills redirect, and pricing page grep.

## Rationale

- **`/private-skills` + permanent redirect from `/paid-skills`**: the corrected scope kills the marketplace framing, but earlier GTM deliverables (prospect list, proposal letters) may already reference `/paid-skills`; a `next.config.ts` 308 keeps every circulated link working at near-zero cost.
- **No-marketplace guard as a negative AC** (AC-US1-02): the correction is a business-truth constraint, so it's encoded as a testable assertion (grep the rendered HTML for banned seller-language), not just a note — prevents regression if copy gets edited later.
- **Server components, native HTML interactivity** (`<details>` FAQ, anchor CTAs): matches every existing marketing page (client islands only where checkout needs them), keeps LCP/SEO strong, and avoids hydration cost on pages whose entire job is to be linked from cold email.
- **Reuse `/api/v1/billing/waitlist` as the enterprise contact path** instead of a new contact endpoint or a calendar placeholder: the endpoint, form UI, and DB capture already exist on the pricing page; an anchor + `tier=enterprise` preselect turns it into a credible "Talk to sales" path in one edit, and leads are captured in the DB instead of a personal inbox. A future calendar/booking URL swaps in via `src/lib/contact.ts` without touching pages. Rejected alternatives: new `/contact` page (scope creep, duplicate form), keeping any mailto (unprofessional, the exact placeholder this increment removes), inventing a branded email (no mailbox exists for verified-skill.com today).
- **Sample report as typed constant mirroring `verify-result.json`**: guarantees the public sample matches the real artifact shape (field names lifted from the actual report + `ScanResult` schema), renders styled instead of a JSON dump for skimmability, and keeps raw JSON available in a collapsible for auditors. Rejected: live-fetching a real ScanResult (couples a marketing page to DB/API and risks leaking real repo data).
- **Honesty constraints as ACs** (AC-US1-02, AC-US2-06): the verification page only works as a trust asset if a security engineer can't catch it overclaiming; "reduces risk, never guarantees safe" is an explicit, testable requirement, and every number is traced to source files so implementation re-verifies before hardcoding.
- **Real screenshots as ACs**: fabricated UI on a trust-marketing page is a credibility (and honesty) failure; the capture plan reuses shipped local-stack knowledge (0826/0862/0874) rather than inventing new tooling.
- **TDD (config: warn)**: unit tests follow the two existing colocated patterns (renderToString for page content/testids; string-grep for layout links), written RED before each page/edit, then GREEN, then a shared-style REFACTOR pass if duplication appears across the two new pages.

## Technology Stack

- Next.js App Router (existing), React server components, inline styles + CSS custom properties
- Vitest (jsdom, colocated `__tests__`), Playwright (e2e, `npm run dev` webServer)
- OpenNext Cloudflare + wrangler (existing deploy chain)
- Playwright CLI for Studio screenshot automation; sips/pngquant for optimization

## Implementation Phases

1. **Assets first**: capture Studio/CLI screenshots (US-003) — pages embed them, so capture precedes page GREEN tasks (placeholder-swap fallback if Studio blocks).
2. **Pages**: /private-skills + redirect (US-001), /verification (US-002) — RED→GREEN each.
3. **Chrome & pricing**: CTA/contact path + hero link (US-004), docs/footer links (US-005) — RED→GREEN.
4. **Refactor + E2E**: shared style constants if duplicated; e2e smoke spec.
5. **Deploy + live verify** (US-006).

## Technical Challenges

### Challenge 1: PaywallModal requires a paywalled state locally
**Solution**: local stack with seeded Free-tier org at the private-skill limit (0874 wiring; `VSKILL_FREE_PRIVATE_SKILL_LIMIT` var), or temporarily lower the limit locally. **Risk**: if Studio can't reach a paywalled state quickly, capture the modal from the 0874 E2E fixtures/storybook-like harness; never mock the UI in an image editor.

### Challenge 2: Numbers drift (patterns/agents counts)
**Solution**: grep the source of truth at implementation time (scanner-patterns.js count, agents registry — resolve the 53-vs-54 discrepancy) and hardcode the verified number in one constants block per page. **Risk**: future drift — acceptable for marketing copy; wording like "52 patterns (and growing)" where safe.

### Challenge 3: OG image convention ambiguity (svg on disk vs .png URLs in metadata)
**Solution**: check what `https://verified-skill.com/og/pricing.png` actually returns before choosing; replicate whichever convention works live.

### Challenge 4: Studio app entry point
**Solution**: `vskill studio` from the vskill repo; if the packaged desktop Studio is required instead, use the dev build — confirm from vskill repo scripts at implementation time. Screenshots must show realistic (non-embarrassing) sample data: seeded skill names, no personal tokens.

### Challenge 5: Redirect behavior on OpenNext/Cloudflare
**Solution**: `next.config.ts` `redirects()` is honored by @opennextjs/cloudflare; verify post-deploy with `curl -sI https://verified-skill.com/paid-skills` (expect 308 + Location: /private-skills). If the worker bypasses it for any reason, fall back to a tiny `src/app/paid-skills/route.ts` returning `NextResponse.redirect(..., 308)`.
