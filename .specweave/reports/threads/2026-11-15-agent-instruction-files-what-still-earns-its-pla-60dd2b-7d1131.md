---
title: "Agent instruction files: what still earns its place"
thread: "mcp:acc7f45f-52fd-47f4-bdbd-22e6c4294eb0"
threadTitle: "Do we still need agent instruction files?"
savedAt: "2026-11-15T00:40:01.045Z"
date: November 14, 2026
type: analysis
scope: read-only, no files changed
---

# Agent instruction files: what still earns its place

**Answer.** Yes, keep instruction files, but only for facts a model cannot get from the code or the tools. That is about 15% of what is loaded today. The 11 hand-written files shrink from 673 lines (about 18,460 tokens) to 136 lines (about 2,970 tokens). SpecWithCode should install no instruction file in a user's project; its own rules already travel in the prompt it builds and in tool descriptions.

Tokens are characters / 4. Measured November 14, 2026 on `specwithcode` `013d05387` and `specweave` `94d9f0108` (3.1.23).

## 1. Inventory

### Files on disk

| File | Lines | Tokens | Loaded by |
|---|---:|---:|---|
| `~/Projects/github/specweave-umb/AGENTS.md` | 96 | 3,097 | Every tool in the umbrella and, for Claude, in every nested repo (parent folders are read too) |
| `~/Projects/github/specweave-umb/CLAUDE.md` | 52 | 617 | Claude; imports `AGENTS.md` |
| `repositories/anton-abyzov/specwithcode/AGENTS.md` | 105 | 5,790 | Every tool in the app checkout |
| `repositories/anton-abyzov/specwithcode/CLAUDE.md` | 5 | 106 | Claude |
| `repositories/anton-abyzov/specweave/AGENTS.md` | 55 | 1,536 | Every tool in the CLI checkout |
| `repositories/anton-abyzov/specweave/CLAUDE.md` | 6 | 57 | Claude |
| `repositories/anton-abyzov/vskill-platform/AGENTS.md` | 45 | 487 | Every tool in the platform checkout |
| `repositories/anton-abyzov/vskill`, `specweave-status` | 0 | 0 | No instruction files |
| `repositories/anton-abyzov/specweave/src/templates/AGENTS.md.template` | 65 | 1,273 | Written into user projects |
| `repositories/anton-abyzov/specweave/src/templates/CLAUDE.md.template` | 19 | 206 | Written into user projects |
| `~/.claude/CLAUDE.md` | 159 | 3,283 | Every Claude session on this Mac |
| `~/.codex/AGENTS.md` | 66 | 2,007 | Every Codex session on this Mac |
| **Total, 11 files** | **673** | **18,459** | |
| `~/.claude/projects/-Users-antonabyzov-Projects-github-specweave-umb/memory/MEMORY.md` | 207 | 5,939 | Claude auto-memory; over its 200-line limit, 7 lines cut off |
| Project memory (`studio_project_memory_list`) | 83 files | index 2,226; all files about 82,760 | Index and file list in every project thread; files on demand |

### What SpecWeave writes into a user project

`specweave init` (`src/cli/commands/init.ts`) writes `.specweave/`, `AGENTS.md` and `CLAUDE.md` from the two templates, `.gitignore`, `.gitattributes` (with `**/ledger.jsonl merge=union`), the memory index, and the sw-* skills into `.claude/skills/` and `.agents/skills/` (9 skills here, about 10,360 tokens, loaded only when used). Nothing outside the project. `specweave update` re-runs the merge (`src/cli/commands/update-instructions.ts`): `required` sections are rewritten, user sections kept, the old file backed up to `.specweave/backups/`.

That rewrite is why the umbrella file needs the note "`specweave update` rewrites the Handoff paragraph, re-apply this rule after each update".

### What SpecWithCode injects and installs

It writes no instruction file into a user's repo. `apps/server/src/project/SpecweaveSetup.ts` runs `specweave init --quick --adapter claude` only when the person ticks "Use SpecWeave" on a new project or presses "Set up SpecWeave" in Project settings. Everything else is prompt text built on every turn.

