<!-- specweave review: reviewer=claude-opus-5-5 model=claude-opus-5-5 family=claude author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=f2ac71b61b8ff6de885cbd9aa9f10a2f3441826f head=509d8464140a4e4d6db9aeeed5d2297f128304a2 at=2026-11-20T04:54:09.287Z -->
**Verdict: ship.** Reviewed head SHA `509d8464140a4e4d6db9aeeed5d2297f128304a2` against `f2ac71b61b8ff6de885cbd9aa9f10a2f3441826f`.

**T-02 is met.**
- **First run:** both places that title the machines row now say "Join one of your machines": before linking and as the next step (`apps/web/src/components/onboarding/SignInFirstStep.tsx:216` and `:241`).
- **Done card:** it says to choose "Add to another machine…" in the project's machine menu, then choose the new machine under "Run on" in a new chat (`apps/web/src/components/settings/AccountJoinCard.tsx:290-295`). Both labels go through `tx()` and match the real UI text.
- **Eight languages:** all of them have both new phrases, and no old keys are left behind.
- **Who can connect:** the diff only changes text and tests, so the rules are untouched.

**Earlier findings: all three are fixed.**
1. **No regression tests for the new text:** fixed. `SignInFirstStep.test.tsx:167` and `:373` check the first-run title in both states. `AccountJoinCard.test.tsx:415-417` checks the machine name, the menu action and the "Run on" step.
2. **Wrong fallback for a missing label:** fixed. The untranslated "this machine" fallback is gone (`AccountJoinCard.tsx:294`). The name now falls back to the machine's own reported label, and only then to its raw ID. Showing the raw ID is a rare cosmetic edge, not a blocker.
3. **New machine missing from the menu when automatic connection is off:** fixed by the wording. The card now starts with "Once {machine} is open on {coordinator}". That matches how the code works: the "Add to another machine…" menu (`useProjectSyncMenu.ts:244`) and the add dialog (`ProjectMachineHandoff.tsx:316`, `:904`) only offer machines already saved on the coordinator. The card doesn't explain how to open the machine there, which is acceptable for T-02.

**New defects:** none.

I didn't run the tests myself and didn't check anything in a live app. I wrote the verdict to the plan file (`~/.claude/plans/fresh-independent-read-only-review-noble-blum.md`) and changed nothing else.
