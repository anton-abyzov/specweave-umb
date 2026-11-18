# Readable block reasons when agents write them

## Problem

Block reasons on the SpecWithCode Board show up as squeezed words. Increment 1391 (Board panel redesign, shipped in SpecWithCode 1.0.352) left this as follow-up F-01 in its D-08: the Board only adds a space after commas and semicolons and does not guess where words split, so the real fix belongs where the reason is written.

The source is the ledger itself. `~/Projects/sw-easychamp/.specweave/increments/0952-premierliga-latest-data-performance/ledger.jsonl` line 268, written by `specweave task block` on October 26, 2026:

`New offline37profileattestation valid;113/148 exactartifactcopies recovered,35unresolved. Existingcreationloader stillFileNotFound on original artifact path; ... nooriginalpathrestore orguardbypass.`

The CLI stores `--reason` with only a trim, so the agent wrote the words already glued. Nothing in the CLI, the skills or the help tells an agent that a reason is read by a person on the Board, and the only length rule next to it (`--line`, at most 100 characters) invites compressing.

Calibration: 373 real block and skip notes from this umbrella and sw-easychamp (`~/.specwithcode/m4/scratch/2026-11-18-1409/notes.json`). Only the 0952 note has glued words; 2 notes lack a space after a comma or semicolon.

## Scope

In: the SpecWeave CLI writers of block and skip reasons (`task block`, `task skip`, `card wait` on T-NN and C-NN cards), a shared reason-text module, CLI help, the sw-do and sw-done skill text, unit and CLI tests, a SpecWeave release.

Out: rewriting old ledger lines; reading or replaying the ledger (old notes still load as written); the Board's display repair (shipped in 1391); claim, done, release and increment notes; guessing word splits.

## Acceptance Criteria

- [ ] AC-01: A reason written by `task block`, `task skip` or `card wait` keeps its words, spaces and punctuation; runs of whitespace (newlines, tabs) become one space, and a missing space after a comma or semicolon is added (`valid;113/148` becomes `valid; 113/148`, `recovered,35unresolved` becomes `recovered, 35unresolved`), but never inside a number (`1,000`), a URL or text in backticks.
- [ ] AC-02: A reason with glued words (the 0952 note: `offline37profileattestation`, `exactartifactcopies`, `35unresolved`) is refused with exit 2, nothing is appended to the ledger or branch card file, and the error names the glued words and asks for one short plain sentence with code in backticks.
- [ ] AC-03: Normal reasons pass unchanged: all 373 calibration notes except the 0952 one, plus words like `SystemAdmin`, `API-equivalent`, `HTTPX`, hex SHAs (`d65dffec9`), paths, URLs, increment slugs, model ids (`claude-opus-5-5`, `qwen3-coder-30b`), camelCase identifiers, long real words (`internationalization`) and non-Latin text.
- [ ] AC-04: A reason longer than 280 characters is stored with a warning on stderr that suggests one short sentence; no reason is ever cut or refused for length.
- [ ] AC-05: Loading a ledger never applies the new rules: an existing line with glued words still loads and shows as written.
- [ ] AC-06: `specweave task --help` and `specweave card --help` say a reason is one short plain sentence a person reads on the Board, with spaces, and code in backticks; the sw-do and sw-done skills say the same where they show `--reason`.
- [ ] AC-07: The change ships in a SpecWeave release from `bash scripts/release/release.sh`, after a review by Muse Wonderful (`muse-wonder-full-1.0`, xhigh) and green CI.

## Approach

1. New `src/core/tasks/reason-text.ts`: `normalizeReason(text)` and `findGluedWords(text)`, plus `checkReason(text)` returning `{ text, glued, long }`. Protected spans (backtick code, URLs up to their trailing punctuation) are never changed or checked. A token with code characters (`/ \ = _ . @ # : < > { } | * $ & + ~`) or a hex string of 7 or more is skipped; hyphenated words are checked part by part. A part is glued when it is Latin lowercase letters of 19 or more (optional first capital) not in a short list of long real words, or 4+ letters, digits, 4+ letters (`offline37profileattestation`), or digits followed by 5+ lowercase letters (`35unresolved`).
2. `src/cli/commands/task.ts`: `block` and `skip` run `checkReason` before appending; glued words exit 2 with the message; a long reason warns. `card wait` on a T-NN id already goes through `taskCommand`; `src/cli/commands/card.ts` runs the same check for C-NN cards.
3. Help: `bin/specweave.js` option text for `task --reason/--note` and `card --reason`; the header comment in `task.ts`.
4. Skills: `skills/sw-do/SKILL.md` and `skills/sw-done/SKILL.md` (the source), then `npm run generate:skills` for `plugins/specweave/skills/`.
5. Tests under `tests/unit/`: a table test over the calibration cases, and CLI tests that a refused reason leaves the ledger unchanged and an accepted one is stored normalized.

Rejected: warning only (F-01's first proposal), because an agent in auto mode ignores stderr and the squeezed note still reaches the Board; refusing for length, because a cap pushes agents to compress, which is how glued words happen; splitting glued words with a dictionary, because guessed splits put words in an agent's mouth; validating on ledger read, because old ledgers must load as written.

Risk: a false refusal on an unusual but real word. The error says how to get past it (backticks for names and code), and calibration shows no false hit on 372 real notes.

## Decisions

### Asked
- D-01 Normalize or reject glued words? Task says "normalize or reject": safe spacing is normalized, glued words are refused (exit 2), since splits cannot be guessed.
### Defaulted (change any before sw-do)
- D-02 Long reasons warn at 280 characters and are never cut (reversible).
- D-03 Rules apply to block and skip reasons only, not claim, done or release notes (reversible).
### Open
- none

## Review

Reviewer: Muse Wonderful (`muse-wonder-full-1.0`) at xhigh, full access, on the pull request head before merge.

## Tasks

### T-01 Reason text module with calibration tests
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specweave/src/core/tasks/reason-text.ts, repositories/anton-abyzov/specweave/tests/unit/core/tasks/reason-text.test.ts | Test: cd repositories/anton-abyzov/specweave && npx vitest run --config vitest.unit.config.ts tests/unit/core/tasks/reason-text.test.ts

### T-02 Check reasons in task block, task skip and card wait
- AC: AC-01, AC-02, AC-04, AC-05 | Files: repositories/anton-abyzov/specweave/src/cli/commands/task.ts, repositories/anton-abyzov/specweave/src/cli/commands/card.ts, repositories/anton-abyzov/specweave/tests/unit/cli/commands/task-reason.test.ts | Test: cd repositories/anton-abyzov/specweave && npx vitest run --config vitest.unit.config.ts tests/unit/cli/commands/task-reason.test.ts tests/unit/cli/commands/card.test.ts

### T-03 Help and skill text
- AC: AC-06 | Files: repositories/anton-abyzov/specweave/bin/specweave.js, repositories/anton-abyzov/specweave/skills/sw-do/SKILL.md, repositories/anton-abyzov/specweave/skills/sw-done/SKILL.md, repositories/anton-abyzov/specweave/plugins/specweave/skills/do/SKILL.md, repositories/anton-abyzov/specweave/plugins/specweave/skills/done/SKILL.md | Test: cd repositories/anton-abyzov/specweave && npm run lint:skills && npm run lint:docs-refs

### T-04 Review, merge and release
- AC: AC-07 | Files: repositories/anton-abyzov/specweave/package.json | Test: bash scripts/release/release.sh verify specweave
