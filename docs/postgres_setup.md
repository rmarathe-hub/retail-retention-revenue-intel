# PostgreSQL Setup (Docker)

This project uses **Docker Postgres on host port 5433** to avoid conflicts with other local PostgreSQL instances that may already use port **5432**.

## Port mapping

| Where | Port | Notes |
|-------|------|-------|
| **Mac host (your scripts)** | `5433` | Always connect via `localhost:5433` |
| **Docker container (internal)** | `5432` | Standard Postgres port inside the container |

`docker-compose.yml` maps `5433:5432` — host `5433` → container `5432`.

## Prerequisites

- Docker Desktop installed and running
- Python virtualenv with project requirements installed
- Day 2–3 data files generated locally

## Setup commands

```bash
cd /Users/rohitmarathe/retail_retention_revenue_intel
source .venv/bin/activate
cp .env.example .env
```

> **Note:** .env is gitignored — never commit local credentials. Use `.env.example` as the template.

```bash
docker compose up -d
docker compose ps
docker compose exec postgres pg_isready -U retail_user -d retail_analytics
python scripts/load_to_postgres.py
python scripts/validate_data.py
python scripts/run_kpi_marts.py
pytest -q -m "db"
```

`validate_data.py` runs `sql/02_data_quality_checks.sql` (25 checks) and writes `data/processed/validation_summary.json`.

`run_kpi_marts.py` applies `sql/03_kpi_definitions.sql` and `sql/04_revenue_analysis.sql`, then writes `data/processed/kpi_mart_summary.json`.

## Environment variables

Configured in `.env` (from `.env.example`):

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=retail_analytics
POSTGRES_USER=retail_user
POSTGRES_PASSWORD=retail_pass
DATABASE_URL=postgresql://retail_user:retail_pass@localhost:5433/retail_analytics
```

Scripts read `DATABASE_URL` first. If missing, they build the URL from `POSTGRES_*` fields with fallback port **5433**.

## Stop / reset

```bash
# stop container
docker compose down

# stop and remove persisted data volume
docker compose down -v
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `connection refused` on 5433 | Run `docker compose up -d` and wait for healthy status |
| Wrong credentials | Ensure `.env` matches `docker-compose.yml` values |
| Stale data after re-load | `python scripts/load_to_postgres.py` truncates load tables by default |

## Related files

- `docker-compose.yml` — Postgres 16 service
- `scripts/db_config.py` — shared connection helper
- `scripts/load_to_postgres.py` — schema + data load
- `scripts/validate_data.py` — connectivity and row-count validation
- `sql/01_schema.sql` — warehouse schema
