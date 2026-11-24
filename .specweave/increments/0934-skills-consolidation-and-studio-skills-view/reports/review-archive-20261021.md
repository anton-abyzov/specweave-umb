# Review: 0934 archive recovery and current acceptance

Verdict: fix first for the full increment; ship for the archive recovery. Risk: high until the acceptance failures are resolved. One current acceptance failure plus the pending publication repair.

Review context: independent fresh context. Reviewed October 21, 2026. No product or skill-tree edits, claims, final verify or close were performed. Installed and npm SpecWeave both reported 3.1.4.

## Archive recovery is correct

The method in /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/archive-scan-20261021.py:20 streams each resolved compressed file, records decompressor exit status and counts only tool-call arguments containing a candidate skill path. Matching-record JSON parse failures fail the scan. This is a conservative path-use audit, not a semantic read of every transcript. Catalogue/output-only mentions do not become uses.

Independent reconciliation verified 158 unique manifest paths and 158 unique real paths, exact manifest/result correspondence, current mounted-file sizes, all 158 successful stream exits, zero matching-record parse errors, and 6,130,100,518 decompressed bytes. A fresh metadata-only find through both scan roots found exactly the same 158 APFS compressed paths and no plain-file duplicates. No 6 GB rescan was needed. Current bounded live inventory has 2,786 files; the report's 2,763/2,763 is the historical snapshot, not a current live count.

A limited decompression of the decisive archive independently confirmed line 15 at October 7, 2026, 2:15 AM EDT: the tool explicitly read /Users/antonabyzov/.agents/skills/asc-id-resolver/SKILL.md. The restored file and /Users/antonabyzov/.claude/skills-trash-20261018/removed-0934/asc-id-resolver/SKILL.md both hash to 44c892e57e89c28448103e1294a190cfc48cc0b8f162bb34ec068ddad808ea60. All 11 used candidates remain present in /Users/antonabyzov/.agents/skills; all 12 zero-use candidates are absent from the three active skill trees. All 13 backup folders remain. The canonical restoration is discovered by Codex and Grok. No unsupported provider link was invented.

## [high] Current hygiene does not pass the full increment's acceptance

The checks at /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/spec.md:48 and /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/spec.md:51 require no bad-name/bad-description/identical-copy findings and a clean doctor. Fresh `vskill doctor --json` from /Users/antonabyzov/Projects/github/specweave-umb exits 1 with 39 findings: 3 identical-copy and 36 redundant-link. The three copies are recorded at /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/archive-scan-20261021-doctor.json:139, /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/archive-scan-20261021-doctor.json:151 and /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/archive-scan-20261021-doctor.json:163. They are hyperframes, hyperframes-creative and media-use between /Users/antonabyzov/.agents/skills and /Users/antonabyzov/.claude/skills. Hyperframes and media-use were in the original hygiene task.

These findings do not invalidate the archive restoration and may be later installer drift, but they cannot all be described as unrelated to 0934 or silently filtered out to claim current full acceptance. Resolve them with owner-safe preservation, or explicitly report the hygiene gate as still red. The prepared manifest retains both strict hygiene checks. No skill tree was modified by this review.

The old T-05 clause requiring /Users/antonabyzov/.agents/skills/asc-build-lifecycle to be absent contradicts AC-06 and proven use. The replacement acceptance checks all 11 used skills are present, including that skill. It does not delete a used skill to make the obsolete clause green.

## Independent checks passed

At SpecWithCode commit bc3fabf56778cb4fe90a64e485bc8ada97e2695d, the five focused app test files pass 54 tests under Node 22 and Vite+. The current attention script reports 116 rows, phantom 0 and attention 5 with all three providers healthy. The five findings are the three real copies above plus sw:do and sw:handoff version skew between 3.1.2 and 3.1.4.

Seven relevant vSkill lock hashes match the current disk content. All seven retained edited trigger descriptions contain Use when; html-report's description is 983 characters. The umbrella instructions are 8,272 bytes, and the SpecWeave block is 4,796 UTF-8 bytes, 1,199 tokens by the required approximation.

## Remaining acceptance

T-09 publication is owned by the parent and was not re-run here. The final command in /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/scoped-verify-20261021-command-manifest.json checks the registry's actual current version content, raw SHA256, source description, source commit, manifest entry and local lock hash. It deliberately does not equate the registry auto-version with the source's declared 1.3.1. The prior green report predates T-08/T-09 and is not final acceptance evidence.

The manifest contains exact scoped commands and environment isolation. It does not claim the aggregate umbrella suite, a fresh whole-product build, full coverage or installed-app visual acceptance.

Verify and close 0934
