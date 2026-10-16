# Review: 0908 Preserve project names

Verdict: ship · risk: low · 2 source files · 0 open findings
Reviewer context: fresh independent subagent; no implementation edits, claims, pickup, push, provider turns or live-state changes.

## Scope

Reviewed Studio baseline `2ef696067a8377269ec5d0396b6bc3e97d01abcd` through `c89bb4e946d0ddddd6aede95e82114bc26074a71`, limited to `packages/client-runtime/src/state/projectGrouping.ts` and `packages/client-runtime/src/state/projectGrouping.test.ts`. Read increment ACs/Approach, grouping consumers, automatic-title derivation and shared path normalization to verify behavior.

One distinct custom title wins over automatic folder, inferred root, repository-name and display-name titles. Conflicting custom titles keep the repository fallback. Grouping keys, physical deduplication, preferred representatives, ordering, project references and fork identity remain unchanged. Direct mobile callers supply the required workspace path.

## Verification

- Independently ran Node 22.20.0 `node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/state/projectGrouping.test.ts` at the reviewed head: 28 tests passed, exit 0.
- Independently exercised monorepo `repository_path` subgroups, repository grouping, separate mode, reversed input order and member preservation using the exported implementation: all assertions passed.
- Implementation agent reported the final shared grouping plus StudioSidebar suite: 50 tests passed. It also reported focused coverage of 84% statements, 68.62% branches, 87.5% functions and 84.29% lines; each exceeds the umbrella's configured 60% unit target.
- `git diff --check` passed. Installed SpecWeave and npm stable both resolved to 3.0.14. Jev routing returned exit 4 because no key is configured; review proceeded manually.

## Resolved finding

The first implementation classified automatic titles for UNC share roots, Windows drive roots and POSIX `/` as custom titles. Alongside `EasyChamp`, these produced the repository fallback. The issue was independently reproduced against `5ebee77b813005237c2b4ccbd985d3c58e5e607e` using `inferProjectTitleFromPath` and the actual exported grouping implementation. Commit `c89bb4e946d0ddddd6aede95e82114bc26074a71` now recognizes inferred titles and the server's root fallback; regressions cover all four cases. Re-running the original UNC, drive-root and POSIX-root reproductions at the reviewed head returned `EasyChamp` in every case.

No remaining correctness, security, portability or scoped AC-01 findings. This verdict covers the naming implementation; production build, rendered-browser, remote-push, publication and installation evidence remain their own gates under T-02 through T-04 and the release owner.

Nits: none.