| Block | Source | Doc says | Code today |
|---|---|---:|---:|
| `live_database` | `packages/contracts/src/agentInstructions.ts` | 82 | 82 |
| `runtime_info` | `apps/server/src/provider/RuntimeInstructions.ts` | 40 | about 40 |
| `response_style` (concise) | same | 217 | **1,057** |
| `presentation` | same | 218 | 228 |
| `reports` | same | not listed | 94 |
| `writing` | same | 108 | 108 |
| `output_formatting` | same | 102 | 102 |
| `pull_requests` | same | 96 | about 96 |
| `browser_automation` | same | 96 | 96 |
| `heavy_checks` | same | not listed | 61 |
| Orchestration | `apps/server/src/provider/StudioOrchestrationInstructions.ts` | 475 | **761** |
| Collaborative browser (Codex, ACP) | same | 404 | 409 |
| Worker role | `projectContextText` in `apps/server/src/project/ProjectWorkspaceService.ts` | 208 | about 290 with the SpecWeave line |
| Coordinator role | same | 1,123 | about 1,500 |
| Launch brief (small-fix, sizing) | `apps/server/src/project/launchIncrement.ts` | not listed | about 150 |

`docs/internals/agent-instructions.md` is out of date. It gives a worker about 1,760 tokens; the code now sends about 3,000. The whole gap is three things: `response_style` grew fivefold, orchestration grew by 286, and `reports` and `heavy_checks` are missing from the table.

### What one thread actually carries

| Thread | Files | Auto-memory | App blocks | Project context | Total |
|---|---:|---:|---:|---:|---:|
| Claude worker in the umbrella | 6,997 | about 5,700 | about 2,725 | about 3,400 | about 18,800 |
| Claude worker in the app checkout | 12,893 | about 5,700 | about 2,725 | about 3,400 | about 24,700 |

## 2. Duplicates across layers

| Rule | Copies | Where |
|---|---:|---|
| Headless browser | 7 | `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, umbrella `AGENTS.md` twice (Rules bullet and its own section), app `AGENTS.md`, CLI `AGENTS.md`, app `browser_automation` block. The env part is also set in code at every provider spawn. |
| Product identity and licensing | 6 | Umbrella `AGENTS.md` (Rules bullet and closing section), umbrella `CLAUDE.md` twice, app `AGENTS.md`, app `CLAUDE.md`, plus memory |
| Worktree and scratch-copy rules | 6 | Umbrella Rules, umbrella Project notes, app `AGENTS.md`, app environment section, two memory files. The git wrapper already refuses `git worktree add` (`ManualWorktreeGuard.ts`). |
| Human tone, no em dashes | 5 | `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, app `CLAUDE.md`, auto-memory, app `writing` block |
| Terse replies | 4 | `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, app `response_style`, Claude Code's Concise output style |
| No AI attribution, short commits | 4 | `~/.claude/CLAUDE.md`, the project's `[instructions]`, auto-memory, project memory `process-rules.md` |
| Stop by PID | 4 | `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, app `AGENTS.md`, app `browser_automation` block |
| App release request | 4 | Umbrella Project notes, app `AGENTS.md`, two memory files |
| Live database ban | 3 | App `live_database` block, app `AGENTS.md`, project memory |
| Small fix or increment | 3 | Umbrella loop step 2, app launch brief on every turn, sw-increment skill |
| Usage never stops work | 3 | Umbrella loop, umbrella Project notes, auto-memory |

Two rules contradict each other. The umbrella says "ask user for manual acceptance: new UI, auth, payments, data migrations"; the app file says "require manual acceptance only when the user or the increment's acceptance criteria explicitly request it". The umbrella `CLAUDE.md` also carries a Commands table of three TODO cells while `AGENTS.md` has the real commands.

## 3. Classification

(a) enforced in code, delete the prose. (b) a current model already knows or can read it from the code, delete. (c) project-specific and not derivable, keep. (d) better in a tool description, skill or doc, move.

