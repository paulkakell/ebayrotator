FROM mcr.microsoft.com/playwright/python:v1.43.1

WORKDIR /bot

COPY ./bot /bot
COPY run_bot.py /bot/

RUN pip install --no-cache-dir playwright python-dotenv

CMD ["python", "run_bot.py"]
