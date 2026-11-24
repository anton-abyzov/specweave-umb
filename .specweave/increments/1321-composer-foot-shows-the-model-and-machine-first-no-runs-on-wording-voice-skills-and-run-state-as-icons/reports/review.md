# 1321 review

Fresh-context review on Sonnet 5.5, November 13, 2026, of PR 333 (merged as `d753b8fc7c`) on `origin/main`.

**Verdict:** SHIP. All 8 ACs met, no blockers or majors.

| AC | Status | Evidence |
|---|---|---|
| AC-01 | met | `reports/composer-foot-mockups.html`, pick with reason (D-05) |
| AC-02 | met | `ThreadMachineComposerChip.tsx:84,142`; `restingComposerControlsMeasurement.ts:102-127,169-189` |
| AC-03 | met | `ChatComposer.tsx:8102,8118,8132`; `ComposerPrimaryActions.tsx:322,365,372` |
| AC-04 | met | `ComposerVoiceMenu.tsx:29-53`; `ComposerSkillsPopover.tsx:110,118` |
| AC-05 | met | `ProjectWorkspaceSurface.tsx:223,2059-2113`; `shell.css:2228-2250` |
| AC-06 | met | `MachineWindowTint.tsx` and `windowMachine.ts` removed; `index.css:2693-2722` |
| AC-07 | met | `index.css:2627-2640,2653` |
| AC-08 | met | `apps/web/tests/composer-foot/verify.mjs`, 24 headless scenarios, light and dark |

## Minor findings (follow-up, not blocking)

1. The short Send label (`ComposerPrimaryActions.tsx:365,372`) is never exercised: the fixture has no send target.
2. The coordinator run state is checked against a copy in `tests/composer-foot/main.tsx:112,182-187`; "Needs you" and "Run failed" words are not asserted against `ProjectWorkspaceSurface.tsx:223`.
3. The 560 px wrap is only visible in screenshots, not asserted; `max-w-48` still cuts machine names over about 192 px (within the spec's "up to the chip's cap").

## Re-review after the passing verify

November 14, 2026, same reviewer (Sonnet 5.5), against `reports/verify.md` PASS (all five commands exit 0, 8 of 8 ACs). Five later commits on specwithcode-dev main touch 1321's files (`48dd3b8c1`, `09643bb1b`, `8d66a1320`, `c0d20a018`, `8d8563c12`); none changes the composer-foot, machine-pane, run-state or banner-border behavior. Verdict still SHIP; the three minors above stand.