| File | Rules | (a) | (b) | (c) | (d) |
|---|---:|---:|---:|---:|---:|
| Umbrella `AGENTS.md` | 30 | 7 | 3 | 11 | 9 |
| Umbrella `CLAUDE.md` | 12 | 2 | 6 | 1 | 3 |
| App `AGENTS.md` | 68 | 6 | 10 | 23 | 29 |
| App `CLAUDE.md` | 3 | 0 | 0 | 1 | 2 |
| CLI `AGENTS.md` | 30 | 1 | 9 | 13 | 7 |
| CLI `CLAUDE.md` | 3 | 0 | 1 | 2 | 0 |
| Platform `AGENTS.md` | 10 | 2 | 0 | 8 | 0 |
| `AGENTS.md.template` | 18 | 2 | 1 | 4 | 11 |
| `CLAUDE.md.template` | 6 | 2 | 2 | 1 | 1 |
| `~/.claude/CLAUDE.md` | 38 | 3 | 11 | 10 | 14 |
| `~/.codex/AGENTS.md` | 20 | 2 | 8 | 4 | 6 |
| **Total** | **238** | **27 (11%)** | **51 (21%)** | **78 (33%)** | **82 (34%)** |

Of the 78 kept rules, about 30 are repeats of a rule kept elsewhere, so roughly 48 distinct rules survive.

### What each class holds

| Class | Main members | Evidence |
|---|---|---|
| (a) | Headless env vars; `git worktree add` refusal; a task is done only when its Test exits 0; stale claims; ledger merge keeps both sides; pickup at session start; Jev guard; design tokens; small-fix reminder | `HEADLESS_BROWSER_ENVIRONMENT` at every spawn; `ManualWorktreeGuard.ts`; `task done --run` exits 5 on failure; `.gitattributes` `merge=union`; SessionStart hook; `designTokens.guard.test.ts`; `launchIncrement.ts` |
| (b) | Terse-reply bullets, "never commit secrets", "use plan mode", package layout tables, the architecture tour of `apps/*` and `packages/*`, UI checklists | A model reads the folder tree faster than the table, and the app already sends its own style block |
| (c) | Folder and scratch policy, one-repo rule, release entry points and who may promote, merge-without-asking and its three exceptions, usage never stops work, identity and notices, `.repos` is read-only, test isolation from live stores, guarded RPC rule, CI blind spots, Commands tables | Owner decisions and traps that cost real incidents |
| (d) | The whole SpecWeave loop (5 steps, handoff, task and ledger formats) into the sw-* skills already installed; 24 of 28 verifier rows and two fixture sections into a doc; release-train paragraph into `docs/studio/releasing.md`; YouTube, Blotato, Kie and take-editing rules into the skills that already state them | The skills `sw-do`, `sw-done`, `sw-handoff`, `sw-increment`, `social-media-posting`, `kie-gemini-omni` and `hyperframes-best-practices` exist and load on demand |

## 4. Biggest wins

| # | Cut | Tokens saved | Reaches |
|---:|---|---:|---|
| 1 | App `AGENTS.md`: move the 28-row verifier table, two fixture sections, the release-train paragraph and the worktree paragraph out | about 5,060 | Every thread in the app checkout |
| 2 | Claude auto-memory `MEMORY.md`: about 170 of 207 lines are status entries that also live in project memory. Keep the standing rules and feedback, about 40 lines | about 4,500 | Every Claude thread in the umbrella |
| 3 | `~/.claude/CLAUDE.md`: drop the style bullets, Tauri, Obsidian structure, take-editing, media and social detail | about 2,900 | Every Claude session on this Mac |
| 4 | Umbrella `AGENTS.md`: the SpecWeave loop goes to the skills, duplicate headless and identity sections go | about 2,330 | Every thread in the umbrella and its repos |
| 5 | App `response_style`: the third bullet (about 3,000 characters of blocker, delivery and closure protocol) moves to the coordinator role and the `studio_thread_record_delivery` description | about 800 | Every thread of every user of the app, and each subagent |
| 6 | `AGENTS.md.template`: 65 lines to 15 | about 1,150 | Every SpecWeave user project |

Win 5 is the only one that reaches other users on every turn. Wins 1 to 4 are local to this setup.

## 5. Recommendations

### 5.1 Should SpecWithCode install an instruction file?

