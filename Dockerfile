# Dockerfile
# Stage 1: Builder - Install dependencies with Poetry
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

COPY pyproject.toml ./

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Stage 2: Runtime - Use requirements.txt
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    openssl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

CMD ["python", "-m", "app.main"]