FROM python:3.12-slim

WORKDIR /app

COPY /src ./src

ENV PYTHONPATH=/app/src

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

CMD ["python", "-m", "src"]