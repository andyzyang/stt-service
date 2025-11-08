#!/usr/bin/env bash
set -e

MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
MODEL_DIR="${1:-./model}"

if [ -d "$MODEL_DIR" ] && [ -f "$MODEL_DIR/.ready" ]; then
  echo "Vosk model already present at $MODEL_DIR"
  exit 0
fi

echo "Downloading Vosk model..."
mkdir -p "$MODEL_DIR"
curl -L "$MODEL_URL" -o /tmp/model.zip
unzip -q /tmp/model.zip -d "$MODEL_DIR"
mv "$MODEL_DIR"/vosk-model-small-en-us-*/* "$MODEL_DIR" || true
rm -rf "$MODEL_DIR"/vosk-model-small-en-us-*
touch "$MODEL_DIR/.ready"
echo "Model ready at $MODEL_DIR"