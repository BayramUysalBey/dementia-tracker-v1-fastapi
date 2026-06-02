# Dementia Tracker v1

Dementia Tracker v1 is a dedicated support application designed for caregivers providing home care for dementia patients. This project leverages FastAPI to provide a modern, high-performance backend infrastructure for tracking, management, and daily journaling.

## Quick Start

### Prerequisites

- Python 3.12+
- FastAPI
- Docker (optional)
- Make (optional)

### Local Installation

1. **Setup Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:

   The project utilizes pip-tools for dependency management. Install dependencies via the lockfile:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**:

   Before running the application, configure your local database:
   - Create a copy of the `.env.example` file and rename it to `.env`.
   - Ensure you have a running PostgreSQL instance matching the `DATABASE_URL` credentials defined in your `.env` file.
   - Run the initial migrations to construct the database schema using Alembic:

     ```bash
     alembic upgrade head
     ```

4. **Run Application**:

   ```bash
   python -m uvicorn app.main:app --reload
   ```

   Access the server at `http://localhost:8000`.

## Docker Usage

This project is fully containerized for consistent development and deployment environments.

### Build and Run

```bash
# Build the image
docker build -t dementia-tracker-v1 .

# Run the container
docker run -p 8000:8000 dementia-tracker-v1
```

### Health Check

Once running, you can verify the system status at:
`http://localhost:8000/api/v1/status/health`

## Project Structure

- `app/main.py`: Main FastAPI application entry point.
- `app/api/routers/`: Modular route handlers (e.g., users, journals, reminders).
- `app/services/`: Core business logic layer.
- `app/db/crud/`: Data access layer for database operations.
- `app/db/models/`: SQLAlchemy database models.
- `app/schemas/`: Pydantic data models for validation and serialization.
- `app/core/`: Application settings and configuration.
- `docs/`: Sphinx documentation source files.
- `tests/`: Automated integration and unit test suite.

## Documentation

The project uses Sphinx to generate HTML documentation from Python docstrings. To build the documentation locally:

```bash
cd docs
.\make.bat html  # On Windows
make html        # On Linux/macOS
```
The generated documentation can be viewed by opening `docs/build/html/index.html` in a web browser.

## Testing

The project includes an automated integration test suite utilizing `pytest` and `pytest-asyncio`. Tests execute against a dynamically generated test database to ensure complete isolation.

### Run Tests

Execute the full test suite from the root directory:

```bash
pytest
```

## Available Commands (Makefile)

If you have `make` installed, you can use the following shortcuts:

- `make install`: Install dependencies from requirements.txt.
- `make run`: Launch the FastAPI server with hot-reload.
- `make build`: Build the Docker image.
- `make docker-run`: Run the application within a Docker container.
- `make test`: Execute the full integration and unit test suite.
- `make clean`: Remove build artifacts (`build`, `dist`, `.egg-info`).

---
*Developed with a focus on supporting home care for dementia patients.*
