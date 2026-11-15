# Credentials this project uses: checklist in the copy dialog

## Problem

Copy to another machine carries the project folder and the secret files inside it. It does not carry what the project needs from outside the folder: command-line sign-ins (GitHub, Azure, Cloudflare, Hetzner, npm, Google Cloud, Kubernetes contexts) and key files in the home folder. After a copy the person finds out one failed command at a time. The November 14, 2026 inventory of two real projects found 12 such items for one and 13 for the other, none of which the dialog mentions today (`.specweave/reports/threads/2026-11-14-easychamp-credentials-when-moving-to-another-mac-f3c816-b6415b.md`, `.specweave/reports/threads/2026-11-15-where-secrets-live-and-what-breaks-on-the-m5-aft-f3c816-f997d5.md`).

The copy dialog already checks the destination's tools (Git, Node.js, SpecWeave) with `machineTools.check` and lists vault-held secrets as hints. Nothing tells the person which sign-ins the project uses, or whether the destination has them.

## Scope

In:

- A credentials manifest, `.specweave/project/credentials.json`, that names each credential the project uses. It never holds a value.
- A scan of the source project that detects credentials by file names and tool markers only.
- Status probes on the destination from a closed catalog in the app's code: Ready, Not signed in, Tool missing, or Unknown.
- A "Credentials this project uses" section in the copy dialog with, per row, Sign in there, Send file (file credentials the catalog allows), or Skip.

Out:

