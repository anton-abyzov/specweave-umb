# Tasks: LLM-Native Multilingual Support

**Increment**: 0006-llm-native-i18n
**Created**: 2025-11-02
**Status**: In Progress

---

## Task Overview

| Phase | Tasks | Status | Assignee |
|-------|-------|--------|----------|
| **Phase 1: Core Infrastructure** | T-001 to T-008 | [ ] Pending | Auto |
| **Phase 2: Translator Plugin** | T-009 to T-015 | [ ] Pending | Auto |
| **Phase 3: Adapter Integration** | T-016 to T-022 | [ ] Pending | Auto |
| **Phase 4: CLI Internationalization** | T-023 to T-028 | [ ] Pending | Auto |
| **Phase 5: Living Docs Translation** | T-029 to T-033 | [ ] Pending | Auto |
| **Phase 6: Testing** | T-034 to T-042 | [ ] Pending | Auto |
| **Phase 7: Documentation** | T-043 to T-045 | [ ] Pending | Auto |

**Total Tasks**: 53 (45 i18n + 8 increment discipline)
**Estimated Effort**: 12-14 days

---

## Phase 0: Increment Discipline Enforcement (NEW - Priority P0)

**CRITICAL**: This phase implements strict increment discipline to prevent multiple incomplete increments.

### T-000: Create IncrementStatusDetector Utility
**User Story**: [US-001: Russian Developer Initializes Project](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-001-russian-developer-initializes-project.md)


**Status**: [x] Completed

**User Story**: [US-001: Russian Developer Initializes Project](../../docs/internal/specs/default/llm-native-i18n/us-001-*.md)

**AC**: AC-US001-01, AC-US001-02, AC-US001-03
**Priority**: P0
**Dependencies**: None
**Estimated Effort**: 2 hours

**Description**:
Create utility to detect increment completion status.

**Files**:
- `src/core/increment-status.ts` (new) ✅

**Implementation**: COMPLETE
- Class `IncrementStatusDetector` with methods:
  - `getStatus(id)` - Get status of specific increment
  - `getAllIncomplete()` - Find all incomplete increments
  - `getLatest()` - Get latest increment ID
  - `isComplete(id)` - Check if increment is complete
- Parses tasks.md to count completed/pending tasks
- Detects COMPLETION-SUMMARY.md markers
- Returns detailed status with pending task lists

**Acceptance Criteria**:
- ✅ Detects incomplete increments
- ✅ Parses tasks.md correctly
- ✅ Returns completion percentage
- ✅ Lists pending tasks

---

### T-001-DISCIPLINE: Create /specweave:status Command

**Status**: [x] Completed
**Priority**: P0
**Dependencies**: T-000
**Estimated Effort**: 1 hour

**Description**:
Create command to show status of all increments.

**Files**:
- `src/commands/specweave-status.md` (new) ✅

**Implementation**: COMPLETE
- Shows completion status for all increments
- Highlights incomplete work
- Offers guidance on how to proceed

**Acceptance Criteria**:
- ✅ Command file created
- ✅ Uses IncrementStatusDetector
- ✅ Clear output format

---

### T-002-DISCIPLINE: Create /specweave:close Command

**Status**: [x] Completed
**Priority**: P0
**Dependencies**: T-000
**Estimated Effort**: 3 hours

**Description**:
Interactive command to close incomplete increments.

**Files**:
- `src/commands/specweave-close-previous.md` (new) ✅

