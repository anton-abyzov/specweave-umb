# Review: 0934 T-10 hygiene reconciliation

Verdict: ship (T-10 only) · risk: low · 0 findings
Reviewer context: fresh delegated context, read-only audit; did not perform the reconciliation.
Reviewed at: 2026-10-21T06:53:02.595816+00:00

## Evidence

- Installed SpecWeave and npm stable both report 3.1.4. Node 22 and vskill 1.2.10 were used. The existing October 20 verify report is PASS; this review did not run final increment verification or closure.
- Fresh `vskill doctor --json` from the umbrella root exited 0, returned zero issues and zero remaining findings, and scanned exactly the same 31 global/project directories as the saved after report. No stderr.
- The supplied preservation check exited 0. An independent walker also checked exact tree membership, lstat types, byte counts and SHA256 values against the receipt: 680 regular-file instances, 109 directories and 8,649,072 bytes across 13 canonical trees and 3 preserved copies. No internal symlinks occurred in those trees.
- Each preserved copy (hyperframes, hyperframes-creative, media-use) exactly matches its canonical manifest, and all counterpart modes match. The three former Claude paths are symlinks resolving to the intended canonical directories. The private recovery root has mode 0700.
- All 39 moved link objects exist at their recorded recovery paths with unchanged literal target strings; all original paths are absent. The removed set exactly equals the union of 36 before-report redundant links and the 3 intermediate Gemini findings. There are exactly 13 moved links per provider: Cursor, Gemini CLI and OpenCode.
- For every moved link, resolving its saved target from its original location reaches the surviving canonical skill. Every recorded reader still has that canonical directory in the installed vskill discovery map. Installed registry declarations confirm shared global discovery for Cursor (`dist/agents/agents-registry.js:116`), Gemini CLI (`:134`) and OpenCode (`:202`). Claude retains its three discovery links because it uses its own skills root (`:253`). These references are under `/Users/antonabyzov/.nvm/versions/node/v22.20.0/lib/node_modules/vskill/`.
- The installer lock still hashes to `c4422157615f765a65ba1db4e76ba5c435510f03fbec63f32402808e64e0cbb5`. All 11 skills with recorded use independently remain readable at their canonical SKILL.md paths.

## Scope and limits

The before/intermediate/after sequence is consistent: 3 identical copies plus 36 redundant links, then 3 newly redundant Gemini links, then zero issues. No skill-content loss or provider-discovery gap was found. Relocated relative link objects are recovery artifacts: they retain their original target text and are intended to be restored at the recorded original paths, not resolved from the recovery folder.

Provider discovery was checked against installed vskill declarations and real filesystem paths; native provider sessions were not launched. Historical ownership/open-handle checks are supported by the mutation receipt, not independently re-observed after the event. No canonical skill, backup, lock, ledger or process was modified by this review. Only this report was written.

This verdict does not approve T-09 social publication or close increment 0934. The earlier archive scan was not repeated.
