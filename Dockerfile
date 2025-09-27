# syntax=docker/dockerfile:1

FROM python:3.12-slim AS runtime

# Avoid interactive prompts & set sensible defaults
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir inside the image
WORKDIR /app

# Copy application code
COPY app.py /app/app.py

# Non-root for better security
RUN useradd -m appuser
USER appuser

# Run the app; it should just print the version and exit
ENTRYPOINT ["python", "/app/app.py"]