**Implementation**: COMPLETE
- Interactive workflow with 4 options:
  1. Force complete (mark all done)
  2. Move tasks to next increment
  3. Reduce scope (mark won't-do)
  4. Create completion report
- Uses inquirer for UX
- Creates documentation for all closures

**Acceptance Criteria**:
- ✅ Command file created
- ✅ All 4 closure options implemented
- ✅ Creates completion reports

---

### T-003-DISCIPLINE: Add Pre-Flight Validation to /specweave:inc

**Status**: [x] Completed
**Priority**: P0
**Dependencies**: T-000
**Estimated Effort**: 2 hours

**Description**:
Add strict pre-flight check to increment command.

**Files**:
- `commands/specweave:increment.md` (update) ✅

**Implementation**: COMPLETE
- Step 0A: STRICT Pre-Flight Check (MANDATORY)
- Hard block if incomplete increments found
- Shows pending tasks
- Offers 3 resolution paths
- `--force` flag for emergencies

**Acceptance Criteria**:
- ✅ Blocks new increment if previous incomplete
- ✅ Clear error messages
- ✅ Helpful guidance provided
- ✅ Force flag documented

---

### T-004-DISCIPLINE: Update CLAUDE.md with Increment Discipline Rules

**Status**: [x] Completed
**Priority**: P0
**Dependencies**: All discipline tasks
**Estimated Effort**: 2 hours

**Description**:
Document the increment discipline rules in CLAUDE.md.

**Files**:
- `CLAUDE.md` (update) ✅

**Implementation**: COMPLETE
- Added comprehensive section: "Increment Discipline (v0.6.0+ MANDATORY)"
- Explains the Iron Rule
- Shows enforcement examples
- Documents 3 options for closing
- Philosophy: Discipline = Quality

**Acceptance Criteria**:
- ✅ Section added to CLAUDE.md
- ✅ Examples provided
- ✅ Helper commands documented
- ✅ Philosophy explained

---

### T-005-DISCIPLINE: Update PM Agent with Validation

**Status**: [x] Completed
**Priority**: P1
**Dependencies**: T-003-DISCIPLINE
**Estimated Effort**: 1 hour

**Description**:
Add validation reminder to PM agent.

**Files**:
- `agents/pm/AGENT.md` (update) ✅

**Implementation**:
Add to PM agent prompt:
```markdown
## Increment Discipline (CRITICAL)

Before planning new increment, ALWAYS check for incomplete increments:

1. Use IncrementStatusDetector to find incomplete work
2. If found, BLOCK and direct user to /specweave:close
3. Never plan new increment with incomplete previous work

This is NON-NEGOTIABLE. Enforce the Iron Rule.
```

**Acceptance Criteria**:
- ✅ PM agent aware of discipline rule
- ✅ Validation step documented
- ✅ Clear blocking behavior

---

### T-006-DISCIPLINE: Close Increments 0002 and 0003

**Status**: [x] Completed
**Priority**: P0
**Dependencies**: T-002-DISCIPLINE
**Estimated Effort**: 1 hour

**Description**:
Close incomplete increments to enforce discipline.

**Files**:
- `.specweave/increments/0002-core-enhancements/COMPLETION-SUMMARY.md` (new) ✅
- `.specweave/increments/0003-intelligent-model-selection/COMPLETION-SUMMARY.md` (new) ✅

**Implementation**: COMPLETE
- 0002: Force-closed (73% complete, core work done)
- 0003: Deferred to 0007 (50% complete, advanced features)
- Created completion summaries for both
- Documented closure rationale

**Acceptance Criteria**:
- ✅ Both increments closed
- ✅ Completion reports created
- ✅ Rationale documented

---

### T-007-DISCIPLINE: Build and Test Enforcement

**Status**: [x] Completed
**Priority**: P1
**Dependencies**: T-000 through T-004-DISCIPLINE
**Estimated Effort**: 2 hours

**Description**:
Build TypeScript code and test enforcement.

**Files**:
- Build output in `dist/`

**Implementation**:
```bash
# Build
npm run build

# Test increment status detector
node -e "
const { IncrementStatusDetector } = require('./dist/core/increment-status');
const detector = new IncrementStatusDetector();
detector.getAllIncomplete().then(console.log);
"

# Test enforcement
/specweave:status
/specweave:inc "test" # Should work (no incomplete)
```

**Acceptance Criteria**:
- ✅ TypeScript compiles
- ✅ IncrementStatusDetector works
- ✅ Commands execute correctly
- ✅ Enforcement blocks when expected

---

### T-008-DISCIPLINE: Update CHANGELOG.md

**Status**: [x] Completed
**Priority**: P1
**Dependencies**: All discipline tasks
**Estimated Effort**: 30 minutes

**Description**:
Document increment discipline in CHANGELOG.

**Files**:
- `CHANGELOG.md` (update)

**Implementation**:
Add v0.6.0 section:
```markdown
## [0.6.0] - 2025-11-02

### Added
- **Increment Discipline Enforcement**: Strict rule - cannot start N+1 until N is DONE
- `/specweave:status` - Show completion status of all increments
- `/specweave:close` - Interactive increment closure
- `IncrementStatusDetector` - Utility to detect incomplete work
- Pre-flight validation in `/specweave:inc` command

### Changed
- `/specweave:inc` now blocks if previous increments incomplete
- Enforces completion before starting new work

### Breaking Changes
- None (enforcement can be bypassed with `--force` flag)
```

**Acceptance Criteria**:
- ✅ CHANGELOG updated
- ✅ v0.6.0 section added
- ✅ All features documented

---

## Phase 1: Core Infrastructure

### T-001: Create Type Definitions
**User Story**: [US-001: Russian Developer Initializes Project](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-001-russian-developer-initializes-project.md)


**Status**: [ ] Pending

**User Story**: [US-001: Russian Developer Initializes Project](../../docs/internal/specs/default/llm-native-i18n/us-001-*.md)

**AC**: AC-US001-01, AC-US001-02, AC-US001-03
**Priority**: P0
**Dependencies**: None
**Estimated Effort**: 1 hour

**Description**:
Create TypeScript type definitions for i18n system.

**Files**:
- `src/core/i18n/types.ts` (new)

**Implementation**:

```typescript
// src/core/i18n/types.ts
export type SupportedLanguage =
  | 'en'
  | 'ru'
  | 'es'
  | 'zh'
  | 'de'
  | 'fr'
  | 'ja'
  | 'ko'
  | 'pt';

export interface TranslateOptions {
  targetLanguage: SupportedLanguage;
  contextType?: 'cli' | 'template' | 'docs' | 'living-docs' | 'code-comments';
  preserveMarkdown?: boolean;
  preserveCodeBlocks?: boolean;
  keepFrameworkTerms?: boolean;
  keepTechnicalTerms?: boolean;
}

export interface LocaleStrings {
  [key: string]: string | LocaleStrings;
}

export interface TranslationConfig {
  method: 'in-session';
  autoTranslateLivingDocs?: boolean;
  keepFrameworkTerms?: boolean;
  keepTechnicalTerms?: boolean;
  translateCodeComments?: boolean;
  translateVariableNames?: boolean;
}

export interface I18nConfig {
  language: SupportedLanguage;
  translation?: TranslationConfig;
}
```

**Acceptance Criteria**:
- ✅ All types exported
- ✅ TypeScript compilation succeeds
- ✅ No type errors in IDE

**Tests**:
- No tests (type definitions only)

---

### T-002: Implement LanguageManager Class
**User Story**: [US-001: Russian Developer Initializes Project](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-001-russian-developer-initializes-project.md)


**Status**: [ ] Pending

**User Story**: [US-001: Russian Developer Initializes Project](../../docs/internal/specs/default/llm-native-i18n/us-001-*.md)

**AC**: AC-US001-01, AC-US001-02, AC-US001-03
**Priority**: P0
**Dependencies**: T-001
**Estimated Effort**: 4 hours

**Description**:
Create `LanguageManager` class for language detection, system prompt generation, and translation coordination.

**Files**:
- `src/core/i18n/language-manager.ts` (new)

**Implementation**:

```typescript
// src/core/i18n/language-manager.ts
import * as path from 'path';
import fs from 'fs-extra';
import {
  SupportedLanguage,
  TranslateOptions,
  LocaleStrings,
  I18nConfig,
} from './types.js';

export class LanguageManager {
  private language: SupportedLanguage;
  private config: I18nConfig;
  private localeCache: Map<string, LocaleStrings> = new Map();

  constructor(config: I18nConfig) {
    this.language = config.language || 'en';
    this.config = config;
  }

  /**
   * Get current language
   */
  getLanguage(): SupportedLanguage {
    return this.language;
  }

  /**
   * Generate system prompt for injection into skills/agents/commands
   */
  getSystemPrompt(): string {
    if (this.language === 'en') return '';

    const languageNames: Record<SupportedLanguage, string> = {
      en: 'English',
      ru: 'Russian (Русский)',
      es: 'Spanish (Español)',
      zh: 'Chinese (中文)',
      de: 'German (Deutsch)',
      fr: 'French (Français)',
      ja: 'Japanese (日本語)',
      ko: 'Korean (한국어)',
      pt: 'Portuguese (Português)',
    };

    const langName = languageNames[this.language];

    return `
**LANGUAGE INSTRUCTION**:
- All responses, generated content, and documentation must be in ${langName}
- Code comments should be in ${langName}
- Variable/function names remain in English (programming convention)
- Technical terms (Git, Docker, Kubernetes, npm, TypeScript, etc.) remain in English
- Framework terms (Increment, Living Docs, SpecWeave, ADR, RFC) remain in English
- User-facing text, explanations, and documentation must be in ${langName}

---

`.trim();
  }

  /**
   * Check if locale files exist for current language
   */
  hasLocale(): boolean {
    const localePath = this.getLocalePath();
    return fs.existsSync(path.join(localePath, 'cli.json'));
  }

  /**
   * Load translated strings for given type
   */
  loadStrings(type: 'cli' | 'errors' | 'templates'): LocaleStrings {
    const cacheKey = `${this.language}:${type}`;

    // Check cache first
    if (this.localeCache.has(cacheKey)) {
      return this.localeCache.get(cacheKey)!;
    }

    // Load from file
    const localePath = this.getLocalePath();
    const filePath = path.join(localePath, `${type}.json`);

    if (!fs.existsSync(filePath)) {
      // Fallback to English
      const fallbackPath = path.join(
        this.getLocalePath('en'),
        `${type}.json`
      );
      if (fs.existsSync(fallbackPath)) {
        const strings = JSON.parse(fs.readFileSync(fallbackPath, 'utf-8'));
        return strings;
      }
      return {};
    }

    const strings = JSON.parse(fs.readFileSync(filePath, 'utf-8'));

    // Cache it
    this.localeCache.set(cacheKey, strings);

    return strings;
  }

  /**
   * Get translated string (i18n.t() helper)
   */
  t(key: string, params?: Record<string, string>): string {
    const keys = key.split('.');
    const type = keys[0] as 'cli' | 'errors' | 'templates';

    // Load strings for type
    const strings = this.loadStrings(type);

    // Navigate to nested value
    let value: any = strings;
    for (const k of keys.slice(1)) {
      value = value?.[k];
    }

    if (typeof value !== 'string') {
      // Return key if not found (fallback)
      return key;
    }

    // Replace placeholders
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        value = value.replace(`{${k}}`, v);
      });
    }

    return value;
  }

  /**
   * Request translation via translator skill
   * (This will be implemented in Phase 2 when plugin exists)
   */
  async translate(text: string, options: TranslateOptions): Promise<string> {
    // TODO: Implement in T-011 (after translator skill exists)
    // For now, return text as-is
    return text;
  }

  /**
   * Get locale directory path
   */
  private getLocalePath(lang?: SupportedLanguage): string {
    const language = lang || this.language;
    // This assumes we're in dist/ after compilation
    return path.join(__dirname, '../../src/locales', language);
  }
}
```

**Acceptance Criteria**:
- ✅ Class instantiates with config
- ✅ `getLanguage()` returns correct language
- ✅ `getSystemPrompt()` returns correct prompt for Russian
- ✅ `getSystemPrompt()` returns empty string for English
- ✅ `hasLocale()` checks for locale files
- ✅ `loadStrings()` loads JSON files
- ✅ `t()` method resolves nested keys
- ✅ `t()` replaces placeholders correctly
- ✅ Fallback to English if locale missing

**Tests**:
- Unit tests in T-034

---

### T-003: Update Config Schema
**User Story**: [US-001: Russian Developer Initializes Project](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-001-russian-developer-initializes-project.md)


**Status**: [ ] Pending

**User Story**: [US-001: Russian Developer Initializes Project](../../docs/internal/specs/default/llm-native-i18n/us-001-*.md)

**AC**: AC-US001-01, AC-US001-02, AC-US001-03
**Priority**: P0
**Dependencies**: T-001
**Estimated Effort**: 1 hour

**Description**:
Update `specweave-config.schema.json` to include i18n fields.

**Files**:
- `src/core/schemas/specweave-config.schema.json` (update)
- `src/core/types/config.ts` (update)

**Implementation**:

Update schema:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "version": {
      "type": "string"
    },
    "language": {
      "type": "string",
      "enum": ["en", "ru", "es", "zh", "de", "fr", "ja", "ko", "pt"],
      "default": "en",
      "description": "Primary language for generated content and CLI"
    },
    "translation": {
      "type": "object",
      "properties": {
        "method": {
          "type": "string",
          "enum": ["in-session"],
          "default": "in-session"
        },
        "autoTranslateLivingDocs": {
          "type": "boolean",
          "default": false
        },
        "keepFrameworkTerms": {
          "type": "boolean",
          "default": true
        },
        "keepTechnicalTerms": {
          "type": "boolean",
          "default": true
        },
        "translateCodeComments": {
          "type": "boolean",
          "default": true
        },
        "translateVariableNames": {
          "type": "boolean",
          "default": false
        }
      }
    }
  }
}
```

Update TypeScript types:
```typescript
// src/core/types/config.ts (update)
export interface SpecweaveConfig {
  version: string;
  language?: SupportedLanguage;
  translation?: TranslationConfig;
  // ... existing fields
}
```

**Acceptance Criteria**:
- ✅ Schema validates correctly
- ✅ All enum values present
- ✅ TypeScript types match schema
- ✅ No compilation errors

**Tests**:
- Config validation tests (existing)

---

### T-004: Create Locale Directory Structure
**User Story**: [US-001: Russian Developer Initializes Project](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-001-russian-developer-initializes-project.md)


**Status**: [ ] Pending

**User Story**: [US-001: Russian Developer Initializes Project](../../docs/internal/specs/default/llm-native-i18n/us-001-*.md)

**AC**: AC-US001-01, AC-US001-02, AC-US001-03
**Priority**: P0
**Dependencies**: None
**Estimated Effort**: 30 minutes

**Description**:
Create directory structure for locale files.

**Files**:
- `src/locales/en/cli.json` (new)
- `src/locales/en/errors.json` (new)
- `src/locales/en/templates.json` (new)
- `src/locales/ru/.gitkeep` (new)
- `src/locales/es/.gitkeep` (new)

**Implementation**:

```bash
mkdir -p src/locales/{en,ru,es}
touch src/locales/en/{cli.json,errors.json,templates.json}
touch src/locales/ru/.gitkeep
touch src/locales/es/.gitkeep
```

Create empty English files:

`src/locales/en/cli.json`:
```json
{
  "init": {
    "welcome": "🚀 SpecWeave Initialization",
    "projectName": "Project name:",
    "detectingTool": "Detecting AI tool...",
    "complete": "✨ Initialization complete!"
  }
}
```

`src/locales/en/errors.json`:
```json
{
  "fileNotFound": "❌ File not found: {path}",
  "invalidConfig": "❌ Invalid configuration",
  "networkError": "❌ Network error: {message}"
}
```

`src/locales/en/templates.json`:
```json
{
  "projectName": "{PROJECT_NAME}",
  "description": "Project description"
}
```

**Acceptance Criteria**:
- ✅ Directory structure exists
- ✅ English locale files present
- ✅ Valid JSON in all files
- ✅ Placeholder directories for ru, es

**Tests**:
- No tests (directory structure)

---

### T-005: Implement Locale Loading in CLI
**User Story**: [US-001: Russian Developer Initializes Project](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-001-russian-developer-initializes-project.md)


**Status**: [ ] Pending

**User Story**: [US-001: Russian Developer Initializes Project](../../docs/internal/specs/default/llm-native-i18n/us-001-*.md)

**AC**: AC-US001-01, AC-US001-02, AC-US001-03
**Priority**: P1
**Dependencies**: T-002, T-004
**Estimated Effort**: 2 hours

**Description**:
Update CLI commands to load and use locale strings instead of hardcoded text.

**Files**:
- `src/cli/commands/init.ts` (update)
- `src/cli/index.ts` (update)

**Implementation**:

```typescript
// src/cli/commands/init.ts (update)
import { LanguageManager } from '../../core/i18n/language-manager.js';

