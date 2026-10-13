# Cross-machine continuation

A handoff needs three independent things: source code at known commits, portable task context, and a working destination environment. SSH connectivity alone proves none of them.

A Git repository is not mandatory for a personal or Scratch conversation: Studio can create a managed directory without initializing Git. A coordinator belongs to a registered project and executes in a real workspace directory. Continuing code work in these three projects requires their actual destination checkouts, including nested repositories and local dependencies; selecting a remote host does not copy them.

## Machine paths

M1 has independent project checkouts at `~/Projects/sw-easychamp-fleet`, `~/Projects/github/sw-jobs-umb-fleet`, and `~/Projects/github/specweave-umb-fleet`. M3 uses the same paths without `-fleet`. JobWeave's application is inside `repositories/anton-abyzov/jobweave` under its umbrella.

The original M1 `~/Projects/sw-easychamp` points to `anton-abyzov/easychamp-umb`, a different repository from the current `anton-abyzov/sw-easychamp` umbrella. The October 13 audit found 37 modified tracked files and 28 untracked files there. Reusing that path requires preserving the old directory, handling its linked worktree, promoting the prepared checkout, and updating Studio's project registration. An ordinary pull does not perform that migration.

Each destination has 46 clean, independent, non-shallow checkouts with no shared object alternates. Promisor metadata remains, so missing historical objects may require network access. These are working clones, not guaranteed complete offline archives.

The live continuation test exposed primary-branch-only fetch mappings left by the initial bounded clone. All 92 owned clones now use Git's normal `+refs/heads/*:refs/remotes/origin/*` mapping, preserving their origins, authentication configuration, current commits and working trees. This lets newly fetched feature branches acquire an upstream normally.

## What is published

The fleet baseline contains published, merged code. It does not include every active M4 edit. The current M4 audit found local modifications in 20 repositories. EasyChamp's umbrella had two local commits absent from the published develop branch; SpecWeave's umbrella had two commits unmerged to main. Do not sweep these into a handoff or commit them on another owner's behalf.

## Source and context transfer

Use a dedicated pushed feature branch for the work. Commit inside every changed nested repository first, then record each nested repository's exact commit and origin in the umbrella checkpoint. Moving the umbrella branch alone does not update nested repositories.

Record the actual source coordinator and worker result, decisions, completed steps, remaining step, exact source paths/commits and required local configuration. Context is a compact continuation brief, not the native model session or its running processes. Stop the source assignment before starting its replacement. Destination workers start fresh and must read the checkpoint and actual local source before continuing.

The normal SpecWeave CLI handoff pushes the source branch and an uncommitted snapshot to the shared `specweave-handoff` and `wip/<branch>` refs. `pickup <explicit increment>` can apply it to a clean compatible checkout. A dirty or diverged checkout requires reconciliation, never a forced reset. Concurrent handoffs share the latest-handoff pointer; explicit branch and commit identification matters.

For the bounded fleet proof, generate the CLI handoff with `--no-push`, commit the checkpoint to the owned feature branch, and push that explicit branch. This preserves other owners' shared latest-handoff pointer. Fetch and check out that exact transport commit at the destination. Read the explicit increment with `pickup <full increment id> --no-apply`; inspect its output before continuing. This is manual portable continuation, not a claim that Studio automatically synchronized Git.

## Shipped Studio boundary

SpecWithCode 1.0.9, source `51c49ab4603c17c87362e9700cd242b24ed83e2e`, exposes device continuation only after a real usage-limit failure. It chooses an eligible matching machine and stages a transcript in the destination coordinator composer. Sending is separate. There is no general idle-session target picker or Git SHA/dirty-tree guard in that release.

Its carried text includes the first and recent user/assistant messages, individually clipped to 1,500 characters with a total budget around 12,000. It does not transfer tool output, files, secrets, project memory, provider session state, task ownership, or worker records. The destination uses its own project settings and starts fresh workers. Preserve essential decisions and source references in durable checkpoint files.

## Local configuration

Git intentionally excludes `.env` and other private configuration. Transfer only required values into each application's actual configuration path over SSH, keep files private, and verify hashes without exposing values. Preserve richer machine-local configuration rather than overwriting it with an older subset. Do not copy runtime identity metadata or provider session databases.

The JobWeave audit found old umbrella-root environment files pointing to Supabase even though current application documentation uses Neon. Those URLs are not a safe local database configuration. Local development uses an isolated localhost database and fresh local-only application secrets; production migrations and background jobs are outside this setup.

The EasyChamp history contains absolute dependency symlinks, including a tracked Python virtual-environment symlink. Rebuild dependencies locally and invoke the host-local environment explicitly; do not follow a link into the preserved old checkout.

