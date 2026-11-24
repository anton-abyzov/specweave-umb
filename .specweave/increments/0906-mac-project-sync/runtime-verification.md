# Fleet runtime verification

Status: source provisioning, final source refresh, Git transport, project registration, code smoke tests and all six native coordinator/worker cycles passed.

## Provisioning evidence

46 canonical repositories were provisioned independently on each destination (92 checkouts). Full inspection verified exact origin, branch, commit, clean tracked/untracked state, configured upstream, and zero ahead/behind. The existing M1 project roots retained identical HEAD, status and diff hashes. M3 previously had no target roots.

M1 uses `~/Projects/sw-easychamp-fleet`, `~/Projects/github/sw-jobs-umb-fleet` and `~/Projects/github/specweave-umb-fleet`. M3 uses those canonical paths without `-fleet`. Each preserves `repositories/anton-abyzov/<repository>`.

The private manifest pins published source. Concurrent owner-held M4 changes were preserved; this is not a claim that every active M4 checkout is clean or merged. Credentials, live session databases, ignored build caches and dependencies were not copied. Historical LFS media and absolute development symlinks require separate preparation if needed.

Before updating, both installed 1.0.7 runtimes passed metadata-only inspection. Their native Codex profiles were authenticated with verified included routes; automatic credit, API-credit and reset use were disabled. Temporary scoped inspection sessions were revoked and global settings were unchanged. These metadata checks are not native execution proof.

Actual code smoke tests also passed on both Macs using Node 22.20.0: EasyChamp 26 tests for time zones and ticket QR handling; JobWeave 141 shared-package tests for schemas, scoring, stages and eligibility; SpecWeave 18 tests for one-file ledgers and nested-repository inspection. That is 185 tests per Mac, 370 total. Locked dependencies were installed locally with lifecycle scripts disabled. Test execution had outbound network access denied. Every tested checkout retained identical source state and lockfile hashes. These bounded tests do not represent full application or deployment acceptance.

## Folder and repository requirements

Both coordinator and worker native execution need a directory on the execution host. Git is optional for a general or personal project: managed project creation can create an empty folder. Code work needs the actual checkout and relevant nested repositories on that host, with dependencies prepared for the task.

Opening a remote environment in a browser does not relocate execution. Device handoff carries conversation context and pushed branch references, not uncommitted files or the complete repository tree. Prepare checkout can clone configured source, but does not recursively install an umbrella's nested repositories and dependencies.

Logical project matching uses normalized repository identity and path within that repository, so the M1 `-fleet` suffix does not change project identity. Each environment retains its own project ID.

Source evidence in `specweave-studio`: `ProjectCoordinatorService.ts` selects the root environment; `RuntimePolicy.ts` resolves the local working directory; `WorkspacePaths.ts` checks existence; `ManagedProjectFolders.ts` creates managed folders; `logicalProjectEnvironments.ts` matches repository identity; `deviceHandoff.ts` carries handoff context; `ProjectEnvironmentService.ts` prepares configured checkouts.

## Final source and registration

A single GitHub branch snapshot at 12:38 UTC identified six completed updates. The new Studio clones were replaced at merged main `34826e95eea37bf5979452773e6f5c75d6803556`, retaining the entire previous clones outside the umbrellas. Five other repositories advanced strictly by fast-forward to the frozen commits. All 46 copies on each Mac remained clean with upstream 0/0. Ordinary origin reads passed for all 92 repositories; push dry-runs passed for all six umbrella copies without writing a remote ref. Machine-specific SSH transport is configured only in the new clones; canonical HTTPS origins and global Git/SSH settings are preserved.

After that refresh, the EasyChamp and SpecWeave test suites passed again on both hosts (88 additional test executions). JobWeave source was unchanged from its 282 passing test executions across the two hosts.

Studio initially returned no repository identity because its Git remote parser does not accept Git's `(fetch) [blob:none]` suffix. Removing the redundant filter setting normalized remote output across all 92 new clones and restored identity recognition for the six registered project roots. Promisor flags remain where Git may still need historical objects; no missing object was discarded. The provisioning helper now omits partial-clone options when reading complete bundles. The failed full-object preflight and failed registration attempts remain in private evidence.

Each of the six new projects has the correct repository identity, goal, local directory, native Codex model defaults, disabled auto-pull and disabled auto-resume. Only these six projects have an explicit ask-before-provider-switch override; unrelated settings were checked unchanged. Temporary administration sessions were revoked.

## Native execution results

All three projects completed a real native Codex coordinator → local worker → automatic coordinator relay on both M1 and M3. Each accepted cycle contains three completed native runs, eight actual file/Git reads, full root and nested commit evidence, and the correct child-thread link. The automatic wake is bound to the server-created completion message, exact delegated task and observing coordinator run. No test supplied expected SHAs to the models. All six cycles retained clean source, their selected model and approval-required mode; temporary administration sessions were revoked.

| Project | Root branch and commit during native proof | Nested branch and commit |
|---|---|---|
| EasyChamp | develop `a417932316a63bab0999be0e1ba05318ed50433b` | ec-console develop `3bb2dd5e6c5d627e95969957410a3866a61c4916` |
| JobWeave | main `3be4019f51161064a5283f34926e4d39c808474d` | jobweave main `d1b1f864b0939dd41e1f4643116929bcf3973aac` |
| SpecWeave | main `61c74cb0864858a1a2eb5fbac1ca65b5afa6ec2e` | specweave develop `a7bd43cabd0b241cea9a3c7cd8bc22fbe3ba9c9a` |

Earlier failed verifier attempts remain retained. Corrections recognize the native shell wrapper, bind automatic completion to its actual message, and allow the shared root checkpoint scope to follow a new run while preserving historical runs and checkpoints. M1 JobWeave also stopped on the macOS Git launcher's temporary-cache warning; subsequent checks used the underlying Command Line Tools Git binary without broadening permissions. Interrupted requests were cancelled through the public API and verified quiescent before retrying. M3 JobWeave's already-completed cycle was revalidated from fresh records without another native run. M1 JobWeave has a separate final audit proving its old child remained unchanged and quiescent.

The private aggregate `~/.local/share/specweave/fleet/project-sync-20261013/receipt.json` links each successful coordinator and worker to retained evidence by SHA-256. Native source pins above describe execution time; the provisioning PR's final merge is copied afterward with a separate clean-checkout receipt. These are bounded source and orchestration checks, plus the documented product test suites; production application deployments and complete end-to-end product tests are outside this increment.