export async function initCommand(
  projectName?: string,
  options: InitOptions = {}
): Promise<void> {
  // Load language manager
  const language = options.language || 'en';
  const langManager = new LanguageManager({ language });

  // Use translated strings
  console.log(chalk.blue.bold(`\n${langManager.t('cli.init.welcome')}\n`));

  // ... rest of init logic with translated strings
  const { name } = await inquirer.prompt([{
    type: 'input',
    name: 'name',
    message: langManager.t('cli.init.projectName'),
    // ...
  }]);

  // ...

  console.log(chalk.green(langManager.t('cli.init.complete')));
}
```

**Acceptance Criteria**:
- ✅ LanguageManager instantiated with config language
- ✅ All console.log() use langManager.t()
- ✅ All inquirer prompts use langManager.t()
- ✅ CLI works in English (default)
- ✅ No hardcoded strings remaining

**Tests**:
- Integration tests in T-036, T-037

---

### T-006: Write Unit Tests for LanguageManager
**User Story**: [US-002: Generate Specification in Russian](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-002-generate-specification-in-russian.md)


**Status**: [ ] Pending

**User Story**: [US-002: Generate Specification in Russian](../../docs/internal/specs/default/llm-native-i18n/us-002-*.md)

**AC**: AC-US002-01, AC-US002-02, AC-US002-03
**Priority**: P1
**Dependencies**: T-002
**Estimated Effort**: 2 hours

**Description**:
Create comprehensive unit tests for LanguageManager class.

**Files**:
- `tests/unit/i18n/language-manager.test.ts` (new)

**Implementation**:

```typescript
// tests/unit/i18n/language-manager.test.ts
import { LanguageManager } from '../../../src/core/i18n/language-manager';

describe('LanguageManager', () => {
  describe('getLanguage()', () => {
    it('should return configured language', () => {
      const langManager = new LanguageManager({ language: 'ru' });
      expect(langManager.getLanguage()).toBe('ru');
    });

    it('should default to English', () => {
      const langManager = new LanguageManager({} as any);
      expect(langManager.getLanguage()).toBe('en');
    });
  });

  describe('getSystemPrompt()', () => {
    it('should return Russian system prompt', () => {
      const langManager = new LanguageManager({ language: 'ru' });
      const prompt = langManager.getSystemPrompt();

      expect(prompt).toContain('LANGUAGE INSTRUCTION');
      expect(prompt).toContain('Russian (Русский)');
      expect(prompt).toContain('Framework terms');
    });

    it('should return empty string for English', () => {
      const langManager = new LanguageManager({ language: 'en' });
      const prompt = langManager.getSystemPrompt();

      expect(prompt).toBe('');
    });

    it('should return Spanish system prompt', () => {
      const langManager = new LanguageManager({ language: 'es' });
      const prompt = langManager.getSystemPrompt();

      expect(prompt).toContain('Spanish (Español)');
    });
  });

  describe('loadStrings()', () => {
    it('should load CLI strings for English', () => {
      const langManager = new LanguageManager({ language: 'en' });
      const strings = langManager.loadStrings('cli');

      expect(strings).toHaveProperty('init');
      expect(strings.init).toHaveProperty('welcome');
    });

    it('should fallback to English if locale missing', () => {
      const langManager = new LanguageManager({ language: 'ru' });
      // Russian locale doesn't exist yet
      const strings = langManager.loadStrings('cli');

      // Should still return English strings
      expect(strings).toHaveProperty('init');
    });
  });

  describe('t()', () => {
    it('should resolve nested key', () => {
      const langManager = new LanguageManager({ language: 'en' });
      const text = langManager.t('cli.init.welcome');

      expect(text).toBe('🚀 SpecWeave Initialization');
    });

    it('should replace placeholders', () => {
      const langManager = new LanguageManager({ language: 'en' });
      const text = langManager.t('errors.fileNotFound', { path: '/foo/bar' });

      expect(text).toContain('/foo/bar');
    });

    it('should return key if not found', () => {
      const langManager = new LanguageManager({ language: 'en' });
      const text = langManager.t('nonexistent.key');

      expect(text).toBe('nonexistent.key');
    });
  });
});
```

**Acceptance Criteria**:
- ✅ All public methods tested
- ✅ Edge cases covered (missing locales, invalid keys)
- ✅ 100% coverage for LanguageManager class
- ✅ All tests pass

**Tests**:
- Self (unit tests)

---

### T-007: Add Language Option to CLI
**User Story**: [US-002: Generate Specification in Russian](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-002-generate-specification-in-russian.md)


**Status**: [ ] Pending

**User Story**: [US-002: Generate Specification in Russian](../../docs/internal/specs/default/llm-native-i18n/us-002-*.md)

**AC**: AC-US002-01, AC-US002-02, AC-US002-03
**Priority**: P1
**Dependencies**: T-005
**Estimated Effort**: 1 hour

**Description**:
Add `--language` option to `specweave init` command.

**Files**:
- `src/cli/index.ts` (update)
- `src/cli/commands/init.ts` (update)

**Implementation**:

```typescript
// src/cli/index.ts (update)
program
  .command('init [project-name]')
  .description('Initialize SpecWeave in a new or existing project')
  .option('--template <template>', 'Project template')
  .option('--adapter <adapter>', 'AI tool adapter (claude|cursor|copilot|generic)')
  .option('--language <language>', 'Primary language (en|ru|es|zh|de|fr|ja|ko|pt)', 'en')
  .action(async (projectName, options) => {
    await initCommand(projectName, options);
  });
```

**Acceptance Criteria**:
- ✅ `--language` option available in help text
- ✅ Option passed to initCommand()
- ✅ Valid languages accepted
- ✅ Invalid languages show error
- ✅ Default is 'en'

**Tests**:
- Integration tests in T-036

---

### T-008: Update .gitignore for Locale Files
**User Story**: [US-002: Generate Specification in Russian](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-002-generate-specification-in-russian.md)


**Status**: [ ] Pending

**User Story**: [US-002: Generate Specification in Russian](../../docs/internal/specs/default/llm-native-i18n/us-002-*.md)

**AC**: AC-US002-01, AC-US002-02, AC-US002-03
**Priority**: P2
**Dependencies**: T-004
**Estimated Effort**: 15 minutes

**Description**:
Ensure locale files are committed to git (not ignored).

**Files**:
- `.gitignore` (verify)

**Implementation**:

```bash
# Verify these are NOT in .gitignore:
# src/locales/
# src/locales/**/*.json

