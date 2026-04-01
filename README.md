<p align="center">
  <img src="app/static/img/logo.svg" alt="Uplift" width="64" height="64">
</p>

# Uplift

Assessment portal that measures product maturity across five dimensions of software development. Teams self-assess against 42 capabilities scored on a 1-4 scale, producing a maturity profile that highlights strengths, gaps, and cloud-readiness.

> **Note:** Uplift does not include authentication or authorization. It is designed to be deployed as an internal tool behind your organization's existing network controls (VPN, reverse proxy with SSO, etc.).

## Screenshots

![Dashboard](docs/screenshots/dashboard.png)

![Assets](docs/screenshots/assets.png)

![Asset Detail](docs/screenshots/asset-detail.png)

![Score History](docs/screenshots/score-history.png)

## The Maturity Model

Products are evaluated across five categories:

| Category | Capabilities | Focus |
|---|---|---|
| **Code** | 12 | Code quality, testing, monitoring, BDD, reuse |
| **Build and Test** | 8 | CI, security scanning, performance testing, automation |
| **Release** | 10 | Deployment strategy, CD, feature flags, dependency management |
| **Operate** | 8 | DevOps practice, on-call, runbooks, SLA monitoring |
| **Optimize** | 4 | Process improvement, tech debt, root cause analysis, metrics |

21 of the 42 capabilities have minimum thresholds that define cloud-readiness requirements. The overall cloud score reflects how many of these thresholds are met.

See [docs/capabilities.md](docs/capabilities.md) for the full model with scoring rubrics.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Open http://localhost:8000

## Docker

### SQLite (default)

```bash
docker-compose up --build
```

### PostgreSQL

```bash
docker-compose -f docker-compose.postgres.yml up --build
```

### OpenShift

```bash
oc new-app https://github.com/maci0/uplift --strategy=docker
oc expose svc/uplift
```

To use PostgreSQL, create a database first and set the connection string:

```bash
oc new-app postgresql-persistent --name=uplift-db \
  -p POSTGRESQL_USER=uplift \
  -p POSTGRESQL_PASSWORD=changeme \
  -p POSTGRESQL_DATABASE=uplift
oc new-app https://github.com/maci0/uplift --strategy=docker \
  -e UPLIFT_DATABASE_URL=postgresql://uplift:changeme@uplift-db:5432/uplift
oc expose svc/uplift
```

## Configuration

All settings use the `UPLIFT_` env var prefix:

| Variable | Default | Description |
|---|---|---|
| `UPLIFT_DATABASE_URL` | `sqlite:///./uplift.db` | Database connection string |
| `UPLIFT_ENABLE_ASSET_CREATION` | `true` | Allow creating new products |
| `UPLIFT_ENABLE_TAG_MODIFICATION` | `true` | Allow modifying tags |
| `UPLIFT_SEED_DB` | `true` | Seed example products on first start |
| `UPLIFT_SLACK_ENDPOINT` | | Slack webhook URL |
| `UPLIFT_SLACK_CHANNEL` | | Slack channel name |

## Tests

```bash
pytest
```

## Credit

Based on the [techmaturity](https://github.com/techmaturity/techmaturity) framework and maturity model by Ticketmaster.
