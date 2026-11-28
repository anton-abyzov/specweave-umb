# anymodel.dev becomes the agent bench in SpecWithCode style, and the hosted Worker retires

## Problem

AnyModel is the owner's MIT package: `github.com/anton-abyzov/anymodel`, npm `anymodel` 2.0.0, site anymodel.dev (Vercel, served from the repository's `site/` folder). On November 27, 2026 the owner approved plan C + E (`decision_anymodel_future`). anymodel.dev is to become a free agent bench in SpecWithCode's style, and the hosted `api.anymodel.dev` Worker is to retire. If the one-week funnel check (1511) shows almost no visitors reaching SpecWithCode, the plan switches to D: retire, park the domain and npm name, point to SpecWithCode.

Evidence (November 27, 2026):

- **The Worker serves no real use.** `anymodel-proxy` on `api.anymodel.dev/*` handled 3,280 invocations in the 30 days to November 27, 2026. Zone analytics for October 30 to November 27, 2026 show only 30 `GET /health` 200s and 10 `/v1/messages` 204 preflights as successful answers. Every `/v1/*` call and the scanner probes (`/.env`, `/secrets.env`, `/.dockercfg`) got 401 or 403. No published npm version since 1.5.0 contains `api.anymodel.dev`. Last week's downloads by version: 2.0.0 58, 1.12.0 34, 1.17.0 19, and 1.5.0 none.
- **The current site is not in SpecWithCode's style** (screenshot from the owner): a cream background with green serif italic type. The owner wants a complete redesign: "compliant with the UI motions and graphics… with a similar style".
- **The bench data already exists.** `site/bench/results-fixed-1.17.0.json` holds Claude Code task runs on `qwen3-coder:30b` through the adapter, 17 of 18 passed. The CLI has `anymodel check <model> --tools`.
- **Mockup:** `~/.specwithcode/m5/evidence/anymodel-rethink/anymodel-mockup.png` (source `anymodel-mockup.html`). It used tokens from `specwithcode/apps/marketing`, but the live SpecWithCode page is built from `specweave/docs-site` (`src/pages/code.tsx`, `code.module.css`).

## Scope

In:

- The Worker answers 410 with a pointer to the README, a reversible redeploy.
- A README and npm deprecation note for the hosted endpoint, published as patch 2.0.1.
- A lean rebuild of anymodel.dev, with 4 pages: home, agent bench, setup per client, and the notice.
  - It uses the tokens of the live SpecWithCode page.
  - It uses provider marks from `ProviderLogoMarks.tsx`.
  - Its hero motion is gated like the SpecWithCode home page: paused off-screen, on hidden tabs, and under reduced motion.
- The `anymodel bench` command, which runs the existing harness locally and writes a result file.

Out:

- The 32 s promo video, which waits for the funnel trigger.
- Deleting the domain or the npm package; the owner must approve that.
- Any paid plan.
- Naming or linking any third-party gateway.
- The SpecWithCode app track, which is increment 1513.

## Acceptance Criteria

- [x] AC-01: `https://api.anymodel.dev/v1/messages` and every other path answer 410. The JSON body names the README section and says the package runs locally with the user's own key. `/health` answers 410 too. The old Worker source stays in the repository, so a redeploy restores it.
- [x] AC-02: The README and npm page for 2.0.1 state:
  - the hosted endpoint is retired (with the date);
  - AnyModel is free and open source (MIT) and never sells, pools or resells model access.

  No other product is named.
- [ ] AC-03: Gated on the funnel decision. anymodel.dev serves the rebuilt site:
  - The tokens (background, text, accent, type, corners) match `specweave/docs-site/src/pages/code.module.css` and the theme it uses.
  - Every provider named shows its mark from `ProviderLogoMarks.tsx`.
  - Every bench cell shows its date.
  - The first matrix row comes from the real result file.
  - There are no savings claims.
  - Lighthouse accessibility is at least 95 on home and bench.
  - Screenshots at 1440 and 390 px are saved to `reports/`.