No, at no point: not on first run, not on project add. Three reasons.

- Its rules are about the app, not the repo, so they belong in the prompt it builds and in tool descriptions, where they already are, on every provider and with no file to drift.
- A file in the user's repo gets committed, reviewed and merged by people who never asked for it, and other tools then read rules for an app they are not running in.
- The model can write a good project file itself from the code when asked.

Keep the one opt-in path that exists: "Use SpecWeave" runs `specweave init`, and then SpecWeave owns the file. Make that file the 15-line form in section 6. Optional addition, on request only: a "Draft project notes" action that has the agent write up to 10 lines of repo-specific traps into the Project notes slot for the user to review. Never automatic.

### 5.2 What the app itself should change

| Change | Why |
|---|---|
| Cut `response_style` from 1,057 to about 250 tokens | Workers and subagents do not act on coordinator closure protocol |
| Trim orchestration from 761 toward 475 | The machine, file-transfer, computer-use and Chrome lines repeat their tool descriptions |
| Set Claude Code's commit and PR attribution to empty at spawn when the user turns attribution off | Replaces a 20-line "no AI attribution" block that exists only because the harness asks for the trailer in every session. Check the exact settings key against the current Claude Code docs first. |
| Re-measure `docs/internals/agent-instructions.md`, add `reports`, `heavy_checks` and the launch brief, and add a test that fails when a block exceeds its documented size | The doc understates a worker by about 1,200 tokens; only `presentation` has a cap today |
| Empty this project's `[instructions]` | It repeats the Git rules in `~/.claude/CLAUDE.md` |

### 5.3 Delete outright

| File or section | Lines |
|---|---:|
| Umbrella `CLAUDE.md`: everything except `@AGENTS.md` (TODO Commands table, March team-lead notes, three identity repeats, manual gates) | 51 |
| Umbrella `AGENTS.md`: "The loop", Handoff paragraph, task and ledger formats, Project hub, Jev, both headless copies, "Project-Specific Gates", closing identity section, the 1,476-PR statistic, the legacy-prefix note | about 60 |
| App `AGENTS.md`: Browser verification, live-database bullet, stop-by-PID bullet, the worktree paragraph, relay and telemetry defaults, the package tour, the UI checklist | about 25 |
| App `CLAUDE.md`: both prose lines | 4 |
| CLI `AGENTS.md`: Layout table, headless bullet, the three long Releasing paragraphs | about 20 |
| `CLAUDE.md.template`: everything except `@AGENTS.md` | 18 |
| `~/.claude/CLAUDE.md`: Communication Style bullets, Tauri section, Obsidian structure and automation, "Not fine as escape hatches" lists | about 90 |
| `~/.codex/AGENTS.md`: "SpecWeave and Claude Code continuity" (EasyChamp-specific; move the EasyChamp half to that project) | 10 |

### 5.4 Move

| From | To |
|---|---|
| 24 verifier rows and two fixture sections in the app `AGENTS.md` | A new `docs/operations/checks.md` in the app repository |
| Release-train paragraph | `docs/studio/releasing.md`, already there |
| CLI release paragraphs and workspace-adoption table | A doc beside `scripts/release/release.sh` and `--help` |
| The SpecWeave loop | The sw-* skills, already there |
| YouTube and Blotato routing, take editing, Kie defaults | `social-media-posting`, `hyperframes-best-practices`, `kie-gemini-omni` already say it; one line each stays as the trigger |

## 6. Minified drafts

### Before and after

| File | Before lines | After lines | Before tokens | After tokens |
|---|---:|---:|---:|---:|
| Umbrella `AGENTS.md` | 96 | 29 | 3,097 | 763 |
| Umbrella `CLAUDE.md` | 52 | 1 | 617 | 3 |
| App `AGENTS.md` | 105 | 37 | 5,790 | 725 |
| App `CLAUDE.md` | 5 | 1 | 106 | 3 |
| CLI `AGENTS.md` | 55 | 16 | 1,536 | 379 |
| CLI `CLAUDE.md` | 6 | 4 | 57 | 30 |
| Platform `AGENTS.md` | 45 | 10 | 487 | 162 |
| `AGENTS.md.template` | 65 | 15 | 1,273 | 124 |
| `CLAUDE.md.template` | 19 | 1 | 206 | 3 |
| `~/.claude/CLAUDE.md` | 159 | 11 | 3,283 | 358 |
| `~/.codex/AGENTS.md` | 66 | 11 | 2,007 | 415 |
| **Total** | **673** | **136** | **18,459** | **2,965** |

