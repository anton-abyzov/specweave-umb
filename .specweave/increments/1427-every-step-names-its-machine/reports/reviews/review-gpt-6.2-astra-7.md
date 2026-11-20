<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=f0a0030ca75456b71501a396fc12832b8fcfe141 at=2026-11-19T23:25:56.015Z -->
# Review: 1427 Window labels, fixture rename
Verdict: ship
Reviewer context: fresh session, static delta review against `ac0d303db80b8d7e8706716414c774e4c5dbc590`.

The only production edit is a comment. The fixture uses `thread-release` for both worker and source. Its source, chip and relay assertions still require `Release notes · M5`; the local source expects `Sign-in check` without a machine suffix. No assertion was removed or weakened. No findings. Tests were not run.
