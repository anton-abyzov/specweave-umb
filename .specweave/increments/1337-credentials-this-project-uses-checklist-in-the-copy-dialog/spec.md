# Credentials this project uses: checklist in the copy dialog

## Problem

Copy to another machine carries the project folder and the secret files inside it. It does not carry what the project needs from outside the folder: command-line sign-ins (GitHub, Azure, Cloudflare, Hetzner, npm, Google Cloud, Kubernetes contexts) and key files in the home folder. After a copy the person finds out one failed command at a time. The November 14, 2026 inventory of two real projects found 12 such items for one and 13 for the other, none of which the dialog mentions today (`.specweave/reports/threads/2026-11-14-easychamp-credentials-when-moving-to-another-mac-f3c816-b6415b.md`, `.specweave/reports/threads/2026-11-15-where-secrets-live-and-what-breaks-on-the-m5-aft-f3c816-f997d5.md`).

The copy dialog already checks the destination's tools (Git, Node.js, SpecWeave) with `machineTools.check` and lists vault-held secrets as hints. Nothing tells the person which sign-ins the project uses, or whether the destination has them.

## Scope

In:

- A credentials manifest, `.specweave/project/credentials.json`, that names each credential the project uses. It never holds a value.
- A scan of the source project that detects credentials by file names and tool markers only.
- Status probes on the destination from a closed catalog in the app's code: Ready, Not signed in, Tool missing, or Unknown.
- A "Credentials this project uses" section in the copy dialog with, per row, Sign in there or Skip. File credentials say they stay on the source and how to recreate them.

Out:

- Send file. Copying any credential file from the home folder, protected folder or not, is out (security review F-06). The existing rule stands: credentials do not move between machines; only project-folder secrets do.
- Running a sign-in on the destination for the person. The app shows the command; the person runs it.
- Keychain reads, a secrets-manager integration, creating per-machine tokens through provider APIs, and revocation lists. Follow-up increments.
- Windows-specific probes beyond what the same commands give.

## Acceptance Criteria

- [ ] AC-01: The security review of this design is recorded in `reports/security-review.md` with each finding's severity and outcome, by a reviewer from another model family, before any product code is committed. No finding rated high or critical is left open.
- [ ] AC-02: A manifest entry is a catalog id plus display text, and nothing in it can change a command. Decoding rejects unknown keys, more than 100 entries, a label over 120 characters, and control, bidirectional or format characters in any text. The sign-in command shown always comes from the catalog; a test with a hostile label proves it. Token-shaped strings (private key header, `ghp_`/`gho_`/`github_pat_`, `sk-`, `xox`, AWS access key id, JWT, long base64 or hex) are also refused as a lint, and the refusal names the entry and field, never the string.
- [ ] AC-03: Scanning a fixture project with an `azurerm` and an `hcloud` Terraform provider, a `wrangler.jsonc`, a GitHub remote, an `.npmrc` and a script naming `KUBECONFIG` returns rows for Azure, Hetzner Cloud, Cloudflare, GitHub, npm and Kubernetes, each with a catalog id and the project-relative file that caused it. The scan reads at most 256 KB of an allowlist of marker files that are never secret-classed, matches `.npmrc` and other secret-classed files by name only, reduces a remote URL to its host inside the function, skips vendored folders, and returns no file content, URL user info or absolute path.
- [ ] AC-04: A probe runs only a catalog command: the binary resolved to an absolute path outside the project and any project-writable folder, an argument list with no shell, the home folder as working directory, a 10 second timeout that ends the wait and stops the tool's whole process group, and an allowlisted environment (`PATH` of system and app-managed folders, never a folder under the home folder; `HOME`; locale) with no inherited `*_CONFIG_DIR`, `KUBECONFIG`, `NODE_OPTIONS`, `LD_*` or `DYLD_*`. Probes are local-only, except `gh auth status --hostname github.com`. npm, Wrangler and Docker have no probe and report `unknown`. Output is not kept: for some tools only whether anything was printed is noted. The RPC returns only the catalog id and one of `ready`, `not_signed_in`, `tool_missing`, `unknown`, and results are never logged, sent as telemetry or put in crash reports. An id outside the catalog is refused. No probe calls `security` or reads a Keychain file.
- [ ] AC-05: The probe RPC needs the destination's orchestration operate scope and the scan and save RPCs the source's filesystem read and write scopes; a caller without them is refused by the server, and the dialog shows no probe results for a machine it may not probe. One probe batch runs at a time per machine, results are cached for 60 seconds, and more than 6 batches a minute are refused.
- [ ] AC-06: The copy dialog shows "Credentials this project uses" with one row per credential: its name, why it is listed, and the destination's status. Sign in there shows the sign-in command for the destination's own platform, taken from the catalog, with Copy and Check again; label and command render as separate plain text. Skip marks the row as not needed and persists for the copy. Rows that are Ready sit under a closed "Ready" group.
- [ ] AC-07: No home-folder credential file is sent. A file credential's row says "Stays on {source}" with how to create or fetch one on the destination, and offers no Send file action. The folder copy still refuses every `~/` file except .NET user secrets on both machines; a test sends a catalog file path and sees it refused.
- [ ] AC-08: "Save list to project" writes the manifest on the source with the scan's rows and the person's skips: parents are opened without following links, the real path stays inside the project, the write is a temporary file plus rename, and a target that is a link is refused. A later copy reads it and merges it with a fresh scan.
- [ ] AC-09: The section renders correctly in light and dark at 1440 and 390 pixels wide in a headless fixture, with captures saved to `reports/`.

