# Review of 1313

Fresh-context subagent review of PR #1234 in `anton-abyzov/specwithcode-dev`.

Round 1 at `eccbb88bbd`: NO-SHIP. A machine filter could stay on with no row to undo it, a stale agent stayed stored, filters forced Resolved open, the waiting dot had gaps. All fixed in `e20c8a560f`.

Round 2 at `e20c8a560f`: NO-SHIP. Folded and paged group headings falsely said "N shown". Fixed in `804a4bcace`, which also makes stale agent cleanup wait for provider lists.

Round 3 at `804a4bcace`: SHIP.

Accepted limit: a one-machine project with an agent filter has no waiting dot. The project-wide summary line still reports the request.
