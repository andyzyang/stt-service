from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from contextlib import asynccontextmanager
from pathlib import Path
from .config import settings
from .transcriber import Transcriber
import os, tempfile, asyncio, aiofiles

transcriber = None


def load_model():
    global transcriber
    model_path = os.environ.get("VOSK_MODEL_PATH", settings.VOSK_MODEL_PATH)
    try:
        transcriber = Transcriber(model_path)
        logger.info("TEST ******* Uploaded new VOSK model from {}", model_path)
    except Exception as e:
        logger.exception("Failed to load model: {}", e)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield


app = FastAPI(title="stt-service", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    filename = file.filename or "upload"
    content = await file.read()
    if not filename.lower().endswith((".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm")):
        raise HTTPException(status_code=400, detail="Unsupported file extension")
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "in")
        out_path = os.path.join(tmp, "out.wav")
        async with aiofiles.open(in_path, "wb") as f:
            await f.write(content)
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            in_path,
            "-ac",
            "1",
            "-ar",
            "16000",
            "-f",
            "wav",
            out_path,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.error("ffmpeg failed: {}", stderr.decode(errors="ignore"))
            raise HTTPException(status_code=400, detail="Audio conversion failed")
        async with aiofiles.open(out_path, "rb") as f:
            wav_bytes = await f.read()

        try:
            if transcriber is None:
                raise ValueError("Transcriber does not have model loaded.")
            text = transcriber.transcribe_wave_bytes(wav_bytes)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.exception("Transcription error: {}", e)
            raise HTTPException(status_code=500, detail="Transcription failed")
        return JSONResponse({"transcript": text})


client_path = Path(__file__).parent.parent / "example_client" / "browser_client"
app.mount("/client", StaticFiles(directory=client_path, html=True), name="client")


@app.get("/")
async def serve_index():
    return FileResponse(client_path / "index.html")
