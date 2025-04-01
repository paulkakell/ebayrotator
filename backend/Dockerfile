FROM python:3.11-slim

WORKDIR /app

# Install system packages needed to build mariadb connector
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev-compat \
    libmariadb-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

# Install Python dependencies (can also use requirements.txt)
RUN pip install --no-cache-dir \
    fastapi uvicorn[standard] \
    python-dotenv sqlalchemy \
    mariadb

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
