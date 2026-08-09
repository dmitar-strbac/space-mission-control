FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY packages/orbital-mechanics /tmp/orbital-mechanics

RUN pip install --upgrade pip \
    && pip install /tmp/orbital-mechanics

COPY services/trajectory-service/pyproject.toml ./
COPY services/trajectory-service/alembic.ini ./
COPY services/trajectory-service/migrations ./migrations
COPY services/trajectory-service/app ./app

RUN pip install .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
