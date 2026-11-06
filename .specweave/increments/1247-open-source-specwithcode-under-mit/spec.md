# Open source SpecWithCode under MIT

## Problem

SpecWithCode is described everywhere as "free, source available" with "no new project-wide license grant". The development repository `anton-abyzov/specwithcode-dev` is private, and the public repository `anton-abyzov/specwithcode` (4 stars) only receives one scrubbed snapshot commit per release from `scripts/public-mirror/publish.mjs`, so nobody can contribute, follow development or check that a build came from the published code (1246 AC-03 needs a public build repository). On November 6, 2026 Anton decided to make SpecWithCode open source under MIT, the license T3 Code uses: "I'd love to go this route... Let's go ahead and do this... do it all as you mentioned." This replaces the "source available, never open source" rule and the "no new project-wide license grant" note.

## Scope

In:
- A secret and private-data audit of the full history of `specwithcode-dev` (gitleaks, the mirror's private scrub list, sensitive paths) and of the public mirror, with a recommendation: publish the real history after cleanup, or start a fresh history.
- An MIT `LICENSE` at the repository root, `license: "MIT"` in the workspace `package.json` files, README, CONTRIBUTING, AGENTS/CLAUDE identity rules and docs reworded from "source available" to open source. Every third-party notice stays, with accurate provenance, including T3 Code's MIT notice.
- A plan to make the public repository the real development repository, keeping the stars.
- Repository polish: README with a demo GIF, a one-line pitch, install buttons and a star badge; CODE_OF_CONDUCT.md; issue and PR templates; about 10 good-first-issues; GitHub topics and description.
- "Star on GitHub" links on the first-run screen and in About (dismissible), and one on specwithcode.com.
- spec-weave.com (specweave repo `docs-site/`) wording: "open source (MIT)" instead of "source available".

Out:
- Rewriting or force-pushing any history, and changing repository visibility, without Anton's explicit yes on that single step.
- Marketing copy claiming SpecWithCode is "built on T3 Code". Legal notices keep the attribution.
- Relicensing third-party code or vendored repositories.

## Acceptance Criteria

- [ ] AC-01: An audit report under this increment's folder lists the gitleaks findings for all commits of `specwithcode-dev` (count by rule, file paths, redacted), the commits that touch any value in the mirror's private scrub list (counts only, never values), sensitive files ever added (`.env`, keys, certificates, databases, user data), and the same checks for `anton-abyzov/specwithcode`, and ends with one recommendation and its evidence.
- [ ] AC-02: `LICENSE` at the root of the repository is the MIT License with `Copyright (c) 2026 Anton Abyzov`; GitHub reports the repository license as MIT; the workspace `package.json` files declare `"license": "MIT"`.
- [ ] AC-03: `THIRD_PARTY_NOTICES.md` keeps T3 Code's MIT notice verbatim (`Copyright (c) 2026 T3 Tools Inc.`) and every other existing notice; no file still says "no new project-wide license grant", "source available" or "never open source" about SpecWithCode.
- [ ] AC-04: No marketing surface (README pitch, specwithcode.com, store copy) says SpecWithCode is built on, based on or a fork of T3 Code; `THIRD_PARTY_NOTICES.md` and `UPSTREAM.md` still state the provenance.
- [ ] AC-05: The README opens with a one-line pitch, a demo GIF, download buttons for macOS, Windows and Linux, and a GitHub stars badge; `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, issue templates and a PR template exist; the repository has a description, at least 6 topics and at least 10 open issues labelled `good first issue`, each with the files to change and how to test.
- [ ] AC-06: The first-run screen and the About section show a "Star on GitHub" link to the public repository that opens in the system browser; dismissing it on the first-run screen keeps it hidden after a restart; About always shows it. A test covers both.
- [ ] AC-07: specwithcode.com shows one "Star on GitHub" link and says "open source (MIT)" wherever it said "source available"; the landing test asserts the new wording.
- [ ] AC-08: The development repository is public (after Anton's yes), its default branch builds in CI, and the public URL that has the stars either is that repository or redirects to it.

## Approach

1. Audit (read-only, no checkout changes): `gitleaks git` over `specwithcode-dev` and a fresh bare clone of `specwithcode` in a scratch folder, `git log --all -S` for each scrub-list value printing counts only, and a path scan of every file ever added. Report at `reports/audit.md` in this increment.
2. Recommendation drives the switch (decision D-03). Options for keeping the stars: (a) rename the public `specwithcode` repository away, rename `specwithcode-dev` to `specwithcode` and flip it public. Stars stay on the old repository, but GitHub redirects only follow renames, so (a) loses the 4 stars. (b) Push the cleaned development history into the existing public `specwithcode` repository (force-push of `main`, stars and watchers kept), make it the development repository, and archive `specwithcode-dev`. (b) keeps the stars, but moving CI, secrets, release workflows, the updater feed URL and open PRs to the new repository is real work. (c) Flip `specwithcode-dev` public under its own name and point the old repository's README to it. Recommendation goes in the audit report.
3. License PR (specwithcode-dev, once the shared checkout is free): `LICENSE`, `package.json` license fields, `THIRD_PARTY_NOTICES.md` header, `README.md`, `CONTRIBUTING.md`, `AGENTS.md`/`CLAUDE.md` identity section, `docs/` wording, `scripts/public-mirror/publish.mjs` (stop removing the license and upstream lines; retire it after the switch).
4. Polish PR: README, `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1), `.github/ISSUE_TEMPLATE/feature_request.yml`, PR template review, demo GIF under `assets/readme/`.
5. Star CTA PR: first-run screen and About in `apps/web`, with a persisted dismiss flag and tests.
6. Website PR (specweave `docs-site/`): wording, translations, star link, landing test. Merged only after the repository is public, because "open source" is false while the code is private.
7. After Anton's yes: the visibility or push step from D-03, topics, description, good-first-issues.

