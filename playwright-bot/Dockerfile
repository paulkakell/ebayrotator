FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

# Add necessary build tools for mariadb connector
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmariadb-dev \
    libmariadb-dev-compat \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy bot logic and app runner
COPY bot /app/bot
COPY run_bot.py /app/run_bot.py
COPY requirements.txt /app/requirements.txt

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 9000

CMD ["uvicorn", "run_bot:app", "--host", "0.0.0.0", "--port", "9000"]
