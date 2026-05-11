# Dementia Tracker v1

Dementia Tracker v1 is a dedicated support application designed for caregivers who provide home care for dementia patients. This project leverages FastAPI to provide a modern, high-performance backend infrastructure for tracking and management.

## 🚀 Quick Start

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

   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**:

   Before running the application, you must configure your local database:
   - Create a copy of the `.env.example` file and instantly rename it strictly to `.env`.
   - Ensure you have a running PostgreSQL instance that exactly matches the `DATABASE_URL` credentials you set in your new `.env` file.
   - Run the initial migrations to construct the database tables using Alembic:

     ```bash
     alembic upgrade head
     ```

4. **Run Application**:

   ```bash
   python -m uvicorn app.main:app --reload
   ```

   Access the server at `http://localhost:8000`.

## 🐳 Docker Usage

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
`http://localhost:8000/health`

## 🛠 Project Structure

- `app/main.py`: Main FastAPI application entry point.
- `app/api/routers/`: Modular route handlers (items, status).
- `app/schemas/`: Pydantic data models for validation.
- `app/core/`: Application settings and configuration.
- `Makefile`: Convenient shortcuts for common tasks (install, run, build, clean).
- `Dockerfile`: Production-ready container configuration.
- `.dockerignore`: Optimized build exclusions.
- `requirements.txt`: Python package dependencies.
- `tests/`: Automated test suite.

## 📜 Available Commands (Makefile)

If you have `make` installed, you can use the following shortcuts:

- `make install`: Install dependencies from requirements.txt.
- `make run`: Launch the FastAPI server with hot-reload.
- `make build`: Build the Docker image.
- `make docker-run`: Run the application within a Docker container.
- `make clean`: Remove build artifacts (`build`, `dist`, `.egg-info`).

## 🧪 Testing

The project includes a suite of automated tests using `pytest`.

### Run Tests

```bash
make test
```

Or manually:

```bash
pytest tests/test.py
```

---
*Developed with focus on supporting home care for dementia patients.*
