<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=689fce3981665e94d585366cfdfbc1b829d501d6 at=2026-11-19T17:53:03.572Z -->
# Review: 1390 T-13 fleet worker provision
Verdict: ship
Reviewer context: new session

Reviewed `c127be286..689fce3981665e94d585366cfdfbc1b829d501d6` from Git objects. Zero findings.

At `apps/server/src/server.ts:720-729`, the final provide covers the peers as well as limit handoff. Both use services from the same exported layer value (`apps/server/src/fleet/RemoteWorkers.ts:1474`), memoized once per runtime build. This does not rebuild workers or change sibling wiring. The only other change is the adjacent comment. Typecheck was not rerun.
