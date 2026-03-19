# Architecture Plan: vskill Plugin Auto-Recommendation

## Overview

Add keyword-based detection of vskill marketplace plugins to the SpecWeave prompt pipeline.
When a user's prompt references domains covered by known vskill plugins (mobile, google-workspace,
marketing, productivity, skills) and that plugin is not already in `vskill.lock`, inject a
suggestion into `additionalContext`. Detection is pure regex in bash -- no LLM calls, no latency.

## Architecture Decision

### Why Regex in the Hook (Not LLM)

The existing LLM detect-intent pipeline (via Haiku) already has a deny-list telling it to NOT
suggest domain plugins like mobile, frontend, etc. These are vskill marketplace plugins with a
different install path (`vskill install` vs `specweave refresh-plugins`).

Adding vskill recommendation to the LLM prompt would:
1. Add latency (Haiku calls take 1-5s)
2. Require restructuring the LLM output schema
3. Conflict with the existing deny-list telling Haiku to ignore these plugins

Regex in the hook is the correct layer because:
- Detection is keyword-based, not intent-based (no ambiguity to resolve)
- The hook already has `check_plugin_in_vskill_lock()` for fast lockfile checks
- Existing pattern: LSP setup suggestions use the same TMPDIR marker approach
- Cost: zero API calls, < 5ms added latency

### Why TMPDIR Session Markers (Not State Files)

The hook already uses two dedup patterns:
1. `$TMPDIR/specweave-ondemand-$$` -- PID-scoped markers for on-demand plugin installs
2. `.specweave/state/lsp-setup-suggested.flag` -- persistent project-level markers

For vskill suggestions, TMPDIR markers (pattern: `$TMPDIR/specweave-vskill-suggested-{plugin}`)
are correct because:
- Suggestions should reset per shell session (new session = fresh suggestions)
- No persistence needed (these are informational, not state transitions)
- Natural cleanup when shell exits (TMPDIR is session-scoped on macOS/Linux)
- NOT using `$$` (PID-scoped) because we want session-scoped dedup, not process-scoped

Note: Unlike the on-demand `$$` pattern, vskill suggestion markers use a flat TMPDIR path
without PID scoping. This means a suggestion shown in one Claude Code instance suppresses it
in other instances within the same shell session -- acceptable since the user already saw it.

## Component Map

```
user-prompt-submit.sh (hook)
    |
    |  1. VSKILL_PLUGIN_REGISTRY (bash assoc array / case-esac fallback)
    |     Maps plugin name -> keywords + skill descriptions
    |
    |  2. detect_vskill_recommendations()
    |     - For each registry entry:
    |       a. check_plugin_in_vskill_lock() -> skip if installed
    |       b. Check TMPDIR marker -> skip if already suggested this session
    |       c. Regex match prompt against keywords
    |          - Short keywords (<5 chars): \b word boundary
    |          - Multi-word/long keywords: substring match
    |       d. On match: create marker, add to results (max 3)
    |     - Returns: formatted suggestion text or empty
    |
    |  3. Integration point: runs BEFORE LLM detect-intent
    |     - Appends suggestion text to additionalContext
    |     - Does NOT exit early (hook continues to LLM detection)
    |
llm-plugin-detector.ts
    |
    |  4. VSKILL_PLUGIN_REGISTRY constant (TypeScript)
    |     - Mirrors bash registry for programmatic access
    |     - Used by detectVskillPlugins() helper
    |
    |  5. detectVskillPlugins(prompt) -> VskillMatch[]
    |     - Exported helper for detect-intent CLI
    |     - Same keyword logic as bash but in TypeScript
    |
    |  6. Deny-list update
    |     - Current: "DO NOT suggest: mobile, skills..."
    |     - Updated: "These are vskill marketplace plugins detected separately"
    |
project-detector.ts
    |
    |  7. vskillPlugins field on ProjectTypeResult
    |     - Existing mobile rules (ios, android, react-native, expo)
    |       already detect with `plugins: []` (empty!)
    |     - Add vskillPlugins mapping to those rules
    |
auto-install.ts
    |
    |  8. vskillPlugin field on COMPONENT_MAPPING entries
    |     - Mobile keywords (ios, android, mobile, etc.)
    |       already mapped with empty skills/agents
    |     - Add vskillPlugin: "mobile" to those entries
    |
    |  9. analyzeUserIntent() returns vskillPlugins: string[]
    |
detect-intent.ts
    |
    | 10. DetectIntentResult.vskillRecommendations field
    |     - Calls detectVskillPlugins() from llm-plugin-detector
    |     - Returns matches in CLI JSON output
```