# If accidentally ignored, update .gitignore
```

**Acceptance Criteria**:
- ✅ `src/locales/` is tracked by git
- ✅ Locale JSON files commit successfully

**Tests**:
- Manual verification

---

## Phase 2: Translator Plugin

### T-009: Create Translator Plugin Directory Structure
**User Story**: [US-002: Generate Specification in Russian](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-002-generate-specification-in-russian.md)


**Status**: [ ] Pending

**User Story**: [US-002: Generate Specification in Russian](../../docs/internal/specs/default/llm-native-i18n/us-002-*.md)

**AC**: AC-US002-01, AC-US002-02, AC-US002-03
**Priority**: P0
**Dependencies**: None
**Estimated Effort**: 30 minutes

**Description**:
Create directory structure for `specweave-translator` plugin.

**Files**:
- `src/plugins/specweave-translator/.claude-plugin/manifest.json` (new)
- `src/plugins/specweave-translator/.claude-plugin/plugin.json` (new)
- `src/plugins/specweave-translator/skills/translator/SKILL.md` (new)
- `src/plugins/specweave-translator/agents/translator-agent/AGENT.md` (new)
- `src/plugins/specweave-translator/commands/translate.md` (new)
- `src/plugins/specweave-translator/README.md` (new)

**Implementation**:

```bash
mkdir -p src/plugins/specweave-translator/{.claude-plugin,skills/translator/test-cases,agents/translator-agent,commands}
```

**Acceptance Criteria**:
- ✅ Directory structure exists
- ✅ Follows plugin architecture from increment 0004

**Tests**:
- No tests (directory structure)

---

### T-010: Write Translator Skill
**User Story**: [US-002: Generate Specification in Russian](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-002-generate-specification-in-russian.md)


**Status**: [ ] Pending

**User Story**: [US-002: Generate Specification in Russian](../../docs/internal/specs/default/llm-native-i18n/us-002-*.md)

**AC**: AC-US002-01, AC-US002-02, AC-US002-03
**Priority**: P0
**Dependencies**: T-009
**Estimated Effort**: 3 hours

**Description**:
Create translator skill that auto-activates for translation requests.

**Files**:
- `src/plugins/specweave-translator/skills/translator/SKILL.md` (new)

**Implementation**:

(See plan.md for full content - skill should match the design spec)

**Acceptance Criteria**:
- ✅ YAML frontmatter valid
- ✅ Activation triggers include: translate, i18n, internationalization, multilingual
- ✅ Examples for CLI, docs, code translation
- ✅ Clear guidelines on what to keep in English
- ✅ Markdown preserved in translations

**Tests**:
- Skill test cases in T-014

---

### T-011: Write Translator Agent
**User Story**: [US-002: Generate Specification in Russian](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-002-generate-specification-in-russian.md)


**Status**: [ ] Pending

**User Story**: [US-002: Generate Specification in Russian](../../docs/internal/specs/default/llm-native-i18n/us-002-*.md)

**AC**: AC-US002-01, AC-US002-02, AC-US002-03
**Priority**: P0
**Dependencies**: T-009
**Estimated Effort**: 2 hours

**Description**:
Create translator agent for batch translation jobs.

**Files**:
- `src/plugins/specweave-translator/agents/translator-agent/AGENT.md` (new)

**Implementation**:

(See plan.md for full content)

**Acceptance Criteria**:
- ✅ YAML frontmatter valid
- ✅ Describes batch translation workflow
- ✅ JSON input/output format specified
- ✅ Quality standards documented

**Tests**:
- Agent test in T-015

---

### T-012: Write Translation Command
**User Story**: [US-003: Execute Tasks with Russian Context](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-003-execute-tasks-with-russian-context.md)


**Status**: [ ] Pending

**User Story**: [US-003: Execute Tasks with Russian Context](../../docs/internal/specs/default/llm-native-i18n/us-003-*.md)

**AC**: AC-US003-01, AC-US003-02, AC-US003-03
**Priority**: P1
**Dependencies**: T-009
**Estimated Effort**: 1 hour

**Description**:
Create `/specweave:translate` command for manual translation.

**Files**:
- `src/plugins/specweave-translator/commands/translate.md` (new)

**Implementation**:

(See plan.md for full content)

**Acceptance Criteria**:
- ✅ YAML frontmatter valid
- ✅ Usage examples clear
- ✅ Preview before apply workflow
- ✅ File path handling

**Tests**:
- Manual testing

---

### T-013: Create Plugin Manifests
**User Story**: [US-003: Execute Tasks with Russian Context](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-003-execute-tasks-with-russian-context.md)


**Status**: [ ] Pending

**User Story**: [US-003: Execute Tasks with Russian Context](../../docs/internal/specs/default/llm-native-i18n/us-003-*.md)

**AC**: AC-US003-01, AC-US003-02, AC-US003-03
**Priority**: P0
**Dependencies**: T-010, T-011, T-012
**Estimated Effort**: 1 hour

**Description**:
Create plugin manifests (SpecWeave custom + Claude native).

**Files**:
- `src/plugins/specweave-translator/.claude-plugin/manifest.json` (new)
- `src/plugins/specweave-translator/.claude-plugin/plugin.json` (new)

**Implementation**:

`manifest.json` (SpecWeave custom):
```json
{
  "$schema": "https://verified-skill.com/schemas/plugin-manifest.json",
  "name": "specweave-translator",
  "version": "1.0.0",
  "description": "In-session translation for multilingual SpecWeave support",
  "author": "SpecWeave Team",
  "license": "MIT",
  "specweave_core_version": ">=0.6.0",

  "auto_detect": {
    "config_fields": ["language"],
    "env_vars": []
  },

  "provides": {
    "skills": ["translator"],
    "agents": ["translator-agent"],
    "commands": ["specweave.translate"]
  },

  "triggers": [
    "translate",
    "translation",
    "i18n",
    "internationalization",
    "multilingual",
    "localization",
    "locale",
    "language",
    "Russian",
    "Spanish",
    "Chinese"
  ]
}
```

`plugin.json` (Claude native):
```json
{
  "name": "specweave-translator",
  "description": "In-session translation for multilingual SpecWeave support",
  "version": "1.0.0",
  "author": {
    "name": "SpecWeave Team"
  }
}
```

**Acceptance Criteria**:
- ✅ Both manifests present
- ✅ JSON valid
- ✅ Triggers comprehensive
- ✅ Metadata accurate

**Tests**:
- JSON schema validation

---

### T-014: Write Translator Skill Test Cases
**User Story**: [US-003: Execute Tasks with Russian Context](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-003-execute-tasks-with-russian-context.md)


**Status**: [ ] Pending

**User Story**: [US-003: Execute Tasks with Russian Context](../../docs/internal/specs/default/llm-native-i18n/us-003-*.md)

**AC**: AC-US003-01, AC-US003-02, AC-US003-03
**Priority**: P1
**Dependencies**: T-010
**Estimated Effort**: 2 hours

**Description**:
Create YAML test cases for translator skill.

**Files**:
- `src/plugins/specweave-translator/skills/translator/test-cases/test-1-cli.yaml` (new)
- `src/plugins/specweave-translator/skills/translator/test-cases/test-2-docs.yaml` (new)
- `src/plugins/specweave-translator/skills/translator/test-cases/test-3-code.yaml` (new)

**Implementation**:

`test-1-cli.yaml`:
```yaml
name: CLI Message Translation
description: Translate CLI message to Russian
input: "Translate to Russian: Enter project name:"
expected_output_contains:
  - "Введите название проекта"
  - "Enter project name" # Context reference
expected_not_contains:
  - "{" # No untranslated placeholders
```

`test-2-docs.yaml`:
```yaml
name: Documentation Translation
description: Translate documentation with framework terms preserved
input: |
  Translate to Russian:
  "SpecWeave uses increments to organize work. Each increment has a spec.md file."
expected_output_contains:
  - "SpecWeave"
  - "increments"
  - "spec.md"
  - "организации работы" # Russian for "organize work"
```

`test-3-code.yaml`:
```yaml
name: Code Comment Translation
description: Translate code comments to Spanish
input: |
  Translate code comments to Spanish:
  ```typescript
  // Initialize authentication service
  const authService = new AuthService();
  ```
expected_output_contains:
  - "// Inicializar servicio de autenticación"
  - "authService" # Variable name unchanged
  - "AuthService" # Class name unchanged
```

**Acceptance Criteria**:
- ✅ 3+ test cases
- ✅ Cover different context types (CLI, docs, code)
- ✅ Test framework term preservation
- ✅ Valid YAML

**Tests**:
- Skill test runner (future)

---

### T-015: Test Translator Agent Batch Translation
**User Story**: [US-003: Execute Tasks with Russian Context](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-003-execute-tasks-with-russian-context.md)


**Status**: [ ] Pending

**User Story**: [US-003: Execute Tasks with Russian Context](../../docs/internal/specs/default/llm-native-i18n/us-003-*.md)

**AC**: AC-US003-01, AC-US003-02, AC-US003-03
**Priority**: P1
**Dependencies**: T-011
**Estimated Effort**: 2 hours

**Description**:
Manually test translator agent with batch translation job.

**Files**:
- Test script (temporary)

**Implementation**:

Create test JSON input:
```json
{
  "targetLanguage": "ru",
  "contextType": "cli",
  "strings": [
    { "key": "init.welcome", "value": "🚀 SpecWeave Initialization" },
    { "key": "init.projectName", "value": "Project name:" },
    { "key": "init.complete", "value": "✨ Initialization complete!" }
  ]
}
```

Invoke translator agent via Task tool:
```
Launch translator-agent with above JSON
Verify output JSON has Russian translations
Verify all keys preserved
Verify placeholders preserved
```

**Acceptance Criteria**:
- ✅ Agent translates all strings
- ✅ Output JSON valid
- ✅ Keys unchanged
- ✅ Quality > 95%

**Tests**:
- Manual verification

---

## Phase 3: Adapter Integration

### T-016: Update ClaudeAdapter for Language Injection
**User Story**: [US-003: Execute Tasks with Russian Context](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-003-execute-tasks-with-russian-context.md)


**Status**: [ ] Pending

**User Story**: [US-003: Execute Tasks with Russian Context](../../docs/internal/specs/default/llm-native-i18n/us-003-*.md)

**AC**: AC-US003-01, AC-US003-02, AC-US003-03
**Priority**: P0
**Dependencies**: T-002, T-010
**Estimated Effort**: 3 hours

**Description**:
Update ClaudeAdapter to inject system prompts when language != 'en'.

**Files**:
- `src/adapters/claude/adapter.ts` (update)

**Implementation**:

```typescript
// src/adapters/claude/adapter.ts (update)
import { LanguageManager } from '../../core/i18n/language-manager.js';
import { SupportedLanguage } from '../../core/i18n/types.js';

export class ClaudeAdapter extends AdapterBase {
  async installSkills(
    skills: Skill[],
    config: SpecweaveConfig
  ): Promise<void> {
    const langManager = new LanguageManager(config);
    const systemPrompt = langManager.getSystemPrompt();

    for (const skill of skills) {
      const sourcePath = path.join(this.sourcePath, 'skills', skill.name, 'SKILL.md');
      const originalContent = await fs.readFile(sourcePath, 'utf-8');

      // Inject system prompt if non-English
      const finalContent = config.language && config.language !== 'en'
        ? `${systemPrompt}\n\n${originalContent}`
        : originalContent;

      const targetPath = path.join(this.targetDir, '.claude/skills', skill.name, 'SKILL.md');
      await fs.ensureDir(path.dirname(targetPath));
      await fs.writeFile(targetPath, finalContent);
    }

    console.log(`✅ Installed ${skills.length} skills (language: ${config.language || 'en'})`);
  }

