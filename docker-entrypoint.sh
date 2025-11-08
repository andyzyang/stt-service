#!/usr/bin/env bash
set -e
if [ ! -d "${VOSK_MODEL_PATH}" ]; then
  echo "VOSK model not found at ${VOSK_MODEL_PATH}. Please mount model dir to container."
fi
exec uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT} --workers 1