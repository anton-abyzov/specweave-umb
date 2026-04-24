# 0693 Tasks — Registry DRY (12 tasks)

## T-001: Add NON_AGENT_CONFIG_DIRS export to agents-registry.ts
**User Story**: US-002 | **AC**: AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given the registry module, When importing `NON_AGENT_CONFIG_DIRS`, Then it equals the 8-entry frozen array `[.specweave, .vscode, .idea, .zed, .devcontainer, .github, .agents, .agent]`.

## T-002: Migrate skill-scanner.ts to import NON_AGENT_CONFIG_DIRS
**User Story**: US-002 | **AC**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given a fixture project, When `getInstalledPrefixes()` runs, Then the returned union of agent prefixes + non-agent dirs is unchanged from baseline (snapshot).

## T-003: Create generate-agents-json.ts build script
**User Story**: US-003 | **AC**: AC-US3-01 | **Status**: [x] completed
**Test Plan**: Given AGENTS_REGISTRY and NON_AGENT_CONFIG_DIRS, When the script runs, Then `vskill/agents.json` exists with shape `{version, generatedAt, agentPrefixes[], nonAgentConfigDirs[]}` and prefix count matches registry-derived count.

## T-004: Wire build script into vskill pipeline
**User Story**: US-003 | **AC**: AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given a fresh checkout, When `npm run build` runs in vskill, Then `vskill/agents.json` is produced as a side effect (no separate command needed).

## T-005: Add prebuild copy script in vskill-platform
**User Story**: US-003 | **AC**: AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given vskill's `agents.json` exists, When vskill-platform's `npm run prebuild` runs, Then copies appear at `crawl-worker/agents.json` and `src/lib/agents.json`. Missing source → loud failure with actionable message.

## T-006: Refactor skill-path-validation.ts to load from agents.json
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given the validator, When called with a path under `.cursor/agents/foo.md`, Then it accepts; When called with `.bogus/agents/foo.md`, Then it rejects. Behavior identical to pre-refactor.

## T-007: Refactor crawl-worker/sources/queue-processor.js to load from agents.json
**User Story**: US-001 | **AC**: AC-US1-02, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given a queue message, When the processor categorizes a `.cursor/`-rooted file, Then it routes to the correct queue. Same routing as before refactor.

## T-008: Refactor crawl-worker/lib/repo-files.js to load from agents.json
**User Story**: US-001 | **AC**: AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given a fixture repo with `.claude/agents/x.md` + `.bogus/y.md`, When `walkRepoFiles()` runs, Then it returns the agent file and skips the bogus one.

## T-009: Delete the 3 hardcoded AGENT_CONFIG_PREFIXES arrays
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given `grep -R "AGENT_CONFIG_PREFIXES = \[" repositories/anton-abyzov/vskill-platform/`, Then zero matches (only imports/derived names remain).

## T-010: Integration test — new agent flows to all 4 consumers
**User Story**: US-001, US-002, US-003 | **AC**: AC-US1-04, AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given a temp agent added to AGENTS_REGISTRY with prefix `testagent`, When `npm run build` runs in vskill and `npm run prebuild` runs in vskill-platform, Then `testagent` appears in skill-scanner output, skill-path-validation accepts `.testagent/agents/x.md`, and both crawl-worker files include it.

## T-011: Update vskill-platform README/CONTRIBUTING with new flow
**User Story**: US-003 | **AC**: AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given the docs, When a contributor reads CONTRIBUTING, Then they find a "How to add a new agent prefix" section pointing to `vskill/src/agents/agents-registry.ts` and noting the prebuild step.

## T-012: Smoke test — full build from scratch in both repos
**User Story**: US-001, US-002, US-003 | **AC**: all | **Status**: [x] completed
**Test Plan**: Given clean `node_modules`, When `npm ci && npm run build` runs in both repos sequentially, Then both succeed with zero errors and `agents.json` artifacts are present.
