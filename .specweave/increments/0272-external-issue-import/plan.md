# Implementation Plan: External Issue Import

## Overview

6-phase implementation: suffix system update → template enhancement → duplicate detector → import bridge → skill definition → tests.

## Architecture

### Components
- `increment-utils.ts`: Core suffix recognition (regex + methods)
- `template-creator.ts`: External source spec generation
- `increment-external-ref-detector.ts`: Metadata scan for duplicate prevention
- `import-to-increment.ts`: ExternalItem → increment conversion bridge
- `import/SKILL.md`: User-facing slash command workflow

### Data Flow
```
/sw:import → ImportCoordinator.importFrom(platform) → ExternalItem[]
  → user selects issues
  → IncrementExternalRefDetector.hasRef() → dedup check
  → ImportToIncrementConverter.createIncrement()
    → IncrementNumberManager.generateIncrementId(name, { platformSuffix })
    → createIncrementTemplates({ externalSource })
    → metadata.json with external_ref
```

## Implementation Phases

1. **Suffix System** — Update increment-utils.ts regex, add platform methods
2. **Template Creator** — Add externalSource option, generate pre-filled specs
3. **Duplicate Detector** — New module scanning metadata.json for external_ref
4. **Import Bridge** — New module converting ExternalItem to increment
5. **Skill Definition** — SKILL.md for /sw:import
6. **Tests** — Unit tests for suffix system and import-to-increment