- [ ] AC-04: The hero motion runs only while visible and the tab is shown, and never under `prefers-reduced-motion`. A headless check confirms all three states.
- [ ] AC-05: `npx anymodel bench --model <id>` runs the bench tasks through Claude Code against the user's own endpoint and writes `bench-results-<model>-<date>.json`. It refuses without explicit credentials, and it never sends results anywhere.

## Approach

1. **Worker.** `worker/index.mjs` gains a `RETIRED` switch, read from a var, that answers 410 before any other handling. Set it in `worker/wrangler.toml` and run `wrangler deploy`. The OpenRouter secret is left untouched, because the handler never reads it.
2. **README and release.** `README.md` gets a short "Hosted endpoint retired" section and the no-resale line. Bump `package.json` to 2.0.1 and publish with `npm publish`.
3. **Site (after the gate).**
   - Rebuild `site/` as static HTML/CSS/JS, keeping Vercel `outputDirectory: site`.
   - Port the design tokens from docs-site `code.module.css`. Copy the marks from `ProviderLogoMarks.tsx`.
   - Generate the bench matrix from `site/bench/*.json` with `scripts/build-bench.mjs`.
   - Run the hero motion as GSAP-free CSS and a small IntersectionObserver gate, following `specwithcode/apps/marketing/src/lib/homeMotion.ts`.
4. **CLI.** `cli.mjs` adds a `bench` subcommand that wraps the existing harness in `evaluation/`.

Risks:

- Bench results go stale, so each cell shows its date.
- Brand confusion with other products of the same name is handled by the no-resale line, with no names.

## Decisions

### Asked
- D-01: Plan → C + E with a lean redesign, Worker retired, D if the funnel is near zero (owner, November 27, 2026).
### Defaulted (change any before sw-do)
- D-02: Worker retirement → 410 with a pointer, not deletion (reversible).
- D-03: The site stays static HTML on Vercel, not Astro, to keep the repository dependency-free like today.
- D-04: Site tasks T-03 to T-05 wait for the 1511 funnel result and the owner's answer on E's timing.
### Open
- none

## Tasks

### T-01 Retire the hosted Worker with a 410
- AC: AC-01 | Files: repositories/anton-abyzov/anymodel/worker/index.mjs, repositories/anton-abyzov/anymodel/worker/wrangler.toml, repositories/anton-abyzov/anymodel/worker/test/retired.test.mjs | Test: curl -s -o /dev/null -w '%{http_code}' https://api.anymodel.dev/v1/messages prints 410

### T-02 README note and 2.0.1 release
- AC: AC-02 | Files: repositories/anton-abyzov/anymodel/README.md, repositories/anton-abyzov/anymodel/package.json, repositories/anton-abyzov/anymodel/CHANGELOG.md | Test: npm view anymodel@2.0.1 readme | grep -i "hosted endpoint"

### T-03 Rebuild anymodel.dev in SpecWithCode style
- AC: AC-03 | Files: repositories/anton-abyzov/anymodel/site/index.html, repositories/anton-abyzov/anymodel/site/styles.css, repositories/anton-abyzov/anymodel/site/script.js, repositories/anton-abyzov/anymodel/site/bench.html, repositories/anton-abyzov/anymodel/site/setup.html, repositories/anton-abyzov/anymodel/scripts/build-bench.mjs | Test: node scripts/build-bench.mjs && headless screenshots at 1440 and 390 px

### T-04 Gated hero motion
- AC: AC-04 | Files: repositories/anton-abyzov/anymodel/site/script.js, repositories/anton-abyzov/anymodel/test/site-motion.test.mjs | Test: node --test test/site-motion.test.mjs

### T-05 anymodel bench command
- AC: AC-05 | Files: repositories/anton-abyzov/anymodel/cli.mjs, repositories/anton-abyzov/anymodel/evaluation/, repositories/anton-abyzov/anymodel/test/bench-cli.test.mjs | Test: node --test test/bench-cli.test.mjs
