# backend/processing.py

import json
import subprocess
import shutil
from pathlib import Path
import logging

from .models import run_detection_model, run_action_recognition
from .utils import evaluate_unlawful_events, call_gemini
from .redis_cache import cache_get, cache_set
from .crime_analyzer import CrimePatternAnalyzer
from .motion_analyzer import integrate_motion_analysis

logger = logging.getLogger(__name__)

FRAMES_DIR = Path("/app/frames")
RESULT_DIR = Path("/app/results")
UPLOADS_DIR = Path("/app/uploads")

FRAMES_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def extract_frames(video_path, frame_dir, fps=3):
    """
    Extract frames from video. INCREASED FPS to 3 for maximum temporal coverage.
    More frames = better chance of catching criminal activity.
    """
    # Ensure frame directory exists
    frame_dir.mkdir(parents=True, exist_ok=True)
    
    # Verify video file exists
    if not Path(video_path).exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # More compatible ffmpeg command with error recovery
    cmd = [
        "ffmpeg", 
        "-i", str(video_path),
        "-vf", f"fps={fps}",
        "-vsync", "vfr",  # Variable frame rate to handle issues
        "-q:v", "2",  # Quality setting (2 is high quality)
        "-start_number", "0",
        str(frame_dir / "frame_%05d.jpg"), 
        "-y",
        "-loglevel", "error"  # Only show errors
    ]
    
    try:
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True,
            timeout=300  # 5 minute timeout
        )
        logger.info(f"FFmpeg extraction successful for {video_path}")
    except subprocess.TimeoutExpired as e:
        logger.error(f"FFmpeg timeout after 300 seconds")
        raise RuntimeError("Video processing timeout - file may be too large or corrupted") from e
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed with exit code {e.returncode}")
        logger.error(f"FFmpeg command: {' '.join(cmd)}")
        logger.error(f"FFmpeg stderr: {e.stderr}")
        logger.error(f"FFmpeg stdout: {e.stdout}")
        
        # Try alternative approach with lower FPS
        logger.warning("Retrying with fps=1 as fallback...")
        try:
            cmd_fallback = [
                "ffmpeg", 
                "-i", str(video_path),
                "-vf", "fps=1",
                "-q:v", "3",
                str(frame_dir / "frame_%05d.jpg"), 
                "-y"
            ]
            subprocess.run(cmd_fallback, check=True, capture_output=True, text=True, timeout=300)
            logger.info("Fallback extraction successful at 1 FPS")
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")
            raise RuntimeError(
                f"Failed to extract frames from video. "
                f"Original error: {e.stderr}. "
                f"Video may be corrupted, in unsupported format, or codec not supported."
            ) from e
    
    frames = sorted(frame_dir.glob("frame_*.jpg"))
    logger.info(f"Extracted {len(frames)} frames from video")
    
    if not frames:
        raise RuntimeError(
            f"No frames extracted from {video_path}. "
            f"Video may be corrupted, empty, or in an unsupported format. "
            f"Supported formats: mp4, avi, mov, mkv with H.264/H.265 codec."
        )
    
    return frames


