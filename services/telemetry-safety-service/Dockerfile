FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV MESSAGING_ENABLED="true"

WORKDIR /app

COPY packages/messaging /tmp/messaging

COPY services/telemetry-safety-service/pyproject.toml ./
COPY services/telemetry-safety-service/app ./app

RUN pip install --upgrade pip \
    && pip install /tmp/messaging \
    && pip install .

EXPOSE 8006

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8006"]
