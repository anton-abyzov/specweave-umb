# 0897 Free-first pricing and launch

## Problem

Anton asked (2026-10-12) to compare T3 Code and BridgeMind monetization with ours, then to "implement this properly": find the best pricing model, decide what enterprises could pay for while SpecWithCode is positioned as a free tool, and set the strategy to spread the word, as an increment SpecWithCode can carry out.

Today:
- **Nothing on the pricing page can actually be bought except the $990 pilot.** On 2026-10-09 hosted private publishing went behind `HOSTED_PRIVATE_PUBLISHING_AVAILABLE=false` (0847, 0874, 0896): new checkout returns 503 and verified-skill.com/pricing says "new subscriptions are unavailable" with a waitlist. spec-weave.com/pricing still sold Pro $20 and Team $30/seat and said "Verified Skill plans are paid by card on verified-skill.com".
- **Free is now the norm in this category.** T3 Code is free, MIT, bring-your-own subscriptions, "no keys resold", 400k+ users, funded by T3 Chat. BridgeMind charges $20 / $50 / $100 a month for the workspace itself plus credits for its own AI features (about $76k ARR, Feb 2026). Conductor Pro is about $50 a month (est., traffic plan). Full comparison with sources: `reports/competitor-monetization.md`.
- **A user who loves SpecWithCode has no way to pay for it,** and the site never says what stays free after early access.
- The traffic plan already exists (SpecWithCode tutorials and promotion thread, doc "SpecWithCode traffic plan", 2026-10-12): Week 0 gates (notarize, current download page, open-source answer), founder accounts, Show HN in week 2, Product Hunt in week 3, comparison pages, Shorts, AI assistant drafting. This increment adds the pricing model and the pricing message to that plan; it does not replace it.

## Pricing model (approved by Anton, 2026-10-12)

Principle: **free for every developer and team; companies pay for what we host, the control they need, and support.** Never charge for running agents on the user's own machines, never resell tokens, never mark up subscriptions. This matches T3 Code's trust position and undercuts every paid workspace.

| Offer | Price | What it includes | State |
|---|---|---|---|
| Free forever: SpecWithCode + SpecWeave CLI | $0, individuals and teams | Desktop app (coordinator, worker threads, plans, routines), any mix of Claude Code / Codex / Grok / Gemini CLI / Cursor on the user's own subscriptions, specs + ledger + evidence in git, auto-handoff, local install of skills from public and private GitHub repos, GitHub / Jira / ADO sync | Live |
| Verified Skill Pro / Team (hosted) | $20/mo; $30/seat/mo, 3+ seats | Hosted, versioned private skills, security scan per version, one install into 50+ agents, seat management (0840/0841 billing already built) | Waitlist until 0896 opens the gate |
| Enterprise | Custom annual; internal floor from $12,000/yr for up to 50 engineers (est., Anton to confirm) | Rollout across teams, priority support with named engineer and response times, export of who ran which agent where with what evidence, and scoped-to-contract items: SSO/SCIM (0842 backlog), provider/model policy, self-hosted skill registry, security review pack, invoice billing | Sold by conversation; build items scheduled per contract |
| Founding team pilot | $990 one time, up to 10 engineers, 5 places | Two-week setup, handoff drill, evidence report, money back if the drill fails | Live; the bridge into Team and Enterprise |

**The extra enterprise value to build next: a team usage view.** Each SpecWithCode machine already knows its own subscription usage (Subscription usage dashboard thread). Aggregated for an org it answers the question an engineering manager pays for: which Claude / Codex / Cursor seats are idle, which hit limits daily, and where work handed off. That turns the licence into a cost-saving line item. It is a follow-up increment (T-08), not part of this one.

Rejected: charging per agent run, per token or per machine (breaks the free-tool position and invites the T3 Code comparison); a paid desktop tier like BridgeMind's (the app is our distribution, not our revenue); credits for built-in AI features (we run no inference).

## Promotion strategy (adds to the traffic plan)

