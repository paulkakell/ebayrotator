FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

# Only install what mysqlclient needs
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY bot /app/bot
COPY run_bot.py /app/run_bot.py
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 9000

CMD ["uvicorn", "run_bot:app", "--host", "0.0.0.0", "--port", "9000"]
