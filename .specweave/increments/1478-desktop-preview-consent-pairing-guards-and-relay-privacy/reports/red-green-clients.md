# 1478 red and green: clients lane (R5 to R10)

App checkout: `repositories/anton-abyzov/specwithcode`, branch `1474d-preview-pairing` from `origin/main` `2b7f17e8b`. Web tests run the way PR Gate does: `cd apps/web && node ../../node_modules/vite-plus/bin/vp test run --passWithNoTests --project unit <file>`.

## R5 `a5d86e6382` Push on a clean default branch only pushes (T-01, AC-05)

Test: `apps/web/src/components/GitActionsControl.logic.test.ts`, "resolveQuickAction only pushes when a clean ref is ahead" and "resolveQuickAction uses push-only on default ref when no upstream exists and commits are ahead". Both existing tests had encoded the defect (`action: "commit_push"` under the label "Push"); they now expect `push`.

Red (unmodified `GitActionsControl.logic.ts`):

```
 FAIL  |unit| src/components/GitActionsControl.logic.test.ts > when: on default ref without open PR > resolveQuickAction only pushes when a clean ref is ahead
AssertionError: expected { Object (label, disabled, ...) } to have deep property 'action' of 'push', but got 'commit_push'
      Tests  2 failed | 67 passed (69)
```

Green: `Test Files  2 passed (2)`, `Tests  81 passed (81)` (logic test plus `GitActionsControl.test.tsx`). The dirty default-branch case still returns `commit_push` ("returns commit and push when local changes exist" passes).

Commit: `9c13e587d`.

## R6 `a3708b5180` Concealed terminal text stays hidden under the block cursor (T-02, AC-06)

Test: `apps/web/src/terminal/ghostty/renderer.test.ts`, "keeps concealed text hidden under the block cursor and undecorated": a row of two concealed (SGR 8), underlined and struck-through cells with the block cursor on the first.

Red (unmodified `renderer.ts`), the cursor redraws the hidden character:

```
AssertionError: expected [ [ 'p', 4, 15, 7.2 ] ] to deeply equal []
      Tests  1 failed | 8 passed (9)
```

Red with only the cursor half fixed, the decoration loop still draws underline and strike over concealed cells:

```
AssertionError: expected [ [ 4, 18, 7.2, 1 ], …(3) ] to deeply equal []
```

Green: `Tests  9 passed (9)`; the whole `src/terminal/ghostty/` folder `Tests  95 passed (95)`. Visible text under the cursor still draws ("constrains text runs and cursor glyphs to their terminal cells" passes).

Commit: `4a3847f3c`.

## R7 `d6a28f4faa` SSH add without a target cannot become a route to a saved machine (T-03, AC-07)

Caller shape checked: the only caller is `apps/web/src/components/settings/ConnectionsSettings.tsx:2477` (`connectSavedBackendSshTarget`). Adding a route from a saved machine's settings passes `expectedEnvironmentId`; "Add machine" passes none. Startup reconnects do not go through `registerSsh`. The known-address check compares the SSH target key (`routes.ts:176`), not the forwarded port, so re-adding the same SSH host still passes.

Tests: `packages/client-runtime/src/connection/onboarding.test.ts`, "SSH onboarding and saved environments", run through the public `ConnectionOnboarding.registerSsh` with the real `EnvironmentRegistry` (`registry.testHarness.ts`) and a saved bearer environment:

- "refuses an SSH host that claims a saved environment it was not added to"
- "adds an SSH route to a saved environment when the add targets it" (must keep working)
- "saves a new SSH host without a target" (must keep working)

Red (unmodified `onboarding.ts`), the SSH route was added to the saved environment:

```
AssertionError: expected [ Array(2) ] to deeply equal [ BearerConnectionTarget{ …(4) } ]
      Tests  1 failed | 15 passed (16)
```

Green: `onboarding.test.ts` plus `registry.accountSaves.test.ts` `Tests  25 passed (25)`.

Commit: `bf70379c5`.

## R8 `ec844a3995` Relay attempt spans carry no machine label (T-03, AC-08)

Test: `packages/client-runtime/src/connection/supervisor.test.ts`, "keeps the machine label out of relay attempt spans" (relay tracer captured, connection to a relay target).

Red (unmodified `supervisor.ts`):

```
AssertionError: expected [ 'environment.id', …(5) ] to not include 'environment.label'
      Tests  1 failed | 89 passed (90)
```

