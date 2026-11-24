# 0874 Tiered private skills: paid unlocks private, clear UI distinction

## Problem
The increment was built in June 2026 (vskill 80f6a23, vskill-platform 85123184, 8ec13da9, 23e678c0) without a spec, so nothing recorded what was accepted or tested. On 2026-10-09 increment 0847 closed hosted private publishing behind a launch gate (`HOSTED_PRIVATE_PUBLISHING_AVAILABLE = false`, vskill-platform d2ed7fe8): private publish and new checkout return 503 and pricing shows a waitlist. Parts of what 0874 shipped now contradict that gate. Skill Studio still offers "Upgrade to publish privately" and "Decide later", sends a private repo's URL and skill name to verified-skill.com on publish, and account pages still say private repos need Pro or promise 50 private skills.

## Scope
In: record and verify what 0874 shipped; make Skill Studio and the account pages agree with the launch gate in both of its states; stop Studio publish from sending private or unconfirmed repos to verified-skill.com; add the missing tests for the 0848 visibility cues finished here (0848 T-003, T-006, T-007).

Out: opening the launch gate, Stripe price configuration or any production billing change (owned by 0847). Tier-gating the GitHub repo connection (free keeps a private allowance by the 2026-06-16 decision, 23e678c0). Mock tenant data on `/publish` and `/orgs/*` (0826 scaffolding). The stale `e2e/0840-stripe-checkout.spec.ts` expectation (0847 changed the page). Sidebar sub-groups in the virtualized list above 200 skills; the row chip still marks private skills there. Browser-only Studio resolving every user to the free tier. The other increment that shares this number, `0874-crawl-coverage-healthcheck-and-email-alerts`.

## Acceptance Criteria
- [ ] AC-01: Tier and caps resolve from the active subscription. A FREE tenant's private allowance is `VSKILL_FREE_PRIVATE_SKILL_LIMIT` (code default 0, malformed falls back to 0); an active PRO or TEAM subscription is unlimited.
- [ ] AC-02: A private publish over the allowance is refused with 402 `TENANT_LIMIT_REACHED` and an `upgradeUrl`. While the launch gate is closed every private or decide-later publish is refused with 503 on both publish routes, for every plan, and nothing is stored.
- [ ] AC-03: Checkout session, Stripe webhook tier flip and billing portal are real code paths with signature verification. While the launch gate is closed new checkout returns 503 and pricing offers only the waitlist.
- [ ] AC-04: Private skills never appear in the public catalog, search, publisher pages, sitemap or public API.
- [ ] AC-05: Private and public skills are visibly distinct: Studio row chip and detail badge, sidebar Private/Public sub-groups, MarketplaceDrawer "Your private plugins", account repos Private and Public sections in both products, the owner-only private footer on a publisher page, and the catalog private-skills hint. Each cue has a test that renders it.
- [ ] AC-06: Skill Studio publish never sends a private repository, or one whose visibility cannot be confirmed, to verified-skill.com. The push still succeeds, no website submit link is offered, and the user is told nothing was submitted and why.
- [ ] AC-07: The Studio privacy chooser matches the launch gate. Closed: only Public can be selected, Private points to the waitlist, Decide later is absent, and every submission carries `privacy: "public"`. Open: a FREE user gets the upgrade paywall with publish wording, a paid user can choose Private.
- [ ] AC-08: Account and plan copy and the tenant cap banner promise only what the API does. No "private repos require Pro" while connecting is not tier-gated, no hard-coded allowance number, the cap banner's upgrade control is a working link, and a zero limit renders without a broken percentage.
- [ ] AC-09: The full vskill and vskill-platform unit suites and both builds pass on the merged heads, and the changes were reviewed independently before merge.

## Approach
Keep 0847's launch gate as the single source of truth and make everything 0874 shipped read from it. vskill-platform already exports `HOSTED_PRIVATE_PUBLISHING_AVAILABLE`; account copy and the cap banner branch on it so they flip with the gate. Skill Studio cannot read a platform constant, and the desktop quota payload is produced by the Rust sync layer, so Studio carries its own mirrored constant in `src/eval-ui/src/hosted-publishing.ts`. Opening the gate later means flipping both constants in one release.

