---
increment: 0611-docs-examples-rewrite-tabs
---

# Architecture Plan

## Approach

Pure documentation updates — 7 MDX files in docs-site. No code changes.

## CommandTabs Pattern

```mdx
import CommandTabs from '@site/src/components/CommandTabs';

<CommandTabs
  natural="Let's build a URL shortener"
  claude='sw:increment "Build URL shortener service"'
  other='increment "Build URL shortener service"'
/>
```

## Real Project Data

| Project | Repos | Increments | Tech | URL |
|---------|-------|-----------|------|-----|
| sw-url-shortener | 3 | 1+ | React+Vite, Express, TS | GitHub |
| sw-meeting-cost | 4 | 1+ | TS monorepo | GitHub |
| sw-wc26-travel | 5 | 36 | Hono, React, Expo | wc-26.net |
| specweave-umb | 3+ | 610+ | TS, Node.js | spec-weave.com |

## Conversion Strategy for Reference Pages

Convert only user-facing invocation examples. Leave reference tables, output formats, and technical blocks as plain code.
