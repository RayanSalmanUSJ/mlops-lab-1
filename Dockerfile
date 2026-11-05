# Stage 1: Builder
FROM python:3.11-slim AS builder

# Install C compiler for dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy only dependency files first to cache them
COPY pyproject.toml uv.lock ./

# Build the virtual environment targeting Python 3.11 and Linux
RUN uv sync --no-dev --no-install-project --python 3.11 --python-platform x86_64-unknown-linux-gnu

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy the built virtual environment from the builder stage
COPY --from=builder /app/.venv ./.venv

# Put the virtual environment on the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy the application code
COPY src/ ./src/

EXPOSE 8000

# Run the API
CMD ["uvicorn", "src.food11.serve:app", "--host", "0.0.0.0", "--port", "8000"]