# Plan: CLI Health Check Command

## Approach
Add a `specweave health` CLI command that runs diagnostic checks on config, plugins, and external sync connectivity.

## Components
1. Health check command handler (`src/cli/commands/health.ts`)
2. Diagnostic check runner (config validation, plugin scan, sync probe)
3. JSON output formatter for CI/CD integration
