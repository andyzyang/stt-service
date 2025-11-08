import pytest
import os
import subprocess
from fastapi.testclient import TestClient
from app.main import app


@pytest.mark.integration
def test_transcribe_integration(tmp_path):
    model_path = os.environ.get("VOSK_MODEL_PATH", "./model")
    assert os.path.exists(model_path), "Model directory missing"
    sample_wav = tmp_path / "sample.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-f",
            "lavfi",
            "-i",
            "anullsrc",
            "-t",
            "1",
            "-ar",
            "16000",
            "-ac",
            "1",
            str(sample_wav),
        ],
        check=True,
        capture_output=True,
    )
    with TestClient(app) as client:
        with open(sample_wav, "rb") as f:
            files = {"file": ("sample.wav", f, "audio/wav")}
            resp = client.post("/transcribe", files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert "transcript" in data
