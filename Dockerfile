# Stage 1: Builder
FROM python:3.12-slim@sha256:65bdf2559b959663f707f50a8d42ea04561081da3039d6796c4664bd9df41009 AS builder

WORKDIR /app

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production Run
FROM python:3.12-slim@sha256:65bdf2559b959663f707f50a8d42ea04561081da3039d6796c4664bd9df41009

WORKDIR /app

# Copy the pre-built virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Run as a non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Run with a production-grade uvicorn setup (multiple workers and proxy headers)
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --proxy-headers"