## Data Flow

```
User types: "deploy ios app to testflight"
                |
                v
    user-prompt-submit.sh
                |
                +--> detect_vskill_recommendations("deploy ios app to testflight")
                |       |
                |       +--> check_plugin_in_vskill_lock("mobile") -> NOT installed
                |       +--> check TMPDIR marker -> NOT suggested yet
                |       +--> regex: \bios\b matches "ios"
                |       +--> touch $TMPDIR/specweave-vskill-suggested-mobile
                |       +--> return suggestion text (< 300 chars)
                |
                +--> append to additionalContext:
                |    "vskill plugin available: mobile (App Store, TestFlight, mobile CI/CD)
                |     Install: vskill install anton-abyzov/vskill --plugin mobile"
                |
                +--> continue to LLM detect-intent (unmodified)
                |
                +--> output_approve_with_context(combined message)
```

## Registry Design

### Bash (hook)

Use case/esac pattern matching (compatible with bash 3.2 on stock macOS) rather than
associative arrays. Each plugin is a function call that checks keywords against the
lowercased prompt:

```bash
# Registry metadata (portable arrays, no bash 4 required)
VSKILL_PLUGINS="mobile google-workspace marketing productivity skills"
VSKILL_DESC_mobile="App Store, TestFlight, mobile CI/CD"
VSKILL_DESC_google_workspace="Google Sheets, Docs, Drive, Calendar"
VSKILL_DESC_marketing="Slack messaging, social media, content marketing"
VSKILL_DESC_productivity="Notion, Todoist, Trello, project management"
VSKILL_DESC_skills="skill discovery, marketplace browsing"
VSKILL_INSTALL_CMD="vskill install anton-abyzov/vskill --plugin"

# Keyword matching per plugin (called with lowercased prompt as $1)
vskill_keywords_match_mobile() {
  local p="$1"
  # Short keywords: word-boundary check
  echo "$p" | grep -qwi 'ios' && return 0
  echo "$p" | grep -qwi 'apk' && return 0
  # Long/multi-word keywords: substring
  case "$p" in
    *testflight*|*"app store"*|*"play store"*|*"react native"*|*react-native*) return 0 ;;
    *expo*|*"mobile app"*|*flutter*|*xcode*|*cocoapods*|*fastlane*) return 0 ;;
    *app-store-connect*|*"app deployment"*) return 0 ;;
  esac
  return 1
}
# ... similar functions for other plugins
```

Keyword rules:
- Short keywords (<5 chars like `ios`): `grep -qwi` for word-boundary matching
- Multi-word keywords (like `app store`): case/esac with quoted patterns
- Long single-word keywords (>=5 chars like `testflight`): case/esac substring match

### TypeScript (llm-plugin-detector.ts)

```typescript
export interface VskillPluginEntry {
  keywords: string[];
  shortKeywords: string[];  // <5 chars, need word-boundary
  description: string;
  installCommand: string;
}

export interface VskillMatch {
  plugin: string;
  matchedKeyword: string;
  installCommand: string;
}

export const VSKILL_PLUGIN_REGISTRY: Record<string, VskillPluginEntry> = {
  mobile: {
    keywords: ['testflight', 'app store', 'play store', 'react native',
               'expo', 'mobile app', 'flutter', 'xcode', 'cocoapods',
               'fastlane', 'app-store-connect', 'app deployment'],
    shortKeywords: ['ios', 'apk'],
    description: 'App Store, TestFlight, mobile CI/CD',
    installCommand: 'vskill install anton-abyzov/vskill --plugin mobile',
  },
  'google-workspace': {
    keywords: ['google sheets', 'google docs', 'google drive',
               'google slides', 'google calendar', 'google workspace',
               'gmail api', 'sheets api'],
    shortKeywords: [],
    description: 'Google Sheets, Docs, Drive, Calendar',
    installCommand: 'vskill install anton-abyzov/vskill --plugin google-workspace',
  },
  marketing: {
    keywords: ['linkedin', 'instagram', 'social media', 'twitter',
               'facebook', 'tiktok', 'content marketing', 'social post',
               'blog post', 'newsletter', 'slack messaging'],
    shortKeywords: [],
    description: 'Slack messaging, social media, content marketing',
    installCommand: 'vskill install anton-abyzov/vskill --plugin marketing',
  },
  productivity: {
    keywords: ['notion', 'todoist', 'trello', 'asana', 'monday.com',
               'obsidian', 'time tracking', 'project management',
               'task management'],
    shortKeywords: [],
    description: 'Notion, Todoist, Trello, project management',
    installCommand: 'vskill install anton-abyzov/vskill --plugin productivity',
  },
  skills: {
    keywords: ['find plugin', 'search plugin', 'discover skill',
               'browse marketplace', 'vskill search', 'plugin search'],
    shortKeywords: [],
    description: 'skill discovery, marketplace browsing',
    installCommand: 'vskill install anton-abyzov/vskill --plugin skills',
  },
};
```

