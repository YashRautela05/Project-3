from .celery_worker import celery_app
from .processing import process_video
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=2)
def analyze_video_task(self, job_id, filepath):
    """
    Celery task for video analysis with error handling and retries.
    """
    try:
        logger.info(f"Starting video analysis task: job_id={job_id}, filepath={filepath}")
        result = process_video(job_id, filepath)
        logger.info(f"Video analysis completed successfully: job_id={job_id}")
        return result
    except FileNotFoundError as e:
        logger.error(f"Video file not found: {e}")
        return {
            "error": "Video file not found",
            "details": str(e),
            "job_id": job_id
        }
    except RuntimeError as e:
        logger.error(f"Video processing error: {e}")
        return {
            "error": "Video processing failed",
            "details": str(e),
            "job_id": job_id,
            "suggestion": "Please ensure the video is in a supported format (MP4, AVI, MOV) with H.264/H.265 codec"
        }
    except Exception as e:
        logger.exception(f"Unexpected error in video analysis: {e}")
        # Retry on unexpected errors
        try:
            self.retry(exc=e, countdown=10)
        except self.MaxRetriesExceededError:
            return {
                "error": "Maximum retries exceeded",
                "details": str(e),
                "job_id": job_id
            }