def process_video(video_hash: str, filepath: str) -> dict:
    """
    Enhanced video processing with advanced crime pattern analysis.
    Steps:
        1. If Redis has result: return cached
        2. Extract frames at 3 FPS for maximum coverage (catch more details)
        3. Run YOLO object detection
        4. Run MoViNet action recognition
        5. Run basic event inference
        6. Run advanced crime pattern analysis
        7. Generate comprehensive crime report
        8. Cleanup and cache results
    """

    # 1. Check redis
    cached = cache_get(video_hash)
    if cached:
        logger.info(f"[CACHE HIT] Reusing results for video hash: {video_hash}")
        return cached

    logger.info(f"[CACHE MISS] Running enhanced analysis for: {video_hash}")

    video_path = Path(filepath)
    frame_dir = FRAMES_DIR / video_hash

    # 2. Extract frames at 3 FPS (increased for better crime detection)
    logger.info("Extracting frames at 3 FPS for maximum crime detection coverage...")
    frames = extract_frames(video_path, frame_dir, fps=3)
    logger.info(f"Extracted {len(frames)} frames")

    # 3. YOLO object detection with enhanced settings
    logger.info("Running YOLOv8x object detection...")
    detections = run_detection_model(frames)
    detected_objects = set()
    for frame in detections:
        for obj in frame.get("objects", []):
            detected_objects.add(obj["label"])
    logger.info(f"Detected objects: {', '.join(sorted(detected_objects))}")

    # 4. MoViNet action recognition
    logger.info("Running MoViNet A2 action recognition...")
    try:
        actions = run_action_recognition(frames)
        if actions:
            logger.info(f"Analyzed {len(actions)} video clips")
    except Exception as e:
        logger.error(f"Action recognition failed: {e}")
        actions = []

    # 4.5. Motion pattern analysis
    logger.info("Analyzing motion patterns for suspicious movement...")
    try:
        motion_analysis = integrate_motion_analysis(frames)
        if motion_analysis.get("analyzed"):
            logger.info(f"Motion pattern: {motion_analysis['motion_pattern']['category']}")
            if motion_analysis['motion_pattern']['crime_relevance'] != "low":
                logger.warning(f"⚠️ Suspicious motion detected: {motion_analysis['motion_pattern']['description']}")
    except Exception as e:
        logger.error(f"Motion analysis failed: {e}")
        motion_analysis = {"analyzed": False, "error": str(e)}

    # 5. Basic event inference
    logger.info("Evaluating unlawful events...")
    events = evaluate_unlawful_events(detections, actions)
    logger.info(f"Detected {len(events)} potential events")

    # 6. Advanced crime pattern analysis
    logger.info("Running advanced crime pattern analysis...")
    crime_analyzer = CrimePatternAnalyzer()
    crime_report = crime_analyzer.generate_crime_report(detections, actions)
    
    logger.info(f"Crime Analysis Complete - Severity: {crime_report['overall_severity'].upper()}")
    if crime_report['crime_detected']:
        logger.warning(f"⚠️ CRIME DETECTED: {len(crime_report['crime_indicators'])} indicators")
        for indicator in crime_report['crime_indicators']:
            logger.warning(f"  - {indicator['type']}: {indicator['severity']} (confidence: {indicator['confidence']:.2f})")

    # 7. Summary with enhanced crime analysis
    summary = {
        "video_hash": video_hash,
        "frames_analyzed": len(frames),
        "frames_per_second": 2,
        "detections_summary": {
            "total_frames": len(detections),
            "unique_objects": list(detected_objects),
            "sample_detections": detections[:4],  # First 4 frames as sample
        },
        "actions_summary": {
            "total_clips": len(actions),
            "clips": actions,
        },
        "motion_analysis": motion_analysis,  # NEW: Motion pattern analysis
        "events": events,
        "crime_report": crime_report,  # Comprehensive crime analysis
    }

    # 8. Gemini description (enhanced with crime report)
    logger.info("Generating AI-powered description...")
    gemini_output = call_gemini(summary)

    result = {
        "summary": summary,
        "gemini_output": gemini_output,
        "crime_analysis": {
            "severity": crime_report["overall_severity"],
            "crime_detected": crime_report["crime_detected"],
            "indicators": crime_report["crime_indicators"],
            "recommendation": crime_report["recommendation"],
            "detailed_analyses": {
                "weapon_threat": crime_report.get("weapon_threat_analysis", {}),
                "violence": crime_report.get("violence_analysis", {}),
                "theft": crime_report.get("theft_analysis", {}),
                "suspicious_behavior": crime_report.get("suspicious_behavior_analysis", {}),
                "motion_patterns": motion_analysis,
            }
        },
        "metadata": {
            "analysis_version": "2.0_enhanced",
            "models_used": ["YOLOv8x", "MoViNet-A2", "CrimePatternAnalyzer", "MotionAnalyzer"],
            "fps": 3,
        }
    }

    # 9. Save to disk
    out_file = RESULT_DIR / f"{video_hash}.json"
    out_file.write_text(json.dumps(result, indent=2))
    logger.info(f"Results saved to {out_file}")

    # 10. Save to redis
    cache_set(video_hash, result)

    # 11. Cleanup frames + file
    try:
        if frame_dir.exists():
            shutil.rmtree(frame_dir)
        video_path.unlink()
        logger.info("Cleanup completed")
    except Exception as e:
        logger.warning(f"[WARN] Cleanup failed: {e}")

    return result
