# The Vertical Slice Workflow

A "Vertical Slice" is a professional architectural pattern. Instead of building horizontally (e.g., building *all* database models, then *all* schemas, then *all* routers), you build vertically. You take one single feature (like "Accounts") and build it from the absolute bottom (the database) all the way up to the top (the API endpoint) in one cohesive unit.

By using this template, you ensure that every layer of your application is perfectly aligned before moving on to the next feature.

---

## Step 1: The Database Model (`app/db/models/`)
**The Foundation.** This is where you define how the data is stored in PostgreSQL.
1. Create a new file (e.g., `app/db/models/new_feature.py`).
2. Create a class inheriting from `BaseDBModel`.
3. Define your columns (`Mapped[...] = mapped_column(...)`).
4. **Crucial Step:** Import your new model into `app/db/base.py` so Alembic can see it!
5. Generate and run your Alembic migration.

## Step 2: The Pydantic Schemas (`app/schemas/`)
**The Gatekeeper.** This is where you define the exact shape of the JSON you expect from the user and the JSON you return to the user.
1. Create a new file (e.g., `app/schemas/new_feature.py`).
2. Create the `Base` schema with the core fields (use `Literal` for strict string validation!).
3. Create the `Create` schema (inherit from Base). *Do not include fields the server generates, like `id`!*
4. Create the `Update` schema (all fields should be `Optional` or `| None`).
5. Create the `Read` schema (inherit from Base, add `id` and timestamps, and set `model_config = ConfigDict(from_attributes=True)`).

## Step 3: The CRUD Layer (`app/db/crud/`)
**The Warehouse Worker.** This layer exclusively handles talking to the database (SQL queries). It contains zero business logic.
1. Create a new file (e.g., `app/db/crud/new_feature.py`).
2. Create a class (e.g., `FeatureCRUD`) that takes `db: AsyncSession` as a dependency.
3. Write simple `create`, `get_by_id`, `update`, and `delete` functions.
4. *Rule:* This layer should almost always return SQLAlchemy Database Models, not Pydantic objects.

## Step 4: The Service Layer (`app/services/`)
**The Brains.** This is where all business logic lives.
1. Create a new file (e.g., `app/services/new_feature.py`).
2. Create a class that injects your new CRUD worker as a dependency.
3. Write functions that mirror your API endpoints.
4. If a feature requires math, checking for duplicates, hashing passwords, or contacting external APIs (like Stripe), the code goes *here*.

## Step 5: The API Router (`app/api/routers/`)
**The Front Desk.** This layer handles HTTP requests and Swagger UI documentation.
1. Create a new file (e.g., `app/api/routers/new_feature.py`).
2. Define `router = APIRouter()`.
3. Write your endpoints (`@router.post()`, `@router.get()`).
4. Inject your Service layer as a dependency.
5. *Rule:* The router should do nothing except receive the Pydantic schema and immediately hand it to the Service layer.
6. **Crucial Step:** Open `app/api/routers/__init__.py` and "plug in" your new router using `api_router.include_router(...)`.

---

## Final Step: Verification
Open your browser to `http://127.0.0.1:8000/docs` and test your new endpoints using the auto-generated Swagger UI!
