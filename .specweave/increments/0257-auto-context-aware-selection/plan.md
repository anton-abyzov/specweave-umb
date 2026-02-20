# Implementation Plan: Context-Aware Auto Mode: Intent-Based Increment Selection

## Overview

This is a shell-script-only change across three existing files (`setup-auto.sh`, `stop-auto-v5.sh`, SKILL.md) plus one new helper script (`score-increment.sh`). No TypeScript, no Node.js dependencies, no new npm packages. All scoring is done via `grep`/`awk` keyword matching to stay within the stop hook's performance budget.

## Architecture

### Components

- **`score-increment.sh`** (NEW): Pure function that scores an increment directory against a text query. Reads title from metadata.json, overview from spec.md, task titles from tasks.md. Returns a numeric score 0-100 based on keyword overlap. Location: `~/.claude/commands/sw/hooks/lib/score-increment.sh`.

- **`setup-auto.sh`** (MODIFIED):
  1. Wire `$PROMPT` into `auto-mode.json` as `userGoal` field.
  2. Replace blind first-match selection with scored selection when `$PROMPT` is non-empty and no explicit IDs given.
  3. When no prompt and multiple active increments, sort by `lastActivity` from metadata.json (most recent first) instead of filesystem order.

- **`stop-auto-v5.sh`** (MODIFIED):
  1. Read `userGoal` from auto-mode.json.
  2. For each incomplete increment, extract the next pending task title.
  3. When `userGoal` is set, score increments against it and order feedback accordingly.
  4. Include enriched context in block message: goal line, next task title, progress fraction.

- **`/sw:auto` SKILL.md** (MODIFIED): Fix the `auto-mode.json` schema example to show `"userGoal": null` and add instruction for LLM to populate `userGoal` from conversation context.

### Data Flow

```
User prompt --> setup-auto.sh --> auto-mode.json { userGoal, incrementIds (scored) }
                                       |
                                       v
                              stop-auto-v5.sh reads userGoal
                                       |
                                       v
                    score-increment.sh scores each active increment
                                       |
                                       v
                    Block message with ranked increments + next task + goal
```

### Scoring Algorithm (FR-001)

Simple keyword overlap, no NLP:

1. Tokenize query into words (lowercase, strip punctuation)
2. For each increment, build a text corpus: `title + spec overview + task titles`
3. Count how many query tokens appear in the corpus
4. Score = `(matching_tokens / total_query_tokens) * 100`
5. Tiebreaker: more pending tasks = higher priority

This runs in <50ms for 10 increments (just `grep -c` calls).

## Technology Stack

- **Language**: Bash (POSIX-compatible where possible, bash-specific where needed)
- **Dependencies**: `jq` (already required by stop-auto-v5.sh), `grep`, `awk`, `tr`
- **No new dependencies**: Everything uses tools already present in the hook environment

**Architecture Decisions**:

- **Keyword scoring over LLM scoring**: Stop hook must complete in <500ms. LLM API call would take 2-5 seconds. Keyword overlap is sufficient for matching "authentication" to an increment titled "0045-user-authentication".
- **Score script as separate sourced file**: Keeps `setup-auto.sh` and `stop-auto-v5.sh` clean. Both source the same scoring function. Testable in isolation.
- **`userGoal` as plain string, not structured**: The goal captures user intent in natural language. Structured extraction would require LLM. The LLM in `/sw:auto` SKILL.md sets it from conversation context.

## Implementation Phases

### Phase 1: Foundation (score-increment.sh + userGoal wiring)
1. Create `score-increment.sh` with `score_increment()` function
2. Wire `userGoal` into `setup-auto.sh` session marker
3. Fix SKILL.md schema example

### Phase 2: Smart Selection (setup-auto.sh)
4. Replace blind first-match with scored selection
5. Add lastActivity fallback for no-prompt scenarios

### Phase 3: Stop Hook Enrichment (stop-auto-v5.sh)
6. Read userGoal and next task title in stop hook
7. Score and rank increments in block message
8. Add progress fraction to feedback

## Testing Strategy

- Unit tests for `score_increment()` function via `bats` or direct bash sourcing
- Integration tests: mock `.specweave/` directory structure, run `setup-auto.sh` with various prompts, verify correct increment selected in `auto-mode.json`
- Performance test: ensure stop hook stays under 500ms with 10 active increments
- Regression: verify single-increment and explicit-ID paths are unchanged

## Technical Challenges

### Challenge 1: Stop hook performance budget
**Solution**: All scoring is grep-based, no subprocess spawning beyond what already exists. Measured via existing `_get_duration_ms()` timing in stop-auto-v5.sh.
**Risk**: Many increments with large spec files could slow grep. Mitigation: limit spec.md read to first 50 lines (overview section).

### Challenge 2: Keyword overlap quality
**Solution**: For the stop hook use case, exact keyword match is sufficient. Users naturally use terms that appear in increment titles ("auth", "deploy", "api"). False positives are harmless -- the model will quickly realize and switch.
**Risk**: Very generic queries ("fix the bug") may not disambiguate. Mitigation: fall back to task-count ordering when scores are tied.
