# syntax=docker/dockerfile:1

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \        
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

RUN useradd -u 10001 -m appuser
COPY --chown=appuser:appuser app /app/app

USER appuser
EXPOSE 8000

LABEL org.opencontainers.image.title="phase3-fastapi" \
    org.opencontainers.image.description="FastAPI service exposing /version and /temperature" \
    org.opencontainers.image.source="https://github.com/<YOUR_USER>/<YOUR_REPO>" \
    org.opencontainers.image.licenses="MIT"

ENTRYPOINT ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]
