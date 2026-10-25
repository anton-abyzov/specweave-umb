# 0981 follow-up review

Reviewed October 23, 2026. Verdict: CHANGES REQUIRED.

Scope: commit `be2d473c08e72b84c654b5c0830af40e5be3e7b6`, two-file diff against `origin/main`, in `/Users/antonabyzov/.specwithcode/m4/worktrees/aide-reusable-tasks`.

## High: remote grant caller can read the existing private assistant through creation

At `/Users/antonabyzov/.specwithcode/m4/worktrees/aide-reusable-tasks/apps/server/src/mcp/toolkits/project/handlers.ts:597`, forwarding `kind: personal` makes `createNamedProject` return the existing assistant. The handler reads and returns that full project record at lines 608–621 without `workGrantOf` or `assertProjectInGrant`.

`/Users/antonabyzov/.specwithcode/m4/worktrees/aide-reusable-tasks/apps/server/src/mcp/McpToolAccess.ts:253` checks only the caller's full-access permission for this operation. Full-access does not imply local ownership: `/Users/antonabyzov/.specwithcode/m4/worktrees/aide-reusable-tasks/apps/server/src/mcp/toolkits/project/workGrants.test.ts:225` uses full-access remote work-grant clients. The adjacent project-read handler correctly calls the grant guard.

Therefore a remote grant client refused by `studio_project_read` can request `studio_project_create` with a title and `kind: personal` to receive the private assistant project, including its workspace settings. This violates 0981 AC-02. Refuse machine-origin callers before a personal creation/reuse operation; add a full-access grant-client regression test. A check only after creation could still create an assistant when none exists, so enforce the boundary before invoking the folder service.

## Other review conclusions

Local kind propagation is correct. Existing `/Users/antonabyzov/.specwithcode/m4/worktrees/aide-reusable-tasks/apps/server/src/project/ManagedProjectFolders.ts` handles existing and concurrent assistants without a new ID. The added mock assertion catches the original dropped-kind regression but cannot catch the grant bypass or prove installed behavior.

Static review and `git diff --check origin/main..HEAD` completed. No tests independently executed in this review; parent reported 53 passing focused tests before rebasing. No live database, browser, provider, project or settings operations performed. The saved installed 1.0.68 failures remain unresolved by this review.
