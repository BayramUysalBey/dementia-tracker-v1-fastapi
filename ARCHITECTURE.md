# Dementia Tracker V1 - Architectural Decisions & Trade-offs

This document outlines the core architectural patterns, technical decisions, and resulting trade-offs within the Dementia Tracker V1 FastAPI application. It is intended to serve as a high-level guide for engineers and interviewers evaluating the system's design.

## 1. System Architecture: Layered vs. Vertical Slicing

**Decision:** The application utilizes a strict **Layered Architecture** (N-Tier) rather than Vertical Slicing. The codebase is divided horizontally into:
- `app/api/routers` (Transport Layer)
- `app/services` (Business Logic Layer)
- `app/db/crud` (Data Access Layer)
- `app/db/models` & `app/schemas` (Domain / DTOs)

**Trade-offs:** 
- *Pros:* High separation of concerns. Replacing FastAPI with a different transport layer (e.g., gRPC or a CLI tool) would only require rewriting the `routers` directory.
- *Cons:* To add a single new feature (e.g., "Notes"), developers must touch 4-5 different files across multiple directories, increasing cognitive load compared to a "Vertical Slice" where all Note-related logic lives in one folder.

## 2. Asynchronous Database Selection (`asyncpg` & SQLAlchemy 2.0)

**Decision:** The system employs asynchronous database drivers (`asyncpg`) and SQLAlchemy 2.0's async extensions rather than traditional synchronous drivers (like `psycopg2` blocking calls).

**Trade-offs:**
- *Pros:* Massive scalability for I/O bound workloads. FastAPI can handle thousands of concurrent requests on a single thread while waiting for PostgreSQL to return data.
- *Cons:* Increased complexity in state management. Developers must be extremely careful with lazy-loading relationships in SQLAlchemy, as lazy-loading requires blocking I/O which will crash an async event loop (requiring explicit `joinedload` or async session handling).

## 3. Data Models & Boundary Control

**Decision:** Strict separation between SQLAlchemy ORM Models (Database representation) and Pydantic Schemas (API Data Transfer Objects).

**Trade-offs:**
- *Pros:* Security and boundary control. It prevents "Mass Assignment" vulnerabilities where a user could send an `is_admin=True` JSON payload that accidentally maps directly to the database. It also ensures passwords are never accidentally leaked in API responses.
- *Cons:* High boilerplate. A single domain entity (like `User`) requires writing its fields multiple times (once in SQLAlchemy, once in `UserCreate`, once in `UserRead`), violating the DRY (Don't Repeat Yourself) principle in favor of explicit safety.

## 4. Identity Validation Layer (JWT & Dependency Injection)

**Decision:** Authentication is handled statelessly via JWT (JSON Web Tokens) and injected into routes using FastAPI's `Depends(get_current_user)`.

**Trade-offs:**
- *Pros:* Zero database round-trips to verify sessions. The API can scale horizontally without needing a centralized Redis session store. FastAPI's Dependency Injection makes securing routes a one-liner.
- *Cons:* Because JWTs are stateless, they cannot be easily revoked before they expire. If a user's account is compromised, the token remains valid until its expiration time unless a complex blocklist architecture is implemented.

## 5. Polymorphic Associations (e.g., The Reminder Mnemonic)

**Decision:** Entities like `Reminder` use generic mapping fields (`related_entity_type`, `related_entity_id`) to associate with multiple different tables (Habits, Medications, Notes) rather than strict Foreign Keys.

**Trade-offs:**
- *Pros:* Extreme flexibility. The system can introduce a new feature (e.g., "Appointments") tomorrow, and the Reminder system can link to it immediately without altering the `reminders` database schema.
- *Cons:* Loss of relational database guarantees. Because there is no strict Foreign Key constraint on `related_entity_id`, the database will not prevent orphaned records, nor can it utilize cascade deletions automatically. Referential integrity must be handled manually in the application layer.

## 6. Testing Strategy

**Decision:** The testing suite prioritizes fast integration testing using a dynamic, transactional test database managed within `conftest.py`. 

**Trade-offs:**
- *Pros:* 100% confidence in the database layer. Tests run against a real PostgreSQL instance via `alembic` migrations, and because every test is wrapped in an SQL transaction that rolls back at the end, tests remain lightning fast and completely isolated from one another.
- *Cons:* High initial setup complexity. The `conftest.py` file requires deep knowledge of SQLAlchemy internals and async test loops, which can be daunting for junior developers joining the project.
