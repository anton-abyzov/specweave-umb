---
increment: 0456-prevent-unwanted-agent-dotfolders
generated_by: sw:test-aware-planner
by_user_story:
  US-001: [T-001]
  US-002: [T-002]
  US-003: [T-003, T-004]
---

# Tasks: Prevent Unwanted Agent Dot-Folders

---

## User Story: US-001 - Fix safeProjectRoot to resolve actual project root

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 1 total, all completed

### T-001: Fix safeProjectRoot() in add.ts and add findProjectRoot import

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** `findProjectRoot()` is mocked to return `/home/user/project` while cwd is a subdirectory
- **When** `safeProjectRoot({})` is called (no `--cwd`)
- **Then** the returned value is `/home/user/project` (not cwd)

- **Given** `findProjectRoot()` returns `os.homedir()`
- **When** `safeProjectRoot({})` is called
- **Then** it silently falls back to `process.cwd()`

- **Given** `findProjectRoot()` returns `null`
- **When** `safeProjectRoot({})` is called
- **Then** it silently falls back to `process.cwd()`

- **Given** `opts.cwd` is `true`
- **When** `safeProjectRoot({ cwd: true })` is called
- **Then** it returns `process.cwd()` directly without calling `findProjectRoot()`

**Test Cases**:
1. **Unit (via add.test.ts integration)**: `src/commands/add.test.ts` — describe "addCommand smart project root resolution"
   - `findProjectRoot integration — uses resolved root when valid`: mock `mockFindProjectRoot` returning `/home/user/project`, cwd `/home/user/project/subdir`; assert `installSymlink` called with `projectRoot: "/home/user/project"`
   - `null fallback — falls back to cwd when findProjectRoot returns null`: mock returns `null`; assert `projectRoot === process.cwd()`
   - `HOME guard — falls back to cwd when findProjectRoot returns homedir`: mock returns `os.homedir()`; assert `projectRoot === process.cwd()`
   - `--cwd bypass — uses cwd directly without calling findProjectRoot`: `{ cwd: true }`; assert `projectRoot === process.cwd()` AND `mockFindProjectRoot` not called
   - **Coverage Target**: 95%

**Implementation**:
1. Open `src/commands/add.ts`
2. Add import (with `.js` extension, alongside other utils): `import { findProjectRoot } from "../utils/project-root.js";`
3. Confirm `import os from "node:os";` is present (check existing imports)
4. Replace stub at lines ~845-847 — rename `_opts` to `opts` and replace body:
   ```typescript
   function safeProjectRoot(opts: { cwd?: boolean }): string {
     if (opts.cwd) return process.cwd();
     const root = findProjectRoot(process.cwd());
     if (root === null || root === os.homedir()) return process.cwd();
     return root;
   }
   ```
5. Run `npx vitest run src/commands/add.test.ts` to confirm no regressions before touching tests

---

## User Story: US-002 - Add boundary guards in canonical installer

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 1 total, all completed

### T-002: Add path traversal guard in resolveAgentSkillsDir() and HOME guard in ensureCanonicalDir()

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** an agent definition with `localSkillsDir: "../../etc"` and `projectRoot: "/home/user/project"`
- **When** `resolveAgentSkillsDir()` is called for a non-global install
- **Then** it throws an error containing "escapes project root"

- **Given** `base === os.homedir()` and `global: false`
- **When** `ensureCanonicalDir(os.homedir(), false)` is called
- **Then** it throws an error referencing HOME directory

- **Given** `base` is a normal project subdirectory of HOME
- **When** `ensureCanonicalDir(join(tempDir, "project"), false)` is called
- **Then** it creates the directory normally without throwing