Green: whole `src/connection` folder `Test Files  20 passed (20)`, `Tests  313 passed (313)`.

Not changed here (follow-up, not this group's file): `packages/shared/src/relayTracing.ts` still exports error messages with stacks. Local, non-relay spans and logs (`supervisor.ts` `connectionLost` span, log annotations) keep the label; they are not exported to the relay.

Commit: `e0995a392`.

## R9 `528c77fe83` Internal network host names never go to the favicon service (T-04, AC-09)

Test: `packages/shared/src/hostClassification.test.ts`, "keeps internal-network names away from the favicon service": `.lan`, `.localdomain`, `.corp`, `.home`, `.intranet`, `.private` hosts (with a bare TLD and a trailing dot) are not public; public domains that only contain those words (`lan.example.co.uk`, `corp.com`, `private.dev`, `home.page`) still are.

Red (unmodified `hostClassification.ts`):

```
AssertionError: nas.lan: expected true to be false // Object.is equality
      Tests  1 failed | 10 passed (11)
```

Green: `hostClassification` and `favicon` tests `Tests  41 passed (41)`; the web caller `apps/web/src/browser/browserTargetResolver.test.ts` `Tests  19 passed (19)`. Only `isPublicFaviconHost` changed; `isPrivateNetworkHost` (used by the server's direct endpoints and the web browser target resolver) is untouched.

Commit: `195a2c2b9`.

## R10 `97b8c9c7c2` Android pairing banner and cleartext guard read the machine the link pairs with (T-05, AC-10)

This machine (M5) has no Java runtime (`java -version`: "Unable to locate a Java Runtime"), so red and green come from the PR's Android CI job (`.github/workflows/android.yml`, `./gradlew --console=plain test`). The test and the fix are two commits so the job can show both: push `671e661e5` alone first (expected red), then `b9995b37d` (expected green).

`PairingLink.parse` (`apps/android/transport/src/main/kotlin/com/specwithcode/transport/PairingLink.kt`) is pure JVM: the `transport` module is `kotlin.jvm` and uses only okhttp's `HttpUrl`, so the JVM unit test exercises the real parser.

Test: `apps/android/app/src/test/kotlin/com/specwithcode/android/PairingInputTest.kt`, `hostedLinksShowAndCheckTheMachineTheyPairWith`:

- `https://my-mac.local/pair?host=https%3A%2F%2Fother.example&label=Mac#token=…` shows `other.example` (today: `my-mac.local`).
- `https://x.example/pair?host=http%3A%2F%2F203.0.113.5%3A3773#token=…` is cleartext and public cleartext (today: false, the outer scheme is https), also inside a `specwithcode://pair?link=` wrapper.
- Plain links keep today's answers (`m4.example.ts.net`, `10.0.0.2` cleartext but not public).

Expected red on unmodified `PairingInput.kt`: `assertEquals("other.example", …)` fails with `my-mac.local`. Red and green: pending CI.

Fix: `PairingInput.host` and `isCleartext` read the target through `PairingLink.parse(link).httpBase` (the address pairing uses), falling back to today's unwrap when the parser refuses the link. A `ws://` link now also counts as cleartext.

Commits: `671e661e5` (test), `b9995b37d` (fix).

## Review follow-ups

From the review of PR #909 at `aab3de9ed` (hold). Commits carry `Anton Abyzov <979819+anton-abyzov@users.noreply.github.com>` as author and committer.

### F1 Nested Android pairing links are judged by the machine pairing reaches (fail-open, AC-10)

Trace: the pairing screen's Connect sends `effectiveLink` = `PairingInput.unwrap(state.link)` (`PairingViewModel.kt:34`) to `MachinePairing.pair`, whose `ConnectAuthorizer.pair` runs `PairingLink.parse(link)` (`ConnectAuthorizer.kt:93`), which unwraps once more. The banner and the guard at `PairingViewModel.kt:103` read `state.link`. My first fix ran `PairingLink.parse(state.link)`: for a wrapper around a wrapper that parse refuses (a wrapper at depth 1 is invalid), the code fell back to the outer wrapper text, which is not `http://`, so `isPublicCleartext` was false while pairing reached the inner public http host.

Fix (`PairingInput.kt` only): `target(link)` is now `PairingLink.parse(unwrap(link))`, exactly what Connect does, so `host`, `isCleartext` and `isPublicCleartext` read the machine pairing sends the code to. When that parse refuses the link, pairing refuses it too and sends nothing.

Test: `PairingInputTest.nestedWrappersAreJudgedByTheMachinePairingReaches`: `specwithcode://pair?link=` around `studio://pair?pairingUrl=` around `http://203.0.113.5:3773/#token=…` must report host `203.0.113.5` and public cleartext; the same with a hosted `?host=http://203.0.113.5` link at the bottom; an https machine at the bottom stays not cleartext.

Expected red on `b9995b37d`: `assertEquals("203.0.113.5", …)` fails (host read from the outer wrapper). Red and green come from the Android CI job: push the test commit `60f9c6d5d` alone first, then the fix `cd53a9251`. No Java runtime on M5.

### F2 Relay spans never record machine names from connection errors (fail-open, AC-08)

Where labels reach a relay span: `TestConnectionDriver.prepare` and every other `Effect.fn` span inside the relay attempt record the failing error, whose `message` and `stack` carry the machine name: the compatibility refusal (`compatibility.ts:20`, `:25`, the server-reported `descriptor.label`), `driver.ts:151` ("did not answer on any saved route"), `supervisor.ts:388` (setup timeout), and the socket errors in `rpc/session.ts:334-337` (`connection.label`, the prepared label). The UI reads the same `message` (`presentation.ts:96`, the registry's `unsupportedReason`), so the text cannot change at the source without changing what the person sees.

Fix: `packages/client-runtime/src/connection/relaySpanPrivacy.ts` wraps the relay tracer for each connection (`supervisor.ts`, outside `withRelayClientTracing`). Spans exported through it get the target label, every label a host reported while connecting (`progress.prepared.label`) and any `machineLabel` a failure carries replaced by `<machine>` in failure messages, stacks and causes, string attributes and events. Connection errors gain an optional `machineLabel` (`model.ts`), set by the compatibility refusal. Error `detail` and `message`, local spans, logs and the UI are unchanged. Errors raised outside relay spans (`onboarding.ts:113`, `registry.ts:630`, `outdatedHostUpdate.ts`) are not exported to the relay.

Test: `supervisor.test.ts`, "keeps the machine label out of what relay spans record for $label", for a newer server's compatibility refusal (server label `Studio Mac Fixture`) and for a route failure naming the saved machine. It checks every relay span's name, attributes, events and failure text, and that `lastFailure.message` still names the machine.

Red (before the fix):

```
AssertionError: expected '{"name":"TestConnectionDriver.prepare…' not to contain 'Studio Mac Fixture'
AssertionError: expected '{"name":"TestConnectionDriver.prepare…' not to contain 'Test environment'
      Tests  2 failed | 1 passed | 89 skipped (92)
```

Green: `src/connection` `Test Files  20 passed (20)`, `Tests  315 passed (315)`; `tsc --noEmit` on `packages/client-runtime` shows no errors.

Commit: `ab8b44cab`.

### F3 Feature-branch route for a clean default-branch Push (regression report; not fixable in my files)

The route is not chosen in `GitActionsControl.logic.ts`: `checkoutFeatureBranchAndContinuePendingAction` (`GitActionsControl.tsx:1495`) replays the pending action with `featureBranch: true`, and the server refuses `featureBranch` for anything but commit actions (`GitManager.ts:2753`).

It did not work before this PR either. With the old `commit_push`, the server ran `runFeatureBranchStep` (`GitManager.ts:2697`), whose `prepareCommitContext` returns null on a clean tree (`GitVcsDriverCore.ts:2454`). It failed with "Cannot create a feature branch because there are no changes to commit." That case is covered by the existing server test "featureBranch returns error when worktree is clean" (`GitManager.test.ts:3505`). The only case where it went ahead was the defect itself: files written while the dialog was open were committed onto the new branch. Only the error text changed.

Change needed, owner of `GitManager.ts` (recommended):

- At `GitManager.ts:2753`, allow `input.featureBranch` when `input.action === "push"`.
- For that case, name the branch from the head commit's subject (`git log -1 --format=%s`, then `sanitizeFeatureBranchName` and `resolveAutoFeatureBranchName`), `createRef` and `switchRef`, run no commit step, and push the new branch.
- Add a server test: a clean default branch one commit ahead, `push` with `featureBranch: true`, yields a created branch, `commit.status` `skipped_not_requested` and a push of that branch, with a file written before the call left uncommitted.

Smaller alternative for the owner of `GitActionsControl.tsx`: at `:2226`, disable "Check out feature branch & continue" while `pendingDefaultBranchAction.includesCommit` is false.

No commit for F3.

## Round-2 follow-ups

From the round-2 review of PR #909 at `175445f1c` (hold). Author and committer `Anton Abyzov <979819+anton-abyzov@users.noreply.github.com>`.

### G1 Relay spans leave out a host's own refusal text and approval code (fail-open, AC-08)

A device-approval refusal is worded by the host (`teamRulesMessage`, with its current name and the approval code). Authorization fails before the supervisor learns a renamed host's name, so the wrapper had nothing to replace. Fix: mapped auth errors carry the host's words and the code as `hostText` (`errors.ts` `hostTextOf`, on the approval wait, the invalid-credential refusal and its DPoP variant; new optional field in `model.ts`). `relaySpanPrivacy.ts` also reads `deviceApprovalCode` and the raw refusal's `teamRulesMessage` and `approvalCode`, which covers spans that record the error before it is mapped. `detail`, `message` and `deviceApprovalCode` (what the person sees) are unchanged.

Test: `supervisor.test.ts` case "a device-approval refusal from a machine renamed since it was saved": the raw `EnvironmentAuthInvalidError` fails inside its own span, then is mapped. Neither `Studio Attic Fixture` nor `K7Q2PX9M` may appear in any relay span; `lastFailure.message` still names the machine.

Red: `expected '{"name":"RemoteEnvironmentAuthorizati…' not to contain 'Studio Attic Fixture'`, 1 failed. Green: `src/connection` `Tests  316 passed (316)`, `tsc` on `packages/client-runtime` clean. Commit `ae8cb8a54`.

### G2 Relay spans replace the longest machine name first (fail-open, AC-08)

Names are now deduplicated and replaced longest first. Test case "a refusal from a server whose name contains the saved label": saved `Mac`, server reports `Mac Upstairs`; neither `Mac` nor `Upstairs` may remain.

Red: `expected '{"name":"TestConnectionDriver.prepare…' not to contain 'Upstairs'`, 1 failed. Green: `src/connection` `Tests  317 passed (317)`. Commit `f6f45ade5`.

### G3 Android banner reads the host with the parser pairing uses (fail-open, AC-10)

`PairingInput.host` now reads the host with OkHttp's `HttpUrl` (what `PairingLink` validates with) instead of `java.net.URI`, which reads no host for `_svc.example.com`. `isPublicCleartext`, the guard for links from other apps (`PairingViewModel.kt:103`), now also refuses when no machine address can be read. That refusal shows the existing "unencrypted over the internet" text, which `PairingViewModel.kt` owns; a more exact message would need a change there.

Test: `PairingInputTest.theBannerReadsHostsTheWayPairingDoes`: `https://_svc.example.com/pair#token=…` (direct and as `?host=`) shows `_svc.example.com` and is allowed; `not a pairing link` has no host and is refused. Expected red on `cd53a9251`: `assertEquals("_svc.example.com", …)` gets null. Red and green come from the Android CI job: test `8df8474f1` first, fix `459944608` second. The existing `ViewModelTest` external-link cases (`attacker.example`, a LAN http link) keep their answers by inspection.

### G4 Split-DNS names under a public domain never go to the favicon service (fail-open, AC-09)

Any label equal to `corp`, `home`, `internal`, `intranet`, `lan`, `localdomain` or `private`, except in the last two labels, marks a host private. The last two are left out so a registrable domain spelled the same (`corp.com`, `private.dev`, `home.page`) stays public.

Test: "keeps split-DNS names under a public suffix away from the favicon service": `build.corp.example.com`, `jenkins.internal.example.org`, `home.example`, `lan.example.co.uk` and others are private; `example.com`, `homedepot.com`, `corporate.example.com`, `internals.example.com`, `lanes.example.com` and `privateer.example.com` stay public. The round-1 test listed `lan.example.co.uk` as public. Under the reviewer's rule it is a split-DNS name, so it moved to the private list and `lanes.example.co.uk` took its place as the public example.

Red: `build.corp.example.com: expected true to be false`, 1 failed. Green: `hostClassification` and `favicon` `Tests  42 passed (42)`; web `browserTargetResolver.test.ts` `Tests  19 passed (19)`. Commit `58154a340`.
