FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code, data, tests, and notebooks
COPY src/ ./src/
COPY data/ ./data/
COPY tests/ ./tests/
COPY README.md ./

# Install project package
RUN pip install --no-cache-dir -e .

# Run pytest by default to verify container health
CMD ["pytest", "tests/", "-v"]