**Test Cases**:
1. **Unit (real fs via canonical.test.ts)**: `src/installer/canonical.test.ts`
   - `resolveAgentSkillsDir — rejects ../  traversal`: agent `localSkillsDir: "../../etc"`, projectRoot `/home/user/project`, global false; assert throws "escapes project root"
   - `resolveAgentSkillsDir — allows normal localSkillsDir`: agent `localSkillsDir: ".cursor/skills"`, projectRoot `tempDir`; assert returns `join(tempDir, ".cursor/skills")`
   - `resolveAgentSkillsDir — global install bypasses traversal check`: global true; assert no throw, returns globalSkillsDir-derived path
   - `ensureCanonicalDir — throws for HOME non-global`: `ensureCanonicalDir(os.homedir(), false)`; assert throws
   - `ensureCanonicalDir — allows HOME subdirectory for non-global`: `ensureCanonicalDir(join(tempDir, "project"), false)`; assert no throw, creates dir
   - `ensureCanonicalDir — allows HOME for global`: `ensureCanonicalDir(os.homedir(), true)`; assert no throw
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/installer/canonical.ts`
2. Add `export` keyword to `resolveAgentSkillsDir` function declaration
3. Add path traversal guard after `join()` inside the non-global branch:
   ```typescript
   export function resolveAgentSkillsDir(agent: AgentDefinition, opts: InstallOptions): string {
     if (opts.global) {
       return expandTilde(agent.globalSkillsDir);
     }
     const resolved = join(opts.projectRoot, agent.localSkillsDir);
     if (!resolved.startsWith(opts.projectRoot)) {
       throw new Error(
         `Agent "${agent.id}" localSkillsDir escapes project root: ${agent.localSkillsDir}`
       );
     }
     return resolved;
   }
   ```
4. Add HOME guard to `ensureCanonicalDir` before the non-global dir creation:
   ```typescript
   export function ensureCanonicalDir(base: string, global: boolean): string {
     if (global) {
       const dir = join(os.homedir(), ".agents", "skills");
       mkdirSync(dir, { recursive: true });
       return dir;
     }
     if (base === os.homedir()) {
       throw new Error(
         "Refusing to install project-scoped skills in HOME directory. Use --global or run from a project directory."
       );
     }
     const dir = join(base, ".agents", "skills");
     mkdirSync(dir, { recursive: true });
     return dir;
   }
   ```
5. Run `npx vitest run src/installer/canonical.test.ts` to confirm no regressions

---

## User Story: US-003 - Update and expand test coverage

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 2 total, all completed

### T-003: Update TC-012 and add new safeProjectRoot tests in add.test.ts

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** TC-012 describes the old stub behavior (always returns cwd)
- **When** the test is updated to reflect `safeProjectRoot()` using `findProjectRoot()`
- **Then** the test passes with the new implementation

- **Given** four new it() blocks cover all branches of safeProjectRoot()
- **When** `npx vitest run src/commands/add.test.ts` runs
- **Then** all new tests pass

**Test Cases**:
1. **Unit**: `src/commands/add.test.ts` — describe "addCommand smart project root resolution"
   - **TC-012 update**: rename test to "uses findProjectRoot() result when valid root is returned"; set `mockFindProjectRoot` to a distinct project path; assert `projectRoot` matches that path (not cwd)
   - **new TC-012a**: findProjectRoot returns valid root above cwd; assert `projectRoot` is the returned root
   - **new TC-012b**: findProjectRoot returns `null`; assert `projectRoot === process.cwd()`
   - **new TC-012c**: findProjectRoot returns `os.homedir()`; assert `projectRoot === process.cwd()`
   - **new TC-012d**: `opts.cwd: true`; assert `projectRoot === process.cwd()` and `mockFindProjectRoot` not called
   - **Coverage Target**: 95%

**Implementation**:
1. Open `src/commands/add.test.ts`
2. Add `import os from "node:os";` near the top if not already present
3. Locate `describe("addCommand smart project root resolution", ...)` at line ~1439
4. Update TC-012 at line ~1464:
   - Change description: "uses findProjectRoot() result as projectRoot when valid"
   - Override `mockFindProjectRoot.mockReturnValue("/home/user/project")` at start of test
   - Assert `callArgs[3].projectRoot` equals `"/home/user/project"` (not cwd)
5. Add four new `it()` blocks after the existing TC-012 and before `afterEach`:
   ```typescript
   it("TC-012a: uses findProjectRoot() result when valid root above cwd", async () => {
     const projectRoot = "/home/user/project";
     mockFindProjectRoot.mockReturnValue(projectRoot);
     vi.spyOn(process, "cwd").mockReturnValue("/home/user/project/subdir");
     await addCommand("owner/safe-repo", {});
     const callArgs = mockInstallSymlink.mock.calls[0];
     expect(callArgs[3].projectRoot).toBe(projectRoot);
   });

   it("TC-012b: falls back to cwd when findProjectRoot returns null", async () => {
     mockFindProjectRoot.mockReturnValue(null);
     const cwd = process.cwd();
     await addCommand("owner/safe-repo", {});
     const callArgs = mockInstallSymlink.mock.calls[0];
     expect(callArgs[3].projectRoot).toBe(cwd);
   });

   it("TC-012c: falls back to cwd when findProjectRoot returns homedir (HOME guard)", async () => {
     mockFindProjectRoot.mockReturnValue(os.homedir());
     const cwd = process.cwd();
     await addCommand("owner/safe-repo", {});
     const callArgs = mockInstallSymlink.mock.calls[0];
     expect(callArgs[3].projectRoot).toBe(cwd);
   });

   it("TC-012d: --cwd bypass skips findProjectRoot entirely", async () => {
     mockFindProjectRoot.mockClear();
     const cwd = process.cwd();
     await addCommand("owner/safe-repo", { cwd: true });
     expect(mockFindProjectRoot).not.toHaveBeenCalled();
     const callArgs = mockInstallSymlink.mock.calls[0];
     expect(callArgs[3].projectRoot).toBe(cwd);
   });
   ```
6. Run `npx vitest run src/commands/add.test.ts` — all tests must pass

---

### T-004: Add boundary guard tests in canonical.test.ts

**User Story**: US-003
**Satisfies ACs**: AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** `resolveAgentSkillsDir` is now exported from `canonical.ts`
- **When** called with a `../` traversal path
- **Then** it throws "escapes project root"

- **Given** `ensureCanonicalDir` is called with `os.homedir()` and `global: false`
- **When** it runs
- **Then** it throws referencing HOME directory

**Test Cases**:
1. **Unit (real fs)**: `src/installer/canonical.test.ts`
   - New `describe("resolveAgentSkillsDir", ...)` block — 3 tests (traversal reject, normal allow, global bypass)
   - Extended `describe("ensureCanonicalDir", ...)` — 3 new tests (HOME throw, subdir allow, global HOME allow)
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/installer/canonical.test.ts`
2. Update named import at line 6-11 to include `resolveAgentSkillsDir`:
   ```typescript
   import {
     installSymlink,
     installCopy,
     createRelativeSymlink,
     ensureCanonicalDir,
     resolveAgentSkillsDir,
   } from "./canonical.js";
   ```
