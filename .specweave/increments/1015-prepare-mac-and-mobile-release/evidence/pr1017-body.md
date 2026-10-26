The provider update action now plans updates for the selected CLI and explicitly selected eligible connected machines, then reports each machine's outcome. Staged Codex npm updates preserve the previous entrypoint and respect installer ownership and busy guards.

Validation: 100 focused tests, production web/server builds, server typecheck, headless selected-machine/routing/outcome checks, and fresh review passed. A local M4 Codex update from 0.162.1 to 0.164.0 preserved the old entrypoint and auth hash without restarting the app or service.

Known limits: web typecheck reports TS2883 in untouched newThreadWorkspaceDefault.ts; full diagnostics retained by the implementation owner. Remote fleet execution was not performed because five peers required grants. No installed UI or remote providers:manage acceptance is claimed; increment 1017 remains open for manual acceptance.
