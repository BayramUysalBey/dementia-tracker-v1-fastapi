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
| `WEB_URL_TOKEN` | Absolute URL the NiceGUI frontend posts to for login (`<DOMAIN>/api/v1/auth/token`). **If unset it defaults to `""` and the login form fails silently with no error in the logs.** |
| `WEB_URL_CREATE` | Absolute URL for user registration (`<DOMAIN>/api/v1/users/create`). Same silent-failure mode if unset. |
| `WEB_URL_HABIT` | Absolute URL for the habit list endpoint (`<DOMAIN>/api/v1/habit`). Same silent-failure mode if unset. |

Not set in production: `TEST_DB_NAME` (local test runs only), `SENTRY_DSN`
(optional), `MEDIA_UPLOAD_DIR` (defaults to `static/uploads/media`).

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

```bash
alembic current               # confirm the new revision is head
Remove-Item Env:\DATABASE_URL # CRITICAL: unset it before any further local command
```

Leaving `DATABASE_URL` pointed at production means the next local `pytest` or `alembic` run executes against the live database. Closing the terminal also clears it, since it only exists in that shell session.

The production connection string is a live credential. Never commit it, never paste it into a chat, an issue or a screenshot. If it is exposed, rotate it in the Neon dashboard and verify the old one is dead by attempting a connection with it.

### Exception: production has no `alembic_version` table

This applies **only** the first time Alembic is pointed at a database whose
schema was built by `create_all`. If `alembic current` returns a revision,
skip this section entirely.

## 4. The Deployment Sequence

For any release that includes a schema change, run these in order. Do not reorder.

1. Bump `VERSION` in `app/core/settings.py` (forces a rebuild).
2. Run the full test suite locally — `pytest` must be green.
Run `pytest` **before** pointing `DATABASE_URL` at production. The test suite
creates and drops its own database; if the variable is already set to
production, it will run there.
3. Point `DATABASE_URL` at production and run `alembic current`, then `alembic upgrade head`.
4. `Remove-Item Env:\DATABASE_URL`.
5. `fastapi deploy`.
6. Run the verification checklist in section 5.

The database must be migrated **before** the code ships. This order is safe because old code ignores new columns; the reverse order means new code queries columns that do not exist.

## 5. Deployment Execution

```bash
fastapi deploy
```

**If the output says `Source unchanged! Reusing image`,** your code changes were not packaged. Force a rebuild by bumping `VERSION` in `app/core/settings.py`, then deploy again.

## 6. Rollback

**Bad code, good schema** — redeploy the previous commit. Bump `VERSION` again so the image actually rebuilds.

**Bad migration** — run `alembic downgrade -1` against production, then redeploy the previous code. This only works if the migration has a correct, tested `downgrade()`. Verify reversibility locally before every production migration:

```bash
alembic upgrade head
alembic downgrade -1
alembic upgrade head
pytest
```

**Dropped or altered columns are not recoverable by downgrade** — a downgrade that drops a column destroys its data. Take a Neon branch or snapshot before any destructive migration.

## 7. Post-Deployment Verification

1. `GET /api/v1/status/health` — confirms the database connection.
2. `GET /docs` — confirms all routers are registered and the build is current.
3. Register a new user — confirms writes and the schema.
4. Register a **duplicate** email — must return **400**, not 500. Run this as the *first* request after deploying: the connection pool is cold, which is the exact condition under which this previously returned 500.
5. Log in — confirms `SECRET_KEY` and JWT generation.
6. Check the logs contain no SQL statements (confirms `DEBUG` is off).

## 8. Known Issues and Gotchas

## 8.1 Neon Idle Compute and Connection Pooling

**Neon suspends idle compute**, which closes pooled connections. The engine is configured with `pool_pre_ping=True` and `pool_recycle=300` in `app/db/session.py` to detect and replace stale connections. Without these, the first request after an idle period fails with `InterfaceError: connection is closed`.

## 8.2 Alembic and PostgreSQL Native Enums

`alembic revision --autogenerate` does **not** fully handle enum changes. Every generated migration involving an enum must be corrected by hand:

* It omits `CREATE TYPE`. Add `sa.Enum(..., name="...").create(op.get_bind(), checkfirst=True)` before the column operation, and the matching `.drop(...)` at the end of `downgrade()`.
* It omits the cast directive. Converting `VARCHAR` to an enum requires `postgresql_using='col::enum_name'` on `alter_column`.
* PostgreSQL refuses to cast a column that has a default. `DROP DEFAULT` before the cast, `SET DEFAULT 'value'::enum_name` after.
* Existing rows may hold values outside the new enum. `UPDATE` them to a valid value before the cast, or the migration fails mid-transaction.

## 8.3 SQLAlchemy Persists Enum NAMES, Not Values

By default SQLAlchemy writes the Python member name (`ACTIVE`), not its value (`active`). Against a PostgreSQL enum defined with lowercase labels this raises `invalid input value for enum`. Every `SAEnum` column in this project must pass:

```python
SAEnum(MyEnum, name="my_enum",
       values_callable=lambda enum_cls: [e.value for e in enum_cls])
```

Omitting this broke 23 tests at once during the `user_role` conversion.

**Large files in the deploy package.** `fastapi deploy` warns about files over
10 MB. `tests/mock_media.jpg` triggers this. Test fixtures are uploaded with
the project on every deploy — keep them small.