The private-repo guard lives in the eval-server proxy, not the UI, because the proxy is the only place every Studio submit passes through (drawer, clean-tree publish button, any future caller). It reuses `isPrivateOrUnknownRepo`, the same fail-closed check `vskill submit` and the 1.2.1 egress work use, so CLI and Studio give the same answer for the same repo.

Existing tests for the open-gate behaviour stay and run with the gate mocked open. New tests cover the closed state.

Work happens in isolated worktrees: `0874-paywall-vskill` and `0874-paywall-platform` on `inc/0874-paywall`, umbrella on `claude/project-thread-ddfj3g`.

## Tasks

### T-01 Verify the shipped tier, paywall, billing and isolation behaviour
- AC: AC-01, AC-02, AC-03, AC-04 | Files: .specweave/increments/0874-tiered-private-skills-paywall/spec.md | Test: cd /Users/antonabyzov/Projects/github/0874-paywall-platform && npx vitest run src/lib/tenant-caps.test.ts src/lib/__tests__/tenant-subscription.test.ts "src/app/api/v1/tenants/[tenantId]/skills/__tests__" src/app/api/v1/submissions/__tests__/route.private-paywall.test.ts src/app/api/v1/submissions/__tests__/route.privacy-gate.test.ts src/app/api/v1/billing src/lib/stripe src/__tests__/billing tests/integration/public-route-isolation.test.ts src/lib/__tests__/publisher-public-scope.test.ts src/lib/__tests__/scanner-public-only.test.ts src/lib/submission/__tests__/publish-privacy-failsafe.test.ts src/lib/org-access.test.ts

