# 0981 follow-up repair review

Reviewed October 23, 2026. Verdict: PASS for the narrow source fix; installed acceptance remains separate.

Scope: `/Users/antonabyzov/.specwithcode/m4/worktrees/aide-reusable-tasks`, `origin/main` through commit `be2d473c08e72b84c654b5c0830af40e5be3e7b6` plus the working repair in `/Users/antonabyzov/.specwithcode/m4/worktrees/aide-reusable-tasks/apps/server/src/mcp/toolkits/project/handlers.ts` and `/Users/antonabyzov/.specwithcode/m4/worktrees/aide-reusable-tasks/apps/server/src/mcp/toolkits/project/workGrants.test.ts`.

The earlier high finding is resolved. The personal-kind guard reads the caller's work-grant origin before either named creation or workspace-path creation. It rejects both remote grant clients and locally executing threads inherited from remote work. It neither calls the create service nor returns private project settings on that path. Local callers retain the existing singleton/reuse behavior, and code-project creation retains its original behavior.

Dependency review: `readCaller` uses already-declared invocation/thread services. `WorkGrants` and `RemoteWorkers` are `Context.Reference` services with defaults, matching their existing use by adjacent project-list/read guards. The repair adds no undeclared mandatory service dependency.

The regression test covers title-only and explicit-path calls from a full-access grant client and its inherited remote worker. These would otherwise reach unimplemented create mocks, so receiving the asserted typed privacy refusal also demonstrates the guard runs before either create service. Existing named-handler coverage verifies personal kind propagation and unchanged omitted-kind behavior.

`git diff --check origin/main` passed. Parent reports 60 focused tests passed; this fresh-context review independently inspected source and coverage but did not rerun tests. No further actionable findings. No installed-runtime or full-increment closure claim is made.
