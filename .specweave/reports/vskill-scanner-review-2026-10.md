# vskill scanner and crawler review, October 2026

Scope: the skill scrapers (`vskill-platform/crawl-worker`), the two scan paths (Workers queue `src/lib/queue/process-submission.ts`, VM `crawl-worker/sources/submission-scanner.js` → `finalize-scan`), the Tier 1 regex scanner and the Tier 2 LLM judge, compared against what competitors ship.

Shipped on branch `inc/scanner-hardening` in vskill-platform.

## Findings that were live in production

| # | Finding | Impact | Fixed |
|---|---|---|---|
| 1 | The Tier 2 primary model, `gemini-2.0-flash`, was shut down on 2026-06-01 ([Gemini deprecations](https://ai.google.dev/gemini-api/docs/deprecations)). | Since June every Workers judge call fell to Claude Opus (costly) or Ollama 8B; the VM's external fallback was dead. Inferred from code and dates, not from logs. | Default is now `gemini-3.5-flash` with schema-constrained output; override with `GEMINI_SCAN_MODEL`. |
| 2 | `https://github.com/anthropics/../attacker/evil` passed the vendor check. `fetch()` normalizes the dot segment to `attacker/evil`. | An attacker repo was treated as a trusted vendor: no scan, published as verified. | Vendor regexes are anchored and reject dot segments and encoded characters; repo-URL and skill-path validation reject them too. |
| 3 | Tier 1 suppressed every finding inside an HTML comment. | `<!-- ignore previous instructions ... -->` is invisible to humans, read by agents, and was never flagged. | Comments are scanned; directives in comments are a new rule (HC-005). |
| 4 | When Tier 2 was unavailable, both paths published on Tier 1 alone. Prompt-injection prose is downgraded to "info" by Tier 1 context rules. | An LLM outage (see #1) meant agent-directed attacks could auto-publish. | Hidden-content and agent-attack findings now hold the skill as RESCAN_REQUIRED until the judge runs. |
| 5 | Fast-approve skipped the judge for "clean" Tier 1 results, including downgraded criticals. | Same as #4 without any outage. | Fast-approve is gated on `judgeRequiredSignals()`. |
| 6 | The judge prompt said "DEFAULT TO false_positive" and "Give it 80+ and PASS"; skill text sat in the prompt unfenced; only the first 15k characters were shown. | Prompt injection of the judge and padding a payload past 15k both worked. | Pass-bias removed; nonce-fenced block; excerpt covers head, every flagged region and tail; forged delimiters are their own rule (HC-009); score caps the model cannot override. |
| 7 | `/crawl` merged caller config over env config. | Anyone with the internal key could point a crawl at their own host and receive the GitHub tokens. | Overrides are allow-listed (numeric/boolean/enum keys only). |
| 8 | DCI-013/014 regexes were super-linear (355–446 ms on a 20k-char line). | ReDoS on the scan path. | Bounded; 1 ms. |
| 9 | Every `res.text()` on fetched skill files was unbounded. | Memory blowup from one large file. | 2 MiB streamed cap with a visible truncation marker (HC-010). |
| 10 | Webhook timestamps from the future were accepted. | Replay window. | 60 s skew limit. |
| 11 | NA-002 regex differed between the TS and JS scanners. | Same skill, different verdict per path. | Aligned. |

## New detection

- **Hidden content** (HC-001 to HC-011): Unicode tag smuggling (decoded), bidi controls, zero-width runs (decoded), variation-selector smuggling (decoded), directives in comments, base64 that decodes to text, punycode/IDN hosts, mixed-script words, text addressed to the scanner, truncated files, compiled/binary files in the bundle. Decoded payloads are rescanned at full severity.
- **Competitor-sourced rules:** CI-009 Python shell exec, CI-010 PowerShell `iex`/`-EncodedCommand`/`FromBase64String`, CE-004 pickle/marshal/decoded `exec`, NA-004 fake prerequisite download (ClawHavoc pattern), NA-005 password-protected archives. NA-004/NA-005 always go to the judge.
- **Judge coherence check:** does every capability match the skill's stated purpose (ClawScan / Cisco approach).
- Bundled scripts are now part of the judge's input; findings are capped most-severe-first.

## Speed

- Bundle directory listings and file reads run 6-way parallel instead of one round trip per file (max 200 files).
- vendor-org-discovery skips repos whose `pushed_at` has not changed since the last sweep; the cache resets weekly.
- The VM scanner rotates GitHub tokens across submissions and resolves the commit SHA authenticated and in parallel (it was anonymous: 60/h per IP, after which scans lost their commit pin).
- The scheduler no longer starts a new run while a timed-out one is still draining.

## Competitors

| Who | What they do that we lacked | Status |
|---|---|---|
| skills.sh (Socket, Snyk, Gen audits) | Per-version third-party audit badges | Follow-up |
| ClawHub | VirusTotal hash of a deterministic ZIP; daily rescans; `.pyc` rejected; ClawScan coherence judge | Coherence judge and binary flag done; VirusTotal and rescans are follow-ups |
| Snyk agent-scan / ToxicSkills | Taxonomy of agent-directed attacks, hidden-instruction detection | Done (HC rules) |
| Cisco skill-scanner | YARA, dataflow over scripts, nonce delimiters, demote-only LLM adjudication | Nonce delimiters and demote-only caps done; YARA and dataflow are follow-ups |
| SkillPlus | Adversarial refute pass, IOC graph across skills | Follow-up |
| Papers: SkillScan (arXiv 2601.10338), MalSkills, MalSkillBench, SkillVetBench, MaliciousSkillBench | Benchmarks and attack corpora | Follow-up: run our scanner against them |

## Follow-ups not in this change

1. VirusTotal hashing of a deterministic bundle ZIP, plus scheduled rescans of published versions.
2. Dataflow analysis and YARA rules over bundled scripts.
3. Sandbox execution of install scripts.
4. IOC graph (domains, hashes, wallets) shared across skills.
5. SARIF export and per-finding UX on the skill page.
6. Port the new rules to the vskill CLI scanner (the site's pattern count comes from the CLI package).
7. Rotate the GitHub PATs already in VM env files; run scanner-worker as non-root.
8. Content-hash verdict cache to skip rescanning identical bundles.

## Deploy notes

- The VMs run older crawl-worker code; they need a redeploy for any VM-side change to take effect.
- `GEMINI_SCAN_MODEL` is optional.
- Expect more skills held for review at first: HTML-comment findings and RESCAN_REQUIRED holds were previously silent.