  // Same pattern for installAgents() and installCommands()
  async installAgents(
    agents: Agent[],
    config: SpecweaveConfig
  ): Promise<void> {
    const langManager = new LanguageManager(config);
    const systemPrompt = langManager.getSystemPrompt();

    for (const agent of agents) {
      const sourcePath = path.join(this.sourcePath, 'agents', agent.name, 'AGENT.md');
      const originalContent = await fs.readFile(sourcePath, 'utf-8');

      const finalContent = config.language && config.language !== 'en'
        ? `${systemPrompt}\n\n${originalContent}`
        : originalContent;

      const targetPath = path.join(this.targetDir, '.claude/agents', agent.name, 'AGENT.md');
      await fs.ensureDir(path.dirname(targetPath));
      await fs.writeFile(targetPath, finalContent);
    }

    console.log(`✅ Installed ${agents.length} agents (language: ${config.language || 'en'})`);
  }
}
```

**Acceptance Criteria**:
- ✅ System prompt injected for Russian
- ✅ System prompt injected for Spanish
- ✅ No injection for English
- ✅ Skills/agents/commands all updated
- ✅ No errors during installation

**Tests**:
- Integration tests in T-038

---

### T-017: Update CursorAdapter for Language Injection
**User Story**: [US-003: Execute Tasks with Russian Context](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-003-execute-tasks-with-russian-context.md)


**Status**: [ ] Pending

**User Story**: [US-003: Execute Tasks with Russian Context](../../docs/internal/specs/default/llm-native-i18n/us-003-*.md)

**AC**: AC-US003-01, AC-US003-02, AC-US003-03
**Priority**: P1
**Dependencies**: T-002
**Estimated Effort**: 2 hours

**Description**:
Update CursorAdapter to inject system prompts in compiled AGENTS.md.

**Files**:
- `src/adapters/cursor/adapter.ts` (update)

**Implementation**:

```typescript
// src/adapters/cursor/adapter.ts (update)
export class CursorAdapter extends AdapterBase {
  async compileAgentsMd(
    skills: Skill[],
    agents: Agent[],
    config: SpecweaveConfig
  ): Promise<string> {
    const langManager = new LanguageManager(config);
    const systemPrompt = langManager.getSystemPrompt();

    let content = '# SpecWeave Agents\n\n';

    // Add system prompt at top if non-English
    if (config.language && config.language !== 'en') {
      content += `${systemPrompt}\n\n`;
      content += `---\n\n`;
    }

    // ... rest of compilation logic
    for (const skill of skills) {
      content += await this.compileSkill(skill);
    }

    for (const agent of agents) {
      content += await this.compileAgent(agent);
    }

    return content;
  }
}
```

**Acceptance Criteria**:
- ✅ System prompt at top of AGENTS.md for Russian
- ✅ System prompt at top for Spanish
- ✅ No prompt for English
- ✅ Compiled file valid

**Tests**:
- Integration tests in T-038

---

### T-018: Update CopilotAdapter for Language Injection
**User Story**: [US-004: Living Docs Auto-Translation](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-004-living-docs-auto-translation.md)


**Status**: [ ] Pending

**User Story**: [US-004: Living Docs Auto-Translation](../../docs/internal/specs/default/llm-native-i18n/us-004-*.md)

**AC**: AC-US004-01, AC-US004-02, AC-US004-03
**Priority**: P1
**Dependencies**: T-002
**Estimated Effort**: 1 hour

**Description**:
Update CopilotAdapter to inject system prompts in instructions.md.

**Files**:
- `src/adapters/copilot/adapter.ts` (update)

**Implementation**:

(Similar pattern to CursorAdapter)

**Acceptance Criteria**:
- ✅ System prompt injected in instructions.md
- ✅ Works for Russian and Spanish

**Tests**:
- Integration tests in T-038

---

### T-019: Update GenericAdapter for Language Injection
**User Story**: [US-004: Living Docs Auto-Translation](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-004-living-docs-auto-translation.md)


**Status**: [ ] Pending

**User Story**: [US-004: Living Docs Auto-Translation](../../docs/internal/specs/default/llm-native-i18n/us-004-*.md)

**AC**: AC-US004-01, AC-US004-02, AC-US004-03
**Priority**: P2
**Dependencies**: T-002
**Estimated Effort**: 1 hour

**Description**:
Update GenericAdapter to inject system prompts in SPECWEAVE-MANUAL.md.

**Files**:
- `src/adapters/generic/adapter.ts` (update)

**Implementation**:

(Similar pattern)

**Acceptance Criteria**:
- ✅ System prompt in manual

**Tests**:
- Manual verification

---

### T-020: Test Adapter Installation with Russian
**User Story**: [US-004: Living Docs Auto-Translation](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-004-living-docs-auto-translation.md)


**Status**: [ ] Pending

**User Story**: [US-004: Living Docs Auto-Translation](../../docs/internal/specs/default/llm-native-i18n/us-004-*.md)

**AC**: AC-US004-01, AC-US004-02, AC-US004-03
**Priority**: P1
**Dependencies**: T-016, T-017, T-018, T-019
**Estimated Effort**: 2 hours

**Description**:
Test all adapters install correctly with language = 'ru'.

**Files**:
- Test script (temporary)

**Implementation**:

```bash
# Test ClaudeAdapter
specweave init test-ru --adapter claude --language ru
# Verify: .claude/skills/increment-planner/SKILL.md contains Russian prompt

# Test CursorAdapter
specweave init test-ru-cursor --adapter cursor --language ru
# Verify: AGENTS.md contains Russian prompt

# Test CopilotAdapter
specweave init test-ru-copilot --adapter copilot --language ru
# Verify: instructions.md contains Russian prompt
```

**Acceptance Criteria**:
- ✅ ClaudeAdapter injects prompt correctly
- ✅ CursorAdapter compiles with prompt
- ✅ CopilotAdapter includes prompt
- ✅ GenericAdapter works

**Tests**:
- Integration tests in T-038

---

### T-021: Test Adapter Installation with Spanish
**User Story**: [US-004: Living Docs Auto-Translation](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-004-living-docs-auto-translation.md)


**Status**: [ ] Pending

**User Story**: [US-004: Living Docs Auto-Translation](../../docs/internal/specs/default/llm-native-i18n/us-004-*.md)

**AC**: AC-US004-01, AC-US004-02, AC-US004-03
**Priority**: P1
**Dependencies**: T-020
**Estimated Effort**: 1 hour

**Description**:
Same tests as T-020 but with Spanish (es).

**Acceptance Criteria**:
- ✅ All adapters work with Spanish
- ✅ System prompt contains "Español"

**Tests**:
- Integration tests in T-038

---

### T-022: Update Adapter Interface Documentation
**User Story**: [US-004: Living Docs Auto-Translation](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-004-living-docs-auto-translation.md)


**Status**: [ ] Pending

**User Story**: [US-004: Living Docs Auto-Translation](../../docs/internal/specs/default/llm-native-i18n/us-004-*.md)

**AC**: AC-US004-01, AC-US004-02, AC-US004-03
**Priority**: P2
**Dependencies**: T-016, T-017, T-018, T-019
**Estimated Effort**: 1 hour

**Description**:
Update adapter interface docs to reflect language parameter.

**Files**:
- `src/adapters/adapter-interface.ts` (update)
- `src/adapters/README.md` (update)

**Implementation**:

Update interface:
```typescript
export interface IAdapter {
  installSkills(skills: Skill[], config: SpecweaveConfig): Promise<void>;
  installAgents(agents: Agent[], config: SpecweaveConfig): Promise<void>;
  installCommands(commands: Command[], config: SpecweaveConfig): Promise<void>;
}
```

**Acceptance Criteria**:
- ✅ Interface updated
- ✅ Documentation updated

**Tests**:
- No tests (docs)

---

## Phase 4: CLI Internationalization

### T-023: Extract All CLI Strings
**User Story**: [US-004: Living Docs Auto-Translation](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-004-living-docs-auto-translation.md)


**Status**: [ ] Pending

**User Story**: [US-004: Living Docs Auto-Translation](../../docs/internal/specs/default/llm-native-i18n/us-004-*.md)

**AC**: AC-US004-01, AC-US004-02, AC-US004-03
**Priority**: P1
**Dependencies**: T-004
**Estimated Effort**: 2 hours

**Description**:
Identify and document all user-facing CLI strings that need translation.

**Files**:
- `src/locales/en/cli.json` (update)
- Extraction script (temporary)

**Implementation**:

Audit files:
- `src/cli/commands/init.ts`
- `src/cli/commands/version.ts`
- `src/cli/index.ts`

Extract to `cli.json`:
```json
{
  "init": {
    "welcome": "🚀 SpecWeave Initialization",
    "projectName": "Project name:",
    "detectingTool": "Detecting AI tool...",
    "foundClaude": "✅ Found Claude Code",
    "foundCursor": "✅ Found Cursor",
    "foundCopilot": "✅ Found GitHub Copilot",
    "installingAdapter": "📦 Installing {adapter} adapter...",
    "installingSkills": "Installing skills...",
    "installingAgents": "Installing agents...",
    "installingCommands": "Installing commands...",
    "installingHooks": "Installing hooks...",
    "complete": "✨ Initialization complete!",
    "errors": {
      "invalidName": "Project name must be lowercase letters, numbers, and hyphens only",
      "alreadyExists": ".specweave directory already exists",
      "cancelled": "❌ Initialization cancelled"
    }
  },
  "version": {
    "current": "SpecWeave version: {version}"
  }
}
```

**Acceptance Criteria**:
- ✅ All CLI strings extracted
- ✅ Nested structure logical
- ✅ Placeholders identified
- ✅ Valid JSON

**Tests**:
- No tests (extraction)

---

### T-024: Translate CLI to Russian
**User Story**: [US-005: Spanish Developer Workflow](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-005-spanish-developer-workflow.md)


**Status**: [ ] Pending

**User Story**: [US-005: Spanish Developer Workflow](../../docs/internal/specs/default/llm-native-i18n/us-005-*.md)

**AC**: AC-US005-01, AC-US005-02, AC-US005-03
**Priority**: P1
**Dependencies**: T-023, T-011
**Estimated Effort**: 1 hour

**Description**:
Use translator agent to translate `en/cli.json` → `ru/cli.json`.

**Files**:
- `src/locales/ru/cli.json` (new)

**Implementation**:

Invoke translator agent with:
```json
{
  "targetLanguage": "ru",
  "contextType": "cli",
  "sourceFile": "src/locales/en/cli.json"
}
```

Output to `src/locales/ru/cli.json`:
```json
{
  "init": {
    "welcome": "🚀 Инициализация SpecWeave",
    "projectName": "Название проекта:",
    "detectingTool": "Определение AI-инструмента...",
    "foundClaude": "✅ Обнаружен Claude Code",
    "foundCursor": "✅ Обнаружен Cursor",
    "foundCopilot": "✅ Обнаружен GitHub Copilot",
    "installingAdapter": "📦 Установка адаптера {adapter}...",
    "installingSkills": "Установка навыков...",
    "installingAgents": "Установка агентов...",
    "installingCommands": "Установка команд...",
    "installingHooks": "Установка хуков...",
    "complete": "✨ Инициализация завершена!",
    "errors": {
      "invalidName": "Название проекта должно содержать только строчные буквы, цифры и дефисы",
      "alreadyExists": "Директория .specweave уже существует",
      "cancelled": "❌ Инициализация отменена"
    }
  },
  "version": {
    "current": "Версия SpecWeave: {version}"
  }
}
```

**Acceptance Criteria**:
- ✅ All keys translated
- ✅ Placeholders preserved
- ✅ Emojis preserved
- ✅ Quality >95%

**Tests**:
- Integration tests in T-036

---

### T-025: Translate CLI to Spanish
**User Story**: [US-005: Spanish Developer Workflow](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-005-spanish-developer-workflow.md)


**Status**: [ ] Pending

**User Story**: [US-005: Spanish Developer Workflow](../../docs/internal/specs/default/llm-native-i18n/us-005-*.md)

**AC**: AC-US005-01, AC-US005-02, AC-US005-03
**Priority**: P1
**Dependencies**: T-023, T-011
**Estimated Effort**: 1 hour

**Description**:
Same as T-024 but for Spanish.

**Files**:
- `src/locales/es/cli.json` (new)

**Acceptance Criteria**:
- ✅ All keys translated
- ✅ Placeholders preserved
- ✅ Quality >95%

**Tests**:
- Integration tests in T-037

---

### T-026: Replace Hardcoded Strings in init.ts
**User Story**: [US-005: Spanish Developer Workflow](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-005-spanish-developer-workflow.md)


**Status**: [ ] Pending

**User Story**: [US-005: Spanish Developer Workflow](../../docs/internal/specs/default/llm-native-i18n/us-005-*.md)

**AC**: AC-US005-01, AC-US005-02, AC-US005-03
**Priority**: P1
**Dependencies**: T-024, T-025
**Estimated Effort**: 2 hours

**Description**:
Replace all hardcoded strings in `init.ts` with `langManager.t()` calls.

**Files**:
- `src/cli/commands/init.ts` (update)

**Implementation**:

Before:
```typescript
console.log(chalk.blue.bold('\n🚀 SpecWeave Initialization\n'));
```

After:
```typescript
console.log(chalk.blue.bold(`\n${langManager.t('cli.init.welcome')}\n`));
```

**Acceptance Criteria**:
- ✅ Zero hardcoded strings
- ✅ All console.log() use langManager.t()
- ✅ All inquirer prompts use langManager.t()
- ✅ Works in English, Russian, Spanish

**Tests**:
- Integration tests in T-036, T-037

---

### T-027: Replace Hardcoded Strings in Other CLI Files
**User Story**: [US-005: Spanish Developer Workflow](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-005-spanish-developer-workflow.md)


**Status**: [ ] Pending

**User Story**: [US-005: Spanish Developer Workflow](../../docs/internal/specs/default/llm-native-i18n/us-005-*.md)

**AC**: AC-US005-01, AC-US005-02, AC-US005-03
**Priority**: P1
**Dependencies**: T-026
**Estimated Effort**: 1 hour

**Description**:
Replace hardcoded strings in `version.ts`, `index.ts`, etc.

**Files**:
- `src/cli/commands/version.ts` (update)
- `src/cli/index.ts` (update)

**Acceptance Criteria**:
- ✅ All CLI files use langManager.t()
- ✅ No hardcoded strings

**Tests**:
- Integration tests

---

### T-028: Test CLI in All Languages
**User Story**: [US-005: Spanish Developer Workflow](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-005-spanish-developer-workflow.md)


**Status**: [ ] Pending

**User Story**: [US-005: Spanish Developer Workflow](../../docs/internal/specs/default/llm-native-i18n/us-005-*.md)

**AC**: AC-US005-01, AC-US005-02, AC-US005-03
**Priority**: P1
**Dependencies**: T-026, T-027
**Estimated Effort**: 2 hours

**Description**:
Manually test CLI with English, Russian, Spanish.

**Files**:
- Test script

**Implementation**:

```bash
# Test English (default)
specweave init test-en
# Verify: All output in English

