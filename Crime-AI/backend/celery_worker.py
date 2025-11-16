# backend/celery_worker.py
from celery import Celery
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

celery_app = Celery(
    "video_tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
)

import backend.tasks


# Celery worker initialization hook
@celery_app.on_after_configure.connect
def setup_models(sender, **kwargs):
    """
    Preload all AI models when Celery worker starts.
    This ensures models are ready for processing tasks immediately.
    """
    logger.info("🚀 Initializing Celery worker...")
    logger.info("📦 Preloading AI models...")
    try:
        from .models import preload_all_models
        preload_all_models()
        logger.info("✅ Celery worker ready! All models loaded.")
    except Exception as e:
        logger.error(f"❌ Failed to preload models: {e}")
        logger.warning("⚠️ Models will load on first task execution instead")
