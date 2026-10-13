# Final 0901 evidence review

Reviewed on 2026-10-13 by an independent agent. This current report supersedes the pending-state wording in historical reports without rewriting their evidence.

## Google and provider failure

The original screenshot showed an exhausted Claude worker failing before any Google API call. The released fixes preserve usage-limit classification and give Aide native Google discovery and content-free readiness diagnostics. A separate Codex admission failure was repaired by the coordinated 0904 release; its historical timeout cause remains indeterminate rather than inferred from a later success.

Anton supplied Google sign-in/consent and replied Connected. On installed 1.0.8 source `291f919c24b600e400b8c64e9f3dd383795f33a6`, native Aide run 6 completed at 12:13:39Z. All three health checks passed, followed by exactly one Gmail, Calendar and Drive read, each returning one real item. No content writes, extra tools, delegation or provider errors occurred. Counts-only receipts retain no returned personal content. Both owned temporary authentication sessions were revoked, preserving pre-existing sessions. See `live-google-success-20261013.md` and its hashed receipts.

## Cancellation behavior

Morning briefing dismissal restores the full validated local origin, including Settings scope and hash. Cancel, X, Escape and backdrop share that behavior. Nested dropdown Escape dismisses only the dropdown. Direct links consume their request parameters without reopening after reload; local editors stay on their list, and successful saves remain on that list. Theme variant Escape no longer exits Settings. Both chat-linked task editor entry points retain their origins.

The audit covered the routed editors, Settings provider/setup dialogs, inline editors, shared overlay primitives, utility-page Escape, project overlays and selected native Settings paths. Existing correct local-dismiss behavior was retained. `navigation/results.md` separates source inspection, real built-server headless navigation proof with fake Google, production builds, focused tests and coverage. All four focused coverage measures exceed the configured 60% unit target; this is logic-module coverage, not whole-application coverage.

Independent review found no remaining source/evidence defect. These restore existing controls and navigation; they introduce no new UI or consent flow requiring another manual acceptance step. The human Connected response and successful authorized proof provide the required authentication acceptance.

## Follow-up shipment

The published 1.0.9 source is `51c49ab4603c17c87362e9700cd242b24ed83e2e`. Independent review verified the navigation implementation/test/runner files against the reviewed follow-up and checked the retained ScheduledTaskLink use in MessagesTimeline. Both repositories published 11 verified assets; the public feed passed anonymous readback. The release audit's SHA-256 is `01825a497f2701b36b3a0e47943bdd4394d1be3e59bda40728b7111cc739a773`.

The sole installer remains chat `01a133f7-afb4-7771-8e87-55cfabfd6858`. At 12:37Z, guarded service installation was still pending the normal release of an idle shared Codex provider process created by the completed Aide run. Read-only correlation found no nonterminal runs and no later Codex run. `install-idle-provider-audit.json` records that boundary; no process was killed or authentication/settings changed by this task.

The idle provider connection subsequently closed normally. The sole installer completed the guarded M4 update at 12:45:41Z and later released its reservation. `verify-shipment-109.py` independently passed: source/version match, all 7,481 installed manifest entries match, service HTTP and web asset respond, the desktop ASAR and code signature match, and the running desktop PID matches native About evidence. Complete database continuity, protected authentication/identity, original services and settings preservation passed; the allowed row difference was an existing browser heartbeat. No competing installation or forced provider cleanup was performed.

T-08 is complete with `shipment-109-verified.json`. Final SpecWeave verification covers all 9 acceptance criteria and 8 tasks, replacing the original 03:40Z verification of only the initial scope. Real Google proof remains explicitly attributed to installed 1.0.8; no duplicate personal-data read was needed for the navigation/formatting follow-up.
