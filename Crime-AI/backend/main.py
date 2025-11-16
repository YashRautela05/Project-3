from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import uuid
import aiofiles
from pathlib import Path
import logging

from .tasks import analyze_video_task
from .models import preload_all_models
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Preload all AI models at server startup.
    This prevents the first request from being slow due to model loading.
    """
    logger.info("🚀 Starting Crime-AI FastAPI server...")
    logger.info("📦 Preloading AI models...")
    try:
        preload_all_models()
        logger.info("✅ Server ready! All models loaded.")
    except Exception as e:
        logger.error(f"❌ Failed to preload models: {e}")
        logger.warning("⚠️ Models will load on first request instead")


UPLOAD_DIR = Path("/app/uploads")
RESULT_DIR = Path("/app/results")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

class JobStatus(BaseModel):
    task_id: str
    status: str
    result: dict | None = None

from fastapi import FastAPI, File, UploadFile, HTTPException
import uuid
import aiofiles
from pathlib import Path

from .tasks import analyze_video_task
from .utils_hash import compute_video_hash


@app.post("/upload", response_model=JobStatus)
async def upload_video(file: UploadFile = File(...)):
    # validate extension
    if not file.filename.lower().endswith((".mp4", ".mov", ".mkv", ".avi")):
        raise HTTPException(status_code=400, detail="Only video files allowed")

    # Step 1: create temp upload path
    temp_id = str(uuid.uuid4())
    upload_path = UPLOAD_DIR / f"{temp_id}_{file.filename}"

    async with aiofiles.open(upload_path, "wb") as out_file:
        await out_file.write(await file.read())

    # Step 2: compute stable video hash (real identifier)
    video_hash = compute_video_hash(upload_path)

    # Step 3: trigger celery worker with video_hash
    task = analyze_video_task.apply_async(args=[video_hash, str(upload_path)])

    return JobStatus(task_id=task.id, status="queued")

@app.get("/status/{task_id}", response_model=JobStatus)
def get_status(task_id: str):
    task = analyze_video_task.AsyncResult(task_id)

    if task.state == "PENDING":
        return JobStatus(task_id=task_id, status="queued")

    if task.state == "SUCCESS":
        return JobStatus(task_id=task_id, status="done", result=task.result)

    if task.state == "FAILURE":
        return JobStatus(task_id=task_id, status="failed")

    return JobStatus(task_id=task_id, status=task.state)


@app.get("/health")
def health_check():
    """
    Health check endpoint that also verifies model loading status.
    """
    from .models import _yolo_model, _movinet_model
    
    return {
        "status": "healthy",
        "models": {
            "yolo_loaded": _yolo_model is not None,
            "movinet_loaded": _movinet_model is not None,
        }
    }
