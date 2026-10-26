# Review: 1078 Project badge stability
Verdict: ship · risk: low · fresh-context reviewer /root/badge_review

Initial finding: fleet.test.ts mock could not evaluate real derived atoms. Repaired by handling Atom.read, retaining exact request assertions. Reviewer reran five fleet/observation tests under Node22 and approved after correction. No product correctness findings.

Validation: 74 sidebar/aggregate/observation tests plus2 fleet cases; observation helper100% coverage; production web build successful. Four headless desktop/narrow light/dark cases,96 transitions, no label movement, hover count visible, unavailable states explicit. Existing unrelated web TS2883 in newThreadWorkspaceDefault.ts recorded separately.

Source: PR781 head27ab536f69dc0e06877c6518a5d5fc6bfdce1b13.

## Release-blocker repair review

Fresh reviewer /root/badge_review: ship. Extracted projectAttentionScope declarations and implementations are byte-identical; existing hook exports remain compatible; test assertions unchanged. Independently reran65 projectWorkspaceModel tests under Node22. Parent ran182 focused cases. Final source head79e5bdbc34a3ed914386fa3b300d17cb6872715a; CI reruns on final head.
