# Copy started from another machine's window sends the secrets after one approval

## Problem

On November 16, 2026 at 05:50 UTC "Copy to another machine…" copied the specweave project from m4 to the M5 with "Copy everything". Both machines ran SpecWithCode 1.0.322, which has secrets included by default (PR 353, first in 1.0.292). The copy ended with "10 secret-like files (.env and similar) stayed on m4".

Evidence (m4 trace, records and session table, read on November 16):

- The copy was driven from the M5 app window, signed in to m4 through Connect. m4's own window made zero `machineHandoff.*` calls; m4's server saw `copyScopes`, `copyOffer` at 05:50:47Z and status polls, and no `copySecrets` call at all. The source record lists 10 secret files (7,222 bytes) and has no `secrets` field.
- A Connect session holds the standard scopes without `access:write` (`apps/server/src/cloud/CloudLink.ts:1818`). Sending a non-empty secret list needs `access:write` on the source, enforced by the server (`packages/contracts/src/clientRpcPermissions.ts:280-285`). The dialog therefore turned the Secrets box off and approved the copy `withoutSecrets`. At 1.0.322 the only notice was a disabled, unticked row with muted text.
- PR 494 (increment 1362, not in a release yet) made that row a warning and fixed the finish text. It kept the rule, so a copy started from the destination's window still cannot carry secrets.

The rule does not protect what it seems to. The same Connect session can already read any `.env` on the source through the terminal (`terminal:operate`), a full-access agent turn or the file read RPC, and it can approve `studio_file_transfer` secret cards one file at a time (`orchestration:operate`), which is how the 10 files were sent afterwards. What the plain path lacks, and the per-file path has, is two things: the receiving machine checks that the sender is the owner's own machine with full access, and the bytes are sealed to a key that machine made.

## Scope

In: a second way to stage a copy's secrets on the source, for a window without `access:write` there. The source sends the ticked secret files only sealed to a key that the destination machine itself hands the source over the fleet link, and only when the destination accepts the source as the owner's own machine with full access (the bar `studio_file_transfer` already sets). The dialog shows the one checked "Secrets: N files, included" line before the copy starts, with no per-file prompt and no second confirmation. A headless two-server end-to-end test with `.env` files at several depths.

Out: changing the Connect scope set; the plain path for a window with `access:write` (unchanged); sealing every file of the copy; authenticating the receiving key against an active relay (the same limit `fileTransfer/seal.ts` documents); a "send only what stayed" action after a finished copy; the drop paths, the Done state and the self-reopening dialog, which increment 1362's follow-up owns.

## Acceptance Criteria

- [ ] AC-01: A caller with the standard client scopes and no `access:write` can stage a copy's secret files on the source through `machineHandoff.copySealedSecrets`; `machineHandoff.copySecrets` with a non-empty list still refuses that caller. Another machine's coordinator key is refused on the new call.
- [ ] AC-02: The source stages them only after the copy's own destination machine (the environment id saved at `copyOffer`, never one the caller passes now) returned a receiving key over the fleet link. With no linked machine for that id, an unreachable or older destination, or a refusal there, nothing is staged and the error names the reason.
- [ ] AC-03: The destination hands out a receiving key only to the machine that offered that copy, under a worker grant that is not revoked, covers all projects, is owner "self" and has a full-access ceiling, for a copy that has not received its secrets yet. An agent running there under that grant is refused.
- [ ] AC-04: For a copy staged this way the source serves each secret file only as ciphertext sealed to that key; the transfer token alone never yields plaintext. The destination opens it with the key it kept, writes the file with mode 0600 at the same relative path, and drops the key when the secrets are in.
- [ ] AC-05: A headless test with two real services (source and destination, each with its own state folder, talking over HTTP) copies a project with `.env` files at the root, one, three and four levels deep, inside a nested repository and in a `~/` location, driven by a caller without `access:write`: every file arrives byte-identical with mode 0600, the bytes on the wire do not contain the secret values, and a copy approved without secrets or with no staging receives none.
- [ ] AC-06: In a window without `access:write` on the source, the setup form asks the source once whether secrets can travel sealed to the chosen machine. When they can, the Secrets line is ticked and reads "included", with "Sent sealed by {source} straight to {destination}." and no warning; unticking leaves them on the source. When they cannot, the line stays off with the reason and PR 494's warning.
- [ ] AC-07: "Copy everything" from such a window stages every ticked secret through the sealed call before approving, with the dialog open or closed (background watcher), and approves with the sent list so the destination fails loudly if one is missing. The finish text reports none left behind.
- [ ] AC-08: Each sealed staging is recorded on the source with the destination id, the paths and sizes, never contents (`secrets-sent.ndjson` as today), and the copy's record says the secrets were sealed.

## Approach

Server and contracts first, web after increment 1362's follow-up PR merges (it edits the same dialog files).

