# 0246: App Store Connect CLI Skill

## Overview

Create a new `appstore` skill for the `specweave-mobile` plugin that provides comprehensive App Store Connect automation via the [`asc` CLI](https://github.com/rudrankriyam/App-Store-Connect-CLI). Modeled after the proven `/sw:npm` skill pattern — a step-by-step playbook that agents follow autonomously for iOS/macOS delivery workflows.

**Why this matters**: The existing 7 mobile skills cover development (React Native, Expo, Flutter, Compose, testing, Capacitor, deep linking) but **none cover App Store delivery**. The `asc` CLI is a Go binary that wraps the entire App Store Connect API — TestFlight, submissions, metadata, signing, analytics, subscriptions, Xcode Cloud, notarization — all JSON-first, no interactive prompts, perfect for agent automation.

## User Stories

### US-001: Agent-Driven TestFlight Distribution
As a mobile developer, I want an agent to handle the full TestFlight distribution flow so that I can get builds to testers with a single command.

**Acceptance Criteria:**
- [x] AC-US1-01: Skill detects `asc` CLI availability and guides installation if missing
- [x] AC-US1-02: Skill authenticates via `asc auth status` or guides `asc auth login` setup
- [x] AC-US1-03: `--testflight` mode uploads IPA and distributes to specified beta groups
- [x] AC-US1-04: Skill handles build processing wait and reports distribution status
- [x] AC-US1-05: Skill manages beta testers (add/remove from groups)

### US-002: App Store Submission Workflow
As a mobile developer, I want an agent to submit my app to the App Store with pre-submission validation so that I avoid common rejection reasons.

**Acceptance Criteria:**
- [x] AC-US2-01: `--submit` mode creates App Store version, attaches build, submits for review
- [x] AC-US2-02: Pre-submission validation runs `asc validate` before submitting
- [x] AC-US2-03: Skill checks metadata completeness (localizations, screenshots, age rating)
- [x] AC-US2-04: `--status` mode checks current submission/review status
- [x] AC-US2-05: Phased release management (create, pause, resume)

### US-003: Build & Metadata Management
As a mobile developer, I want to manage builds and app metadata from my IDE so that I don't need to context-switch to App Store Connect web.

**Acceptance Criteria:**
- [x] AC-US3-01: List/inspect builds with filtering by version and platform
- [x] AC-US3-02: Expire old builds (with `--dry-run` safety)
- [x] AC-US3-03: Update app metadata (description, keywords, what's new) per locale
- [x] AC-US3-04: Upload/manage screenshots and preview videos
- [x] AC-US3-05: Manage app categories and pricing

### US-004: Signing & Certificates
As a mobile developer, I want the agent to help manage signing identities so that I can resolve certificate/profile issues without navigating the web portal.

**Acceptance Criteria:**
- [x] AC-US4-01: `asc signing fetch --create-missing` for quick signing setup
- [x] AC-US4-02: List/create/revoke certificates
- [x] AC-US4-03: List/create/download provisioning profiles
- [x] AC-US4-04: Bundle ID management with capabilities

### US-005: Analytics, Finance & Subscriptions
As a mobile developer, I want to query app analytics and manage in-app purchases from the CLI so that agents can include data in reports and automate IAP setup.

**Acceptance Criteria:**
- [x] AC-US5-01: Download sales reports and analytics data
- [x] AC-US5-02: Subscription group and subscription CRUD
- [x] AC-US5-03: In-app purchase management
- [x] AC-US5-04: Customer review monitoring and response
- [x] AC-US5-05: Finance report download by region

### US-006: CI/CD Integration (Xcode Cloud & Notarization)
As a mobile developer, I want agents to trigger Xcode Cloud builds and handle macOS notarization so that delivery pipelines are fully automated.

**Acceptance Criteria:**
- [x] AC-US6-01: Trigger Xcode Cloud workflows with `--wait` for completion
- [x] AC-US6-02: Check build run status and download artifacts
- [x] AC-US6-03: Submit macOS apps for notarization with `--wait`
- [x] AC-US6-04: Check notarization status and retrieve logs

### US-007: Workflow Automation
As a power user, I want to define reusable multi-step workflows so that complex delivery sequences are repeatable.

**Acceptance Criteria:**
- [x] AC-US7-01: Document `.asc/workflow.json` usage in the skill
- [x] AC-US7-02: Validate, list, and run workflows
- [x] AC-US7-03: Support for dry-run mode on all destructive operations

## Command Modes

| Command | Flow | Use Case |
|---------|------|----------|
| `/sw-mobile:appstore` | Auth check → Build list → Submit → Status | **DEFAULT: Full submission** |
| `/sw-mobile:appstore --testflight` | Auth → Upload → Distribute to groups → Wait | **TestFlight distribution** |
| `/sw-mobile:appstore --submit` | Auth → Validate → Create version → Attach build → Submit | **Submit for review** |
| `/sw-mobile:appstore --status` | Auth → Check review status | **Quick status check** |
| `/sw-mobile:appstore --metadata` | Auth → Update localizations/screenshots/info | **Metadata only** |
| `/sw-mobile:appstore --validate` | Auth → Run `asc validate --strict` | **Pre-submission check** |
| `/sw-mobile:appstore --builds` | Auth → List/manage builds | **Build management** |
| `/sw-mobile:appstore --signing` | Auth → Fetch/create certificates & profiles | **Signing setup** |
| `/sw-mobile:appstore --analytics` | Auth → Download reports/reviews | **Analytics & data** |

## Technical Details

### `asc` CLI Installation
```bash
# Homebrew (recommended)
brew tap rudrankriyam/tap && brew install asc

# Install script
curl -fsSL https://raw.githubusercontent.com/rudrankriyam/App-Store-Connect-CLI/main/install.sh | bash

# GitHub Actions
- uses: rudrankriyam/setup-asc@v1
```

### Authentication
```bash
# Initial setup
asc auth login --name "MyApp" --key-id "ABC123" --issuer-id "DEF456" --private-key /path/to/AuthKey.p8

# Verify
asc auth status --validate

# Multi-profile
asc auth switch --name "ClientApp"
asc --profile "ClientApp" apps list
```

### Environment Variables
- `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_PRIVATE_KEY_PATH` — Core auth
- `ASC_PRIVATE_KEY_B64` — Base64 key (CI-friendly)
- `ASC_PROFILE` — Named profile
- `ASC_APP_ID` — Default app ID
- `ASC_VENDOR_NUMBER` — For finance reports
- `ASC_TIMEOUT`, `ASC_MAX_RETRIES` — Tuning

## Out of Scope
- Building IPA/PKG files (handled by Xcode, EAS Build, fastlane)
- Google Play Store (separate skill if needed)
- Custom MCP server for `asc` (CLI-first approach, MCP can wrap later)

## Dependencies
- `asc` CLI installed (brew or install script)
- Apple Developer account with API key (.p8 file)
- `specweave-mobile` plugin (where the skill lives)
