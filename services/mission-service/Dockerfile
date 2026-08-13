FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MESSAGING_ENABLED="true"

WORKDIR /app

COPY packages/messaging /tmp/messaging

COPY services/mission-service/pyproject.toml ./
COPY services/mission-service/app ./app
COPY services/mission-service/alembic.ini ./
COPY services/mission-service/migrations ./migrations

RUN pip install --upgrade pip \
    && pip install /tmp/messaging \
    && pip install .

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
