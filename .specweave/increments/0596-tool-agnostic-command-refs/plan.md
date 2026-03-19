# Plan: Tool-Agnostic Command References

## Architecture Decision

**Canonical format**: `sw:do` (namespace:command, no leading slash)

Rationale:
- `/sw:do` is Claude-specific (the `/` triggers Claude's skill system)
- `specweave do` is misleading — most commands are NOT CLI commands (LLM skill activations)
- `sw:do` is the actual identifier, already used in CLAUDE.md backtick contexts

## Files to Modify

| File | Changes | Risk |
|------|---------|------|
| AGENTS.md.template | ~29 substitutions + new "How to Invoke" section | Low |
| agents-md-compiler.ts | ~7 substitutions (eliminate `/specweave.` format) | Low |
| README.md.template | ~17 substitutions + prose changes | Low |
| tasks.md.template | 2 substitutions | Trivial |
| CLAUDE.md.template | Add 1-line mapping note (keep all `/sw:`) | Trivial |

## Testing

- Grep for remaining `/sw:` in modified templates (should be zero, except Claude-specific columns)
- Grep for `/specweave.` in compiler (should be zero)
- Verify CLAUDE.md.template retains all `/sw:` references
