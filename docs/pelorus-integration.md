# Pelorus Integration

This document outlines how Uplift can integrate with [Pelorus](https://github.com/dora-metrics/pelorus), Red Hat's open-source tool for measuring software delivery performance using DORA metrics.

## Why integrate?

Uplift and Pelorus are complementary:

| | Uplift | Pelorus |
|---|---|---|
| **What it measures** | Qualitative maturity (human assessments, 1-4 scale) | Quantitative performance (actual system metrics) |
| **How** | Self-assessment surveys | Automated data collection from Git, CI/CD, issue trackers |
| **Perspective** | "How mature are our practices?" | "How well are we actually delivering?" |

A team could score themselves at level 3 on Continuous Delivery but have a lead time of 14 days. The integration surfaces these gaps -- pairing what teams *believe* with what the data *shows*.

## Pelorus overview

Pelorus tracks the four DORA metrics:

| Metric | What it measures | Data sources |
|--------|-----------------|--------------|
| **Lead Time for Change** | Time from commit to production deployment | Git commits + deployment events |
| **Deployment Frequency** | How often code ships to production | Deployment events |
| **Mean Time to Restore (MTTR)** | Time to recover from a failure | Issue tracker (Jira, GitHub Issues, ServiceNow, PagerDuty) |
| **Change Failure Rate** | Percentage of deployments causing failures | Failure events / deployment count |

Pelorus runs on OpenShift, collects data via exporters, stores it in Prometheus, and visualizes through Grafana dashboards. It also supports a webhook exporter for push-based ingestion from any system.

## Capability mapping

The following Uplift capabilities map directly to Pelorus DORA metrics. These are candidates for data-informed scoring.

### Lead Time for Change

| Uplift Capability | How Pelorus data informs it |
|---|---|
| **C2 -- Release Frequency** | Lead time directly measures release cadence. Level 4 ("released on every successful build") implies sub-hour lead times. |
| **C6 -- Continuous Delivery** | Lead time trend shows progression from manual (level 1) to zero-touch (level 4). |
| **B5 -- Continuous Integration** | Long lead times often indicate CI pipeline bottlenecks. |
| **C4 -- Build Pipeline Traceability** | Pelorus links commits to deployments, providing the traceability this capability measures. |

**Suggested thresholds:**

| Lead Time | Suggested Level |
|-----------|----------------|
| > 1 month | 1 |
| 1 week -- 1 month | 2 |
| 1 day -- 1 week | 3 |
| < 1 day | 4 |

### Deployment Frequency

| Uplift Capability | How Pelorus data informs it |
|---|---|
| **C2 -- Release Frequency** | Direct measurement of what this capability assesses. |
| **C9 -- Push Button Releases** | High frequency implies automated, push-button deployments. |
| **C1 -- Deployment Strategy** | Consistent, frequent deployments indicate a mature strategy. |

**Suggested thresholds:**

| Deployment Frequency | Suggested Level |
|---------------------|----------------|
| Less than once per sprint | 1 |
| Once per sprint | 2 |
| Multiple times per sprint | 3 |
| On every successful build | 4 |

### Mean Time to Restore (MTTR)

| Uplift Capability | How Pelorus data informs it |
|---|---|
| **D4 -- On-Call Strategy** | MTTR directly measures on-call effectiveness. Levels 3-4 explicitly reference "consistently low MTTR". |
| **D3 -- Monitoring and Alerting** | Low MTTR indicates alerts are firing correctly and are actionable. |
| **D2 -- Runbook Adoption** | Effective runbooks reduce MTTR. |
| **D1 -- DevOps Practice** | Teams that own production (level 4) typically have lower MTTR. |

**Suggested thresholds:**

| MTTR | Suggested Level |
|------|----------------|
| > 1 week | 1 |
| 1 day -- 1 week | 2 |
| 1 hour -- 1 day | 3 |
| < 1 hour | 4 |

### Change Failure Rate

| Uplift Capability | How Pelorus data informs it |
|---|---|
| **A3 -- Test Suite** | High failure rate indicates gaps in test coverage. |
| **B4 -- Automated Testing** | Automated tests should catch issues before production. |
| **A9 -- Build for Availability** | Availability testing reduces change failures. |
| **B5 -- Continuous Integration** | A mature CI pipeline catches failures before deployment. |

**Suggested thresholds:**

| Change Failure Rate | Suggested Level |
|--------------------|----------------|
| > 45% | 1 |
| 16--45% | 2 |
| 1--15% | 3 |
| < 1% | 4 |

## Integration architecture

### Option A: Dashboard overlay (recommended first step)

Uplift queries Pelorus's Prometheus API and displays DORA metrics alongside assessment scores. No scoring logic changes -- purely informational.

```
+------------------+          PromQL queries          +-------------------+
|                  |  -------------------------------->|                   |
|     Uplift       |  GET /api/v1/query               |  Pelorus          |
|     (FastAPI)    |  ?query=sdp:lead_time:by_app     |  (Prometheus)     |
|                  |<--------------------------------  |                   |
+------------------+       JSON time-series           +-------------------+
```

**What Uplift shows:**
- On the product detail page, display actual DORA metrics next to the self-assessed scores
- On the org dashboard, overlay org-wide DORA performance against org-wide maturity averages
- Highlight discrepancies (e.g., team claims level 3 on CI but lead time is 3 weeks)

**What it requires:**
- New config: `UPLIFT_PELORUS_URL` (Prometheus/Thanos endpoint)
- A service module that queries PromQL
- Template changes to render DORA metrics on product and dashboard pages
- Mapping between Uplift product names and Pelorus `app` labels

### Option B: Score suggestions

Uplift uses Pelorus data to *suggest* capability scores. Assessors still make the final call, but they see what the data indicates.

```
+------------------+                                  +-------------------+
|                  |  1. Fetch DORA metrics            |                   |
|     Uplift       |  -------------------------------->|  Pelorus          |
|                  |<--------------------------------  |  (Prometheus)     |
|                  |  2. Apply threshold mapping       |                   |
|                  |  3. Pre-fill assessment form      +-------------------+
|                  |     with suggested scores
+------------------+
```

**What changes in Uplift:**
- The "New Assessment" form pre-fills mapped capabilities with suggested levels
- Suggested values are visually distinct (e.g., different color, "suggested by Pelorus" label)
- Assessor can accept or override each suggestion
- The assessment records whether each score was human-entered or data-suggested

### Option C: Automated scoring (future)

Certain capabilities are scored entirely by Pelorus data, no human input required. The assessment form skips those fields and fills them automatically.

This is only appropriate for capabilities that have a clear, unambiguous mapping to a metric (e.g., C2 Release Frequency ↔ Deployment Frequency). Most capabilities require human judgment and should not be fully automated.

## Implementation plan

### Phase 1: Configuration and connectivity

Add Pelorus connection settings:

```python
# app/config.py
class Settings(BaseSettings):
    # ... existing settings ...
    pelorus_url: str = ""          # Prometheus/Thanos query endpoint
    pelorus_token: str = ""        # Bearer token if auth required
    pelorus_app_label: str = ""    # Label used to match products to Pelorus apps
```

New env vars: `UPLIFT_PELORUS_URL`, `UPLIFT_PELORUS_TOKEN`, `UPLIFT_PELORUS_APP_LABEL`.

### Phase 2: Prometheus query service

New service module to query Pelorus:

```python
# app/services/pelorus.py

async def get_dora_metrics(app_name: str) -> dict | None:
    """Fetch DORA metrics for a product from Pelorus Prometheus."""
    # Query these PromQL expressions:
    #   sdp:lead_time:by_app{app="<app_name>"}
    #   count_over_time(deploy_timestamp{app="<app_name>"}[30d])
    #   sdp:time_to_restore:by_app{app="<app_name>"}
    #   sdp:change_failure_rate:by_app{app="<app_name>"}
    ...
```

The existing `httpx` dependency already supports this -- no new packages needed.

### Phase 3: Product-to-app mapping

Products in Uplift need to be linked to Pelorus app labels. Options:

1. **Tag-based** -- A tag with key `pelorus_app` maps the product to its Pelorus app name. No schema changes needed; uses existing tag infrastructure.
2. **Name matching** -- Attempt to match `product.name` to Pelorus `app` label directly. Simple but fragile.
3. **Dedicated field** -- Add a `pelorus_app` column to the Product model. Clean but requires a migration.

Recommendation: Start with tag-based (option 1). It works today with zero code changes to the data model.

### Phase 4: Dashboard integration

Display DORA metrics on:
- **Product detail page** -- Show current DORA metrics in a sidebar or card
- **Assessment form** -- Show metrics as context while scoring
- **Org dashboard** -- Aggregate DORA metrics alongside maturity averages

### Phase 5: Score suggestions (optional)

Apply the threshold mappings defined above to pre-fill assessment scores. Store whether each score was human-entered or data-suggested for audit purposes.

## PromQL queries reference

These are the Pelorus recording rules that Uplift would query:

```promql
# Lead time (seconds) -- per app
sdp:lead_time:by_app{app="myapp"}

# Lead time -- org-wide average
sdp:lead_time:global

# Deployment count in last 30 days -- per app
count_over_time(deploy_timestamp{app="myapp"}[30d])

# MTTR (seconds) -- per app
sdp:time_to_restore:by_app{app="myapp"}

# MTTR -- org-wide average
sdp:time_to_restore:global

# Change failure rate (ratio 0-1) -- per app
sdp:change_failure_rate:by_app{app="myapp"}

# Change failure rate -- org-wide
sdp:change_failure_rate:global

# List all tracked applications
sdp:applications
```

All queries go through the standard Prometheus HTTP API:

```
GET {pelorus_url}/api/v1/query?query=sdp:lead_time:by_app{app="myapp"}
```

## Mapping products to Pelorus apps

Pelorus identifies applications by the `app.kubernetes.io/name` label on Kubernetes resources (configurable via `APP_LABEL`). Uplift products need a way to reference this.

Recommended approach using existing tags:

| Uplift Product | Tag Key | Tag Value | Pelorus App Label |
|---|---|---|---|
| Payment Service | `pelorus_app` | `payment-service` | `payment-service` |
| Auth Gateway | `pelorus_app` | `auth-gw` | `auth-gw` |

Products without a `pelorus_app` tag simply don't show DORA metrics -- graceful degradation.

## Prerequisites

- Pelorus deployed on OpenShift with exporters configured
- Pelorus Prometheus/Thanos endpoint accessible from where Uplift runs (network connectivity)
- If authentication is required, a bearer token or service account with read access to the Prometheus API
- Products tagged with `pelorus_app` matching Pelorus application labels

## Risks and considerations

- **Network access**: Pelorus typically runs inside an OpenShift cluster. Uplift may need a Route or Ingress to reach the Prometheus endpoint, or both could run in the same cluster.
- **Data freshness**: Pelorus exporters scrape on intervals (typically 60s for Prometheus). DORA metrics are inherently lagging indicators -- this is fine for maturity assessment purposes.
- **Metric availability**: Not all products will have Pelorus data (e.g., non-deployed services, documentation, internal tools). The integration must handle missing data gracefully.
- **Threshold calibration**: The suggested score thresholds above are starting points based on DORA's "Accelerate" research. Organizations should calibrate these to their own context.
- **OpenShift dependency**: Pelorus currently requires OpenShift. Organizations using vanilla Kubernetes or other platforms would need an alternative DORA metrics source (e.g., custom Prometheus exporters, or tools like Four Keys/Sleuth).
