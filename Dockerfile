FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --upgrade pip setuptools wheel
RUN pip install dotenv discord.py asyncio requests

CMD ["python", "-m", "src"]