- `packages/contracts/src/folderCopy.ts`, `machineHandoffRpc.ts`, `clientRpcPermissions.ts`: two calls. `machineHandoff.copySecretsRoute {destinationEnvironmentId}` answers `{sealed, reason?}` (read plus `orchestration:operate`). `machineHandoff.copySealedSecrets` takes the same input as `copySecrets` and needs read plus `orchestration:operate`. `copySecrets` keeps `access:write`. A separate method keeps the rule in the scope table, where it can be read and tested, with no session plumbing in the handler.
- `apps/server/src/auth/RpcAuthorization.ts`: `copySealedSecrets` joins the owner-only methods, so a coordinator key is refused.
- `apps/server/src/fleet/folderTransfer/sealedSecrets.ts` (new): the `SecretsPeer` service. Live: resolves the copy's destination by environment id in `RemoteWorkers` and calls the destination's `studio_folder_copy_receive` with the new action `secretsKey` (or `secretsCheck` for the route question).
- `apps/server/src/fleet/folderTransfer/agentCopy.ts`, `apps/server/src/mcp/toolkits/project/handlers.ts`: the destination half of `secretsKey` and `secretsCheck`, with the owner "self" and full-access check.
- `destinationService.ts`: `secretsKey(operationId, sourceEnvironmentId)` makes an X25519 key (`fileTransfer/seal.ts`), keeps the private half in the copy's record, returns the public half; `receiveSecrets` opens sealed bodies and clears the key.
- `sourceService.ts`, `secrets.ts`, `sourceRoutes.ts`, `sourceClient.ts`: `approveSecrets` takes `sealTo`; `secretFile` seals when it is set; the route marks sealed bodies with their own content type.
- `MachineHandoff.ts`: the two service methods and their handlers.
- Web: `useSecretsGate.ts` learns the "sealed" sender from `copySecretsRoute`; `copySecretsPolicy.ts` sends through the sealed call for a denied window; `HandoffCopySetup.tsx` and `HandoffSecretsStep.tsx` show the line; the watcher follows the same policy helpers.

Risks: the fleet link from source to destination must exist (m4 can start work on the M5 today); where it does not, the copy behaves as after PR 494. An older destination answers the new action with an input error, read as "update needed". An older source has no route call: the window reads a failed call as "cannot".

Rejected: lowering `copySecrets` to `orchestration:operate` with only a destination check (the transfer token returns to the window, so a destination check alone binds nothing); an approval card on the source machine's own window (the person is at the destination; it would not be one flow); pushing each file through `studio_file_transfer` (a second secrets pipeline without the copy's conflict handling and `~/` rules).

## Decisions

### Asked
- none yet; Anton accepts before release (see Review)
### Defaulted (change any before sw-do)
- D-01 The ticked Secrets line is the one approval; no extra card → default. The window that ticks it holds the same scope that answers today's per-file secret cards, so a second click by the same session adds nothing. The server-side conditions (owner's own machine, full access, sealed to its key) are the gate.
- D-02 Sealed route only for a caller without `access:write`; the source's own window keeps the plain path → default. It keeps this change away from the path that works and from destinations with no fleet link.
- D-03 The receiving key is not signed → default. Same limit as file transfer: it stops anything that only reads traffic and anyone holding only the transfer token, not a relay that actively swaps keys.
- D-04 `copySealedSecrets` is owner-only (coordinator keys refused) → default.
### Open
- none

## Review

Reviewer: muse, model muse-wonder-1.0, effort xhigh, security lens, until "Verdict: ship". Auth-sensitive: Anton accepts before any release.

## Tasks

### T-01 Contracts and scope table for the sealed secrets calls
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/folderCopy.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/machineHandoffRpc.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/clientRpcPermissions.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/RpcAuthorization.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/RpcAuthorization.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/observability/RpcInstrumentation.ts | Test: cd ~/.specwithcode/m4/scratch/2026-11-16-copy-secrets-one-approval/specwithcode/apps/server && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/auth/RpcAuthorization.test.ts src/fleet/folderTransfer/twoServer.secrets.test.ts

### T-02 Destination hands out a receiving key and opens sealed secrets
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/agentCopy.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/secretsKey.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/destinationService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceClient.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/wire.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/MachineHandoff.ts | Test: cd ~/.specwithcode/m4/scratch/2026-11-16-copy-secrets-one-approval/specwithcode/apps/server && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/fleet/folderTransfer/twoServer.secrets.test.ts src/fleet/folderTransfer/agentCopy.test.ts

### T-03 Source stages sealed secrets through the fleet link
- AC: AC-02, AC-04, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sealedSecrets.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sealedSecretsPeer.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/secrets.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceRoutes.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/FolderCopyHandoff.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/MachineHandoff.ts, repositories/anton-abyzov/specwithcode/apps/server/src/server.ts | Test: cd ~/.specwithcode/m4/scratch/2026-11-16-copy-secrets-one-approval/specwithcode/apps/server && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/fleet/folderTransfer

### T-04 Two-server end-to-end proof with .env files at several depths
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/twoServer.secrets.test.ts | Test: cd ~/.specwithcode/m4/scratch/2026-11-16-copy-secrets-one-approval/specwithcode/apps/server && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/fleet/folderTransfer/twoServer.secrets.test.ts

### T-05 Dialog and watcher send secrets sealed from a window without access:write
- AC: AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/machineHandoff.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/copySecretsRoute.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/copySecretsRoute.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/copySecretsPolicy.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/useSecretsGate.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/useCopySecrets.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopySetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffSecretsStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyStepPanels.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopyWatcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.secretsGate.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopyWatcher.test.tsx | Test: cd ~/.specwithcode/m4/scratch/2026-11-16-copy-secrets-one-approval/specwithcode/apps/web && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run --project unit src/studio/copySecretsRoute.test.ts src/components/studio/HandoffFolderCopy.secretsGate.test.tsx src/components/studio/HandoffFolderCopyWatcher.test.tsx
