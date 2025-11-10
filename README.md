# Architecture overview

FastAPI service using VOSK for speech-to-text. Service accepts uploaded audio files, converts to WAV PCM 16-bit mono with ffmpeg, uses VOSK model to transcribe, returns JSON {"transcript":"..."}. Dockerized and deployable with docker-compose. CI builds image and deploys to server via SSH.

# Prerequisites

- Python 3.10+ (tested with 3.13)
- Docker and Docker Compose
- ffmpeg

  `sudo apt install ffmpeg`

- unzip (used to unzip VOSK model)

  `sudo apt install unzip`

# Local development

- clone repo
- put VOSK model in ./model (or set VOSK_MODEL_PATH env)

```
cd stt-service
docker compose up --build
```

# Run tests

```
pip install -r app/requirements.txt
# run uni tests
pytest -q -m "not integration"
# run integration tests, needs ffmpeg installed and VOSK model
pytest -q -m integration
```

# Start locally (without Docker)

```
export VOSK_MODEL_PATH=./model
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

# Deployment

```
# on server
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
# from CI or local machine, copy image and deploy with docker compose:
scp stt-service.tar ubuntu@<SERVER_IP>:~
ssh ubuntu@<SERVER_IP> 'docker load -i ~/stt-service.tar && cd ~/ && docker compose up -d'
```

# Example usage

```
curl http://localhost:8000/health
curl -X POST "http://localhost:8000/transcribe" -F "file=@example.wav"
```

# Supported formats and limits

Supported extensions: .wav, .mp3, .m4a, .ogg, .flac.

Conversion uses ffmpeg to 16k mono 16-bit WAV.

File size: default practical limit depends on server RAM/disk; recommend 100MB max. Enforce in code if desired by checking len(content).

Runtime: CPU bound; expect near realtime or slower depending on CPU and model size.

# Trade-offs

1. VOSK chosen for simplicity and offline operation; higher accuracy models (Whisper variants) need GPU or optimized C builds (e.g., whisper.cpp).

2. Single FastAPI service + Docker container (no message queues, no separate worker).

   Reason: Keeps infrastructure simple for deployment review.

   Pros: Quick setup and easy debugging.

   Cons: Doesn’t scale horizontally; concurrent long requests block worker threads.

3. Lightweight unit and integration tests, using a generated 1-second silent WAV file for integration.

   Reason: Avoid bundling large audio assets or increasing test runtime.

   Pros: Fast CI pipeline (<2 min).

   Cons: Doesn’t test real transcription accuracy under varied speech conditions.

# Next steps if given more time

Add authentication, rate limiting, chunked streaming, speaker diarization, punctuation/casing, and model selection endpoint.

Add async streaming transcription for live audio and observability (metrics, Prometheus).

Explore whisper.cpp + ggml models for improved quality or GPU-accelerated Whisper for faster, more accurate transcripts.