- Copying any file from a protected home folder (`~/.ssh`, `~/.kube`, `~/.azure`, `~/.aws`, `~/.docker`, `~/.config/gcloud`, `~/.config/gh`, Wrangler's token, `~/.npmrc`). The existing rule stands: those never move between machines.
- Running a sign-in on the destination for the person. The app shows the command; the person runs it.
- Keychain reads, a secrets-manager integration, creating per-machine tokens through provider APIs, and revocation lists. Follow-up increments.
- Windows-specific probes beyond what the same commands give.

## Acceptance Criteria

- [ ] AC-01: The security review of this design is recorded in `reports/security-review.md` with each finding's severity and outcome, by a reviewer from another model family, before any product code is committed. No finding rated high or critical is left open.
- [ ] AC-02: A manifest that holds a value is refused. Decoding rejects unknown keys, any field longer than its bound, a login command outside the catalog's own text, and any string that matches a token shape (private key header, `ghp_`/`gho_`/`github_pat_`, `sk-`, `xox`, AWS access key id, JWT, 32 or more characters of high-entropy base64 or hex). The refusal names the entry and field, never the string.
- [ ] AC-03: Scanning a fixture project with an `azurerm` and an `hcloud` Terraform provider, a `wrangler.jsonc`, a GitHub remote, an `.npmrc` with a registry line and a script naming `KUBECONFIG` returns rows for Azure, Hetzner Cloud, Cloudflare, GitHub, npm and Kubernetes, each with the file that caused it. The scan reads tracked and untracked file names and at most 256 KB of each marker file, skips vendored folders, never reads a file classed as a secret, and returns no file content.
- [ ] AC-04: A probe runs only a catalog command, as an argument list with no shell, with a timeout of 10 seconds and a reduced environment. Its output is discarded: the RPC returns only the catalog id and one of `ready`, `not_signed_in`, `tool_missing`, `unknown`. A request naming an id outside the catalog is refused. No probe calls `security` or reads a Keychain file.
- [ ] AC-05: The probe RPC is guarded on the destination: a caller without the destination's environment scope is refused by the server, and the dialog shows no probe results for a machine it may not probe.
- [ ] AC-06: The copy dialog shows "Credentials this project uses" with one row per credential: its name, why it is listed, and the destination's status. Sign in there shows that machine's sign-in command with Copy and Check again. Skip marks the row as not needed and persists for the copy. Rows that are Ready sit under a closed "Ready" group.
- [ ] AC-07: Send file is offered only for a home file the catalog names as sendable. It travels through the folder copy's existing secret step (same encryption, mode 0600, never overwriting a different file) and starts unticked. A home file in a refused location shows "Stays on {source}" with what to do instead, and the server refuses it on both machines whatever the client sends.
- [ ] AC-08: "Save list to project" writes the manifest on the source with the scan's rows and the person's skips. A later copy reads it and merges it with a fresh scan.
- [ ] AC-09: The section renders correctly in light and dark at 1440 and 390 pixels wide in a headless fixture, with captures saved to `reports/`.

## Approach

The pattern is the existing machine readiness feature (`packages/contracts/src/machineTools.ts`, `apps/server/src/machineTools/`, `apps/web/src/components/machineTools/DestinationReadiness.tsx`): a contract, an RPC group guarded per environment, and a small web hook.

1. `packages/contracts/src/projectCredentials.ts`: the catalog ids, the manifest schema, scan and probe results, three RPCs (`projectCredentials.scan` and `projectCredentials.saveManifest` on the source, `projectCredentials.probe` on the destination) and their guarded scopes.
2. `apps/server/src/projectCredentials/catalog.ts`: the closed catalog. Per entry: id, label, kind (`login` or `file`), detection markers, the probe argument list, the sign-in command text, and for files the exact home-relative pattern and whether it may be sent.
3. `manifest.ts`: read, validate and write `.specweave/project/credentials.json`. `scan.ts`: walk file names with the folder copy's vendored-folder rules. `probe.ts`: run a catalog probe and reduce it to a status. `rpc.ts`: the handlers.
4. Send file: `folderTransfer/secretLocations.ts` gains a catalog check beside `isDotnetUserSecretsFile`, so a sendable catalog file found on the source is offered as a `~/` secret file. The destination applies the same check before writing. No new transfer path.
5. Web: `apps/web/src/studio/projectCredentials.ts` (queries) and `apps/web/src/components/studio/CopyCredentialsChecklist.tsx`, mounted in the copy dialog beside the destination readiness card. Phrases added in every language file.

Key decisions and why:

- **The catalog is code, not data.** A manifest is a file in a repository, and a repository can come from anyone. If the manifest could name a command, cloning a project and opening the copy dialog would run it. So the manifest references catalog ids; anything else in it is display text.
- **Probe output never leaves the function.** `gh auth status` and `az account show` print account names and sometimes masked tokens. Only the exit code is read.
- **No widening of what moves.** The existing refusal lists (`PROTECTED_HOME_FOLDERS`, `isHomeSecretPathRefused`) already encode "reaching another machine goes through a grant, not a copied key". This feature points the person at a sign-in instead.
- **Sendable files are a closed list of exact patterns**, because a denylist of dangerous home paths can never be complete (`~/.gradle/init.d`, `~/.config/systemd/user`, editor configs). First entries: `~/.config/hcloud/cli.toml` and `~/.appstoreconnect/private_keys/AuthKey_*.p8`.

Rejected: free-form probe commands in the manifest; a "copy my whole `~/.kube`" option; opening a terminal on the destination and typing the command for the person (an interactive login needs that machine's browser or a device code, and the app should not type into a shell).

Risks: a probe that touches the network can be slow or hang, hence the timeout and `unknown`. A CLI may print a token to a terminal it thinks it has; probes run with no TTY and output piped to nowhere. `sourceService.ts` and `destinationService.ts` are at the 1,500-line limit, so new code goes in new files.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Files in protected home folders are never sent, including a file-only kubeconfig. The row says to fetch or recreate it on the destination. Reversible by adding a catalog pattern, after its own review.
- D-02 Sign in there shows and copies the command; it does not run it or open a terminal.
- D-03 Sendable home files start unticked, unlike in-folder secrets (which start ticked per 1325): a per-machine token is the better default.
- D-04 Probes run when the destination is chosen and on Check again, never on a timer.
- D-05 Docker registry sign-ins are listed with status Unknown: their state is in the Keychain or in `~/.docker/config.json`, which the app does not read.
### Open
- none

## Review

Reviewer from another model family than the author for both the design review (T-01) and the ship review.

## Tasks

### T-01 Security review of the design
- AC: AC-01 | Files: .specweave/increments/1337-credentials-this-project-uses-checklist-in-the-copy-dialog/reports/security-review.md, .specweave/increments/1337-credentials-this-project-uses-checklist-in-the-copy-dialog/spec.md | Test: test -s .specweave/increments/1337-credentials-this-project-uses-checklist-in-the-copy-dialog/reports/security-review.md && ! grep -Eq '^\| *(high|critical) *\|.*\| *open *\|' .specweave/increments/1337-credentials-this-project-uses-checklist-in-the-copy-dialog/reports/security-review.md

### T-02 Contract, catalog and manifest
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/projectCredentials.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/projectCredentials.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/index.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/rpc.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/clientRpcPermissions.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/catalog.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/manifest.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/manifest.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/contracts/src/projectCredentials.test.ts apps/server/src/projectCredentials/manifest.test.ts

### T-03 Source scan and save manifest
- AC: AC-03, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/scan.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/scan.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/projectCredentials/scan.test.ts

### T-04 Destination probes and guarded RPCs
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/probe.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/probe.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/rpc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/rpc.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/server.ts, repositories/anton-abyzov/specwithcode/apps/server/src/ws.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/projectCredentials/probe.test.ts apps/server/src/projectCredentials/rpc.test.ts packages/contracts/src/clientRpcPermissions.test.ts

### T-05 Send file through the existing secret step
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/secretLocations.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/secretLocations.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceSecrets.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/secrets.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/folderTransfer/secretLocations.test.ts apps/server/src/fleet/folderTransfer/secrets.test.ts

### T-06 Checklist in the copy dialog
- AC: AC-06, AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectCredentials.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CopyCredentialsChecklist.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CopyCredentialsChecklist.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyStepPanels.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/CopyCredentialsChecklist.test.tsx

### T-07 Headless fixture and captures
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/folder-copy/, .specweave/increments/1337-credentials-this-project-uses-checklist-in-the-copy-dialog/reports/ | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/folder-copy/vite.config.ts && node apps/web/tests/folder-copy/verify.mjs

### T-08 Verify and close 1337
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09 | Files: .specweave/increments/1337-credentials-this-project-uses-checklist-in-the-copy-dialog/ | Test: specweave verify 1337
