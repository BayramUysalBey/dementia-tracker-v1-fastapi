# Deployment Guide (FastAPI Cloud & Neon Tech)

This document outlines the standard operating procedure for deploying the Dementia Tracker application to production using **FastAPI Cloud** and a serverless PostgreSQL database via **Neon Tech**.

## 1. Prerequisites

* A provisioned **Neon Tech** PostgreSQL database.
* The `fastapi` CLI installed and authenticated on your local machine.
* A `SECRET_KEY` of at least 32 characters. Generate one with:
  `python -c "import secrets; print(secrets.token_hex(32))"`

## 2. Environment Configuration

FastAPI Cloud does not read your local `.env` file. Configure these variables in the FastAPI Cloud Dashboard:

| Variable Name | Description / Format |
| --------------- | ---------------------- |
| `DATABASE_URL` | Your Neon connection string. The settings validator rewrites `postgresql://` to `postgresql+asyncpg://`, converts `sslmode=require` to `ssl=require`, and strips `channel_binding=require` (unsupported by asyncpg). |
| `SECRET_KEY` | Minimum 32 characters. The app refuses to start if it is shorter. |
| `DEBUG` | **Do not set in production.** Defaults to `False`. Setting it to `true` enables SQLAlchemy echo, which writes every SQL statement — including user emails and password hashes — to the logs. |
| `BASE_URL_FRONT_ONE` | Absolute live URL for the authentication endpoint (`<DOMAIN>/api/v1/auth/token`). |
| `BASE_URL_FRONT_TWO` | Absolute live URL for a feature-specific data endpoint. |

## 3. Database Schema and Migrations

**Important: `create_all` is not a migration tool.**

The lifespan event in `app/main.py` runs `BaseDBModel.metadata.create_all` on boot. This creates **missing tables only**. It does **not** alter existing columns, add constraints, or convert types.

Therefore:

* **New tables** — handled automatically on deploy by `create_all`.
* **Any schema change to an existing table** (column type, constraint, default) — you **must** run Alembic against the production database **before** deploying the code that depends on it. Otherwise the new code will fail against the old schema.

### Running a migration against production

```bash
# PowerShell — single quotes, and remove channel_binding from the string
$env:DATABASE_URL='postgresql://user:password@host/neondb?sslmode=require'

alembic current          # check where production stands
alembic upgrade head
```

**If `alembic_version` does not exist** (schema was built by `create_all`, not Alembic), stamp first — at the revision matching production's **actual** state, not necessarily the latest:

```bash
alembic history          # inspect the chain
alembic stamp <revision> # the last migration genuinely reflected in production
alembic upgrade head
```

Stamping too far forward causes Alembic to skip migrations production still needs.

## 4. Deployment Execution

```bash
fastapi deploy
```

**If the output says `Source unchanged! Reusing image`,** your code changes were not packaged. Force a rebuild by bumping `VERSION` in `app/core/settings.py`, then deploy again.

## 5. Post-Deployment Verification

1. `GET /api/v1/status/health` — confirms the database connection.
2. `GET /docs` — confirms all routers are registered and the build is current.
3. Register a new user — confirms writes and the schema.
4. Register a **duplicate** email — must return **400**, not 500.
5. Log in — confirms `SECRET_KEY` and JWT generation.
6. Check the logs contain no SQL statements (confirms `DEBUG` is off).

## 6. Known Operational Notes

**Neon suspends idle compute**, which closes pooled connections. The engine is configured with `pool_pre_ping=True` and `pool_recycle=300` in `app/db/session.py` to detect and replace stale connections. Without these, the first request after an idle period fails with `InterfaceError: connection is closed`.