## Approach

The pattern is the existing machine readiness feature (`packages/contracts/src/machineTools.ts`, `apps/server/src/machineTools/`, `apps/web/src/components/machineTools/DestinationReadiness.tsx`): a contract, an RPC group guarded per environment, and a small web hook.

1. `packages/contracts/src/projectCredentials.ts`: the catalog ids, the manifest schema, scan and probe results, three RPCs (`projectCredentials.scan` and `projectCredentials.saveManifest` on the source, `projectCredentials.probe` on the destination) and their guarded scopes.
2. `apps/server/src/projectCredentials/catalog.ts`: the closed catalog. Per entry: id, label, kind (`login` or `file`), detection markers, the probe argument list, the sign-in command text, and for files the exact home-relative pattern and whether it may be sent.
3. `manifest.ts`: read, validate and write `.specweave/project/credentials.json`. `scan.ts`: walk file names with the folder copy's vendored-folder rules. `probe.ts`: run a catalog probe and reduce it to a status. `rpc.ts`: the handlers.
4. No transfer change. A test pins that the folder copy refuses catalog file paths.
5. Web: `apps/web/src/studio/projectCredentials.ts` (queries) and `apps/web/src/components/studio/CopyCredentialsChecklist.tsx`, mounted in the copy dialog beside the destination readiness card. Phrases added in every language file.

Key decisions and why:

- **The catalog is code, not data.** A manifest is a file in a repository, and a repository can come from anyone. If the manifest could name a command, cloning a project and opening the copy dialog would run it. So the manifest references catalog ids; anything else in it is display text.
- **Probe output never leaves the function.** `gh auth status` and `az account show` print account names and sometimes masked tokens. Only the exit code is read.
- **No widening of what moves.** The existing refusal lists (`PROTECTED_HOME_FOLDERS`, `isHomeSecretPathRefused`) already encode "reaching another machine goes through a grant, not a copied key". This feature points the person at a sign-in instead.
- **Findings from the design review** are in `reports/security-review.md`; every must-fix is an acceptance criterion above.

Rejected: free-form probe commands in the manifest; a "copy my whole `~/.kube`" option; opening a terminal on the destination and typing the command for the person (an interactive login needs that machine's browser or a device code, and the app should not type into a shell).

Risks: a probe that touches the network can be slow or hang, hence the timeout and `unknown`. A CLI may print a token to a terminal it thinks it has; probes run with no TTY and output piped to nowhere. `sourceService.ts` and `destinationService.ts` are at the 1,500-line limit, so new code goes in new files.

## Decisions

### Asked
- D-06 Send file (owner, November 14, 2026). Asked whether a later version may send a fixed list of home credential files, the owner answered not to pursue sending and to explain instead what was not copied and what access to set up on the other machine so the project works the same there. Built that way: each row names the home files that stayed behind (`keptIn`) and gives the destination's set-up command; nothing is sent.
### Defaulted (change any before sw-do)
- D-01 No home-folder credential file is sent in this increment, including a file-only kubeconfig, an hcloud token file or an App Store Connect key (security review F-06). The row says how to create or fetch one on the destination. The owner was asked on November 14, 2026 whether a later version may send a fixed list; a yes becomes its own increment with its own review.
- D-02 Sign in there shows and copies the command; it does not run it or open a terminal.
- D-03 The token-shape check on the manifest is a lint. The boundary is that a manifest can only name catalog ids (security review F-05).
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
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/probe.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/probe.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/rpc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/MachineHandoff.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/RpcAuthorization.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/projectCredentials/probe.test.ts apps/server/src/auth/RpcAuthorization.test.ts

### T-05 Home credential files stay refused
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/homeFiles.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/projectCredentials/homeFiles.test.ts

### T-06 Checklist in the copy dialog
- AC: AC-06, AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectCredentials.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CopyCredentialsChecklist.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CopyCredentialsChecklist.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyStepPanels.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.busy.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.cancel.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.held.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.retention.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.secretsGate.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.sourceChanges.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.wizard.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMachineHandoff.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/CopyCredentialsChecklist.test.tsx

### T-07 Headless fixture and captures
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/folder-copy/, .specweave/increments/1337-credentials-this-project-uses-checklist-in-the-copy-dialog/reports/ | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/folder-copy/vite.config.ts && STUDIO_PLAYWRIGHT_MODULE="$PWD/node_modules/.pnpm/playwright-core@1.60.0/node_modules/playwright-core" node apps/web/tests/folder-copy/credentials.mjs "$PWD/../../../.specweave/increments/1337-credentials-this-project-uses-checklist-in-the-copy-dialog/reports"

### T-08 Verify and close 1337
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09 | Files: .specweave/increments/1337-credentials-this-project-uses-checklist-in-the-copy-dialog/ | Test: specweave verify 1337