1. **One message everywhere:** "Free for every developer and team. No markup, no token resale, no seat fee to run agents on your own machines." Hook from the traffic plan stays: "Stop being the router between Claude Code and Codex."
2. **Gates first (Week 0, owned elsewhere):** notarized build, current download page, the open-source answer, and this increment's /pricing (PR #2038) merged. No audience traffic before these.
3. **Week 1:** founder posts on Threads and LinkedIn with the explainer video, ending on the free pledge; SpecWeave README and the next CLI release note get a "SpecWithCode is free" section pointing at spec-weave.com/studio (26k monthly npm downloads is the largest audience we own).
4. **Week 2:** Show HN. The maker comment states the business model in one line ("free; we'll charge companies for hosted private skills and support, never for running agents") because HN asks.
5. **Week 3:** Product Hunt, awesome-claude-code submission, GitHub Trending push.
6. **Ongoing:** comparison pages with sourced pricing facts (vs BridgeMind, plus the traffic plan's vs Conductor, vs Codex app, vs Claude Code agent teams); 5 Shorts a month; one tutorial a week.
7. **Company funnel:** every enterprise-flavoured post (usage limits costing a team an afternoon, AI seat spend) links to /pricing; each pilot ends in a case study and a referral ask; Anton sends personal notes to engineering leaders he knows, drafted by the assistant.
8. **Measure weekly:** .dmg downloads, /studio and /pricing visits (Cloudflare analytics), waitlist sign-ups referred from spec-weave.com, pilot applications, enterprise emails, npm downloads, stars.

Four-week targets to calibrate against (not forecasts): 500 .dmg downloads, 100 waitlist sign-ups, 5 pilot applications, 2 enterprise conversations.

## Scope

In: the public pricing page and pricing message across spec-weave.com and READMEs; comparison pages; an enterprise page and inquiry path; waitlist and funnel measurement; launch drafts that carry the pricing message; the pilot-to-case-study loop; the spec for the team usage view.

Out: opening the hosted publishing gate and any Stripe or production billing change (0896); SSO/SCIM (0842); notarization, the download page and the open-source decision (production-readiness thread and traffic plan); buying domains, creating accounts or posting anywhere public without Anton's go-ahead; building the team usage view itself.

## Acceptance Criteria

- [ ] AC-01: spec-weave.com/pricing leads with free for individuals and teams, lists Free forever, Verified Skill Pro/Team as waitlist, Enterprise and the $990 pilot, and never presents as purchasable anything that cannot be bought while `HOSTED_PRIVATE_PUBLISHING_AVAILABLE` is false. `npm run build` in `docs-site` passes, with no horizontal scroll at 390 px.
- [ ] AC-02: The free pledge (no markup, no token resale, no seat fee to run agents on your own machines; what is free stays free) reads the same on /pricing, /studio, the home release pill or hero, docs/overview/studio.mdx, the SpecWeave README and the specwithcode release repo README; no page still says only "free in early access" without saying what stays free.
- [ ] AC-03: A comparison page for BridgeMind exists under the site's comparison route alongside the traffic plan's pages, each stating competitor prices with a checked date and a source link, and making no claim about a competitor that its own site does not support.
- [ ] AC-04: An enterprise path exists: a /pricing Enterprise card and a short page or section that separates what is offered today (rollout, support, evidence export) from items scoped per contract (SSO/SCIM, policy, self-hosted registry), with a prefilled inquiry email.
- [ ] AC-05: Waitlist sign-ups referred from spec-weave.com are countable (referrer captured by the verified-skill.com waitlist; a UTM query on the link failed the docs link check on PR #2038, so the link stays plain), and a weekly report (existing routine or a new one) lists the eight numbers in the promotion strategy, including waitlist sign-ups, pilot applications and enterprise emails.
- [ ] AC-06: Launch drafts for Show HN (title and maker comment), Product Hunt, LinkedIn, Threads, X, r/ClaudeAI megathread, the README section and the CLI release note are written into `reports/launch-drafts/`, each stating the free pledge and the business model in one line, each checked against the current build; nothing is posted without Anton's approval.
- [ ] AC-07: A pilot case-study template and referral ask are in `reports/`, and the pilot email flow ends with a request for a case study.
- [ ] AC-08: A follow-up increment spec for the team usage view exists (org-wide view of subscription usage across members' machines: idle seats, daily limit hits, handoffs), with its privacy boundary stated: usage counts only, no prompts or code leave the machine.

## Approach

Website work lands in `repositories/anton-abyzov/specweave/docs-site` on a branch from `develop`, PR to `develop` (deploys to spec-weave.com). T-01 is PR #2038 (branch `pricing-free-first`): `src/pages/pricing.tsx` rebuilt on the existing `continuity.module.css` and `pricing.module.css`, footer link renamed to "Pricing". Reuse the traffic plan's channel order and its decisions list; this increment only adds pricing content to it. Launch drafts go through the existing social routine with per-post approval. Facts about competitors come from their own sites, re-checked on the day a page ships.

## Decisions (Anton approved, 2026-10-12)

Anton approved the model and the recommended defaults in the project thread ("Yes, I approve, complete the job").

1. Model approved: free forever core, hosted Pro/Team on waitlist, Enterprise custom, pilot $990.
2. Enterprise floor: from $12,000 a year for up to 50 engineers, internal only; the page says "Custom".
3. Free hosted private skill limit for 0896 AC-07: 0. Installing private skills locally from your own GitHub stays free; hosted is the paid thing. Recorded in the 0896 ledger; production config changes with 0896, not here.
4. Pilot price after the five places: decide after the first two pilots.
5. App source: already public. anton-abyzov/specwithcode carries the source under MIT, with T3 Code's license and upstream pin kept, so the answer is "open source, built on the open-source SpecWeave CLI".

6. No public SpecWithCode vs T3 Code page (decided 2026-10-13). SpecWithCode started from T3 Code's MIT codebase; answer the fork question honestly when asked, but do not publish a comparison page or run comparison ads against T3 Code.

## Tasks

### T-01 Rebuild /pricing free-first with hosted plans on waitlist
- AC: AC-01 | Files: repositories/anton-abyzov/specweave/docs-site/src/pages/pricing.tsx, repositories/anton-abyzov/specweave/docs-site/src/theme/Footer/index.tsx | Test: cd repositories/anton-abyzov/specweave/docs-site && npm run build | Note: PR https://github.com/anton-abyzov/specweave/pull/2038

### T-02 Put the free pledge on every surface
- AC: AC-02 | Files: repositories/anton-abyzov/specweave/docs-site/src/pages/index.tsx, repositories/anton-abyzov/specweave/docs-site/src/pages/studio.tsx, repositories/anton-abyzov/specweave/docs-site/src/components/ecosystem/StudioSections.tsx, repositories/anton-abyzov/specweave/docs-site/docs/overview/studio.mdx, repositories/anton-abyzov/specweave/README.md | Test: cd repositories/anton-abyzov/specweave/docs-site && npm run build && grep -rln "no markup" src/pages docs/overview/studio.mdx

### T-03 Comparison pages (BridgeMind; no T3 Code page by decision)
- AC: AC-03 | Files: repositories/anton-abyzov/specweave/docs-site/docs/guides/specwithcode-vs-bridgemind.md, repositories/anton-abyzov/specweave/docs-site/sidebars.ts | Test: cd repositories/anton-abyzov/specweave/docs-site && npm run build

### T-04 Enterprise section and inquiry path
- AC: AC-04 | Files: repositories/anton-abyzov/specweave/docs-site/src/pages/pricing.tsx, repositories/anton-abyzov/specweave/docs-site/docs/enterprise/index.md | Test: cd repositories/anton-abyzov/specweave/docs-site && npm run build

### T-05 Waitlist tracking and weekly funnel report
- AC: AC-05 | Files: repositories/anton-abyzov/vskill-platform, .specweave/increments/0897-free-first-pricing-and-launch/reports/weekly-funnel.md | Test: test -f .specweave/increments/0897-free-first-pricing-and-launch/reports/weekly-funnel.md

### T-06 Launch drafts carrying the pricing message
- AC: AC-06 | Files: .specweave/increments/0897-free-first-pricing-and-launch/reports/launch-drafts | Test: test $(ls .specweave/increments/0897-free-first-pricing-and-launch/reports/launch-drafts | wc -l) -ge 8

### T-07 Pilot case study template and referral ask
- AC: AC-07 | Files: .specweave/increments/0897-free-first-pricing-and-launch/reports/pilot-case-study-template.md | Test: test -f .specweave/increments/0897-free-first-pricing-and-launch/reports/pilot-case-study-template.md

### T-08 Spec the team usage view as a follow-up increment
- AC: AC-08 | Files: .specweave/increments | Test: ls .specweave/increments | grep -i "team-usage"
