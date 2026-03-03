# Plan: Deploy Living Docs to Website

## Overview

Simple 2-step deployment: build living docs from current codebase, then deploy to specweave.com. No new infrastructure or services needed — uses existing `specweave sync-docs` and website deployment pipeline.

## Components

### C1: Living Docs Build
- Run `specweave sync-docs` to regenerate all living documentation
- Validate output in `.specweave/docs/internal/specs/`
- Ensure no build errors or missing feature specs

### C2: Website Deployment
- Deploy updated docs to specweave.com
- Verify deployed docs are accessible and current

## Technology Stack

- **CLI**: SpecWeave CLI (`sync-docs` command)
- **Deployment**: Existing website deployment tooling

## Implementation Phases

### Phase 1: Build Docs
- Run living docs generation
- Validate output

### Phase 2: Deploy
- Push to website
- Verify accessibility

## Testing Strategy

- AC-US1-01: Verify build completes with exit code 0
- AC-US1-02: Verify deployed docs contain latest feature specs

## Technical Challenges

None significant — routine deployment of existing documentation pipeline.
