---
status: completed
---
# Increment 0411J: Add CLI health check command for deployment verification

> Imported from JIRA: [SWE2E-3](https://antonabyzov.atlassian.net/browse/SWE2E-3)

## Overview
As a DevOps engineer, I want a CLI health check command that verifies all SpecWeave services are running correctly after deployment.

## User Stories

### US-001: CLI Health Check Command
**As a** DevOps engineer
**I want** a CLI health check command
**So that** I can verify all SpecWeave services are running correctly after deployment

#### Acceptance Criteria
- [x] AC-US1-01: specweave health command checks config validity, plugin availability, and sync connectivity
- [x] AC-US1-02: Returns exit code 0 on success and non-zero on failure with diagnostic details
- [x] AC-US1-03: JSON output mode for CI/CD pipeline integration