Both `CLAUDE.md` files and the template become the single line `@AGENTS.md`. The CLI `CLAUDE.md` keeps its hook-reload note.

### Umbrella `AGENTS.md` (29 lines)

```markdown
# specweave umbrella

Work is planned as SpecWeave increments in `.specweave/increments/NNNN-slug/` (`spec.md`, `ledger.jsonl`). `specweave pickup` prints the next task; the sw-* skills carry the loop (plan, do, review, done, handoff).

## Rules

- Nested repos live under `repositories/anton-abyzov/<repo>/`. Commit inside the nested repo, then the umbrella. Task `Files` are written from the umbrella root (`repositories/anton-abyzov/specwithcode/apps/server/...`).
- The app has one repository and one checkout: `repositories/anton-abyzov/specwithcode`. `specwithcode-dev` is retired; never recreate it.
- Nothing new goes directly in `~/Projects/github`. Scratch and logs: `~/.specwithcode/m4/scratch/<date>-<task>/`. Evidence: the increment's `reports/`, else `~/.specwithcode/m4/evidence/<topic>/`. Old evidence: `/Volumes/SanDisk APFS/Archive/specwithcode/`.
- A scratch copy of a repository is yours to remove once its PR merges or closes. Before removing any folder, check no thread is bound to it (`specweave-studio db query`). Never symlink another checkout's `node_modules`.
- Usage readings never stop work here: no handoff at any threshold (owner's rule, October 10, 2026).
- Merge green PRs, release, deploy and verify without asking. Ask before discarding work that exists nowhere else, and for data migrations, auth changes and payment flows. `claude-review` and `E2E Live (nightly)` never block.
- Releases: `bash scripts/release/release.sh status|ship|verify|cleanup <track>`; runbook `.specweave/release/README.md`. App releases: `bash scripts/release/request-release.sh --by "<thread>"` in the app repository; never pick or dispatch a version.
- Waits: never hold a call on CI or a registry for more than 540s; use `bash scripts/release/ci-wait.sh` (exit 2 means call again).
- SpecWithCode is an independent product: never market it as a fork, keep third-party notices and existing license grants, add no project-wide license grant.
- Files stay under 1,500 lines. Use Node 22 and SpecWeave 3.1.21 or newer.

## Commands

| Action | Command |
|---|---|
| Build | `npm --prefix repositories/anton-abyzov/specweave run build && npm --prefix repositories/anton-abyzov/vskill run build && npm --prefix repositories/anton-abyzov/vskill-platform run build` |
| Test | `npm --prefix repositories/anton-abyzov/specweave run test:unit:fast && npm --prefix repositories/anton-abyzov/vskill test && npm --prefix repositories/anton-abyzov/vskill-platform test` |
| Lint | `npm --prefix repositories/anton-abyzov/specweave run lint:skills && npm --prefix repositories/anton-abyzov/specweave run lint:docs-refs && npm --prefix repositories/anton-abyzov/vskill run lint:skills-spec` |
| Fleet checkout safety | `python3 scripts/fleet-project-sync.py --self-test` |
| Handoff verifier | `python3 -m unittest discover -s tests -p test_handoff_evidence.py` |
| Release tooling | `python3 scripts/release/timing.py --self-test && bash scripts/release/release-self-test.sh` |

The platform has no ESLint command; never claim a clean platform lint run.
```

### App `repositories/anton-abyzov/specwithcode/AGENTS.md` (37 lines)

