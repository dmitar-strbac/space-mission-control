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

COPY services/vehicle-service/pyproject.toml ./
COPY services/vehicle-service/alembic.ini ./
COPY services/vehicle-service/migrations ./migrations
COPY services/vehicle-service/app ./app

RUN pip install .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
