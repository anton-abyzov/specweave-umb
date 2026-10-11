# 0874 manual acceptance run, 2026-10-11

Spec section: "Manual acceptance (owner)", steps 1 to 9.
Code under test: vskill main `bf63bf4`, vskill-platform main `5f2d280b`. Both contain the 0874 merges (vskill `5c0b73cd`, platform `c0bcae86`).
Screenshots and scripts: `scratchpad/e2e/0874-acceptance/` in the session scratchpad (`/private/tmp/claude-501/-Users-antonabyzov-Projects-github-specweave-umb/ac3b010d-5ca3-4d8f-8256-14b4ffe54eb8/scratchpad/e2e/0874-acceptance/`). The scratchpad is temporary, so this file records every result.

## Result

| Step | Result | Notes |
|---|---|---|
| 1 Studio, private repo, Commit & Push | FAIL as shipped, PASS with fix | The Overview tab Publish button sent no skill name, so the drawer fell back to "Sign in to submit in-app, or finish on the website" with an "Open on website" link. The Edit tab button passed. Fixed in vskill PR #165. |
| 2 Studio, public repo | PASS | Private reads "not open yet" with Join the waitlist. Decide later is absent. The submission body carried `"privacy":"public"` and no tenant, and the submission reached the local queue. |
| 3 Platform account copy | FAIL as shipped, PASS with fix | No "require Pro" and no "50 private skills" on `/account/repos`, `/account/repos/connect` or `/account/billing`. The free CTA on the plan card that `/account/billing` renders went to `/pricing`, not `/pricing#hosted-waitlist`. 0874 T-03 changed `components/account/PlanCard`, which no page renders. Fixed in vskill-platform PR #105. |
| 4 Open gate, local only | PASS | Both constants set to true and both 503 branches removed, only in scratch exports of the repos. The checkouts were never edited. |
| 5 `stripe listen` | PASS | Stripe CLI profile `skill-studio-prod` (acct_1PQegES8F0HBR06W, test mode) forwarded to the local webhook. |
| 6 Pro checkout, 4242 card | PASS | Checkout session `cs_test_…`, Stripe Sandbox page, 13 webhook events all answered 200. User.tier became PRO, the Subscription row became PRO/ACTIVE, and `/api/v1/billing/quota` changed from `"tier":"free"` to `"tier":"pro"`. A forged signature returned 400 `invalid_signature`. |
| 7 Studio chooser, gate open | PASS | Paid user (live quota `pro`): Private, "Only your org can see, search, or install it.", can be selected. Free user (live quota `free`): "Upgrade to publish privately", which opens the paywall "Publish private skills with Skill Studio Pro … Publishing publicly stays free … Upgrade to Pro". |
| 8 Private skill publish and isolation | FAIL (publish) / PASS (isolation) | Publishing from Studio and through the real pipeline does not produce a private skill (details below). A PRIVATE, tenant-scoped row created through the tenant route stayed out of the catalog, search, sitemap and public API. The publisher page showed "+ 1 private skill not listed publicly" to its owner only. |
| 9 Billing portal, then revert | PASS | "Manage subscription" opened billing.stripe.com in Test mode, showing Skill Studio Pro $20.00/month and Visa •••• 4242. The free user's portal call returned 404 `no_subscription`. The open-gate changes existed only in the scratch exports, which were deleted. `git status` is clean in both checkouts. |

## Setup and safety

- `vskill-platform/.env.local` and `.dev.vars` point `DATABASE_URL` at the production Hetzner Postgres. The dev server therefore ran from a `git archive` export of platform main in the scratchpad. Its environment came from sourcing `.env.local` read-only, then overriding `DATABASE_URL` and `CLOUDFLARE_HYPERDRIVE_LOCAL_CONNECTION_STRING_HYPERDRIVE` with a throwaway local database (`vskill_0874_acc` on localhost:5432, schema from `prisma db push`, search_vector SQL from its migrations), and `STRIPE_WEBHOOK_SECRET` with the whsec from `stripe listen --print-secret`. The server log confirmed "Hyperdrive will connect to this database". Seeded rows landed in the local DB.
- KV, queues and Durable Objects were local miniflare bindings. The export's `wrangler.jsonc` lost its remote-only `ai` binding because wrangler otherwise tried to open a remote session on the Cloudflare account. That change lived only in the scratch export.
- `.env.local` was copied before the run and was byte-identical afterwards (`cmp`). No key was printed or committed. `STRIPE_SECRET_KEY` and the publishable key are `sk_test`/`pk_test` by prefix.
- Skill Studio ran as two private instances from a scratch build (ports 3175 and 3176) with a scratch `HOME`, `VSKILL_PLATFORM_URL=http://localhost:3074` and `VSKILL_GITHUB_TOKEN` from `gh auth token`. Nothing was submitted to verified-skill.com. Fixture repos used a GitHub `origin` URL for the visibility check (private: `anton-abyzov/vskill-test-private-skills-826`, public: `anton-abyzov/vskill`), with `pushurl` pointing at local bare repos. No GitHub repo was created or pushed to.
- Every browser ran headless Playwright (`@playwright/test` 1.63.0). Processes were stopped by PID. The test subscription was cancelled afterwards (`sub_1UPFUYS8F0HBR06WoZthdB2e`, test mode), and the local DB and scratch exports were deleted. Nothing was deployed.

