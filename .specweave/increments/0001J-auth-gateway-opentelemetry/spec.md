---
project: colibri-identity-keycloak
---

# Auth Gateway (NodeJS API) OpenTelemetry

**Increment**: 0001J-auth-gateway-opentelemetry
**Source**: [ID-300](https://farside.atlassian.net/browse/ID-300) (JIRA)
**Parent**: [ID-213](https://farside.atlassian.net/browse/ID-213) - Support Integrations with SFCC, LMS, WP, etc.
**Priority**: P2 (Medium)
**Status**: In Progress

---

## Description

Integrate OpenTelemetry into the Colibri Node.js API (auth gateway) for distributed tracing, metrics collection, and observability across authentication flows.

---

## User Stories

### US-001: OpenTelemetry Integration
**As a** platform engineer,
**I want** distributed tracing and metrics in the auth gateway,
**So that** I can observe authentication flows end-to-end and diagnose issues quickly.

#### Acceptance Criteria

- [x] **AC-US1-01**: OpenTelemetry SDK is integrated into the Node.js auth gateway
- [x] **AC-US1-02**: Distributed tracing captures authentication flow spans
- [x] **AC-US1-03**: Key metrics (request latency, error rates, auth success/failure) are collected
- [x] **AC-US1-04**: Trace context propagates across service boundaries
- [x] **AC-US1-05**: Observability data exports to the configured backend (e.g., OTLP endpoint)

---

## Notes

- Labels: `3_27_ProofPoint`
- Imported from JIRA on 2026-03-12
