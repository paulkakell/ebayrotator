FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app
COPY bot /app/bot
COPY run_bot.py /app/run_bot.py

RUN pip install mariadb sqlalchemy python-dotenv

CMD ["python", "run_bot.py"]