### T-02 Platform tests for the private hint and the owner-only publisher footer
- AC: AC-05 | Files: repositories/anton-abyzov/vskill-platform/src/app/skills/PrivateSkillsHint.tsx, repositories/anton-abyzov/vskill-platform/src/app/skills/__tests__/PrivateSkillsHint.test.tsx, repositories/anton-abyzov/vskill-platform/src/app/publishers/[name]/page.tsx, repositories/anton-abyzov/vskill-platform/src/app/publishers/[name]/__tests__/* | Test: cd /Users/antonabyzov/Projects/github/0874-paywall-platform && npx vitest run src/app/skills/__tests__ "src/app/publishers/[name]/__tests__" src/__tests__/account-repos.test.tsx

### T-03 Platform copy and cap banner follow the launch gate
- AC: AC-08 | Files: repositories/anton-abyzov/vskill-platform/src/components/account/ConnectedReposTable.tsx, repositories/anton-abyzov/vskill-platform/src/app/account/repos/ReposClient.tsx, repositories/anton-abyzov/vskill-platform/src/app/account/repos/connect/page.tsx, repositories/anton-abyzov/vskill-platform/src/components/account/PlanCard.tsx, repositories/anton-abyzov/vskill-platform/src/lib/billing/quota-shape.ts, repositories/anton-abyzov/vskill-platform/src/app/components/TenantCapBanner.tsx, repositories/anton-abyzov/vskill-platform/src/lib/hosted-publishing.ts, their tests | Test: cd /Users/antonabyzov/Projects/github/0874-paywall-platform && npx vitest run src/__tests__ src/app/components src/components src/app/account src/lib/billing

### T-04 Studio tests for the visibility cues
- AC: AC-05 | Files: repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/*, repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/account/ConnectedReposTable.test.tsx, repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useSkillRepoVisibility.ts, repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/useSkillRepoVisibility.test.ts | Test: cd /Users/antonabyzov/Projects/github/0874-paywall-vskill && npx vitest run src/eval-ui/src/components/__tests__ src/eval-ui/src/__tests__/account src/eval-ui/src/hooks/__tests__

### T-05 Studio publish refuses private and unconfirmed repos
- AC: AC-06 | Files: repositories/anton-abyzov/vskill/src/eval-server/platform-proxy.ts, repositories/anton-abyzov/vskill/src/eval-server/__tests__/*, repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts, repositories/anton-abyzov/vskill/src/eval-ui/src/components/PublishDrawer.tsx, repositories/anton-abyzov/vskill/src/eval-ui/src/components/PublishButton.tsx, repositories/anton-abyzov/vskill/src/eval-ui/src/components/PublishStatusRow.tsx | Test: cd /Users/antonabyzov/Projects/github/0874-paywall-vskill && npx vitest run src/eval-server src/eval-ui/src/components/__tests__ src/lib/__tests__/private-source-egress-1.2.1.test.ts

### T-06 Studio privacy chooser and paywall follow the launch gate
- AC: AC-07 | Files: repositories/anton-abyzov/vskill/src/eval-ui/src/hosted-publishing.ts, repositories/anton-abyzov/vskill/src/eval-ui/src/components/PublishDrawer.tsx, repositories/anton-abyzov/vskill/src/eval-ui/src/components/PaywallModal.tsx, repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/PublishDrawerPrivacy.test.tsx, repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/PaywallModal.test.tsx | Test: cd /Users/antonabyzov/Projects/github/0874-paywall-vskill && npx vitest run src/eval-ui/src/components/__tests__ && npm run lint:voice && npm run build && npm run build:eval-ui

### T-07 Review, full suites and merge
- AC: AC-09 | Files: .specweave/increments/0874-tiered-private-skills-paywall/reports/* | Test: cd /Users/antonabyzov/Projects/github/0874-paywall-vskill && npx vitest run && cd /Users/antonabyzov/Projects/github/0874-paywall-platform && npx vitest run

## Delivery
Merged 2026-10-10: vskill#147 (merge 5c0b73cd) and vskill-platform#99 (merge c0bcae86), both with green CI. They were reviewed independently before merge. The review found that the website fallback could prefill a private repo URL in `?repo=`; that was fixed and tested before merge. Neither repo was deployed or released. Studio ships with the next vskill release, the platform with the next deploy.

Out of scope and left open:
- `ConnectedRepoWidget` still shows a "Pro" chip for a free user's private repo. Connect tier-gating is Out.
- Both platform publish routes return 503 for private publishing without reading `HOSTED_PRIVATE_PUBLISHING_AVAILABLE`. Opening the gate needs those routes, both constants and Stripe prices changed together (0847).

## Manual acceptance (owner)
Use Stripe test mode only. The test key in `vskill-platform/.env.local` returned `api_key_expired` on 2026-10-10, and the Stripe CLI test sessions expired in August. Roll a new test key and run `stripe login` first.

Closed gate, as shipped:
1. Studio: in a skill from a private GitHub repo, open Publish and Commit & Push. The push succeeds. The drawer says nothing was submitted to verified-skill.com and gives the reason. It shows no website link and no sign-in prompt.
2. Studio: in a public repo, open Publish. Private reads "not open yet" and offers Join the waitlist. Decide later is absent. The submission reaches the queue as public.
3. Platform `/account/repos`, the connect page, and the account plan card: no "require Pro", no "50 private skills", and the free CTA goes to `/pricing#hosted-waitlist`.

Open gate, local only, nothing deployed:
4. Set both constants to true. Open the two publish routes as described in 0847.
5. Run `stripe listen --forward-to localhost:3000/api/v1/billing/webhooks/stripe`.
6. Check out Pro with card 4242 4242 4242 4242. The webhook sets the tier to PRO, and `/api/v1/billing/quota` reports pro.
7. Studio: Private is now selectable for the paid user. A free user gets the paywall with the publish wording.
8. Publish a private skill. It does not appear in the catalog, search, the sitemap or the publisher page, except in the owner's footer.
9. The billing portal opens. Then revert both constants.
