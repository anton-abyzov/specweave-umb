# Cross-machine continuation

A handoff needs three independent things: source code at known commits, portable task context, and a working destination environment. SSH connectivity alone proves none of them.

A Git repository is not mandatory for a personal or Scratch conversation: Studio can create a managed directory without initializing Git. A coordinator belongs to a registered project and executes in a real workspace directory. Continuing code work in these three projects requires their actual destination checkouts, including nested repositories and local dependencies; selecting a remote host does not copy them.

## Machine paths

M1 has independent project checkouts at `~/Projects/sw-easychamp-fleet`, `~/Projects/github/sw-jobs-umb-fleet`, and `~/Projects/github/specweave-umb-fleet`. M3 uses the same paths without `-fleet`. JobWeave's application is inside `repositories/anton-abyzov/jobweave` under its umbrella.

The original M1 `~/Projects/sw-easychamp` points to `anton-abyzov/easychamp-umb`, a different repository from the current `anton-abyzov/sw-easychamp` umbrella. The October 13 audit found 37 modified tracked files and 28 untracked files there. Reusing that path requires preserving the old directory, handling its linked worktree, promoting the prepared checkout, and updating Studio's project registration. An ordinary pull does not perform that migration.

Each destination has 46 clean, independent, non-shallow checkouts with no shared object alternates. Promisor metadata remains, so missing historical objects may require network access. These are working clones, not guaranteed complete offline archives.

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

## Evidence

Private receipts live under `~/.local/share/specweave/fleet/handoff-proof-20261013`. The source audit is verified with `python3 scripts/fleet/verify-handoff-evidence.py --phase audit`. Native continuation and environment phases require successful current receipts and fail when a route or runtime check is missing. Earlier 0906 destination-only cycles do not count as M4 handoff evidence.
