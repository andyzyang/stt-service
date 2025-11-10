FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 VOSK_MODEL_PATH=/model APP_PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app
COPY example_client/browser_client /app/example_client/browser_client

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE ${APP_PORT}
ENTRYPOINT ["/app/docker-entrypoint.sh"]