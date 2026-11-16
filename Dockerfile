# LegitCheck API. Works on Render (sets $PORT) and Hugging Face Spaces (port 7860).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=7860

RUN useradd --create-home --uid 1000 app
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-compile -r requirements.txt

COPY legitcheck ./legitcheck
COPY models/legitcheck.joblib models/metrics.json ./models/
COPY migrations ./migrations

# The SQLite fallback writes next to the code, so the app user must own it.
RUN chown -R app:app /app
USER app

EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import os,urllib.request;urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/health',timeout=4)"

CMD ["sh", "-c", "uvicorn legitcheck.api.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
