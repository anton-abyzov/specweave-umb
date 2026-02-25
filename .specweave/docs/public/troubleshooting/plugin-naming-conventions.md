# Plugin Naming Conventions

SpecWeave plugins are split across two marketplaces and use two naming systems that must be used correctly in different contexts.

## The Two Marketplaces

| Marketplace | Scope | Plugin Examples |
|-------------|-------|-----------------|
| **@specweave** | Core framework plugins (keep `sw-` prefix) | `sw`, `sw-github` |
| **@vskill** | Domain plugins (no `sw-` prefix) | `frontend`, `backend`, `testing`, `mobile`, `infra`, `k8s`, `ml`, `payments`, `kafka` |

## The Two Naming Systems

| System | Format | Examples |
|--------|--------|----------|
| **Marketplace names** | `sw`, `sw-*` (core) / bare name (domain) | `sw`, `sw-github`, `frontend`, `backend`, `testing` |
| **Directory names** | `specweave`, `specweave-*` (core) / bare name (domain) | `specweave`, `specweave-github`, `frontend`, `backend` |

## When to Use Each Format

### Use Marketplace Names For:

1. **Claude CLI commands**:
   ```bash
   # Core plugins (@specweave marketplace)
   claude plugin install sw@specweave
   claude plugin install sw-github@specweave
   # Domain plugins (@vskill marketplace)
   claude plugin install frontend@vskill
   claude plugin install backend@vskill
   ```

2. **API inputs** (function parameters):
   ```typescript
   await cacheManager.installPlugins({ plugins: ['sw', 'sw-github'] });
   await cacheManager.installPlugins({ plugins: ['frontend', 'backend'], marketplace: 'vskill' });
   ```

3. **LLM responses** (detectPluginsViaLLM returns these):
   ```typescript
   const result = await detectPluginsViaLLM(prompt);
   // result.plugins = ['frontend', 'backend']
   ```

4. **Registry keys** in `~/.claude/plugins/installed_plugins.json`:
   ```json
   {
     "plugins": {
       "sw@specweave": [{ "scope": "user", ... }],
       "sw-github@specweave": [{ "scope": "user", ... }],
       "frontend@vskill": [{ "scope": "user", ... }],
       "backend@vskill": [{ "scope": "user", ... }]
     }
   }
   ```

5. **State files** (`loadedPlugins` array):
   ```json
   {
     "loadedPlugins": ["sw", "sw-github", "frontend", "backend"]
   }
   ```

6. **Keyword detector constants**:
   ```typescript
   // keyword-detector.ts
   PLUGIN_GROUPS = { frontend: 'frontend', ... }
   KEYWORD_PLUGIN_MAP = { react: 'frontend', ... }
   ```

### Use Directory Names For:

1. **Filesystem paths** (marketplace directories):
   ```
   # Core plugins (specweave marketplace)
   ~/.claude/plugins/marketplaces/specweave/plugins/specweave-github/
   # Domain plugins (vskill marketplace)
   ~/.claude/plugins/marketplaces/vskill/plugins/frontend/
   ~/.claude/plugins/marketplaces/vskill/plugins/backend/
   ```

2. **Test mocks for directories**:
   ```typescript
   createMockPlugin(path, 'specweave');
   createMockPlugin(path, 'specweave-github');
   createMockPlugin(path, 'frontend');   // vskill marketplace
   ```

## Conversion Functions

The `cache-manager.ts` module provides conversion functions:

```typescript
import {
  marketplaceNameToDirectory,
  directoryToMarketplaceName
} from './cache-manager.js';

// Core plugins (specweave marketplace): sw-* ↔ specweave-*
marketplaceNameToDirectory('sw')          // → 'specweave'
marketplaceNameToDirectory('sw-github')   // → 'specweave-github'

directoryToMarketplaceName('specweave')          // → 'sw'
directoryToMarketplaceName('specweave-github')   // → 'sw-github'

// Domain plugins (vskill marketplace): name stays the same
marketplaceNameToDirectory('frontend')    // → 'frontend'
directoryToMarketplaceName('frontend')    // → 'frontend'
```

## Common Issues

### 1. Wrong Format in Registry Check

```typescript
// ❌ WRONG - using directory name for registry check
isPluginRegistered('specweave-github');  // Registry uses 'sw-github@specweave'

// ✅ CORRECT - using marketplace name with marketplace qualifier
isPluginRegistered('sw-github');       // core plugin
isPluginRegistered('frontend');        // domain plugin (@vskill)
```

### 2. Wrong Format in Plugin Map

```typescript
// ❌ WRONG - using old sw-* names for domain plugins
const KEYWORD_PLUGIN_MAP = {
  react: 'sw-frontend',  // Should be 'frontend'
  nodejs: 'sw-backend',  // Should be 'backend'
};

// ✅ CORRECT - domain plugins use bare names
const KEYWORD_PLUGIN_MAP = {
  react: 'frontend',
  nodejs: 'backend',
};
```

### 3. Mixed Formats in Tests

When testing, always use the appropriate format:

```typescript
// For CLI commands (marketplace names)
execFileNoThrowSync('claude', ['plugin', 'install', 'frontend@vskill']);
execFileNoThrowSync('claude', ['plugin', 'install', 'sw-github@specweave']);

// For checking filesystem (directory names)
fs.existsSync(path.join(vskillMarketplacePath, 'frontend'));
fs.existsSync(path.join(specweaveMarketplacePath, 'specweave-github'));

// Both can be checked with fallback mapping
const PLUGIN_FOLDER_TO_SHORT = {
  specweave: 'sw',
  'specweave-github': 'sw-github',
  // vskill domain plugins have no mapping needed (same name)
};
```

## Cache Directory Structure

The installed plugin cache uses marketplace names in registry but stores files with specific paths:

```
~/.claude/plugins/
├── installed_plugins.json           # Uses: sw-github@specweave, frontend@vskill
└── cache/
    ├── specweave/                   # Core marketplace
    │   └── sw-github/              # Core plugin short name
    │       └── 1.0.0/
    │           └── hooks/
    └── vskill/                      # Domain marketplace
        └── frontend/                # Domain plugin name (no sw- prefix)
            └── 1.0.0/
                └── hooks/
```

**Important**: Domain plugins in the `vskill` marketplace use bare names (`frontend`, not `sw-frontend`). Core plugins in `specweave` keep the `sw-` prefix.

| Location | Core Plugin Example | Domain Plugin Example |
|----------|--------------------|-----------------------|
| Registry key | `sw-github@specweave` | `frontend@vskill` |
| Cache path | `cache/specweave/sw-github/1.0.0/` | `cache/vskill/frontend/1.0.0/` |
| Marketplace source | `marketplaces/specweave/plugins/specweave-github/` | `marketplaces/vskill/plugins/frontend/` |

## Key Rules

1. **Core plugins** (`sw`, `sw-github`): Use `sw-*@specweave` format in registry
2. **Domain plugins** (`frontend`, `backend`, etc.): Use `name@vskill` format in registry
3. **Cache paths**: Core under `specweave/`, domain under `vskill/`
4. **API calls**: Use the correct marketplace-qualified name
5. **Use conversion functions** when crossing between contexts

## Related

- [Plugin Management Guide](../guides/plugin-management.md)
- [Plugin Auto-Reinstall Issues](./plugin-auto-reinstall.md)
- [VSCode Debug Child Processes](./vscode-debug-child-processes.md)
