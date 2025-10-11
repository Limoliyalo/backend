FROM python:3.13-slim AS base
LABEL authors="NEZuko1337"

RUN apt-get update && apt-get install -y curl build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml poetry.lock alembic.ini /app/

RUN poetry install --only main --no-root

COPY . /app
