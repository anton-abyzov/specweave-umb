# 1495 adversarial review

November 28, 2026. Reviewer: GPT-6.2 Sol (Codex) on m4, thread "1495 adversarial review: MCP form deadlines". Gemini 4 Neon was out of quota until December 1. Two earlier GPT-6.2 Sol attempts on M5 failed with "Selected model is at capacity".

| Round | Head | Verdict | Findings |
|---|---|---|---|
| 1 | `98a400944` | fix first | 1 blocker (a Stop mark cleared at finalize), 5 should-fix (exit and steer, parallel URL keys, `claude.ai` name form, failed commit notice, AC-03 wording) |
| 2 | `3c2f063f6` | fix first | 1 blocker (a steer silenced later forms), 2 should-fix (a quick finish, a slow cleanup) |
| 3 | `1eb55980d` | fix first | 1 blocker (an old query's output end marked a new query's form), 2 should-fix (error results, a late steer) |
| 4 | `eb614ed76` | fix first | 2 should-fix (Stop then output end, a failed commit waiting out the grace) |
| 5 | `49958c836` | fix first | 2 should-fix (serial turn-end wait fixed; a commit failing after the 2 s bound accepted as D-06) |
| 6 | `19bc63df8` | nothing serious | none; D-06 can stay closed |

Round 2 showed that reading turn state after the abort could not work. From round 3 on, the app records each form's abort cause itself (D-04).

Merged as app PR #1007, merge commit `03cdc099c`, with 27 checks green on `19bc63df8`. The three test files pass 269 tests, and each fix has a mutation that fails its own test.

Follow-up the reviewer named, not in scope: route a late note through the session event pump with its original run and turn ids (`apps/server/src/orchestration-v2/ProviderSessionManager.ts`), so D-06's late note persists while the session is live.
