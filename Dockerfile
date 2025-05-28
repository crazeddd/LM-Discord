FROM python:3.12-slim

WORKDIR /app

COPY /src ./src

RUN pip install --upgrade pip setuptools wheel
RUN pip install dotenv discord.py asyncio requests sentence-transformers

CMD ["python", "-m", "src"]