Risks: published history exposes any secret or private value that gitleaks misses; the 1244, PR 1138 and signing work hold the shared checkout; the updater and install scripts hard-code `anton-abyzov/specwithcode` release URLs, so moving releases needs care.

## Decisions

### Asked
- D-01 License → MIT, the license T3 Code uses (Anton, November 6, 2026).
- D-02 Rewrite/force-push history, and the visibility flip → each needs Anton's explicit yes on that single step (Anton, November 6, 2026).
### Defaulted (change any before sw-do)
- D-04 Copyright holder → "Anton Abyzov" (reversible).
- D-05 Code of conduct → Contributor Covenant 2.1 (reversible).
- D-06 Website claims "open source" only after the repository is public (reversible).
- D-03 Fresh history in `anton-abyzov/specwithcode`: the cleaned tree lands as an ordinary commit on top of its snapshots (no force-push), it becomes the development repository, and `specwithcode-dev` stays private and is archived (Anton, November 6, 2026).
- D-07 Secrets → only the public repository's encrypted Actions secrets, sourced from Keychain, Obsidian or local release files, never printed or committed; fork PRs can never read them (no `pull_request_target` with secrets, release jobs in a protected environment) (Anton, November 6, 2026).
- D-08 `LINUX_UPDATE_SIGNING_KEY` → generate a new key for `specwithcode`, private half in Keychain and the repository secret, because no copy exists outside GitHub and PR #1256, the only user of the key, is unmerged, so no installed app pins it yet (defaulted, reversible until #1256 ships).
### Open
- D-09 `RELEASE_GH_TOKEN` is a fine-grained token scoped to `specwithcode-dev`; the new repository needs a new token made in GitHub settings.

## Tasks

### T-01 Audit history for secrets and private data
- AC: AC-01 | Files: .specweave/increments/1247-open-source-specwithcode-under-mit/reports/audit.md | Test: `test -s .specweave/increments/1247-open-source-specwithcode-under-mit/reports/audit.md`

### T-02 Add MIT license, notices and reworded docs
- AC: AC-02, AC-03, AC-04 | Files: LICENSE, package.json, apps/*/package.json, packages/*/package.json, THIRD_PARTY_NOTICES.md, README.md, CONTRIBUTING.md, AGENTS.md, CLAUDE.md, docs/, scripts/public-mirror/publish.mjs | Test: `! git grep -nI -iE "source available|no new project-wide license" -- ':!**/node_modules/**' ':!.repos' && grep -q "T3 Tools Inc." THIRD_PARTY_NOTICES.md`

### T-03 Repository polish for contributors and stars
- AC: AC-05 | Files: README.md, CODE_OF_CONDUCT.md, .github/ISSUE_TEMPLATE/, .github/pull_request_template.md, assets/readme/demo.gif | Test: `test -f CODE_OF_CONDUCT.md && head -20 README.md | grep -q stargazers`

### T-04 Star on GitHub links in the app
- AC: AC-06 | Files: apps/web/src/ (first-run screen, About settings), tests | Test: `pnpm vitest run` on the new tests

### T-05 Open source wording and star link on specwithcode.com
- AC: AC-07 | Files: specweave docs-site/src/pages/code.tsx, docs-site/src/pages/code/download.tsx, docs-site/src/theme/Footer/index.tsx, docs-site/i18n/, docs-site/docs/guides/, docs-site/src/__tests__/code-landing.test.ts | Test: `cd docs-site && npx vitest run src/__tests__/code-landing.test.ts`

### T-06 Switch the public repository to the development repository
- AC: AC-08 | Files: none (GitHub settings), .github/workflows/, scripts/install.sh, scripts/install.ps1 | Test: `gh repo view anton-abyzov/specwithcode-dev --json visibility,licenseInfo`

### T-07 Verify and close 1247
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: none | Test: `specweave verify 1247-open-source-specwithcode-under-mit`
