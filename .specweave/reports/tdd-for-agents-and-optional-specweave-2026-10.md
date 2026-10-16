# TDD for agents, and whether SpecWeave should be optional

2026-10-11. Covers the post you meant, what it means for SpecWeave, and how SpecWeave fits into SpecWithCode.

## Answers

1. **The post** is by Kun Chen ([@kunchenguid](https://x.com/kunchenguid/status/2108030810691629403)), from Oct 8, 2026 UTC. Agent-written unit and integration tests did not improve results and cost more. His June eval found that a TDD skill made results worse. Two independent checkers verified every number below against his posts and charts.
2. **Is SpecWeave "doing TDD wrong"?** Mostly no. No SpecWeave gate enforces test-first or unit tests. The one hard rule is that a task's `Test` must exit 0, and SpecWeave's ACs are human-approved intent, which the evidence says is where tests do earn their cost. Two leftovers did point agents toward unit tests: a hidden `TDD` default with 95% coverage, and template examples that paired every task with a new `*.test.ts`. **PR [#2019](https://github.com/anton-abyzov/specweave/pull/2019)** fixes both.
3. **Is SpecWeave mandatory in SpecWithCode?** No, and it is not under the hood. SpecWithCode never runs `specweave init`, never creates `.specweave/`, never installs sw-* skills, and has no dependency on the CLI. Its SpecWeave-aware features only switch on when they find SpecWeave files. What's missing is an explicit, honest choice, which is your idea of picking at project creation or folder pick. The design is below.

## The evidence

| Study | Setup | Result |
|---|---|---|
| Kun Chen, DeepSWE ban on agent tests (Oct 8) | DeepSWE v1.1, 111 tasks, 444 runs, Sonnet 5.5 high | Pass rate 65.3% with tests vs 66.2% without (not significant). Without tests: 6% less time (62.0h vs 58.0h), 9% less spend ($304 vs $278). Of 3,000+ agent tests, 65% were unit and 35% integration. Only 17 were e2e, so e2e is **untested**; his e2e eval is still running. Turning off existing tests on a 44-task subset: 59% vs 59%. |
| Kun Chen, TDD skill (Jun 9) | ProgramBench, 192 tasks, GPT 5.5 in Codex, obra/superpowers TDD skill | Pass rate dropped at every difficulty (easy 72.5→67.2, medium 56.6→53.1, hard 28.2→26.2), mean 52.4→48.8, p<0.0001. Cost rose 47-70%. |
| Böckeler, "TDD inside the agent loop" (martinfowler.com, Aug 10) | Three greenfield Python tasks, 2-6 runs per arm | No clear quality difference. TDD cost 3-8.5x the tokens and sometimes faked the red step. She stopped telling agents to write tests first. She recommends mutation testing, static analysis and human-approved scenarios instead. |
| Chen et al., arXiv 2602.07900 | SWE-bench Verified, six models | How many tests an agent writes doesn't change outcomes, only cost. Agents mostly use prints, not assertions. |
| TDFlow, arXiv 2510.23761 | SWE-bench Verified | Human-written tests: 94.3%. LLM-written tests: 68.0%. Test quality is the variable. |
| TDDev, arXiv 2605.17242 (ASE '26) | 20 web apps | Acceptance tests derived from requirements improved accuracy by 15.5-23.7 points with capable models. |

**The pattern:** a test helps when it carries intent a human approved, such as a spec, an AC, a curated suite or an acceptance scenario. A test the agent writes for itself is "a second copy of its own reading of the spec," so it adds cost without adding truth. E2E tests are the open question; Kun's next eval covers them.

**Caveats:** Kun's evals are self-published, his harness and statistics are not public, and the significance labels on time and spend are his. Böckeler's sample is tiny. Nobody has yet tested acceptance-level or e2e tests written by agents.

## SpecWeave's test model, audited

- **Gates** (`task done`, `verify`, `complete`): a task needs a command that exits 0, or written evidence. A Test can be any command, e2e included, and its type is never checked. Coverage is a warning only. No code checks for a red phase.
- **Leftovers**, fixed in PR #2019:
  - `DEFAULT_CONFIG.testing = { mode: 'TDD', coverage: 95/90/100 }` (`src/core/config/types.ts:881`). Init writes no mode, but anything that reads config through ConfigManager saw TDD.
  - The AGENTS.md template and sw-increment example tasks each pair a task with a new unit-test file. The example is what agents copy.
- **PR #2019 changes:**
  - The AGENTS.md rule now reads "Tests check ACs as users would (CLI, HTTP, UI, API); unit tests only if asked." It still fits the 3,300-character budget.
  - Example tasks use e2e Tests.
  - sw-do says not to write tests first.
  - sw-review flags tests that only restate the implementation.
  - The default test mode and coverage target are removed.
  - Checks: typecheck, skill lint and build are clean, and 824 related tests pass.
- **Not changed:** the "Test must exit 0" gate. It is the human-approved-intent check that the evidence supports.

## SpecWeave in SpecWithCode today

| Feature | Without `.specweave/` |
|---|---|
| Starter suggestions ("Continue increment", "pickup") | Hidden |
| Library artifacts | The folder's own files show; "Add artifact" is disabled |
| Plan | Native SQLite plan by default; SpecWeave only via "Connect SpecWeave source" |
| Handoff checkpoint | Skipped quietly |
| Coordinator prompt | Always says "...and SpecWeave where configured" (small leak) |
| `SPECWEAVE_STUDIO_THREAD_ID` env | Always set; inert unless the CLI's hooks are installed |

Detection has one bug: a bare `.specweave/` folder counts as SpecWeave, and stale ones exist in umbrella child repos.

## When SpecWeave is worth it

| Use SpecWeave | Skip it |
|---|---|
| Work spans sessions, agents, tools or accounts (handoff, pickup) | Single-session work, questions, small fixes |
| Several agents work in parallel and need claims on files | One agent, one thread |
| Specs and ACs should live in git and show up in PR review | Personal projects and scratch |
| A verify gate before release; GitHub/Jira/ADO sync | Repos you don't own (OSS clones, client repos) |

**Measured cost** (naming thread's audit, 58 Claude Code sessions, $2,632 at Opus 5.5 prices): SpecWeave is **$132, or 5.0%** of spend. The median share per session is 3.9%; in loop sessions the median is 4.5% and p90 9.8%.
- 57% of that cost is always-on text (AGENTS.md, CLAUDE.md, the skill listing).
- 35% is the turns spent on loop commands, about 21 per 6-task increment, or about $2.
- Only 8% is command output.

For comparison, this project's MEMORY.md costs $112 by itself. The audit's proposal fits this report:
- trim the always-on text,
- have `task done` auto-claim and `complete` run verify, which cuts about 21 turns to about 8,
- make the default unit a one-line intent closed by its PR,
- create an increment only for handoff, parallel agents, cross-repo work, or work still open at session end.

Together these bring SpecWeave to about 1.5-2% of spend. See [token-audit.md](/mnt/project-files/token-audit.md), [increments-rethink.md](/mnt/project-files/increments-rethink.md) and [specweave-simplification.md](/mnt/project-files/specweave-simplification.md).

SpecWithCode's native Plan already gives you ACs, tasks and evidence without any repo files, so it is the light tier between "off" and a full increment.

## Recommended design: an explicit, disk-based switch

Three independent designs were scored by three judges, and this one won unanimously (8.5-9 out of 10). It takes about 2.5 days.

- **Source of truth:** SpecWeave is on exactly when `.specweave/config.json` exists. There's no stored flag, so nothing can drift and no migration is needed. This also fixes the bare-folder bug.
- **New project (code kind):** an unchecked "Use SpecWeave" checkbox that lists the files it adds. When checked, `specweave init --quick --adapter <claude|codex>` runs after git init and lands in the first commit. If it fails, the project is still created and a toast gives the manual command.
- **Add existing folder:** if SpecWeave is detected, the dialog says "SpecWeave detected." Otherwise the same unchecked box appears. Studio never runs init silently on a repo you didn't create, and its changes are left uncommitted.
- **Project settings row:** shows on or off, with a "Set up SpecWeave" button. Off says "Studio's Plan and memory are used; nothing added to your repo."
- **Gated features:** starter suggestions, the coordinator prompt line (with the rule that small fixes get no increment), the Plan source, and Library artifacts.
- **Order:** ship PR #2019 first, so Studio-created SpecWeave projects don't inherit the TDD default.
- **Deferred:** a three-tier planning model (off / Studio plan / SpecWeave) and an "ignore SpecWeave here" override. Build them only if users ask.

## Sources

- Kun Chen: [DeepSWE post](https://x.com/kunchenguid/status/2108030810691629403), [follow-up](https://x.com/kunchenguid/status/2108244512808243470), [TDD post](https://x.com/kunchenguid/status/2064196342248030352), [OPINIONS.md](https://github.com/kunchenguid/kun/blob/main/OPINIONS.md), [ProgramBench write-up](https://github.com/kunchenguid/programbench-bench/blob/main/blog/does-tdd-help-coding-agents/index.md)
- [Böckeler, TDD inside the agent loop](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html); [Emily Bache's response](https://coding-is-like-cooking.info/2026/09/the-last-year-has-changed-everything-i-knew-about-tdd-after-20-years/)
- [arXiv 2602.07900](https://arxiv.org/abs/2602.07900), [2510.23761](https://arxiv.org/abs/2510.23761), [2605.17242](https://arxiv.org/abs/2605.17242), [2603.17973](https://arxiv.org/abs/2603.17973)
