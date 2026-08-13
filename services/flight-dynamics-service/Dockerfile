FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV MESSAGING_ENABLED="true"

WORKDIR /app

COPY packages/orbital-mechanics /tmp/orbital-mechanics
COPY packages/messaging /tmp/messaging

RUN pip install --upgrade pip \
    && pip install /tmp/orbital-mechanics \
    && pip install /tmp/messaging

COPY services/flight-dynamics-service/pyproject.toml ./
COPY services/flight-dynamics-service/alembic.ini ./
COPY services/flight-dynamics-service/migrations ./migrations
COPY services/flight-dynamics-service/app ./app

RUN pip install .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