The October 13 local checks passed on both hosts: EasyChamp and JobWeave served their actual Next.js interfaces with HTTP 200 and application markers; SpecWeave compiled from source and its CLI launched. JobWeave's isolated PostgreSQL database on loopback port 45432 passed all repository migrations, pgvector operations and real Prisma model queries. Existing PostgreSQL on M3 port 5432 was preserved. Seven private configuration files per host were verified with mode 0600, Git-ignore status and hash readback.

These checks cover local startup and the isolated database. JobWeave uses the repository's auth-schema rehearsal stubs; a local Supabase Auth service was not installed. The checks do not establish production authentication, payments, email delivery, external AI-provider calls, or the entire EasyChamp microservice fleet. Test web processes and isolated database servers were stopped after verification.

Both hosts have a private reusable launcher at `~/.local/share/specweave/fleet/handoff-proof-20261013/local-dev-control.py`. Use Python 3 and the actual host name (`m1` or `m3`) followed by one action:

| Action | Result |
| --- | --- |
| `db-start` / `db-status` / `db-stop` | Control only the isolated JobWeave database on 45432 |
| `web-jobweave` | Run the JobWeave web app on 43802 after starting its database |
| `web-easychamp` | Run EasyChamp's console on 43801 |
| `specweave-version` | Launch the verified source CLI |

For example: `python3 ~/.local/share/specweave/fleet/handoff-proof-20261013/local-dev-control.py m1 db-start`. The launcher reads private configuration locally; commands do not contain credentials. Its private runbook records remaining feature-level limitations.

## Evidence

The October 13 continuation runs passed all six routes. Each project first ran a real M4 coordinator and worker, deliberately left package inspection as the next step, and transported that actual checkpoint to both hosts. Each destination coordinator launched one fresh local worker, read the checkpoint and matching local code, completed the deferred package inspection, and resumed automatically from the worker's completion. Nine cycles produced 27 completed native runs. No provider session or running worker moved between machines.

| Project | Tested transport root commit | Nested code commit | M1 | M3 |
| --- | --- | --- | --- | --- |
| EasyChamp | `73b0efcc9a873ff24ad2490b5dfe20810d8929f3` | `3bb2dd5e6c5d627e95969957410a3866a61c4916` | Passed | Passed |
| JobWeave | `7a4ac3cd1e5e44b5987a471242c6c8bc73e4ad24` | `d1b1f864b0939dd41e1f4643116929bcf3973aac` | Passed | Passed |
| SpecWeave | `a8c47fca7a1b2b4f1a25516c665cd8f4b528f574` | `a7bd43cabd0b241cea9a3c7cd8bc22fbe3ba9c9a` | Passed | Passed |

The source root commits precede the transport commits because the transport adds the actual checkpoint and handoff documents. The nested application code remains at the same recorded commit. Later proof-branch commits record the destination results; they are not substituted for the tested transport commits.

After the manual proof, all six destination project roots returned to their original published default branches. A fresh check verified all 92 repository commits, clean working trees, zero ahead/behind counts and normal fetch mappings. Completed proof branches remain available. Configuration hashes and all 14 private environment files were preserved. The three M4 proof project registrations were archived with their histories and folders intact; canonical JobWeave was registered at its existing M4 umbrella folder without starting a coordinator.

Earlier failed attempts remain in the private evidence: the first feature-branch checkout exposed the fetch-mapping defect; bounded test-harness retries corrected terminal completion acknowledgement and the macOS `cat` path. Failed attempts are not counted as successful routes. Successful receipts independently record clean source preservation, native command execution, actual carried context, server-triggered coordinator wake, retained checkpoint/package command output and revoked temporary control sessions.

Private receipts live under `~/.local/share/specweave/fleet/handoff-proof-20261013`. The source audit is verified with `python3 scripts/fleet/verify-handoff-evidence.py --phase audit`. Native continuation and environment phases require successful current receipts and fail when a route or runtime check is missing. Earlier 0906 destination-only cycles do not count as M4 handoff evidence.

## Product handoff work still open

Increment 0907 also tracks ordinary coordinator destination selection, guarded opt-in source transfer, a new Mac release and six subsequent routes through that app-owned flow. The manual proof above does not satisfy those product gates. Its current `--phase all` command covers audit, manual continuation and local environment only. Product acceptance must include an owned source code change, carried decisions and unfinished coding/test work, destination workers completing that work without receiving the answers again, and authoritative evidence of the app's own code transfer. The release owner coordinates one build/install and concrete manual UI acceptance.
