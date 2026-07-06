# Continuous Integration

GitHub Actions runs on every push and pull request to `main`.

## Workflow

| Item | Value |
|------|-------|
| File | `.github/workflows/ci.yml` |
| Job | `test` on `ubuntu-latest` |
| Python | 3.12 |
| Command | `pytest -q -m "not db and not network and not data"` |

## What CI validates

- Documentation and README contracts  
- SQL file structure and embedded DQ expected values  
- Script module entrypoints and hygiene checks  
- Repository structure and secret-safety patterns  

Roughly **960+** fast tests. Full suite including local data artifacts and Docker Postgres is **1,100+** tests — run locally after loading data.

## Local commands

```bash
# Same as CI (no dataset or Postgres required)
pytest -q -m "not db and not network and not data"

# Full local suite with Docker on port 5433
pytest -q -m "db"

# Everything (requires raw/processed data + Postgres)
pytest -q
```

## Badge

README displays the workflow status badge:

`https://github.com/rmarathe-hub/retail-retention-revenue-intel/actions/workflows/ci.yml/badge.svg`