## Step details

1. Overview tab Publish (`step1-drawer-open.png`, `step1-outcome.png`): the push to the bare remote succeeded (`ef1d691..fd7833b`). The UI never called `/api/v1/submissions` and the outcome was `website-fallback`. `PublishStatusRow` renders `<PublishButton>` without `skillName`, so the drawer takes its "no skill identity" branch. The Edit tab button (`step1-edit-tab-outcome.png`) gave the expected result: the eval-server returned 422 `private_repository`, the outcome was `not-submitted` with "Nothing was submitted to verified-skill.com … only verifies public repos", there was no website link and no sign-in prompt, and the platform log shows no submission POST. After the fix, the Overview tab gives the same `not-submitted` result (`step1-overview-fixed-outcome.png`).
2. `step2-public-body-drawer-open.png`, `step2-public-outcome.png`: the body was `{"repoUrl":"https://github.com/anton-abyzov/vskill","skillName":"greet-anton","skillPath":"skills/greet-anton/SKILL.md","source":"studio-submit","privacy":"public"}`. The response was 201 RECEIVED ("Submitted to the queue"), and the local Submission and Skill rows are PUBLIC.
3. `step3-account_repos.png`, `step3-account_repos_connect.png`, `step3-account_billing.png`: the repos pages say private repos connect on any plan and hosted publishing is not open yet.
6. `step6-stripe-checkout.png`, `step6-stripe-filled.png` (Link "save my info" was confirmed unchecked before submitting), `step6-return.png` (`/account/billing?status=success`).
7. `step7-paid-drawer.png`, `step7-paid-private-selected.png`, `step7-free-drawer.png`, `step7-free-paywall.png`. Browser-mode Studio always reports the free tier, which 0874 lists as out of scope. The desktop quota IPC was stubbed with each user's live `/api/v1/billing/quota` answer from the local platform.
8. Publish attempts with the gate open:
   - Studio, paid user, Private selected: the body had `"privacy":"private"` and no `tenantId`. The platform returned 400 `missing_tenant` and the drawer fell back to "Sign in … website" (`step8-studio-private-submit-paid.png`). No Studio caller passes `tenantId` to `PublishButton`.
   - `POST /api/v1/submissions` with private intent for the private repo: 422 "SKILL.md not found", because the platform cannot read the private repo.
   - `POST /api/v1/submissions` with private intent for a public repo: 201 RECEIVED into the public pipeline. The Submission table has no privacy or tenant column, so the private intent is dropped. Local processing stopped at "Repository visibility unavailable" (unauthenticated GitHub rate limit), so the publish was not followed to the end.
   - Tenant route, E2E harness path: the paid user's personal tenant got 201 with privacy PRIVATE, and the free user's personal tenant got 402 `TENANT_LIMIT_REACHED` with an `upgradeUrl`. An organization tenant was refused for the personal Pro plan, as designed.
   - Isolation for anonymous, free and owner viewers: `/api/v1/skills` search, `/api/v1/skills/search` (q=acc0874, private, skill), `/skills?q=acc0874` and `/sitemap.xml` never contained the private skill, while public rows appeared. The skill detail API returned 404. `/publishers/acc0874-paid` showed the footer to the owner only (`step8-*-_publishers_acc0874_paid.png`).
9. `step9-paid-account-billing.png`, `step9-paid-stripe-portal.png`, `step9-free-account-billing.png`.

## Bugs fixed (PRs open, not merged, not deployed)

- vskill #165 `fix/0874-overview-publish-skill-identity`: SkillOverview passes `skillName` and `skillPath` through PublishStatusRow to PublishButton. Two new tests fail without the change. The eval-ui component suite passes 127 files and 843 tests. `lint:voice` and `tsc --noEmit` are clean.
- vskill-platform #105 `fix/0874-billing-plan-card-waitlist`: the free CTA on the billing PlanCard follows the gate (`/pricing#hosted-waitlist` while closed). PlanCard and BillingClient tests fail without the change. The related suites pass 13 files and 100 tests. In the T-03 set, 4 `account-repos-parity` tests fail only from a detached worktree because they read the sibling repo by relative path, and they pass 4/4 in the normal checkout.

## Open-gate gaps for 0896 (not fixed here)

- Studio never sends `tenantId`, so a paid user's Private publish gets 400 `missing_tenant`.
- The eval-server guard refuses every private repo whatever the gate state, so Studio cannot publish a private-repo skill privately even with the gate open.
- Submission persistence has no privacy or tenant field. Opening only the routes would send private intent for public repos into the public pipeline.
- Production `wrangler.jsonc` sets `VSKILL_FREE_PRIVATE_SKILL_LIMIT=50`, so free tenants would get 50 private skills, not the code default of 0.
- The billing PlanCard Pro copy hard-codes "Hosted private publishing is not available yet" and does not follow the gate.
- After an immediate test cancellation (`customer.subscription.deleted`), the Subscription row is CANCELED but keeps `currentPeriodEnd` 2026-11-11, and `/api/v1/billing/quota` still reports `pro`. This needs a decision: is it intended grace, or should it end at `ended_at`?
