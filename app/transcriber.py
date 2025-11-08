import os
import wave
import json
import io
from vosk import Model, KaldiRecognizer


class Transcriber:
    def __init__(self, model_path: str) -> None:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"VOSK model not found at {model_path}")
        self.model = Model(model_path)

    def transcribe_wave_bytes(self, wav_bytes: bytes) -> str:
        wf = wave.open(io.BytesIO(wav_bytes), "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            raise ValueError("Unsupported WAV format: require 16-bit PCM mono")
        rec = KaldiRecognizer(self.model, wf.getframerate())
        result_texts = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                result_texts.append(res.get("text", ""))
        final = json.loads(rec.FinalResult()).get("text", "")
        result_texts.append(final)
        return " ".join([t for t in result_texts if t]).strip()