3. Add `import os from "node:os";` after existing imports
4. Add new `describe("resolveAgentSkillsDir", ...)` block inside the outer `describe("canonical installer", ...)`, placed before `describe("installSymlink", ...)`:
   ```typescript
   describe("resolveAgentSkillsDir", () => {
     it("throws when localSkillsDir escapes projectRoot via ../", () => {
       const agent = makeAgent({ localSkillsDir: "../../etc" });
       expect(() =>
         resolveAgentSkillsDir(agent, { global: false, projectRoot: "/home/user/project" })
       ).toThrow("escapes project root");
     });

     it("returns joined path for normal localSkillsDir", () => {
       const agent = makeAgent({ localSkillsDir: ".cursor/skills" });
       const result = resolveAgentSkillsDir(agent, { global: false, projectRoot: tempDir });
       expect(result).toBe(join(tempDir, ".cursor/skills"));
     });

     it("bypasses traversal check for global installs", () => {
       const agent = makeAgent({
         localSkillsDir: "../../etc",
         globalSkillsDir: "~/.cursor/skills",
       });
       expect(() =>
         resolveAgentSkillsDir(agent, { global: true, projectRoot: "/any" })
       ).not.toThrow();
     });
   });
   ```
5. Extend existing `describe("ensureCanonicalDir", ...)` block with three new tests:
   ```typescript
   it("throws when base is HOME directory for non-global install", () => {
     expect(() => ensureCanonicalDir(os.homedir(), false)).toThrow();
   });

   it("allows subdirectory of HOME for non-global install", () => {
     const projectDir = join(tempDir, "project");
     expect(() => ensureCanonicalDir(projectDir, false)).not.toThrow();
   });

   it("allows HOME as base for global install", () => {
     expect(() => ensureCanonicalDir(os.homedir(), true)).not.toThrow();
   });
   ```
6. Run `npx vitest run src/installer/canonical.test.ts` — all tests pass
7. Run full suite: `npx vitest run` from `repositories/anton-abyzov/vskill/` — no regressions
