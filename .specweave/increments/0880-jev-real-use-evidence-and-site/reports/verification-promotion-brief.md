# Promotion and activation brief

## Positioning
Jev helps software choose among a fixed set of outcomes when people phrase the same request differently. Start with a bounded read router or triage label. Keep rules, permissions and writes deterministic.

## Evidence to lead with
Show the actual input, both handler outputs and their limits in one frame. The EasyChamp selected example returned fixture league data in 0.307 seconds, where the current Gemini fallback took 1.988 seconds and could not list it. Say “live models, actual Python handler, fixture API data” on the same frame. Link all five paired results and the larger 62-case replay. The broader replay recovered five direct reads across 41 model calls; it does not establish a production speedup.

## Draft launch copy — not posted
We put Jev into EasyChamp’s existing chat handler and published the failures alongside the wins. It recovered five safe read routes in 62 authored cases. A selected live-model demo returned fixture league data in 0.31s; the existing fallback took 1.99s and could not list it. Most classifier calls still fell back, so routing stays off in production until a representative canary proves a net gain. Inspect the inputs, raw outputs, and implementation: https://spec-weave.com/jev

Publish only after the URL is live. The screenshot is application evidence; premium generated artwork is a supporting illustration.

## First-user journey
1. Read one real example and its caveats on /jev.
2. Inspect raw input/output JSON without signing up.
3. Install SpecWeave, provide an allowed provider key, run `specweave jev setup` and `specweave jev doctor`.
4. Run one bounded routing decision with `specweave jev route "Classify the failing unit test and suggest the next debugging step"`; inspect the suggestion rather than executing it as authority.
5. Check `specweave jev usage`, then compare a labelled sample from a real integration against the existing baseline.

## Measure before expanding promotion
Instrument only with an approved analytics destination and privacy configuration. No analytics account or existing event stream was verified in this audit, and no new tracking was silently installed.

Track /jev visit → evidence view/download → setup guide → successful first decision → first real integration → seven-day repeat use. Use those counts to locate drop-off rather than assuming traffic equals adoption. For the integration, measure p50/p95 total response latency, total billed cost, fallback rate, wrong accepted routes, corrections and timeouts. Include every request and fallback in the comparison.

A useful next experiment is five backend teams bringing a representative labelled read-routing or triage sample. Review failures before enabling an opt-in canary. Stop expansion if net latency or cost worsens, or any newly accepted route violates the deterministic allowed set. These are proposed experiments and metrics, not achieved customer or growth outcomes.