```markdown
# SpecWithCode

Independent, MIT-licensed workbench for native coding agents. SpecWeave owns portable intent, claims and handoffs; the app owns sessions and control on each machine.

## Rules

- Public repository: never commit secrets, personal paths, machine names, customer data or private reports.
- Third-party code keeps its own license. Keep `THIRD_PARTY_NOTICES.md` and the notices in Settings complete; `node scripts/studio-brand-audit.mjs` checks it.
- In anything a person reads, say SpecWithCode, then "the app"; never "Studio". Code identifiers stay literal (`docs/studio/naming.md`).
- `.repos/` holds read-only reference trees: never edit, import, package or bulk-transform them.
- Production runs on Node 22.20.0 with pnpm 11.10.0; some builds need a separately scoped Node 24. Never change shared toolchains or provider installs to fix a build.
- Tests never touch live stores, credential folders or OAuth tokens: use a new private test home and a scratch repository. A check that must drive the live app creates its project with `origin: "automated"` and deletes it after.
- Run the smallest focused test plus the web and server builds your change touches. No repo-wide tests, lint or typecheck unless asked (`docs/operations/heavy-checks.md`).
- Phone availability, restored native sessions and subscription capacity need real outcome evidence; a fixture does not prove them. Record what is unverified as a proof limit.
- Releases: `bash scripts/release/request-release.sh --by "<thread>"`; never choose a version or mark a release stable by hand (`docs/studio/releasing.md`).

## Architecture

WebSocket request -> command -> pure orchestrator -> events -> atomic sink (events, projections, receipts, outbox) -> effect worker does I/O and feeds results back as commands.

- Mutations use `createEnvironmentRpcCommand`; protected methods go in `CLIENT_GUARDED_RPC_SCOPES`; the destination machine checks grants at execution. Test both the UI gate and the server refusal.
- Read `docs/internals/effect-services.md` before adding an Effect service.
- In tests, drain `OrchestrationEffectWorkerV2` or await a persisted event; never sleep.
- Keep same-origin routing; never bake localhost `VITE_HTTP_URL`/`VITE_WS_URL` into a remote bundle.
- UI text, sizes, corners and colours come from the tokens in `docs/studio/design-guidelines.md`.

## Commands

| Check | Command |
|---|---|
| Web typecheck | `node node_modules/typescript/bin/tsc --noEmit --project apps/web/tsconfig.json` |
| Server typecheck | `node node_modules/typescript/bin/tsc --noEmit --project apps/server/tsconfig.json` |
| Web build (from `apps/web`) | `node ../../node_modules/vite-plus/bin/vp build` |
| Server build | `node apps/server/scripts/cli.ts build` |
| One test file | `node node_modules/vite-plus/bin/vp test run <file>` |

Headless fixtures and live verifiers are listed in `docs/operations/checks.md`.
```

`docs/operations/checks.md` does not exist yet; it receives the 24 moved rows.

### CLI `repositories/anton-abyzov/specweave/AGENTS.md` (16 lines)

```markdown
# SpecWeave (this repository)

Source of the `specweave` npm package: a CLI plus a Claude Code plugin. The file SpecWeave writes into user projects is `src/templates/AGENTS.md.template`.

- Node 22. `npm ci`, then `npm run build`. The CLI runs from `dist/`, so rebuild before trying `node bin/specweave.js <cmd>`.
- CI runs `npm run test:unit` (`tests/unit/**`). Co-located `src/**/*.test.ts` files are not in CI; put new tests under `tests/unit/`.
- `skills/sw-*` is the one skill source; `npm run generate:skills` writes `plugins/specweave/skills/`. Never edit the copies.
- After adding or renaming a command or option: `node scripts/completions/generate.mjs`.
- `init` refuses to run inside the system temp directory; try it in a scratch folder elsewhere.
- Default branch is `develop`; PRs target it. Feature PRs merge with `gh pr merge --squash --admin`. Push over HTTPS.
- Release: `bash scripts/release/release.sh patch|minor|major|X.Y.Z` (6 to 8 minutes; run it in the background).
- Increment state lives only in `ledger.jsonl`; never write derived state back into markdown.
- Hooks stay fast and offline: no network, no Git in SessionStart, and a hook error never blocks the user's tool.
- Changing an increment's status never calls a tracker; only `specweave sync push` does.
- `src/core/workspace/` owns planning context and checkout adoption: reuse it, never scan parent directories, never merge checkouts because their remotes match.
- Files stay under 1,500 lines.
```

