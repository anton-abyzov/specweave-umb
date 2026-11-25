# Repository, pull request and preview-browser safety

## Problem

The November 14 to 25 review of the last open upstream copy (increment 1474, wave 1, group C) found thirteen security rows in the app's repository identity, pull request, asset, preview-browser and scheduled-task code. Each lets a hostile remote, page, pull request or webhook caller read or write something it should not:

| Row | Upstream sha | Defect in ours |
|---|---|---|
| R1 | `6348824b45` | `gh auth token --hostname <remote host>` inherits `GH_ENTERPRISE_TOKEN` (`processRunner.ts:312` extends the parent env), so gh hands the enterprise token to any host a remote URL names; undoes the `GH_HOST` guard in `environmentToken` (`sourceControl/GitHubCredentials.ts:131`). |
| R2 | `f30874fef7` + `aab127d7fb` | `https://user:token@host/o/r` remotes enter `repositoryIdentity` verbatim (`project/RepositoryIdentityResolver.ts:82`); one-segment URL remotes keep userinfo and query in the canonical key (`packages/shared/src/git.ts:202`); webhook tasks keep the raw Cookie header (`scheduledTasks/webhookRoute.ts:95`). |
| R3 | `78cffe29ec` | A GitHub merge sends `expectedHeadOid` only when it rewrote the message (`pullRequest/GitHubPullRequestCli.ts:2779`), so a commit pushed after the person looked can be merged. |
| R4 | `8a3b1bdbe0` | Review-thread reply and resolve act on any thread id, from any pull request (`GitHubPullRequestCli.ts:2818`, `:2869`). |
| R5 | `30c5df0971` | A per-commit diff forwards any caller-named commit (`pullRequest/PullRequestService.ts:1877`, `:1899`), so the PR viewer reads commits outside the pull request. |
| R6 | `f1cd57bbf9` | Merge credit cleanup regexes backtrack polynomially on contributor-written text (`pullRequest/mergeMessage.ts:55`, `:74`, link pattern). |
| R7 | `ce884e3a9d` | A `request.frame()` throw inside a page `request` listener is uncaught and ends the server (`preview/ServerBrowser.ts:846`). |
| R8 | `4cff209428` + `e6e1ce70c8` | Preview Chrome is pinned to 157.0.8103.78, behind the 158 security builds (`preview/PreviewBrowser.ts:34`). |
| R9 | `bdcca0d703` + `b4744496f8` | A symlinked workspace preview file or HTML preview dependency is served by its target's type without checking the target (`assets/AssetAccess.ts:502`, `:1161`, `:1169`). |
| R10 | `e65a790ac5` | Host-returned asset and upload URLs may point at another origin (`packages/contracts/src/assets.ts:122`, `:162`). |
| R11 | `30f141e2e7` | A relay-delivered webhook run exports its spans to the relay tracer (`scheduledTasks/ScheduledTaskWebhookTrigger.ts:541`). |
| R12 | `4a3be943c9` | A refused scheduled dispatch stores `Cause.pretty` text (stack, nested causes) in `lastRunError` (`scheduledTasks/ScheduledTaskService.ts:1416`). |
| R13 | `6931171217` | Snapshot and snapshot-window reads serve a deleted thread (`orchestration-v2/ProjectionStore.ts:5622`, `:5824`). |
| R14 | `2dd323463a` (from group A, coordinator, November 24, 2026) | The pull request body's video tag source pattern scans attributes with `[^>]*`, quadratic on a long run of unclosed tags (`apps/web/src/components/pullRequest/pullRequestMarkdown.logic.ts:35`). |

## Scope

In: the thirteen rows above, including R3's client half (the head the person saw, carried from the web UI through `packages/contracts/src/pullRequest.ts` and client-runtime; added by the coordinator on November 24, 2026, as its own PR after the server half; an older client that sends no head keeps the server-half behaviour), rewritten in our own code, inside `apps/server/src/{sourceControl,project,pullRequest,assets,scheduledTasks,preview}/*`, `apps/server/src/orchestration-v2/ProjectionStore.ts`, `packages/shared/src/git.ts`, `packages/contracts/src/assets.ts` and their tests. Each row gets a test that fails on today's `main`.

Out (coordinator, November 24, 2026): to wave 2, the rest of `f30874fef7` (webhook signing secrets and URL tokens withheld from thread reads and search, the relay hook forwarder, the SSH tunnel) and a changed-file restriction for `diffFileContents` (upstream had one before `30c5df0971`). Skipped: the GitLab and Forgejo parts of `f30874fef7`, because we don't ship them. Not in scope: the check-rollup half of the lane note's `62a7108904` pairing.

