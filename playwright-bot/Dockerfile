FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app
COPY bot /app/bot
COPY run_bot.py /app/run_bot.py
COPY requirements.txt /app/
RUN pip install -r requirements.txt


EXPOSE 9000
CMD ["uvicorn", "run_bot:app", "--host", "0.0.0.0", "--port", "9000"]
