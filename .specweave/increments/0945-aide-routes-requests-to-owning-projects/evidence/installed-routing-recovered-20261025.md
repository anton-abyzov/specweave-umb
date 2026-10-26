# Recovered positive installed routing receipt

Recovered October 25 from durable source and recipient thread activity. On October 22 at 16:00 UTC, Aide routed one user request to both EasyChamp and SpecWeave. Both successful `studio_project_route` results name the correct project, approved folder, existing coordinator, target message ID, and one attachment. Exact target-message reads confirm delivery into both owning coordinators with the source Aide thread/message provenance and the respective project-specific PHP review note.

This closes the missing positive-dispatch evidence identified in the October 25 adjudication. The original 1.0.60 receipt remains unchanged: that check made no route call. The recovered event is later real service activity, not a new 1.0.85 test. Its installed version is not established by these records. The separate completed 0981 privacy scope is unchanged.

The receipt validator recomputes the deterministic SHA-256 route key from source thread, source message and target project and matches both returned message IDs. This is identity evidence, not a live retry test or a complete duplicate census. No historical request was replayed. Both target texts preserve the request wording and provenance; the source's one trailing space was trimmed. The route results report one attachment each; attachment bytes were not independently compared. Downstream PHP remediation is outside this receipt's claim.

Evidence and reproducible check:

- /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0945-aide-routes-requests-to-owning-projects/evidence/installed-routing-recovered-20261025.json
- /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0945-aide-routes-requests-to-owning-projects/evidence/validate-recovered-routing.mjs

Run the second path with Node. Only the relevant source request, two successful tool events and two recipient messages are included; unrelated personal thread content is excluded. No runtime mutation, update, restart, new dispatch, browser session or database-file access was used in recovery.