# Test Russian
specweave init test-ru --language ru
# Verify: All output in Russian

# Test Spanish
specweave init test-es --language es
# Verify: All output in Spanish
```

**Acceptance Criteria**:
- ✅ CLI works in all 3 languages
- ✅ No untranslated strings
- ✅ Placeholders replaced correctly
- ✅ User experience smooth

**Tests**:
- Manual + integration tests

---

## Phase 5: Living Docs Translation

### T-029: Create translate-living-docs.ts Script
**User Story**: [US-005: Spanish Developer Workflow](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-005-spanish-developer-workflow.md)


**Status**: [ ] Pending

**User Story**: [US-005: Spanish Developer Workflow](../../docs/internal/specs/default/llm-native-i18n/us-005-*.md)

**AC**: AC-US005-01, AC-US005-02, AC-US005-03
**Priority**: P1
**Dependencies**: T-002, T-010
**Estimated Effort**: 3 hours

**Description**:
Create Node.js script to translate living docs updates.

**Files**:
- `src/hooks/translate-living-docs.ts` (new)

**Implementation**:

```typescript
// src/hooks/translate-living-docs.ts
import { execSync } from 'child_process';
import fs from 'fs-extra';
import path from 'path';
import { LanguageManager } from '../core/i18n/language-manager.js';

async function translateLivingDocs(): Promise<void> {
  // 1. Load config
  const config = JSON.parse(
    fs.readFileSync('.specweave/config.json', 'utf-8')
  );

  const language = config.language || 'en';
  if (language === 'en') {
    console.log('Language is English, skipping translation');
    return;
  }

  if (!config.translation?.autoTranslateLivingDocs) {
    console.log('Auto-translate living docs disabled');
    return;
  }

  console.log(`🌐 Translating living docs to ${language}...`);

  // 2. Get changed files in .specweave/docs/
  const changedFiles = execSync(
    'git diff --name-only .specweave/docs/',
    { encoding: 'utf-8' }
  )
    .split('\n')
    .filter(f => f.endsWith('.md'));

  if (changedFiles.length === 0) {
    console.log('No living docs changed');
    return;
  }

  // 3. Initialize LanguageManager
  const langManager = new LanguageManager(config);

  // 4. Translate each file
  for (const file of changedFiles) {
    const content = fs.readFileSync(file, 'utf-8');

    // Invoke translator skill
    // This will auto-activate in current session
    const translated = await langManager.translate(content, {
      targetLanguage: language as any,
      contextType: 'living-docs',
      preserveMarkdown: true,
      preserveCodeBlocks: true,
      keepFrameworkTerms: true,
      keepTechnicalTerms: true,
    });

    // Write back
    fs.writeFileSync(file, translated);
  }

  console.log(`✅ Living docs translated (${changedFiles.length} file${changedFiles.length === 1 ? '' : 's'})`);
}

translateLivingDocs().catch(console.error);
```

**Acceptance Criteria**:
- ✅ Loads config correctly
- ✅ Detects changed files via git diff
- ✅ Invokes translator skill for each file
- ✅ Writes translated content back
- ✅ Handles errors gracefully

**Tests**:
- Integration tests in T-041

---

### T-030: Update post-task-completion.sh Hook
**User Story**: [US-006: Mixed Language Input](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-006-mixed-language-input.md)


**Status**: [ ] Pending

**User Story**: [US-006: Mixed Language Input](../../docs/internal/specs/default/llm-native-i18n/us-006-*.md)

**AC**: AC-US006-01, AC-US006-02, AC-US006-03
**Priority**: P1
**Dependencies**: T-029
**Estimated Effort**: 1 hour

**Description**:
Update post-task completion hook to call translate-living-docs.ts.

**Files**:
- `src/hooks/post-task-completion.sh` (update)

**Implementation**:

Add at end of hook:
```bash
#!/bin/bash

# ... existing hook logic ...

# Auto-translate living docs if enabled
if command -v node &> /dev/null; then
  node dist/hooks/translate-living-docs.js || true
