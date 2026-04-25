# ADR 0724-01: Delegate every `enabledPlugins` mutation to the `claude` CLI

- **Status**: Accepted
- **Date**: 2026-04-25
- **Increment**: 0724-vskill-cli-install-enable-skills
- **Deciders**: Anton Abyzov (product), architect agent
- **Related ADRs**: none direct (this is the first ADR in the vskill enable/disable surface)

## Context

`vskill enable <name>` and `vskill disable <name>` (new in 0724) need to flip
the `enabledPlugins[<pluginId>]` flag in `~/.claude/settings.json` (user
scope) or `<projectDir>/.claude/settings.json` (project scope). Today this
file is touched by:

1. **Claude Code itself** — the editor reads and rewrites the file as the
   user toggles plugins inside the IDE.
2. **The `claude plugin install/uninstall` CLI subcommand** — Anthropic's
   sanctioned write path. It also populates the plugin cache at
   `~/.claude/plugins/cache/<marketplace>/<plugin>/`.
3. **`vskill` itself, indirectly** — `src/utils/claude-plugin.ts` already
   wraps (2) for the install/remove paths. `src/settings/settings.ts`
   exposes only read-only helpers (`isPluginEnabled`,
   `listEnabledPlugins`, `purgeStalePlugins`) by deliberate convention —
   see the file's header comment.

Two write strategies were considered for the new commands:

- **A. Direct JSON mutation.** vskill reads the JSON, updates the
  `enabledPlugins` map, writes back atomically (tmp-then-rename). One
  fewer subprocess; no dependency on the `claude` binary being on PATH.
- **B. Subprocess delegation.** vskill calls
  `claude plugin install --scope <s> -- <pluginId>` /
  `claude plugin uninstall --scope <s> -- <pluginId>`. Same path the user
  would use by hand; same path that already exists in
  `claudePluginInstall` / `claudePluginUninstall`.

## Decision

**Option B — every mutation goes through the `claude` CLI.** vskill never
writes `~/.claude/settings.json` (or any project-scope counterpart)
directly. The new `enable` / `disable` commands wrap
`claudePluginInstall` / `claudePluginUninstall` in `src/utils/claude-plugin.ts`,
which is the same wrapper that the install (`add.ts`) and remove
(`remove.ts`) paths use today.

The read side stays as it is: `isPluginEnabled` and `listEnabledPlugins` in
`src/settings/settings.ts` continue to do plain `readFileSync` of the JSON
file, because reads have no atomicity hazard.

## Rationale

1. **Race-free with Claude Code itself.** Claude Code holds settings.json
   open and rewrites it as the user toggles plugins in the IDE. Any
   third-party process that writes the file directly risks last-writer-wins
   data loss. The `claude plugin install/uninstall` subcommand is the
   canonical writer Anthropic ships, so any locking, atomicity, or schema
   migration logic they add in the future is automatically picked up by
   vskill.
2. **One source of truth for the side-effects.** `claude plugin install`
   does more than flip a flag — it populates `~/.claude/plugins/cache/`
   with the marketplace contents. Reproducing that side-effect in vskill
   (and keeping it in sync as Claude Code's plugin format evolves) is
   strictly worse than shelling out.
3. **Existing invariant in `settings/settings.ts`.** The file's header
   comment already declares it read-only and forbids direct writes. New
   commands honour that invariant rather than break it.
4. **Idempotency comes for free.** `claude plugin install` is idempotent
   on its own — running it twice is harmless. We add a pre-check via
   `isPluginEnabled` only to suppress the second subprocess invocation
   (and the corresponding "already enabled" log line); correctness does
   not depend on that pre-check.

## Consequences

- **Positive**: race-free with Claude Code; future schema migrations
  inherited automatically; one canonical wrapper module in
  `src/utils/claude-plugin.ts` covers install / enable / disable / remove.
- **Positive**: tests mock `execFileSync` once and cover all four flows;
  no JSON-merge logic to test in vskill.
- **Negative**: requires the `claude` binary on PATH (already required by
  `add.ts` and `remove.ts`). Surface a clear error via
  `resolveCliBinary("claude")` if missing, with an upgrade hint.
- **Negative**: each subprocess takes ~50-200 ms. Acceptable for a CLI
  command users invoke ad-hoc; not on a hot path.
- **Negative**: drift risk if the CLI subcommand syntax changes. Mitigated
  by an integration test that asserts the exact `argv` passed
  (`["plugin", "install", "--scope", scope, "--", pluginId]`) so a syntax
  change shows up as a test failure rather than a silent break.

## Alternatives considered

- **Direct JSON mutation with file-locking.** Rejected for the race-free
  argument above; the `claude` binary is the canonical writer.
- **Hybrid (write + side-effect via CLI).** Rejected — splits state
  ownership between vskill and Claude Code, doubles the surface that has
  to evolve in lockstep.

## References

- `repositories/anton-abyzov/vskill/src/utils/claude-plugin.ts` — the
  wrapper that this ADR sanctions as the only write path.
- `repositories/anton-abyzov/vskill/src/settings/settings.ts` — read-only
  invariant carrier.
- 0724 spec.md — full user-stories and ACs for the enable/disable surface.
- 0724 plan.md — component map referencing this ADR.
