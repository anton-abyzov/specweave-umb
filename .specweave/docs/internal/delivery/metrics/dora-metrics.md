# DORA Metrics - Engineering Performance Tracking

**Purpose**: Track DORA (DevOps Research and Assessment) metrics to measure engineering excellence and continuous improvement.

**Last Updated**: 2026-02-25 (Auto-updated by CI/CD)
**Owner**: Engineering Leadership
**Data Source**: `.specweave/metrics/dora-latest.json` (updated twice daily at 06:00 and 18:00 UTC)

---

## What are DORA Metrics?

DORA metrics are four key metrics that indicate the performance of software delivery and operational stability:

1. **Deployment Frequency** - How often we deploy to production
2. **Lead Time for Changes** - Time from code commit to production deployment
3. **Change Failure Rate** - Percentage of deployments causing production failures
4. **Time to Restore Service** - How quickly we recover from production incidents

**Source**: [DORA State of DevOps Research](https://dora.dev/)

---

## Performance Levels

| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| **Deployment Frequency** | On-demand (multiple/day) | Weekly - Monthly | Monthly - 6 months | < 6 months |
| **Lead Time for Changes** | < 1 hour | 1 hour - 1 week | 1 week - 1 month | > 1 month |
| **Change Failure Rate** | 0-15% | 15-30% | 30-45% | > 45% |
| **Time to Restore Service** | < 1 hour | < 1 day | 1 day - 1 week | > 1 week |

**Goal**: Achieve **High** performance across all metrics (Elite is aspirational).

---

## Current SpecWeave Performance

Current values are auto-generated and stored in `.specweave/metrics/dora-latest.json`.
See the live dashboard at [spec-weave.com/docs/metrics](https://spec-weave.com/docs/metrics) and the detailed report at `.specweave/metrics/dora-report.md`.

**Data Source**: Calculated from GitHub commits, releases, and issues via automated workflow (twice daily).

---

## How We Measure

### 1. Deployment Frequency
**Data Source**: Commits to the `develop` branch (each commit = 1 deployment in trunk-based development)

**Calculation**: Count commits to develop in last 30 days, extrapolate to annual rate for tier classification.

**Tracking**: Automated via GitHub Actions workflow (`dora-metrics.yml`)

---

### 2. Lead Time for Changes
**Data Source**: Git commits and GitHub Releases API

**Calculation**: For each release, find commits since previous release, compute time delta (commit date → release date). Reports average, P50, and P90.

**Tracking**: Automated via GitHub Actions workflow (`dora-metrics.yml`)

---

### 3. Change Failure Rate
**Data Source**: GitHub Issues labeled `incident` or `production-bug`, and GitHub Releases

**Calculation**: Link each incident to the most recent release before it, calculate percentage of releases with incidents.

**Tracking**: Automated via GitHub Actions workflow (`dora-metrics.yml`)

---

### 4. Time to Restore Service (MTTR)
**Data Source**: Closed GitHub Issues labeled `incident` or `production-bug`

**Calculation**: Time from `created_at` to `closed_at` for each closed incident. Reports average, P50, and P90.

**Tracking**: Automated via GitHub Actions workflow (`dora-metrics.yml`)

---

## Action Items to Improve

### Deployment Frequency
- ✅ **Implemented**: CI/CD pipeline with automated testing
- 🔄 **In Progress**: Feature flags for gradual rollouts
- 📅 **Planned**: Blue-green deployments for zero-downtime

### Lead Time for Changes
- ✅ **Implemented**: Branch protection rules, fast PR reviews (< 4 hours SLA)
- 🔄 **In Progress**: Automated E2E test suite (reduce manual QA time)
- 📅 **Planned**: Pre-merge integration testing environments

### Change Failure Rate
- ✅ **Implemented**: Pre-commit hooks, PR code review checklists
- 🔄 **In Progress**: Automated smoke tests post-deployment
- 📅 **Planned**: Canary deployments for high-risk changes

### Time to Restore Service
- ✅ **Implemented**: On-call rotation, runbooks for common incidents
- 🔄 **In Progress**: Automated rollback procedures
- 📅 **Planned**: Chaos engineering for failure testing

---

## Dashboard

**Live Dashboard**: [spec-weave.com/docs/metrics](https://spec-weave.com/docs/metrics) (Shields.io dynamic badges pulling from `dora-latest.json`)

**Historical Data**: `.specweave/metrics/dora-history.jsonl` (append-only JSONL for trending)

---

## Quarterly Review

**Schedule**: Every quarter (end of Q1, Q2, Q3, Q4)

**Participants**: Engineering leads, DevOps, product managers

**Agenda**:
1. Review current DORA metrics vs. goals
2. Identify trends (improving/declining metrics)
3. Root cause analysis for degraded metrics
4. Action items for next quarter
5. Update goals if needed

**Next Review**: End of Q1 2026

---

## Related Documentation

- [Release Process](./release-process) - Links to deployment frequency
- [Testing Strategy](./guides/testing-strategy) - Links to change failure rate
- **Incident Response** - *Coming soon* - Performance incident handling and MTTR tracking
- **CI/CD Pipeline** - *Coming soon* - Automated deployment and lead time tracking
- [Branching Strategy](./branch-strategy) - Links to lead time

---

## References

- [DORA Research](https://dora.dev/) - Source of DORA metrics
- [Accelerate Book](https://www.amazon.com/Accelerate-Software-Performing-Technology-Organizations/dp/1942788339) - DORA metrics background
- [Google Cloud DORA Metrics](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance) - Implementation guide
