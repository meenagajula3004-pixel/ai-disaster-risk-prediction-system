FROM python:3.11-slim

WORKDIR /app

# Prevent bytecode writing & unbuffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements & install (works with both root context and backend/ context)
COPY requirements.txt* backend/requirements.txt* /app/
RUN if [ -f /app/requirements.txt ]; then \
        pip install --no-cache-dir -r /app/requirements.txt; \
    elif [ -f /app/backend/requirements.txt ]; then \
        pip install --no-cache-dir -r /app/backend/requirements.txt; \
    fi

# Copy codebase
COPY . /app/

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
