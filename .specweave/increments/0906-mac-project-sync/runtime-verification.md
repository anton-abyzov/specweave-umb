# Fleet runtime verification

Status: source provisioning passed; native coordinator/worker execution pending the coordinated release.

## Provisioning evidence

46 canonical repositories were provisioned independently on each destination (92 checkouts). Full inspection verified exact origin, branch, commit, clean tracked/untracked state, configured upstream, and zero ahead/behind. The existing M1 project roots retained identical HEAD, status and diff hashes. M3 previously had no target roots.

M1 uses `~/Projects/sw-easychamp-fleet`, `~/Projects/github/sw-jobs-umb-fleet` and `~/Projects/github/specweave-umb-fleet`. M3 uses those canonical paths without `-fleet`. Each preserves `repositories/anton-abyzov/<repository>`.

The private manifest pins published source. Concurrent owner-held M4 changes were preserved; this is not a claim that every active M4 checkout is clean or merged. Credentials, live session databases, ignored build caches and dependencies were not copied. Historical LFS media and absolute development symlinks require separate preparation if needed.

Both installed 1.0.7 runtimes passed metadata-only inspection. Their native Codex profiles were authenticated with verified included routes; automatic credit, API-credit and reset use were disabled. Temporary scoped inspection sessions were revoked and global settings were unchanged. These metadata checks are not native execution proof.

Actual code smoke tests also passed on both Macs using Node 22.20.0: EasyChamp 26 tests for time zones and ticket QR handling; JobWeave 141 shared-package tests for schemas, scoring, stages and eligibility; SpecWeave 18 tests for one-file ledgers and nested-repository inspection. That is 185 tests per Mac, 370 total. Locked dependencies were installed locally with lifecycle scripts disabled. Test execution had outbound network access denied. Every tested checkout retained identical source state and lockfile hashes. These bounded tests do not represent full application or deployment acceptance.

## Folder and repository requirements

Both coordinator and worker native execution need a directory on the execution host. Git is optional for a general or personal project: managed project creation can create an empty folder. Code work needs the actual checkout and relevant nested repositories on that host, with dependencies prepared for the task.

Opening a remote environment in a browser does not relocate execution. Device handoff carries conversation context and pushed branch references, not uncommitted files or the complete repository tree. Prepare checkout can clone configured source, but does not recursively install an umbrella's nested repositories and dependencies.

Logical project matching uses normalized repository identity and path within that repository, so the M1 `-fleet` suffix does not change project identity. Each environment retains its own project ID.

Source evidence in `specweave-studio`: `ProjectCoordinatorService.ts` selects the root environment; `RuntimePolicy.ts` resolves the local working directory; `WorkspacePaths.ts` checks existence; `ManagedProjectFolders.ts` creates managed folders; `logicalProjectEnvironments.ts` matches repository identity; `deviceHandoff.ts` carries handoff context; `ProjectEnvironmentService.ts` prepares configured checkouts.

## Remaining acceptance

Install the coordinated audited release, register the three new local project roots per destination through supported APIs, and record six real coordinator → worker → automatic relay cycles. Each cycle must inspect real source, compare independently observed commits, retain run/provider evidence, and leave the source clean. No failed, simulated or metadata-only cycle counts as completed runtime verification.
