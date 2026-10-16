# API image for Railway (or any container host). The UI is deployed separately (Vercel).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ARROW_DEFAULT_MEMORY_POOL=system

WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend backend
COPY reports reports
COPY deploy/bundle deploy/bundle

# Secrets (TOKEN_FACTORY_API_KEY etc.) come from the host's environment variables, never from the image.
EXPOSE 8000
CMD ["sh", "-c", "uvicorn backend.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
