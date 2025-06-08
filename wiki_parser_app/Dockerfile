FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONBUFFERED 1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONPATH=/app


WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