fi
```

**Acceptance Criteria**:
- ✅ Hook calls translate script
- ✅ Errors don't break hook
- ✅ Works when no translation needed

**Tests**:
- Integration tests in T-041

---

### T-031: Implement File Change Detection
**User Story**: [US-006: Mixed Language Input](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-006-mixed-language-input.md)


**Status**: [ ] Pending

**User Story**: [US-006: Mixed Language Input](../../docs/internal/specs/default/llm-native-i18n/us-006-*.md)

**AC**: AC-US006-01, AC-US006-02, AC-US006-03
**Priority**: P1
**Dependencies**: T-029
**Estimated Effort**: 1 hour

**Description**:
Robust file change detection for living docs.

**Files**:
- `src/hooks/translate-living-docs.ts` (update)

**Implementation**:

Handle edge cases:
- New files (not in git yet)
- Deleted files
- Renamed files
- Files in subdirectories

**Acceptance Criteria**:
- ✅ Detects all changed .md files
- ✅ Ignores non-markdown
- ✅ Handles nested directories
- ✅ No errors on empty diffs

**Tests**:
- Unit tests for detection logic

---

### T-032: Implement Translator Skill Invocation
**User Story**: [US-006: Mixed Language Input](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-006-mixed-language-input.md)


**Status**: [ ] Pending

**User Story**: [US-006: Mixed Language Input](../../docs/internal/specs/default/llm-native-i18n/us-006-*.md)

**AC**: AC-US006-01, AC-US006-02, AC-US006-03
**Priority**: P1
**Dependencies**: T-029, T-010
**Estimated Effort**: 2 hours

**Description**:
Implement `LanguageManager.translate()` to invoke translator skill.

**Files**:
- `src/core/i18n/language-manager.ts` (update)

**Implementation**:

```typescript
async translate(text: string, options: TranslateOptions): Promise<string> {
  if (this.language === 'en') return text;

  // Build prompt for translator skill
  const contextPrompt = this.getContextPrompt(options.contextType || 'docs');

  const prompt = `
Translate the following text to ${options.targetLanguage}.

${contextPrompt}

${options.keepFrameworkTerms ? '- Keep framework terms (Increment, Living Docs, SpecWeave, ADR, RFC) in English' : ''}
${options.keepTechnicalTerms ? '- Keep technical terms (Git, Docker, Kubernetes, etc.) in English' : ''}
${options.preserveMarkdown ? '- Preserve all markdown formatting' : ''}
${options.preserveCodeBlocks ? '- Do not translate code blocks' : ''}

Text to translate:
${text}

Translation:
  `.trim();

  // Invoke translator skill
  // This relies on the skill auto-activating in the current session
  // For now, we'll return a placeholder - actual implementation will involve
  // communicating with the current LLM session (implementation detail TBD)

  // TODO: Actual implementation
  // For MVP, we can output the prompt and expect user to provide translation
  console.log('Translation prompt:', prompt);
  console.log('Awaiting translator skill response...');

  return text; // Placeholder
}

private getContextPrompt(contextType: string): string {
  switch (contextType) {
    case 'cli':
      return 'Context: CLI messages for developer tool. Use imperative tone.';
    case 'docs':
      return 'Context: Technical documentation. Use explanatory tone.';
    case 'living-docs':
      return 'Context: Auto-generated documentation. Maintain technical accuracy.';
    case 'code-comments':
      return 'Context: Code comments. Keep concise and technical.';
    default:
      return '';
  }
}
```

**Note**: The actual mechanism for invoking the translator skill in the current session is a design decision. Options:
1. Output prompt to console, user provides translation (manual)
2. Use Task tool to spawn translator agent (automated)
3. Leverage Claude Code skill auto-activation (ideal)

**Acceptance Criteria**:
- ✅ Builds correct prompt
- ✅ Context-aware
- ✅ Preserves markdown/code based on options
- ✅ Returns translated text

**Tests**:
- Integration tests in T-041

---

### T-033: Test Living Docs Auto-Translation
**User Story**: [US-006: Mixed Language Input](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-006-mixed-language-input.md)


**Status**: [ ] Pending

**User Story**: [US-006: Mixed Language Input](../../docs/internal/specs/default/llm-native-i18n/us-006-*.md)

**AC**: AC-US006-01, AC-US006-02, AC-US006-03
**Priority**: P1
**Dependencies**: T-030, T-032
**Estimated Effort**: 2 hours

**Description**:
End-to-end test of living docs auto-translation.

**Files**:
- Test script

**Implementation**:

```bash
# 1. Init Russian project
specweave init test-living-docs --language ru
cd test-living-docs

# 2. Enable auto-translation
# Edit .specweave/config.json:
# "translation": { "autoTranslateLivingDocs": true }

# 3. Create increment
/specweave:inc "test feature"

# 4. Complete a task (triggers hook)
/specweave:do

# 5. Verify living docs translated
cat .specweave/docs/internal/delivery/implementation-notes/TEST-NOTES.md
# Should be in Russian
```

**Acceptance Criteria**:
- ✅ Hook fires after task
- ✅ Changed docs detected
- ✅ Translation happens
- ✅ Content written back
- ✅ Markdown preserved
- ✅ Code blocks preserved

**Tests**:
- E2E test in T-041

---

## Phase 6: Testing

### T-034: Unit Tests for LanguageManager
**User Story**: [US-006: Mixed Language Input](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-006-mixed-language-input.md)


**Status**: [ ] Pending

**User Story**: [US-006: Mixed Language Input](../../docs/internal/specs/default/llm-native-i18n/us-006-*.md)

**AC**: AC-US006-01, AC-US006-02, AC-US006-03
**Priority**: P1
**Dependencies**: T-002
**Estimated Effort**: 2 hours

**Description**:
Already covered in T-006 (duplicate check).

**Acceptance Criteria**:
- ✅ Tests from T-006 complete

---

### T-035: Skill Test Cases for Translator
**User Story**: [US-006: Mixed Language Input](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-006-mixed-language-input.md)


**Status**: [ ] Pending

**User Story**: [US-006: Mixed Language Input](../../docs/internal/specs/default/llm-native-i18n/us-006-*.md)

**AC**: AC-US006-01, AC-US006-02, AC-US006-03
**Priority**: P1
**Dependencies**: T-014
**Estimated Effort**: 1 hour

**Description**:
Already covered in T-014 (duplicate check).

**Acceptance Criteria**:
- ✅ Test cases from T-014 complete

---

### T-036: Integration Test - Russian CLI
**User Story**: [US-007: Language Configuration](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-007-language-configuration.md)


**Status**: [ ] Pending

**User Story**: [US-007: Language Configuration](../../docs/internal/specs/default/llm-native-i18n/us-007-*.md)

**AC**: AC-US007-01, AC-US007-02, AC-US007-03
**Priority**: P1
**Dependencies**: T-026, T-027
**Estimated Effort**: 2 hours

**Description**:
Integration test for Russian CLI.

**Files**:
- `tests/integration/i18n/cli-russian.test.ts` (new)

**Implementation**:

```typescript
// tests/integration/i18n/cli-russian.test.ts
import { execSync } from 'child_process';
import fs from 'fs-extra';