## Integration Points

### 1. Hook: detect_vskill_recommendations() -- NEW function

Position in hook execution: runs in the "non-slash-command" code path, AFTER plugin
auto-load checks but BEFORE the LLM detect-intent call (~line 1090 area). The function
builds a string that gets prepended to any existing `additionalContext`.

Why before LLM: The LLM call is async and can take 1-5s. Vskill suggestions are instant
(< 5ms) and should appear regardless of whether LLM detection succeeds or fails.

Cap at 3 suggestions. If > 3 match, sort by keyword match length (longer match = more
specific = higher priority).

### 2. LLM Detector: VSKILL_PLUGIN_REGISTRY + detectVskillPlugins() -- NEW exports

Added as a pure utility -- does NOT modify the LLM prompt or Haiku call. The constant
and function are consumed only by detect-intent CLI and project-detector.

Deny-list in `buildDetectionPrompt()` updated from:
```
DO NOT suggest: frontend, backend, testing, infra, k8s, mobile, skills, payments, ml, kafka, confluent, security, blockchain -- these are NOT available as plugins.
```
to:
```
DO NOT suggest: frontend, backend, testing, infra, k8s, payments, ml, kafka, confluent, security, blockchain -- these are NOT available as plugins.
Note: mobile, google-workspace, marketing, productivity, skills are vskill marketplace plugins detected via keyword matching (not LLM). Do not recommend them here.
```

### 3. Project Detector: vskillPlugins field -- EXTEND interface

`ProjectTypeResult` gets `vskillPlugins?: string[]` (optional, defaults to `[]`).

Existing detection rules for mobile types already detected but with `plugins: []`:
- `react-native` (line 263)
- `expo` (line 268)
- `ios` (line 273)
- `android` (line 279)

These rules get a new field on `DetectionRule`: `vskillPlugins?: string[]`.
Mobile rules get `vskillPlugins: ['mobile']`.

`detectProjectType()` collects vskillPlugins into a separate `Set<string>` and
returns them alongside existing `types` and `plugins`.

### 4. Auto-Install: vskillPlugin field -- EXTEND mapping

COMPONENT_MAPPING entry type extends to `{ skills: string[], agents: string[], vskillPlugin?: string }`.

Entries updated:
```
'react native'  -> vskillPlugin: 'mobile'
'react-native'  -> vskillPlugin: 'mobile'
'expo'          -> vskillPlugin: 'mobile'
'ios'           -> vskillPlugin: 'mobile'
'android'       -> vskillPlugin: 'mobile'
'mobile'        -> vskillPlugin: 'mobile'
'app store'     -> vskillPlugin: 'mobile'
'play store'    -> vskillPlugin: 'mobile'
```

`analyzeUserIntent()` return type extends to `{ skills: string[], agents: string[], vskillPlugins: string[] }`.

### 5. Detect-Intent CLI: vskillRecommendations field -- EXTEND result

`DetectIntentResult` gets:
```typescript
vskillRecommendations?: {
  plugin: string;
  matchedKeyword: string;
  installCommand: string;
}[]
```

`detectIntentCommand()` calls `detectVskillPlugins(prompt)` after LLM detection
and merges results. Only includes plugins NOT in `vskill.lock`.

## Suggestion Format

Each suggestion is a compact line (< 300 chars):

