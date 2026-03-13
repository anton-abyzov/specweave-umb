# Plan: Remove scope selection prompt

## Architecture Decision

Remove the 7-line scope selection prompt from `promptInstallOptions()` in `add.ts`.
Replace with a single line that defaults to project scope unless `opts.global` is set.

The `--global` flag pathway is preserved for explicit opt-in.

## Changes

### `src/commands/add.ts` (lines ~809-816)

Remove:
```typescript
if (!opts.global && !opts.cwd) {
  const prompter2 = createPrompter();
  const scopeIdx = await prompter2.promptChoice("Installation scope:", [
    { label: "Project", hint: "install in current project root" },
    { label: "Global", hint: "install in user home directory" },
  ]);
  useGlobal = scopeIdx === 1;
}
```

Replace with:
```typescript
useGlobal = !!opts.global;
```

### `src/commands/add.test.ts`

Remove or update tests that mock the scope prompt (`promptChoice` for "Installation scope:").
Tests expecting project-scope installation now pass without the mock.

### `package.json`

Bump: `0.4.15` → `0.4.16`