### `AGENTS.md.template`, the file for user projects (15 lines)

```markdown
# {PROJECT_NAME}

This project plans work with SpecWeave: `specweave pickup` prints the open increment, the next task and its acceptance criteria. The sw-* skills in `.agents/skills/` and `.claude/skills/` carry the rest (plan, do, review, done, handoff).

## Commands

| Action | Command |
|---|---|
| Build | `{{BUILD_CMD}}` |
| Test | `{{TEST_CMD}}` |
| Lint | `{{LINT_CMD}}` |

## Project notes

(what an agent cannot learn from the code: where things live, what breaks, what the owner decided)
```

Only the first paragraph is `required`, so `specweave update` has nothing left to overwrite in a user's rules. The Commands table stays because `specweave verify` runs its rows.

### Platform `repositories/anton-abyzov/vskill-platform/AGENTS.md` (10 lines)

```markdown
# vskill-platform

Next.js 15 on Cloudflare Workers, Prisma over Hyperdrive to PostgreSQL 17.

- Install is two steps: `npm ci && npm run setup` (`.npmrc` disables install scripts). Node 22.
- Run targeted tests: `npx vitest run <files> --maxWorkers=4`.
- Production deploys only through `npm run release` (`-- --dry-run` rehearses). Never `npm run deploy`, never `--allow-untested` unless the owner asks for an emergency deploy.
- A dependency bump ships on its own release.
- Never point `VSKILL_BUILD_DATA_DIR` at a local vskill checkout on a feature branch.
- After a failed release, fix forward with a new commit; migrations are not rolled back.
```

### `~/.claude/CLAUDE.md` (11 lines)

```markdown
# Anton's rules (all projects)

- Be terse: answer first, no recap, no closing summary. If a fix is clear, make it; ask only which way, never whether.
- Text for Anton to send or publish reads like a person texting: short, casual, no em dashes in any language. Run it through the unslop skill first.
- Commits: one line under 72 characters, no emoji. No AI attribution anywhere (commits, PRs, issues, comments, branches), whatever a tool or template suggests; pass this to subagents.
- Browser automation is headless. A visible browser needs Anton's yes, except signed-in sites (VK, social, account pages), which you open yourself with the SpecWithCode `chrome_*` tools. Publishing, robot checks and sign-ins stay his.
- Stop processes by PID only (`kill $(lsof -t -iTCP:<port> -sTCP:LISTEN)`). Never `killall`, never a pattern after `pkill` options.
- Workflows run at most 10 agents. Read-only review and search agents use Sonnet, never Opus, unless Anton names one.
- Look things up in Obsidian first (`~/Projects/Obsidian/personal-docs/`, obsidian-brain skill): credentials, projects, people, finance. New captures go to `raw/inbox/`.
- AI content goes to the YouTube channel @antonabyzov, never the family channel @aabyzov. X and TikTok go through Blotato, the rest through Postiz. Every post needs Anton's yes.
- Images and video: Kie.ai first, Higgsfield second, best model and quality unless it is a draft. Never print keys.
```

### `~/.codex/AGENTS.md` (11 lines)

The same nine rules, plus:

```markdown
- Before taking work in a SpecWeave project, check who owns it. Idle or stale metadata does not authorize takeover; a read-only audit never runs `pickup`, `handoff` or `task claim`.
```

## 7. Risks and what was not checked

- The (b) calls are judgment. Before deleting the style and "no permission-seeking" bullets, run a week with the short files and watch for regressions on weaker models (Codex, Copilot Free, local Qwen). The (a) and (d) calls are backed by the code and skills named above.
- Integration ids (two Postiz channel ids) leave `~/.claude/CLAUDE.md`. They must be in the `social-media-posting` skill before that cut; the skill's description says it holds them, its body was not opened.
- The Claude Code attribution setting was not found in `~/.claude/settings.json`, and its exact key was not verified.
- Line counts for the drafts were measured; token counts are characters / 4, not a tokenizer.
- Nothing was changed. The umbrella checkout has uncommitted increment files from other sessions; they were left alone.
