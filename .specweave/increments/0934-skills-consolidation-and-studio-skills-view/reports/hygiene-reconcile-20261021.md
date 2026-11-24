# 0934 T-10 hygiene reconciliation

Completed October 21, 2026. `vskill doctor --json` now exits 0 with zero findings. The prior three identical-copy findings and all redundant-link findings are resolved without deleting skill content.

## Scope and ownership

The original 0934 hygiene report identifies duplicate HyperFrames-family copies and redundant Cursor/Gemini/OpenCode links as its scope. The new copies and links were recreated by a later installer, principally October 20, 2026, 11:17 PM EDT, rather than being unique skills. The full three copied folders matched their canonical folders across 223 files, including references and scripts. All 13 affected skills were already present in the original inventory.

Project thread inventory showed no other running skill-maintenance task; no current 0934 task claimed these paths. `lsof +D` returned no open handles in the three copied folders immediately before mutation, and the process check found no active skill-installer command. Canonical folders and installer lock metadata were not edited. No process was stopped.

## Preserved changes

The full folders /Users/antonabyzov/.claude/skills/hyperframes, /Users/antonabyzov/.claude/skills/hyperframes-creative and /Users/antonabyzov/.claude/skills/media-use were moved intact into /Users/antonabyzov/.specweave/recovery/0934-hygiene-20261021/copies. Their former paths now resolve through symlinks to their unchanged counterparts under /Users/antonabyzov/.agents/skills.

The 39 redundant symlink objects were moved into /Users/antonabyzov/.specweave/recovery/0934-hygiene-20261021/links, retaining each original relative link text in the receipt and the saved link object. Their providers already discover the same canonical content through /Users/antonabyzov/.agents/skills. Full original paths, saved paths, canonical paths and hashes are recorded in /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/hygiene-reconcile-20261021-receipt.json. The backup root is mode 0700; its receipt is mode 0600.

First pass: 39 doctor findings became 3. After the copied folders became canonical links, Gemini's hyperframes, hyperframes-creative and media-use links also became redundant. Those three link objects were preserved in the same backup, then doctor returned 0 findings. The intermediate failure is retained in /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/hygiene-reconcile-20261021-doctor-intermediate.json. No test was weakened.

## Acceptance

The read-only check at /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/hygiene-reconcile-20261021-check.py verifies all 13 canonical inventories against their before-state, all 3 full backups against original inventories, all 39 saved link texts, the unchanged installer-lock SHA256, the new canonical symlink targets, and presence of all 11 candidates with recorded use. It passes.

Before and after doctor reports are /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/hygiene-reconcile-20261021-doctor-before.json and /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/hygiene-reconcile-20261021-doctor-after.json.

The 39 original symlinks can be restored from their receipt's target strings at their original paths. To restore a full copy, remove only its newly created symlink and move its preserved full folder back. This is a recovery procedure, not a requested rollback. Keep the private backup.

The social publication task T-09 remains separate and is not changed here. The old T-05 absence test for /Users/antonabyzov/.agents/skills/asc-build-lifecycle remains contradicted by its proven use; the skill remains installed under AC-06.

Verify and close 0934
