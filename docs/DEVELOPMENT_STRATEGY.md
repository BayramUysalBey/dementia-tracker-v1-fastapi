# Backend Development Strategy & Career Focus

This document outlines the strategic direction for the Dementia Tracker project, specifically tailored to building a portfolio that highlights strong Python Backend Developer skills.

## Core Philosophy
As a backend developer candidate, the primary focus is on demonstrating deep mastery of backend systems rather than building complex frontends. The effort is allocated towards reliability, scalability, and advanced architecture.

## Post-Feature Roadmap (After Domain Modules)

Once the core domain modules (CAT-56 through CAT-67) are complete, the development focus will shift to the following areas:

### 1. Test Automation
*   **Goal:** Prove the API works and doesn't break.
*   **Action:** Write a robust suite of unit and integration tests using `pytest`. Implement mock database sessions and ensure high test coverage.

### 2. DevOps & CI/CD
*   **Goal:** Prove the development workflow is professional.
*   **Action:** Set up automated pipelines (e.g., GitHub Actions) so the `pytest` suite runs automatically on every push. Optimize the Dockerfile for production.

### 3. Deployment
*   **Goal:** Prove the application can scale and be accessed publicly.
*   **Target Platform:** **fastapicloud.com**
*   **Action:** Deploy the FastAPI backend and PostgreSQL database to fastapicloud.com, providing a live Swagger UI URL (`/docs`) for recruiters to interact with.

### 4. Advanced Backend Concepts
*   **Goal:** Stand out from the crowd with advanced engineering skills.
*   **Action:** 
    *   Implement cursor-based pagination and filtering.
    *   Integrate **Redis** for caching frequently accessed endpoints.
    *   Use **Celery** or `BackgroundTasks` for asynchronous processes (like the Exporter module).

## Frontend Strategy
*   **No Javascript Frameworks:** Avoid spending extensive time on React/Vue.
*   **Alternative:** If a visual interface is absolutely necessary for demonstration, it will be built natively within the Python ecosystem using **Jinja2 Templates** or **Streamlit**.