Forwarded from the review rounds (November 24, 2026), fail-open and outside this increment's files or rows; not changed here, for the coordinator to route:
- `apps/server/src/http.ts:236`, `:316` (group A): the asset response reopens the file path after authorization, so a workspace writer who swaps the checked file for a symlink in between can get protected bytes served.
- `apps/server/src/assets/AssetAccess.ts:382`: a signed URL follows a workspace root that is replaced by a symlink after issuance; containment is then checked against the replacement folder.
- `apps/server/src/ws.ts:1058` (group A): a client reconnecting after a thread is deleted can replay retained message events from an earlier cursor, past the snapshot guards.
- `apps/server/src/pullRequest/ForgejoPullRequestProvider.ts:477`, `:604`: comment edits and numeric reactions use repository-wide comment ids without checking the pull request (pre-existing).
- `packages/client-runtime/src/state/pullRequests.ts` quick merge (PR #922 review round 2, disputed): against a server that does not advertise `pullRequestHeadPin`, the head a quick merge names is dropped and a push after the preparation read can still be merged. Identical to `main`, which sends no head (`pullRequests.ts:388` on `main`). Refusing quick merges against older servers would close it; that is a compatibility decision for the coordinator.
- `apps/server/src/scheduledTasks/ScheduledTaskStorage.ts:81` (PR #921 review round 5, disputed): `ScheduledTaskError.cause` travels on the wire, so a routine row that fails to decode returns the decoder's multi-line message inside it. Identical to `main`; `ScheduledTaskAdmission.ts:34` reads that cause, so sanitising it changes the error contract for every caller.
- `apps/server/src/pullRequest/PullRequestService.ts` pinned diff (PR #922 review round 6): a push and its revert inside one host read can pass both head checks with the other commit's patch. The server no longer caches a pinned read (`4ac498e8b`), but round 7 held it FIX FIRST: the client's diff query (60 s fresh, 5 min idle, unchanged from `main`) and the mounted code tab keep what that one read returned. Closing it needs per-host diff reads by commit range. Main is wider: its GitHub review sends no `commit_id`, so an approval lands on whatever head stands at submit. Round 8 (same head) accepted it as a residual narrower than main and said SHIP at `4ac498e8b`; #922 merged as `b12c354e7` on November 25, 2026. Wave 2: per-host diff reads by commit range.

Listed in the PR text, not blocking: a video tag with a quoted `<` before `src` falls back to Markdown (R14, fails closed); an encoded slash in a preview path (R9, rated low in review).

## Acceptance Criteria

- [ ] AC-01: The `gh auth token` call for any host runs with `GH_ENTERPRISE_TOKEN` and `GITHUB_ENTERPRISE_TOKEN` blanked; the host `GH_HOST` names still gets its enterprise token from the environment. The failed-check log call (`gh run view`) also blanks both unless the app's own credential supplies the token (review round 1). (R1)
- [ ] AC-02: A remote `https://u:tok@github.com/o/r` yields a repository identity whose `remoteUrl` fields hold no `u` or `tok`; SSH remotes keep their user. A one-segment URL remote `https://u:p@host/repo?x=1#f` keys as `https://host/repo`; credential-free remotes (`https://host/repo`, `ssh://git@host/repo`, `github.com/o/r` forms) key exactly as today. (R2)
- [ ] AC-03: A webhook request with `Cookie: a=b` reaches the task with no `cookie` header; other headers (signature, content type, `authorization`) still arrive. (R2)
- [ ] AC-04: Every GitHub merge or auto-merge mutation carries `expectedHeadOid` equal to the head read for that action, with or without a rewritten message; update-branch is unchanged. (R3, server half)
- [ ] AC-15: A merge, auto-merge or review sent from the pull request view carries the head SHA the person was looking at; the server refuses it with a "head moved" error when the pull request's head is no longer that commit, and a GitHub merge pins `expectedHeadOid` to it. A request without a head (older client) behaves as AC-04. (R3, client half)
- [ ] AC-16: Splitting a pull request body whose standalone `<video ...</video>` line holds 10,000 unclosed `<source ` tags takes under 200 ms; single- and multi-line video embeds still lift out their source. (R14)
- [ ] AC-05: Reply and resolve/unresolve on a review thread that belongs to another pull request fail with `GitHubSubjectScopeError` and send no mutation; on the pull request's own thread they still run. (R4)
- [ ] AC-06: `diff` and `diffFileContents` with a `commit` forward it only when it is a 7 to 64 character hex prefix matching exactly one commit the pull request lists, and forward that commit's full oid; anything else fails as not part of the change request. A diff without `commit` is unchanged. (R5)
- [ ] AC-07: `removeAgentCredits` and `isAgentCreditLine` finish in under 100 ms on 50,000-character adversarial inputs (spaces after a co-author prefix, `"\n "` runs, `[` runs); every existing credit and non-credit case keeps its answer. (R6)
- [ ] AC-08: The main-navigation predicate returns false when `request.frame()` throws, and the `requestfailed` path is guarded the same way. (R7)
- [ ] AC-09: The preview browser pins Chrome for Testing 158.0.8127.88 with byte counts and SHA-256 values computed from our own downloads for all six platforms. (R8)
- [ ] AC-10: An asset URL for a workspace preview file whose link target is not previewable (`a.png -> notes.env`) is refused at issue and at serve time; an HTML preview dependency whose resolved target is a non-asset or dot-path file (`logo.png -> src/server.ts`) is not served. Plain preview files, plain dependencies and in-workspace links to asset files still serve. Links into dot directories (for example pnpm's `node_modules/.pnpm`) are refused as dependencies, by design. (R9)
- [ ] AC-11: `AssetCreateUrlResult.relativeUrl` accepts only `/api/assets/<token>/<name>` and `AttachmentCreateUploadUrlResult.relativeUrl` only `/api/attachments/upload/<token>`; absolute, protocol-relative, `data:`, `file:` and dot-segment values fail to decode. URLs from the real asset and upload issuers decode. (R10)
- [ ] AC-12: A relay-delivered webhook's run spans (including the run's root span) go to the local tracer, not the relay tracer. (R11)
- [ ] AC-13: A refused or failed scheduled dispatch stores a one-line reason with no stack or nested cause text; team-rules, tracks and held reasons come through verbatim. (R12)
- [ ] AC-14: `getThreadSnapshot` and `getThreadSnapshotWindow` report a deleted thread as not found; live threads read as before. (R13)

## Approach

Four PRs from `origin/main`, one theme each, no upstream names in code, commits or PR text:

1. Credentials and repository identity (R1, R2): blank enterprise variables in `GitHubCredentials.fromGh`; strip URL logins in `RepositoryIdentityResolver.parseRemoteFetchUrls` with a new helper in `packages/shared/src/git.ts`; make the one-segment fallback of `normalizeGitRemoteUrl` drop password, query, fragment and non-SSH users; skip `cookie` in `webhookRoute`.
2. Pull request safety (R3 server half, R4, R5, R6): always send `expectedHeadOid` on merge; add the review-thread type to the subject scope query (aliased field) and check it before reply/resolve; a small `listedCommit` helper in a new `pullRequest/listedCommit.ts` used by the exported `diff` and `diffFileContents`; rewrite trailer parsing with `lastIndexOf` and trailing-blank trimming with a loop.
3. Preview and assets (R7 to R10): exported `isMainFrameNavigation` with try/catch; Chrome 158 pin; canonical-target type checks at issue and serve, dependency rule on the resolved path; route patterns in the asset contracts.
4. Scheduled tasks and thread reads (R11 to R13): `withLocalTracing` outside the delivery span; one-line dispatch reason helper; deleted-thread check in both snapshot reads.

Three files already exceed 1,500 lines (`GitHubPullRequestCli.ts`, `PullRequestService.ts`, `ProjectionStore.ts`); additions there stay to a few lines and new logic goes in new small modules.

Risks: the scope query change is only fixture-tested unless a read-only `gh api graphql` run confirms GitHub accepts it. The commit restriction depends on each provider listing full commit oids in activity.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 R3 server half ships in PR 2; the client half ships as its own PR after it (coordinator, November 24, 2026).
- D-04 The HTML preview dependency rule is applied below the page's own folder, not from the workspace root, so reports under dot folders keep working (accepted by the coordinator, November 24, 2026).
- D-02 Webhook headers drop only `cookie`; `authorization` stays because signature schemes and templates may read it.
- D-03 The one-segment key keeps its scheme (`https://host/repo`) so credential-free keys stay byte-identical.
### Open
- none

## Tasks

### T-01 Enterprise GitHub token stays with GH_HOST
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/sourceControl/GitHubCredentials.ts, repositories/anton-abyzov/specwithcode/apps/server/src/sourceControl/GitHubCredentials.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/pullRequest/checkLogEnvironment.ts, repositories/anton-abyzov/specwithcode/apps/server/src/pullRequest/checkLogEnvironment.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/pullRequest/GitHubPullRequestCli.ts | Test: vp test run apps/server/src/sourceControl/GitHubCredentials.test.ts apps/server/src/pullRequest/checkLogEnvironment.test.ts

### T-02 Remote logins and cookies stay out of identity and webhook input
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/RepositoryIdentityResolver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/RepositoryIdentityResolver.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/git.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/git.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/webhookRoute.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/webhookRoute.test.ts | Test: vp test run packages/shared/src/git.test.ts apps/server/src/project/RepositoryIdentityResolver.test.ts apps/server/src/scheduledTasks/webhookRoute.test.ts

### T-03 Merges pin the head; review threads stay on their pull request
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/pullRequest/GitHubPullRequestCli.ts, repositories/anton-abyzov/specwithcode/apps/server/src/pullRequest/gitHubPullRequestJson.ts, repositories/anton-abyzov/specwithcode/apps/server/src/pullRequest/GitHubPullRequestProvider.ts, repositories/anton-abyzov/specwithcode/apps/server/src/pullRequest/GitHubPullRequestCli.test.ts | Test: vp test run apps/server/src/pullRequest/GitHubPullRequestCli.test.ts

### T-04 Commit diffs only for listed commits
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/pullRequest/listedCommit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/pullRequest/PullRequestService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/pullRequest/PullRequestService.test.ts | Test: vp test run apps/server/src/pullRequest/PullRequestService.test.ts

### T-05 Bounded merge credit parsing
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/pullRequest/mergeMessage.ts, repositories/anton-abyzov/specwithcode/apps/server/src/pullRequest/mergeMessage.test.ts | Test: vp test run apps/server/src/pullRequest/mergeMessage.test.ts

### T-06 Preview browser survives frameless requests; Chrome 158
- AC: AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/preview/ServerBrowser.ts, repositories/anton-abyzov/specwithcode/apps/server/src/preview/mainFrameNavigation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/preview/mainFrameNavigation.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/preview/PreviewBrowser.ts, repositories/anton-abyzov/specwithcode/apps/server/src/preview/PreviewBrowser.test.ts | Test: vp test run apps/server/src/preview/mainFrameNavigation.test.ts apps/server/src/preview/PreviewBrowser.test.ts

### T-07 Linked preview files and dependencies checked at their target
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/assets/AssetAccess.ts, repositories/anton-abyzov/specwithcode/apps/server/src/assets/AssetAccess.test.ts | Test: vp test run apps/server/src/assets/AssetAccess.test.ts

### T-08 Asset and upload URLs validated at the RPC boundary
- AC: AC-11 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/assets.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/assets.test.ts | Test: vp test run packages/contracts/src/assets.test.ts packages/client-runtime/src/state/assets.test.ts packages/client-runtime/src/state/attachments.test.ts apps/server/src/assets/AttachmentUpload.test.ts

### T-09 Webhook runs trace locally; short dispatch reasons; deleted threads read as missing
- AC: AC-12, AC-13, AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskWebhookTrigger.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/dispatchFailureReason.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskService.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskTurnFailure.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskFollow.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskStorage.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskOccurrence.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskService.turnFailure.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProjectionStore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProjectionStore.test.ts | Test: vp test run apps/server/src/scheduledTasks/ScheduledTaskService.test.ts apps/server/src/orchestration-v2/ProjectionStore.test.ts

### T-10 Merges and reviews pinned to the head the person saw; bounded video tag scan
- AC: AC-15, AC-16 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/pullRequest.ts, repositories/anton-abyzov/specwithcode/apps/server/src/pullRequest/*, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/pullRequests.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/pullRequest/*, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadDetailsPrRow.tsx, repositories/anton-abyzov/specwithcode/packages/contracts/src/environment.ts, repositories/anton-abyzov/specwithcode/apps/server/src/environment/ServerEnvironment.ts | Test: vp test run apps/server/src/pullRequest/PullRequestService.test.ts packages/client-runtime/src/state/pullRequests.test.ts apps/web/src/components/pullRequest/pullRequestHeadPin.test.ts apps/web/src/components/pullRequest/pullRequestMarkdown.logic.test.ts
