# Handoff — no active increment
agent: codex-0881 · 2026-09-22T03:49:53.623Z · branch codex/0881-portable-project-hub @ d43b766a5 · tree: clean · redactions: 0
active claims: none

## Where I left off
Why: Manual UI acceptance required before increment closure
0881 portable project hub implemented, independently reviewed, globally installed as 2.3.0-rc.1 and verified. Draft PR #1953 stacked on #1952. Final verification: 7/7 ACs, 5/5 tasks, 16793 unit tests passed; real installed headless desktop/tablet/mobile and native skill refresh passed.
No active SpecWeave increment — git + notes handoff.
Gotcha: Source is /tmp/specweave-0881-root, branch codex/0881-portable-project-hub, HEAD d43b766a58ece6a5f294baa39cdb32c4b7d37115. Preserve unrelated dirty umbrella state and original nested checkout. Stable npm remains 2.2.3; locally installed release candidate is 2.3.0-rc.1.

## Done / Pending
_No task state available._

## Decisions
- Portable files and existing intent/evidence stores; native hosts own agent launch, schedules and permissions.
- Additive minor 2.3, no breaking migration. Rebased on published 2.2.3 gitHead a8b4fd0d4.

## Files touched
Working tree clean.

## Next steps
Get Anton acceptance of the project hub screenshots under reports/artifacts/installed. Then close increment 0881 from /Users/antonabyzov/Projects/github/specweave-umb using the normal sw:done flow; do not assume stable publication or merge is authorized by UI acceptance.

## Resume
1. Read this file; if the path does not exist on your machine, ask for it to be pasted.
2. `specweave task next` → claim → implement → `task done --run`.
3. Original transcript (optional): Claude Code: `claude -r <uuid>` · Codex: `codex resume <uuid>` · OpenCode: `opencode -s <id>`.

---
<!-- Doc format v2 -->