describe('Russian CLI Integration', () => {
  afterEach(() => {
    // Cleanup
    fs.removeSync('test-ru-cli');
  });

  it('should display Russian prompts during init', () => {
    const output = execSync(
      'specweave init test-ru-cli --language ru',
      { encoding: 'utf-8' }
    );

    expect(output).toContain('🚀 Инициализация SpecWeave');
    expect(output).toContain('Название проекта:');
    expect(output).toContain('✨ Инициализация завершена!');
  });

  it('should create Russian locale config', () => {
    execSync('specweave init test-ru-cli --language ru');

    const config = JSON.parse(
      fs.readFileSync('test-ru-cli/.specweave/config.json', 'utf-8')
    );

    expect(config.language).toBe('ru');
  });

  it('should inject Russian system prompt in skills', () => {
    execSync('specweave init test-ru-cli --language ru --adapter claude');

    const skillContent = fs.readFileSync(
      'test-ru-cli/.claude/skills/increment-planner/SKILL.md',
      'utf-8'
    );

    expect(skillContent).toContain('LANGUAGE INSTRUCTION');
    expect(skillContent).toContain('Russian (Русский)');
  });
});
```

**Acceptance Criteria**:
- ✅ CLI outputs Russian text
- ✅ Config saved correctly
- ✅ System prompts injected
- ✅ All tests pass

**Tests**:
- Self (integration tests)

---

### T-037: Integration Test - Spanish CLI
**User Story**: [US-007: Language Configuration](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-007-language-configuration.md)


**Status**: [ ] Pending

**User Story**: [US-007: Language Configuration](../../docs/internal/specs/default/llm-native-i18n/us-007-*.md)

**AC**: AC-US007-01, AC-US007-02, AC-US007-03
**Priority**: P1
**Dependencies**: T-026, T-027
**Estimated Effort**: 1 hour

**Description**:
Same as T-036 but for Spanish.

**Files**:
- `tests/integration/i18n/cli-spanish.test.ts` (new)

**Acceptance Criteria**:
- ✅ CLI outputs Spanish text
- ✅ All tests pass

**Tests**:
- Self

---

### T-038: Integration Test - Adapter Installation
**User Story**: [US-007: Language Configuration](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-007-language-configuration.md)


**Status**: [ ] Pending

**User Story**: [US-007: Language Configuration](../../docs/internal/specs/default/llm-native-i18n/us-007-*.md)

**AC**: AC-US007-01, AC-US007-02, AC-US007-03
**Priority**: P1
**Dependencies**: T-020, T-021
**Estimated Effort**: 2 hours

**Description**:
Test adapter installation with different languages.

**Files**:
- `tests/integration/i18n/adapter-installation.test.ts` (new)

**Implementation**:

```typescript
describe('Adapter Installation with Languages', () => {
  it('should inject Russian prompt in ClaudeAdapter', async () => {
    await initWithAdapter('claude', 'ru');

    const skillPath = '.claude/skills/increment-planner/SKILL.md';
    const content = fs.readFileSync(skillPath, 'utf-8');

    expect(content).toContain('Russian (Русский)');
  });

  it('should inject Spanish prompt in CursorAdapter', async () => {
    await initWithAdapter('cursor', 'es');

    const agentsPath = 'AGENTS.md';
    const content = fs.readFileSync(agentsPath, 'utf-8');

    expect(content).toContain('Spanish (Español)');
  });

  // ... more adapter tests
});
```

**Acceptance Criteria**:
- ✅ All adapters tested
- ✅ System prompts verified
- ✅ All tests pass

**Tests**:
- Self

---

### T-039: E2E Test - Russian Workflow
**User Story**: [US-007: Language Configuration](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-007-language-configuration.md)


**Status**: [ ] Pending

**User Story**: [US-007: Language Configuration](../../docs/internal/specs/default/llm-native-i18n/us-007-*.md)

**AC**: AC-US007-01, AC-US007-02, AC-US007-03
**Priority**: P1
**Dependencies**: T-036, T-038, T-033
**Estimated Effort**: 3 hours

**Description**:
Full end-to-end workflow in Russian.

**Files**:
- `tests/e2e/i18n/workflow-russian.spec.ts` (new)

**Implementation**:

```typescript
// tests/e2e/i18n/workflow-russian.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Russian Workflow E2E', () => {
  test('should complete full increment in Russian', async () => {
    // 1. Init
    await exec('specweave init test-ru-e2e --language ru');

    // 2. Create increment
    await exec('/specweave:inc "добавить аутентификацию"');

    // 3. Verify spec.md is in Russian
    const spec = await readFile('.specweave/increments/0001-auth/spec.md');
    expect(spec).toContain('# Спецификация:');
    expect(spec).toContain('## Обзор');
    expect(spec).toContain('## Пользовательские истории');

    // 4. Verify framework terms preserved
    expect(spec).toContain('SpecWeave');
    expect(spec).toContain('Increment');

    // 5. Execute task
    await exec('/specweave:do');

    // 6. Verify living docs (if auto-translate enabled)
    const notes = await readFile('.specweave/docs/internal/delivery/AUTH-NOTES.md');
    expect(notes).toContain('Реализация');
    expect(notes).toMatch(/Git/); // Technical term preserved

    // 7. Validate and close
    await exec('/specweave:validate 0001');
    await exec('/specweave:done 0001');

    // Success!
  });
});
```

**Acceptance Criteria**:
- ✅ Full workflow succeeds
- ✅ All output in Russian
- ✅ Generated docs in Russian
- ✅ Framework/technical terms preserved
- ✅ Test passes

**Tests**:
- Self (E2E)

---

### T-040: E2E Test - Spanish Workflow
**User Story**: [US-007: Language Configuration](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-007-language-configuration.md)


**Status**: [ ] Pending

**User Story**: [US-007: Language Configuration](../../docs/internal/specs/default/llm-native-i18n/us-007-*.md)

**AC**: AC-US007-01, AC-US007-02, AC-US007-03
**Priority**: P1
**Dependencies**: T-037, T-038, T-033
**Estimated Effort**: 2 hours

**Description**:
Same as T-039 but for Spanish.

**Files**:
- `tests/e2e/i18n/workflow-spanish.spec.ts` (new)

**Acceptance Criteria**:
- ✅ Full workflow in Spanish
- ✅ Test passes

**Tests**:
- Self

---

### T-041: E2E Test - Living Docs Translation
**User Story**: [US-007: Language Configuration](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-007-language-configuration.md)


**Status**: [ ] Pending

**User Story**: [US-007: Language Configuration](../../docs/internal/specs/default/llm-native-i18n/us-007-*.md)

**AC**: AC-US007-01, AC-US007-02, AC-US007-03
**Priority**: P1
**Dependencies**: T-033
**Estimated Effort**: 2 hours

**Description**:
Test living docs auto-translation specifically.

**Files**:
- `tests/e2e/i18n/living-docs-translation.spec.ts` (new)

**Implementation**:

```typescript
test('should auto-translate living docs on task completion', async () => {
  // 1. Init with auto-translate enabled
  await exec('specweave init test-living-docs --language ru');
  await updateConfig({ translation: { autoTranslateLivingDocs: true } });

  // 2. Create increment (spec already in Russian from system prompt)
  await exec('/specweave:inc "test feature"');

  // 3. Complete task
  await exec('/specweave:do');

  // 4. Verify living docs translated
  const docs = await readFile('.specweave/docs/internal/delivery/TEST-NOTES.md');
  expect(docs).toContain('Реализация'); // Russian word
  expect(docs).not.toContain('Implementation'); // English word

  // 5. Verify markdown preserved
  expect(docs).toMatch(/^#/m); // Headers preserved
  expect(docs).toMatch(/```/); // Code blocks preserved
});
```

**Acceptance Criteria**:
- ✅ Hook fires correctly
- ✅ Translation happens
- ✅ Markdown structure preserved
- ✅ Code blocks not translated
- ✅ Test passes

**Tests**:
- Self

---

### T-042: Validate Test Coverage
**User Story**: [US-008: Cost Transparency](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-008-cost-transparency.md)


**Status**: [ ] Pending

**User Story**: [US-008: Cost Transparency](../../docs/internal/specs/default/llm-native-i18n/us-008-*.md)

**AC**: AC-US008-01, AC-US008-02, AC-US008-03
**Priority**: P1
**Dependencies**: T-006, T-036, T-037, T-038, T-039, T-040, T-041
**Estimated Effort**: 1 hour

**Description**:
Run test coverage report and ensure >90%.

**Files**:
- Coverage report

**Implementation**:

```bash
npm run test:coverage

# Check coverage:
# - LanguageManager: 100%
# - Adapters: >90%
# - CLI: >90%
# - Overall: >90%
```

**Acceptance Criteria**:
- ✅ Overall coverage >90%
- ✅ Critical paths 100%
- ✅ All tests green

**Tests**:
- Coverage report

---

## Phase 7: Documentation

### T-043: Update CLAUDE.md
**User Story**: [US-008: Cost Transparency](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-008-cost-transparency.md)


**Status**: [ ] Pending

**User Story**: [US-008: Cost Transparency](../../docs/internal/specs/default/llm-native-i18n/us-008-*.md)

**AC**: AC-US008-01, AC-US008-02, AC-US008-03
**Priority**: P1
**Dependencies**: All previous tasks
**Estimated Effort**: 2 hours

**Description**:
Update CLAUDE.md with i18n section.

**Files**:
- `CLAUDE.md` (update)

**Implementation**:

Add section:
```markdown
## Multilingual Support (v0.6.0+)

SpecWeave supports multiple languages using LLM-native translation:

**Supported Languages**:
- English (en) - default
- Russian (ru)
- Spanish (es)
- Chinese (zh) - coming soon
- German (de) - coming soon
- French (fr) - coming soon

**How It Works**:
1. **System Prompt Injection**: Skills/agents receive "Respond in Russian" instruction
2. **In-Session Translation**: Translator plugin uses current LLM for translation (no external API)
3. **Living Docs Auto-Translation**: Optional automatic translation of doc updates

**Usage**:
```bash
# Initialize in Russian
specweave init my-project --language ru

# All generated content (spec, plan, tasks) will be in Russian
/specweave:inc "добавить аутентификацию"

# CLI output also in Russian
✅ Инкремент 0001 создан!
```

**Configuration**:
```json
{
  "language": "ru",
  "translation": {
    "autoTranslateLivingDocs": true,
    "keepFrameworkTerms": true,
    "keepTechnicalTerms": true
  }
}
```

**Zero Cost**: Uses current LLM session - no additional API calls!
```

**Acceptance Criteria**:
- ✅ Section added to CLAUDE.md
- ✅ Usage examples clear
- ✅ Configuration documented

**Tests**:
- Manual review

---

### T-044: Update README.md
**User Story**: [US-008: Cost Transparency](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-008-cost-transparency.md)


**Status**: [ ] Pending

**User Story**: [US-008: Cost Transparency](../../docs/internal/specs/default/llm-native-i18n/us-008-*.md)

**AC**: AC-US008-01, AC-US008-02, AC-US008-03
**Priority**: P1
**Dependencies**: T-043
**Estimated Effort**: 1 hour

**Description**:
Update README.md with multilingual support info.

**Files**:
- `README.md` (update)

**Implementation**:

Add to features section:
```markdown
## Features

- 🌐 **Multilingual Support** - Generate specs, plans, and docs in Russian, Spanish, Chinese, and more
- ...
```

Add usage section:
```markdown
## Multilingual Support

SpecWeave supports 8+ languages out of the box:

```bash
specweave init my-project --language ru  # Russian
specweave init my-project --language es  # Spanish
specweave init my-project --language zh  # Chinese
```

All generated content (specs, plans, tasks, docs) will be in your chosen language!
```

**Acceptance Criteria**:
- ✅ Feature highlighted
- ✅ Usage examples added
- ✅ Language list updated

**Tests**:
- Manual review

---

### T-045: Create Multilingual Guide
**User Story**: [US-008: Cost Transparency](../../docs/internal/specs/default/FS-25-11-03-llm-native-i18n/us-008-cost-transparency.md)


**Status**: [ ] Pending

**User Story**: [US-008: Cost Transparency](../../docs/internal/specs/default/llm-native-i18n/us-008-*.md)

**AC**: AC-US008-01, AC-US008-02, AC-US008-03
**Priority**: P2
**Dependencies**: T-043, T-044
**Estimated Effort**: 2 hours

**Description**:
Create comprehensive user guide for multilingual support.

**Files**:
- `.specweave/docs/public/guides/multilingual-support.md` (new)

**Implementation**:

Create guide with sections:
1. Introduction
2. Supported Languages
3. Quick Start
4. Configuration Options
5. How Translation Works
6. Living Docs Auto-Translation
7. Framework Term Preservation
8. FAQ
9. Troubleshooting

**Acceptance Criteria**:
- ✅ Comprehensive guide
- ✅ Examples for each language
- ✅ Configuration explained
- ✅ FAQ addresses common questions

**Tests**:
- Manual review

---

## Summary

**Total Tasks**: 45
**Estimated Effort**: 10-12 days
**Priority Breakdown**:
- P0: 11 tasks (core infrastructure)
- P1: 32 tasks (main features + tests)
- P2: 2 tasks (docs)

**Phase Completion Order**:
1. Phase 1: Core Infrastructure (2-3 days)
2. Phase 2: Translator Plugin (3-4 days)
3. Phase 3: Adapter Integration (2 days)
4. Phase 4: CLI Internationalization (2 days)
5. Phase 5: Living Docs Translation (1-2 days)
6. Phase 6: Testing (3 days)
7. Phase 7: Documentation (1 day)

**Ready to Execute!** 🚀

---

**Version**: 1.0
**Last Updated**: 2025-11-02
**Status**: Ready for Implementation
