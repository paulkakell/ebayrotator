FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY bot /app/bot
COPY run_bot.py /app/run_bot.py
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 9000

CMD ["uvicorn", "run_bot:app", "--host", "0.0.0.0", "--port", "9000"]
