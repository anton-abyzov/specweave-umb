# T3 Code changes since October 30 and organization policies

## Problem

SpecWithCode's last selective port stopped at T3 Code nightly `v0.1.6-nightly.20261030.3904` (increment `1146`). T3 Code has landed 767 commits since then, through `v0.1.7-nightly.20261102.4066`, including a machine-wide managed policy for companies (`d897d3f3f0`, PR #27197, November 1, 2026).

Nothing in SpecWithCode lets a company set rules for its people: every setting belongs to whoever runs the app, permission modes default to full access for workers, and a coordinator can start work on other machines. A team lead has no way to cap permissions, restrict providers or keep phones and Connect off a laptop.

## Scope

In: a take, adapt or skip verdict for each meaningful upstream change; small verified bug fixes rewritten as our own code and merged; an organization policy spec and a designed HTML decision page with a mockup.

Out: building organization policies in this increment, any new paid infrastructure, and work owned by active workers (artifact cards, update install audit, Linux chat session errors, coordinator handoff redesign).

## Acceptance Criteria

- [ ] AC-01: `reports/triage.md` covers every commit in `v0.1.6-nightly.20261030.3904..v0.1.7-nightly.20261102.4066`, with a one-line take, adapt or skip reason for each meaningful one, checked against our code.
- [ ] AC-02: Small takes with no product decision are rewritten by hand, tested, reviewed and merged; no upstream history enters our branches, and `UPSTREAM.md` records them.
- [ ] AC-03: `reports/organization-policy-spec.md` specifies our own organization policy using SpecWithCode's concepts, and states what it cannot enforce.
- [ ] AC-04: `reports/organization-policy-decision.html` shows the recommendation, a mockup, the options with recurring cost, and the one decision needed, checked in light and dark at 390px and desktop widths.

## Approach

Read upstream through `mit-reference` only as evidence. Never cherry-pick or merge it (rule of October 27, 2026). Each fix is rewritten in `@specweave-studio/*` code, in the worktree `worktrees/t3-1169`, on `feat/1169-t3-small-takes`.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Small valuable fixes merge with `gh pr merge --squash --admin`; organization policies stop at a spec and decision page (coordinator's default for this task).
### Open
- D-02 Organization policy direction, decided by the user on the HTML page.

## Tasks

### T-01 Triage upstream changes
- AC: AC-01 | Files: reports/triage.md | Test: test -s /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1169-t3-code-changes-since-october-30-and-organization-policies/reports/triage.md

### T-02 Build and merge the small takes
- AC: AC-02 | Files: UPSTREAM.md and the fixed files listed in the PR | Test: focused vitest runs named in the PR, plus required CI

### T-03 Write the organization policy spec
- AC: AC-03 | Files: reports/organization-policy-spec.md | Test: test -s /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1169-t3-code-changes-since-october-30-and-organization-policies/reports/organization-policy-spec.md

### T-04 Design the decision page
- AC: AC-04 | Files: reports/organization-policy-decision.html | Test: test -s /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1169-t3-code-changes-since-october-30-and-organization-policies/reports/organization-policy-decision.html

### T-05 Verify and close 1169
- AC: AC-01, AC-02, AC-03, AC-04 | Files: spec.md | Test: specweave verify 1169-t3-code-changes-since-october-30-and-organization-policies
