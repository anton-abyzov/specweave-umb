<!-- specweave review: reviewer=claude-opus-5-5 model=claude-opus-5-5 family=claude author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=f2ac71b61b8ff6de885cbd9aa9f10a2f3441826f head=9bdd2cff4bf746e2e1ec1147aad86996c142c1c4 at=2026-11-20T04:50:01.251Z -->
Verdict: ship. 9bdd2cff4bf746e2e1ec1147aad86996c142c1c4 has no critical or high findings.

# Review: 1422-joining-a-machine-sets-up-both-directions-and-says-what-each-approval-adds Joining a machine is one way, and says what each approval adds
Verdict: ship · risk: low · 10 files · 3 findings (1 medium, 2 low)

## [medium] apps/web/src/components/settings/AccountJoinCard.tsx:288 no test pins the new wording
T-02 says "focused web test", but the PR changes no test file. Nothing in `apps/web/src` checks `join-next-step` or "Join one of your machines". Only the two components use them (`SignInFirstStep.tsx:216`, `:241`). If someone puts back "Open Settings > Machines there…" or "Choose your main machine", all 431 tests still pass, so AC-04 and AC-09 have no automated proof. Fix: in `AccountJoinCard.test.tsx`, check that the done card shows the "Add to another machine…" and "Run on" labels, and check the row title in both its "later" and "next" states.

## [low] apps/web/src/components/settings/AccountJoinCard.tsx:294 the "this machine" fallback names the wrong machine
`name(environmentId, here?.label ?? tx("this machine"))`: if `here` is missing, the fallback skips `labels.get(environmentId)` (`studio/machineNickname.ts:118`) and puts in the word "this machine". The sentence is an instruction to follow on {coordinatorLabel}, so "select this machine under Run on" now points at the coordinator. In German it also breaks the grammar ("den Rechner dieser Rechner"). Fix: pass `here?.label` and let `name` fall back to the known label.

## [low] apps/web/src/components/studio/useProjectSyncMenu.ts:245 the menu entry needs the coordinator to have saved the new machine
Both "Add to another machine…" (`:277`) and "Run on" (`components/chat/DraftMachinePicker.tsx:102-103`) list only machines saved in the coordinator's app. Today the coordinator saves a granted machine through `cloud/GrantedAccountMachines.tsx` automatic connect. With "Connect automatically" off (`studio/grantedAccountMachines.ts:115`), the new machine is not in that menu, and the done card points at an entry that is not there for it. Other cases read correctly:
- **Project already on the new machine:** the entry is hidden, and "To add a copy" reads as conditional.
- **No project on the coordinator:** there is no menu, and the instruction implies that.
- **Personal project:** the entry is hidden.

Proof limit (wording only, not a code bug): "Run on" lists the machine only once the coordinator's app has opened it with the second code. The card leaves that to the saved notice above it.

Checked and fine:
- **Authorization:** unchanged. The diff is two components plus eight catalogs, with no RPC, scope or grant code.
- **First-run states:** both the "later" and "next" states use the new title, and the done states keep their own titles.
- **Real menu label:** "Add to another machine…" is the item at `OrchestratorSwitcher.tsx:482`.
- **Localization:**
  - The labels go in through `tx`, so each language shows the menu's own words.
  - All eight catalogs have the new keys, plus "Add to another machine…", "Run on" and "this machine".
  - No old keys are left.

Nits: Russian mixes "компьютере" and "меню машин" in one sentence; Korean uses `{machineLabel}을` where the catalog uses `을(를)`; Spanish adds "recuerda que"; Portuguese uses "Em um novo chat" while the catalog uses "num chat"; ja, ko, pt, ru and zh drop "Next".
