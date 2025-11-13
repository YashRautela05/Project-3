from fastapi import FastAPI
from fastapi import UploadFile, File, HTTPException
import os
from datetime import datetime
from tasks import process_media_task
from tasks import celery_app
from config import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS

app = FastAPI(title="Crime-AI API", description="AI-powered media analysis for crime detection")

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")
    
    # Check file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = ALLOWED_EXTENSIONS["video"] + ALLOWED_EXTENSIONS["audio"]
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate a unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Dispatch Celery task
    task = process_media_task.delay(file_path)
    return {
        "message": "File uploaded successfully, processing started", 
        "file_name": filename, 
        "task_id": task.id,
        "file_size": len(content)
    }

@app.get("/status/{task_id}")
def get_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    if result.state == "PENDING":
        return {"status": "pending"}
    elif result.state == "STARTED":
        return {"status": "processing"}
    elif result.state == "SUCCESS":
        return {"status": "completed", "result": result.result}
    elif result.state == "FAILURE":
        return {"status": "failed", "error": str(result.result)}
    else:
        return {"status": result.state.lower()} 