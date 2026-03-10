---
id: US-004
feature: FS-460
title: "Provider registry foundation (P2)"
status: completed
priority: P0
created: 2026-03-09
tldr: "**As a** platform architect."
project: vskill-platform
related_projects: [vskill]
---

# US-004: Provider registry foundation (P2)

**Feature**: [FS-460](./FEATURE.md)

**As a** platform architect
**I want** a provider registry that can represent GitHub orgs and future external providers
**So that** the system is ready for diverse skill sources beyond GitHub org scanning

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given a new file `src/lib/trust/provider-registry.ts`, when imported, then it exports a `ProviderDefinition` type with fields: `id: string`, `type: "github-org" | "external-api"`, `name: string`, `trustLevel: "vendor" | "trusted" | "community"`, and `config: Record<string, unknown>`
- [x] **AC-US4-02**: Given the provider registry, when `PROVIDER_REGISTRY` constant is exported, then it contains entries for all current vendor orgs (anthropics, openai, google-gemini, google, microsoft, vercel, cloudflare) with `type: "github-org"` and `trustLevel: "vendor"`
- [x] **AC-US4-03**: Given the provider registry, when `VENDOR_ORGS` is derived from it, then `VENDOR_ORGS` equals the set of provider IDs where `trustLevel === "vendor"` and `type === "github-org"`
- [x] **AC-US4-04**: Given `trusted-orgs.ts` is migrated to use the registry, when existing callers import `VENDOR_ORGS`, `TRUSTED_ORGS`, `isVendorOrg`, `isTrustedOrg`, or `checkVendorRepo`, then all exports remain backward-compatible with identical behavior
- [x] **AC-US4-05**: Given the migration, when unit tests run, then equivalence tests verify that `VENDOR_ORGS` and `TRUSTED_ORGS` from the migrated module produce identical sets to the current hardcoded values

---

## Implementation

**Increment**: [0460-vendor-provider-discovery](../../../../../increments/0460-vendor-provider-discovery/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Create provider-registry.ts with ProviderDefinition type and PROVIDER_REGISTRY constant
- [x] **T-002**: Migrate trusted-orgs.ts to derive sets from provider registry
- [x] **T-003**: Sync vendor-org-discovery.js comment to reference provider-registry.ts
