# Deployment Guide (FastAPI Cloud & Neon Tech)

This document outlines the standard operating procedure for deploying the Dementia Tracker application to production using **FastAPI Cloud** and a serverless PostgreSQL database via **Neon Tech**.

## 1. Prerequisites

Before deploying, ensure you have the following ready:
* A provisioned **Neon Tech** PostgreSQL database.
* The `fastapi` CLI installed and authenticated on your local machine.
* A securely generated `SECRET_KEY` for JWT authentication.

## 2. Environment Configuration

FastAPI Cloud does not read your local `.env` file for security reasons. You must configure the following environment variables directly in your FastAPI Cloud Dashboard:

| Variable Name | Description / Format |
|---------------|----------------------|
| `DATABASE_URL` | Your Neon connection string. **Crucial:** You must use the `postgresql+asyncpg://` driver format for high-performance async operations. The backend parser will automatically handle `sslmode=require` translation. |
| `SECRET_KEY` | A highly secure, random cryptographic string used to sign JWTs. |
| `BASE_URL_FRONT_ONE` | The absolute live URL for the primary authentication endpoint (e.g., `<YOUR_DOMAIN>/api/v1/auth/token`). |
| `BASE_URL_FRONT_TWO` | The absolute live URL for a secure, feature-specific data endpoint. As your application scales, you can add as many of these frontend variables as needed to securely route to new API features. |

## 3. Database Migrations (Lifespan Events)

We utilize FastAPI's modern `@asynccontextmanager` lifespan events to manage schema generation in production.
* When the FastAPI Cloud container boots, the lifespan event establishes a synchronous connection and automatically executes `BaseDBModel.metadata.create_all`.
* This guarantees the tables exist before the first user request arrives.
* **Note:** We intentionally do not run `alembic upgrade head` in the `Dockerfile` to prevent the container from crashing during the isolated build phase.

## 4. Deployment Execution

Once your environment variables are set in the cloud dashboard, deploy the application using the CLI:

```bash
# Push your current branch to the cloud infrastructure
fastapi deploy
```

Wait for the build logs to confirm successful compilation and server boot.

## 5. Post-Deployment Verification

1. Navigate to your live URL.
2. **Register a User:** Validate the database connection by registering a new account.
3. **Authentication:** Log in to ensure the `SECRET_KEY` is generating valid JWTs.
4. **Data Retrieval:** Verify the frontend accurately pulls secure data using the JWT bearer token.
