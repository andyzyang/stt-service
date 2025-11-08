#!/usr/bin/env bash
DURATION=10
OUT=example.wav
ffmpeg -f alsa -i default -t $DURATION -ac 1 -ar 16000 -y $OUT
# ffmpeg -f avfoundation -i ":0" -t $DURATION -ac 1 -ar 16000 -y $OUT
curl -X POST "http://localhost:8000/transcribe" -F "file=@${OUT}"