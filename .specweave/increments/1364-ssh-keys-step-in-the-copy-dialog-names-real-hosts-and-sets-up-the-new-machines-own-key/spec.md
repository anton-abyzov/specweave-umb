# SSH keys step in the copy dialog names real hosts and sets up the new machine's own key

## Problem

After a copy to another machine, the "SSH keys" row of "Credentials this project uses" does not help (Anton, November 16, 2026, on the M5). Its command is clipped and not runnable (`ssh-keygen -t ed25519 -C "$(hostname)" (then add the ...`), its check is a literal `ssh <host> true`, and it lists generic key names (`~/.ssh/id_ed25519`, `~/.ssh/id_rsa`) that are not the keys the source has.

For this project the row named two scripts. `vskill-platform/scanner-worker/deploy.sh` does use SSH, as `root` to two worker addresses written in the script. `specweave/contrib/subscription-switch/scripts/add-peer.sh` is a false match: the pattern read `"${ssh_opts[@]}"` as `user@host`, and that script uses its own fleet key. All Git remotes are HTTPS.

## Scope

In: the source reads where the project connects over SSH and the dialog shows those places with steps that run as written; the row is hidden when nothing needs a key; commands wrap.

Out: the app creating a key on the new machine, the app carrying or showing a public key, moving a private key, copying `~/.ssh/config`, the source writing `authorized_keys`, the app running the per-host check.

## Acceptance Criteria

- [x] AC-01: A script's written `user@host` destinations of `ssh`, `scp` and `rsync`, and Git remotes that use SSH, appear on the SSH row as targets; a host held in a variable is filled in only from one plain assignment in the same file, else named by the variable.
- [x] AC-02: A project whose only match was a Bash array expansion, or a command with its own `-i` key and `-F /dev/null`, gets no SSH row.
- [x] AC-03: A host, user, variable or source name that could change a copied command (leading hyphen, shell characters, quotes, non-ASCII, IPv6, direction marks) never reaches a command: refused in the scan, in the wire schema and in the dialog.
- [x] AC-04: The SSH steps show one check per target that runs as written (`ssh -o BatchMode=yes -- user@host true`), a key page link for GitHub, GitLab and Bitbucket, and no `<host>` placeholder when targets are known.
- [x] AC-05: Commands wrap instead of being clipped.
- [x] AC-06: Targets are labelled as unverified, private addresses are marked, and a dropped or capped target is said.
- [x] AC-07: No key, public or private, crosses the wire, and no new RPC or scope is added.

## Approach

Three options were drawn in `reports/options.html`: A better instructions only, B a new key per machine set up from the dialog (picked), C an opt-in move of the private key (rejected: a shared key cannot be revoked per machine, and choosing it means reading `~/.ssh/config`).

The design review by muse-wonder-1.0 (`reports/reviews/review-muse-wonder-1.0-1.md`) returned SHIP WITH CHANGES. Its five blockers all concern the app creating a key or carrying a public key between machines. This increment ships the smallest form it named, one step smaller: no key RPC at all.

Files: `packages/contracts/src/projectCredentials.ts` (target schema and patterns), `apps/server/src/projectCredentials/sshTargets.ts` (new), `scan.ts`, `catalog.ts`, `apps/web/src/components/studio/CopySshKeySteps.tsx` (new), `CopyCredentialCommand.tsx` (new, moved out of the checklist), `CopyCredentialsChecklist.tsx`.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 A new key per machine, never a moved private key (reversible; the reviewer agreed).
- D-02 Host and user names from project scripts leave the source under filesystem read, the scope that already reads those scripts.
- D-03 A written default stands in for positional parameters (`WORKERS=("$@")` then `WORKERS=(a b)`), shown with its variable name and the unverified label.
### Open
- D-04 "Create a key on {machine}" button and showing the public key in the dialog: needs an owner-only RPC, approval on the new machine, a fingerprint shown there, and proof the `.pub` matches a private key (review findings 1, 2, 5, 6). Auth change, so it needs Anton's yes.

## Review

- Reviewer: muse-wonder-1.0 on Muse Code, effort xhigh, security lens (named by Anton).

## Tasks

### T-01 Read SSH targets on the source
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/sshTargets.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/scan.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/catalog.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/projectCredentials.ts | Test: cd apps/server && npx vp test run src/projectCredentials

### T-02 SSH steps in the dialog
- AC: AC-03, AC-04, AC-05, AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CopySshKeySteps.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CopyCredentialCommand.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CopyCredentialsChecklist.tsx | Test: cd apps/web && npx vp test run src/components/studio/CopyCredentialsChecklist.test.tsx

### T-03 Code review at the exact head, green CI, merge, release request
- AC: AC-01 to AC-07 | Files: none | Test: gh pr checks 495
