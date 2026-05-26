# 0853 — Implementation Plan

## Architecture (one diagram, in prose)

```
                ┌───────────────────────────┐
                │  scripts/units/*.verify.mjs│  ← VerifiableUnit definitions
                │  (install + skill-new)    │     fixtures, invariants, schema
                └─────────────┬─────────────┘
                              │ registerUnit()
                              ▼
                ┌───────────────────────────┐
                │  scripts/registry.mjs     │  ← Map<unitId, Unit>
                └─────────────┬─────────────┘
                              │ runAll()
                              ▼
                ┌───────────────────────────┐
                │  scripts/runner.mjs       │  ← mount → act → read surface
                │                           │     → run verifiers → verdict
                └─────────────┬─────────────┘
                              │ writes
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
   reports/verify-result.json   .specweave/state/verify-current.json   stdout grid
   (per-run snapshot)           (agent handle)                          (human)
```

Everything is ESM (`.mjs`) so it runs without a build step. Zod is imported from the vskill repo's node_modules to avoid adding deps to the umbrella.

## File layout

```
.specweave/increments/0853-verify-runtime-vskill/
├── spec.md
├── plan.md
├── tasks.md
├── metadata.json
├── scripts/
│   ├── verify-types.mjs        # VerifiableUnit, Fixture, Invariant, Verdict shapes (JSDoc)
│   ├── registry.mjs            # registerUnit / listUnits / buildManifest
│   ├── runner.mjs              # runFixture / runUnit / runAll
│   ├── verifiers/
│   │   ├── schema.mjs          # zod parse
│   │   ├── invariants.mjs      # run declared predicates
│   │   └── filesystem.mjs      # surface reader for install (lockfile/skill files)
│   ├── units/
│   │   ├── install.verify.mjs  # U-INSTALL: 1 happy + 1 probe
│   │   └── skill-new.verify.mjs# U-SKILL-NEW: 1 happy + 1 probe
│   ├── run-verify.mjs          # CLI entry (US-001)
│   └── matrix.test.mjs         # node --test entry (US-002)
├── fixtures/
│   └── tiny-skill-source/      # local plugin used by install happy fixture
│       ├── plugin.json
│       └── skills/
│           └── hello-world/
│               └── SKILL.md
├── reports/
│   ├── verify-result.json      # written by runner
│   └── run-log.md              # human-readable history
└── logs/
    └── runner-<ts>.log         # stderr of each subprocess call
```

## Surface contracts

### U-INSTALL surface JSON
```ts
{
  unit: "U-INSTALL",
  command: "vskill install <source>",
  installRoot: "/tmp/vskill-verify-<ts>/.claude",
  installed: [
    { name: "hello-world", path: "<installRoot>/skills/hello-world/SKILL.md", sha: "abc...", frontmatterName: "hello-world" }
  ],
  lockfile: { path: "...", entries: [...] },
  exitCode: 0,
  stdoutLen: 1284,
  stderrLen: 0
}
```

### U-SKILL-NEW surface JSON
```ts
{
  unit: "U-SKILL-NEW",
  command: "vskill skill new <prompt>",
  emitRoot: "/tmp/vskill-verify-<ts>/emit",
  files: [
    { path: "<emitRoot>/SKILL.md", bytes: 1842, frontmatterName: "test-skill", frontmatterVersion: "1.0.0" }
  ],
  divergence: [],
  engineMode: "universal",
  exitCode: 0
}
```

## Verifier set

| id | purpose | fails when |
|---|---|---|
| `schema` | Zod parse the surface | shape doesn't match |
| `invariants` | run declared predicates | predicate returns false / throws |
| `filesystem` | (install only) stat declared files | file missing / wrong mode |

Three verifiers is enough for MVP. Anthropic ships four (their fourth is `a11y` for DOM); we don't need it.

## Why no dashboard yet

Anthropic's dashboard exists because their artifact is a React app the user already clicks through. Our artifact is a CLI invocation — printing a colored grid to stdout is the human surface. We can promote to HTML in 0855 once the JSON shape is locked.

## Test commands

```bash
# Run everything (USER-001)
node .specweave/increments/0853-verify-runtime-vskill/scripts/run-verify.mjs

# CI matrix (US-002)
node --test .specweave/increments/0853-verify-runtime-vskill/scripts/matrix.test.mjs

# Read the agent handle (US-003)
cat .specweave/state/verify-current.json | jq .current.verdict
```

## Risk + mitigation

| Risk | Mitigation |
|---|---|
| `vskill install` writes to real `~/.claude` and pollutes user state | Every fixture sets `XDG_CONFIG_HOME` + `CLAUDE_HOME` to a tmp dir. Cleaned up via `trap` in shell wrapper. |
| `vskill skill new` calls live LLM, flaky/slow | Use `--engine stub` if supported; else mock by writing a known SKILL.md template directly and asserting on it (= we're verifying CLI invocation contract, not LLM quality). Decision recorded in tasks.md. |
| Lockfile schema drifts in vskill 1.0.19+ | `schema` verifier uses `.passthrough()` on Zod object — accepts new fields, fails only on missing required ones. |
| Tests need network for github fetch | Happy fixture uses a `file://` source pointing at `fixtures/tiny-skill-source/` — no network. |

## Rollout

1. Build harness + run locally — capture `reports/verify-result.json`.
2. Show real outcome to user with paths + key JSON fragments.
3. If green, propose 0854 to promote harness to `vskill verify` subcommand.
4. Do **not** modify `vskill` source in this increment. The harness lives only under `.specweave/increments/0853-.../scripts/`.
