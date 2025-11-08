FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 VOSK_MODEL_PATH=/model APP_PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY scripts/download_model.sh /app/scripts/download_model.sh
RUN bash /app/scripts/download_model.sh /model
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE ${APP_PORT}
ENTRYPOINT ["/app/docker-entrypoint.sh"]