```
---
Available vskill plugins for your task:
- mobile (App Store, TestFlight, mobile CI/CD)
  Install: vskill install anton-abyzov/vskill --plugin mobile
---
```

Multiple plugins listed as additional bullets:
```
---
Available vskill plugins for your task:
- mobile (App Store, TestFlight, mobile CI/CD)
  Install: vskill install anton-abyzov/vskill --plugin mobile
- marketing (Slack messaging, social media, content marketing)
  Install: vskill install anton-abyzov/vskill --plugin marketing
---
```

## Edge Cases

| Case | Behavior |
|------|----------|
| No vskill.lock file | All plugins treated as not-installed; suggestions fire for any match |
| vskill CLI not installed | Still show install command text (informational) |
| Empty/malformed prompt | No keywords match, no suggestions |
| Keyword inside URL/code | May match (accepted; suggestion is informational only) |
| TMPDIR not writable | Skip dedup silently; suggestion may repeat |
| additionalContext near 3000 limit | Existing truncation guard in `output_approve_with_context()` handles overflow |
| 4+ plugins match | Cap at 3, sorted by keyword match length (longer = more specific) |
| "curious" containing "ios" | `grep -qwi 'ios'` with word boundary prevents false positive |
| bash 3.2 on macOS | case/esac fallback (no associative arrays needed) |

## Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `plugins/specweave/hooks/user-prompt-submit.sh` | MODIFY | Add `detect_vskill_recommendations()`, registry metadata, keyword match functions, integration into main flow |
| `src/core/lazy-loading/llm-plugin-detector.ts` | MODIFY | Add VSKILL_PLUGIN_REGISTRY constant, VskillPluginEntry/VskillMatch interfaces, `detectVskillPlugins()` export, update deny-list text |
| `src/core/lazy-loading/project-detector.ts` | MODIFY | Add `vskillPlugins` to `ProjectTypeResult` and `DetectionRule`, populate for mobile rules, collect in `detectProjectType()` |
| `src/utils/auto-install.ts` | MODIFY | Add `vskillPlugin` to COMPONENT_MAPPING type and mobile entries, extend `analyzeUserIntent()` return type |
| `src/cli/commands/detect-intent.ts` | MODIFY | Add `vskillRecommendations` to `DetectIntentResult`, call `detectVskillPlugins()`, merge into output |

## Testing Strategy

- **Hook tests**: Shell-level verification
  - Verify keyword matching (positive cases for each plugin)
  - Verify word-boundary for short keywords ("curious" must NOT match "ios")
  - Verify multi-word keywords ("google sheets" matches)
  - Verify TMPDIR dedup (second call for same plugin returns empty)
  - Verify cap at 3 suggestions
  - Verify suggestion format under 300 chars per plugin
  - Verify integration with existing `output_approve_with_context()`

- **TypeScript tests**: Vitest
  - `detectVskillPlugins("deploy ios app")` returns `[{plugin: "mobile", matchedKeyword: "ios", ...}]`
  - `detectVskillPlugins("update react component")` returns `[]`
  - `detectVskillPlugins("post on linkedin and update google sheets")` returns marketing + google-workspace
  - Word-boundary: `detectVskillPlugins("I am curious about this")` returns `[]` (no "ios" match)
  - Cap: prompt matching 4+ plugins returns only 3
  - `ProjectTypeResult.vskillPlugins` populated for ios/android/react-native/expo project types
  - `analyzeUserIntent("deploy ios app").vskillPlugins` returns `["mobile"]`
  - `DetectIntentResult.vskillRecommendations` present in CLI JSON output

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| False positives on short keywords | Word-boundary matching (`grep -qwi` / regex `\b`) for <5 char keywords |
| Registry goes stale as new plugins publish | Both registries in a single codebase; document update process |
| Context budget overflow | Cap at 3 suggestions (~900 chars max); existing truncation guard |
| Duplicate suggestions (hook + project-detector) | Both paths check vskill.lock; TMPDIR markers deduplicate within hook |
| macOS bash 3.2 incompatibility | case/esac pattern matching (no associative arrays needed) |

## Not In Scope

- Auto-installation of vskill plugins (suggest-only; auto-install is a future increment)
- Adding new plugins to registry (hardcoded 5 known plugins)
- VSCode extension integration
- Telemetry for suggestion impressions
- Config toggle specific to vskill suggestions (uses existing `pluginAutoLoad.enabled`)
