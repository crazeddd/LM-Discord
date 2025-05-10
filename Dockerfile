FROM python:3.12-slim


RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    curl \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel
RUN pip install llama-cpp-python dotenv discord.py discord.py[voice] asyncio 

CMD ["python3"]
