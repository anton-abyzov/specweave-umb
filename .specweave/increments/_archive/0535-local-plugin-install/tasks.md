# Tasks

### T-001: Add copyPluginSkillsToProject() to plugin-copier.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-03
**Test Plan**: Given specweave root with plugins → When copyPluginSkillsToProject called → Then SKILL.md files copied to .claude/skills/

### T-002: Update plugin-installer.ts — always full install
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02
**Test Plan**: Given init → When installAllPlugins called → Then all skills copied locally, no claude plugin install

### T-003: Remove on-demand plugin install from user-prompt-submit.sh
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-03
**Test Plan**: Given user prompt → When hook fires → Then no plugin install attempted, increment detection still works

### T-004: Remove plugin install triggers from llm-plugin-detector.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**AC**: AC-US2-02
**Test Plan**: Given LLM detection → When plugins detected → Then no installation triggered

### T-005: Update init.ts — remove lazyMode flag
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**AC**: AC-US1-01
**Test Plan**: Given specweave init → When called → Then always installs all plugins (no lazy mode)
