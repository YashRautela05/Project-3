from ultralytics import YOLO
import numpy as np
import cv2
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Load models once at module level
_yolo_model = None
_movinet_model = None
_movinet_labels = None


def preload_all_models():
    """
    Preload all models at startup to avoid loading on first request.
    Call this from FastAPI startup event or Celery worker initialization.
    """
    logger.info("Preloading all models...")
    _get_yolo_model()
    _load_movinet()
    logger.info("✅ All models preloaded successfully!")


def _get_yolo_model():
    """
    Lazy-load YOLOv8x (extra large) model for maximum accuracy.
    YOLOv8x provides the best detection accuracy for critical crime detection scenarios.
    Trade-off: Slightly slower but significantly more accurate than YOLOv8m.
    """
    global _yolo_model
    if _yolo_model is None:
        logger.info("Loading YOLOv8x model for maximum accuracy...")
        _yolo_model = YOLO("yolov8x.pt")
        logger.info("✅ YOLOv8x model loaded")
    return _yolo_model


def _filter_detections_by_confidence(
    frame_objects: List[Dict[str, Any]], 
    min_confidence: float = 0.4
) -> List[Dict[str, Any]]:
    """
    Filter detections by confidence threshold.
    Lower threshold for critical items (weapons, persons) vs others.
    Enhanced with more crime-relevant object categories.
    """
    # ULTRA-EXPANDED: Critical objects that indicate potential criminal activity
    critical_labels = {
        "person", "knife", "gun", "pistol", "rifle", "weapon",
        "baseball bat", "scissors", "hammer", "axe", "sword",
        "machete", "crowbar", "bat", "stick", "club",
        "bottle", "glass bottle", "beer bottle"  # Potential weapons
    }
    
    # ULTRA-EXPANDED: High-value items often targeted in theft
    valuable_items = {
        "handbag", "backpack", "suitcase", "cell phone", "laptop", 
        "wallet", "purse", "briefcase", "luggage", "bag",
        "watch", "clock", "bottle", "cup", "wine glass",  
        "remote", "book", "tie", "umbrella", "sports ball",
        "keyboard", "mouse", "tv", "monitor", "camera",  # Electronics
        "vase", "potted plant", "teddy bear"  # Items that might be grabbed
    }
    
    # ULTRA-EXPANDED: Vehicle-related for potential car theft or break-ins
    vehicle_items = {
        "car", "truck", "motorcycle", "bicycle", "bus", "train", 
        "skateboard", "scooter"
    }
    
    # ULTRA-EXPANDED: Objects often seen in vandalism/damage scenarios
    damage_related = {
        "bottle", "baseball bat", "sports ball", "frisbee", 
        "skateboard", "scissors", "fork", "spoon", "bowl"
    }
    
    filtered = []
    for obj in frame_objects:
        label = obj.get("label", "").lower()
        conf = obj.get("conf", 0.0)
        
        # ULTRA-AGGRESSIVE thresholds - MAXIMUM SENSITIVITY!
        if label in critical_labels:
            threshold = 0.10  # ULTRA low - was 0.15, catch EVERYTHING weapon-like!
        elif label in valuable_items:
            threshold = 0.15  # Very low - was 0.20
        elif label in vehicle_items:
            threshold = 0.20  # Low - was 0.25
        elif label in damage_related:
            threshold = 0.20  # Low - was 0.25
        else:
            threshold = min(0.30, min_confidence)  # Still very low - was 0.35
        
        if conf >= threshold:
            filtered.append(obj)
    
    return filtered


def _apply_nms(frame_objects: List[Dict[str, Any]], iou_threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Apply Non-Maximum Suppression to remove duplicate detections.
    """
    if not frame_objects:
        return []
    
    # Extract bboxes
    bboxes = np.array([obj["bbox"] for obj in frame_objects])
    confidences = np.array([obj["conf"] for obj in frame_objects])
    
    # Convert xyxy to (x, y, w, h) for NMS
    x1, y1, x2, y2 = bboxes.T
    w = x2 - x1
    h = y2 - y1
    areas = w * h
    
    # Sort by confidence
    order = confidences.argsort()[::-1]
    
    keep = []
    while len(order) > 0:
        i = order[0]
        keep.append(i)
        
        if len(order) == 1:
            break
        
        # Calculate IoU with remaining boxes
        xx1 = np.maximum(bboxes[i, 0], bboxes[order[1:], 0])
        yy1 = np.maximum(bboxes[i, 1], bboxes[order[1:], 1])
        xx2 = np.minimum(bboxes[i, 2], bboxes[order[1:], 2])
        yy2 = np.minimum(bboxes[i, 3], bboxes[order[1:], 3])
        
        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h
        
        iou = inter / (areas[i] + areas[order[1:]] - inter)
        
        # Keep boxes with IoU below threshold
        inds = np.where(iou <= iou_threshold)[0]
        order = order[inds + 1]
    
    return [frame_objects[i] for i in keep]


def run_detection_model(frames: List[Path]) -> List[Dict[str, Any]]:
    """
    Run YOLOv8x on frames for object detection with enhanced settings.
    
    Returns list of frame detections with filtering and NMS applied.
    Includes temporal tracking for suspicious object patterns.
    """
    results = []
    model = _get_yolo_model()
    
    # Track object persistence across frames for better event detection
    object_tracker = {}  # {label: [frame_indices]}
    
    for frame_idx, frame_path in enumerate(frames):
        try:
            # ULTRA LOW initial threshold - catch EVERYTHING even remotely suspicious
            # This is MAXIMUM sensitivity mode for crime detection
            pred = model(
                str(frame_path),
                conf=0.10,  # ULTRA low - was 0.15, now even lower!
                iou=0.30,   # Lower IOU for better separation of overlapping objects
                verbose=False,
                agnostic_nms=False,  # Class-aware NMS for better accuracy
                max_det=400,  # Increased from 300 - detect MORE objects
            )
            
            result = pred[0]
            frame_objects = []
            
            # Iterate over each bounding box
            for box in result.boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                
                # xyxy format: [x1, y1, x2, y2]
                xyxy = box.xyxy[0].tolist()
                
                # class label
                label = result.names[cls_id]
                
                # Calculate bbox area for size analysis
                bbox_area = (xyxy[2] - xyxy[0]) * (xyxy[3] - xyxy[1])
                
                frame_objects.append({
                    "label": label,
                    "conf": conf,
                    "bbox": xyxy,
                    "bbox_area": bbox_area,
                    "class_id": cls_id,
                })
                
                # Track object across frames
                if label not in object_tracker:
                    object_tracker[label] = []
                object_tracker[label].append(frame_idx)
            
            # Apply confidence filtering with adaptive thresholds
            frame_objects = _filter_detections_by_confidence(frame_objects, min_confidence=0.45)
            
            # Apply NMS to remove duplicates
            frame_objects = _apply_nms(frame_objects, iou_threshold=0.45)
            
            results.append({
                "frame": frame_path.name,
                "frame_index": frame_idx,
                "objects": frame_objects,
                "unique_labels": list(set(obj["label"] for obj in frame_objects)),
            })
            
            logger.debug(f"Processed {frame_path.name}: {len(frame_objects)} objects detected")
            
        except Exception as e:
            logger.error(f"Error processing frame {frame_path.name}: {e}")
            results.append({
                "frame": frame_path.name,
                "frame_index": frame_idx,
                "objects": [],
                "unique_labels": [],
            })
    
    # Add temporal patterns to results
    if results:
        results[0]["object_persistence"] = {
            label: {
                "frame_count": len(frames),
                "persistence_ratio": len(frames) / len(results)
            }
            for label, frames in object_tracker.items()
            if len(frames) >= 2  # Object appears in at least 2 frames
        }
    
    return results


# --- Enhanced MoViNet action recognition (Kinetics-600) ---


def _softmax(x: np.ndarray) -> np.ndarray:
    """Numerically stable softmax."""
    x = x - x.max()
    e = np.exp(x)
    return e / e.sum()


def _load_movinet():
    """
    Lazy-load MoViNet A2 model for improved action recognition.
    A2 variant provides better accuracy than A0 for complex actions.
    
    Runs only once when first called (inside Celery worker or first request).
    """
    global _movinet_model, _movinet_labels
    if _movinet_model is not None and _movinet_labels is not None:
        return _movinet_model, _movinet_labels
    
    try:
        import tensorflow as tf
        import tensorflow_hub as hub
        import pathlib
        
        logger.info("Loading MoViNet A2 model for enhanced action recognition...")
        
        # Upgraded to A2 variant for better accuracy in crime detection
        # A2 balances accuracy and speed better than A0
        hub_url = "https://tfhub.dev/tensorflow/movinet/a2/base/kinetics-600/classification/3"
        model = hub.load(hub_url)
        movinet_fn = model.signatures["serving_default"]
        
        # Download Kinetics-600 label file
        logger.info("Downloading Kinetics-600 labels...")
        labels_path = tf.keras.utils.get_file(
            fname="kinetics_600_labels.txt",
            origin=(
                "https://raw.githubusercontent.com/tensorflow/models/"
                "f8af2291cced43fc9f1d9b41ddbf772ae7b0d7d2/"
                "official/projects/movinet/files/kinetics_600_labels.txt"
            ),
        )
        lines = pathlib.Path(labels_path).read_text().splitlines()
        labels = np.array([line.strip() for line in lines])
        
        _movinet_model = movinet_fn
        _movinet_labels = labels
        
        logger.info(f"✅ MoViNet A2 loaded successfully with {len(labels)} action classes")
        return _movinet_model, _movinet_labels
        
    except Exception as e:
        logger.error(f"Failed to load MoViNet A2: {e}")
        logger.warning("Falling back to MoViNet A0...")
        try:
            # Fallback to A0 if A2 fails
            hub_url = "https://tfhub.dev/tensorflow/movinet/a0/base/kinetics-600/classification/3"
            model = hub.load(hub_url)
            movinet_fn = model.signatures["serving_default"]
            
            import tensorflow as tf
            import pathlib
            labels_path = tf.keras.utils.get_file(
                fname="kinetics_600_labels.txt",
                origin=(
                    "https://raw.githubusercontent.com/tensorflow/models/"
                    "f8af2291cced43fc9f1d9b41ddbf772ae7b0d7d2/"
                    "official/projects/movinet/files/kinetics_600_labels.txt"
                ),
            )
            lines = pathlib.Path(labels_path).read_text().splitlines()
            labels = np.array([line.strip() for line in lines])
            
            _movinet_model = movinet_fn
            _movinet_labels = labels
            logger.info("✅ MoViNet A0 loaded as fallback")
            return _movinet_model, _movinet_labels
        except Exception as fallback_error:
            logger.error(f"Failed to load fallback model: {fallback_error}")
            raise


def _preprocess_frame(frame_path: Path, image_size: tuple = (172, 172)) -> np.ndarray:
    """
    Load and preprocess a single frame.
    Returns normalized RGB image or None on failure.
    """
    try:
        img = cv2.imread(str(frame_path))
        if img is None:
            return None
        
        # BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize maintaining aspect ratio then pad
        h, w = img.shape[:2]
        scale = min(image_size[0] / h, image_size[1] / w)
        new_h, new_w = int(h * scale), int(w * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Pad to target size
        pad_h = (image_size[0] - new_h) // 2
        pad_w = (image_size[1] - new_w) // 2
        img = cv2.copyMakeBorder(
            img, pad_h, image_size[0] - new_h - pad_h,
            pad_w, image_size[1] - new_w - pad_w,
            cv2.BORDER_CONSTANT, value=(0, 0, 0)
        )
        
        # Normalize to [0, 1]
        img = img.astype("float32") / 255.0
        
        return img
        
    except Exception as e:
        logger.error(f"Error preprocessing frame {frame_path.name}: {e}")
        return None


def run_action_recognition(
    frames: List[Path],
    image_size: tuple = (224, 224),  # Increased from 172x172 for better quality
    max_frames: int = 50,  # Increased from 32 for longer temporal context
    num_clips: int = 5,  # Increased from 3 for more comprehensive coverage
) -> List[Dict[str, Any]]:
    """
    Run MoViNet on multiple overlapping clips for rich action context.
    Enhanced with more clips and better temporal sampling.
    
    Creates multiple clips from the video to capture different actions:
      - Beginning clip: detects opening actions
      - Multiple middle clips: detects main actions with overlap
      - End clip: detects closing actions
    
    Returns list of clip predictions with top-K actions and timestamps.
    This gives comprehensive temporal context about what happened.
    """
    if not frames:
        return []
    
    try:
        # Ensure chronological order
        frames_sorted = sorted(frames, key=lambda p: p.name)
        num_total_frames = len(frames_sorted)
        
        logger.info(f"Action recognition: analyzing {num_total_frames} frames with {num_clips} overlapping clips")
        
        # Create overlapping clips to capture different temporal moments
        clips_data = []
        
        if num_total_frames < 8:
            logger.warning(f"Insufficient frames for action recognition: {num_total_frames} < 8")
            return []
        
        # Determine clip boundaries with 50% overlap for better coverage
        clip_length = min(max_frames, num_total_frames)
        stride = max(1, clip_length // 2)  # 50% overlap between clips
        
        # Calculate actual number of clips we can extract
        actual_clips = min(num_clips, max(1, (num_total_frames - clip_length) // stride + 1))
        
        for clip_idx in range(actual_clips):
            # Calculate start and end indices for this clip
            start_idx = clip_idx * stride
            end_idx = min(start_idx + clip_length, num_total_frames)
            
            # Adjust if we're near the end
            if end_idx == num_total_frames and (end_idx - start_idx) < clip_length:
                start_idx = max(0, num_total_frames - clip_length)
            
            if start_idx >= num_total_frames:
                break
            
            clip_frames = frames_sorted[start_idx:end_idx]
            
            # Sample frames uniformly from this clip
            if len(clip_frames) > max_frames:
                idxs = np.linspace(0, len(clip_frames) - 1, max_frames).astype(int)
                sampled_frames = [clip_frames[i] for i in idxs]
            else:
                sampled_frames = clip_frames
            
            # Preprocess frames
            images = []
            for frame_path in sampled_frames:
                img = _preprocess_frame(frame_path, image_size)
                if img is not None:
                    images.append(img)
            
            if len(images) < 8:
                logger.debug(f"Clip {clip_idx}: insufficient frames ({len(images)}), skipping")
                continue
            
            # Stack into batch: (T, H, W, 3) -> (1, T, H, W, 3)
            video = np.stack(images, axis=0)
            video = np.expand_dims(video, axis=0)
            
            # Load model and run inference
            movinet, labels = _load_movinet()
            outputs = movinet(image=video)
            logits = outputs["classifier_head"].numpy()[0]  # (600,)
            probs = _softmax(logits)
            
            # Get top-K predictions with ULTRA AGGRESSIVE filtering for crime detection
            top_k = 20  # Get MORE actions to catch anything suspicious
            top_idx = probs.argsort()[-top_k:][::-1]
            
            # EXPANDED crime-relevant keywords - be VERY aggressive
            crime_keywords = [
                # Violence keywords
                'fight', 'punch', 'kick', 'shoot', 'stab', 'hit', 'slap', 'beat',
                'attack', 'assault', 'strangle', 'choke', 'headbutt', 'tackle',
                'wrestling', 'boxing', 'martial', 'combat', 'brawl',
                # Theft keywords
                'steal', 'rob', 'snatch', 'grab', 'take', 'theft', 'shoplift',
                'pickpocket', 'burglar', 'loot', 'pilfer',
                # Vandalism keywords
                'vandal', 'spray', 'break', 'smash', 'destroy', 'damage', 'shatter',
                'demolish', 'wreck', 'ruin',
                # Weapon keywords
                'gun', 'knife', 'weapon', 'shoot', 'fire', 'aim', 'point', 'wield',
                'sword', 'blade',
                # Suspicious behavior
                'threat', 'menac', 'intimidat', 'chase', 'run', 'escape', 'flee',
                'pursue', 'stalk', 'lurk', 'sneak', 'hide', 'creep',
                # General criminal activity
                'crime', 'illegal', 'unlawful', 'violent', 'aggressive', 'hostile'
            ]
            
            # More sophisticated filtering with LOWER thresholds
            top_actions = []
            for i in top_idx:
                prob = float(probs[i])
                label = str(labels[i])
                label_lower = label.lower()
                
                # Check if crime-relevant
                is_relevant = any(kw in label_lower for kw in crime_keywords)
                
                # ULTRA LOW thresholds - we MUST catch criminal activity!
                if is_relevant:
                    # If it's crime-related, keep it even with very low probability
                    if prob > 0.0005:  # Keep almost anything crime-related
                        top_actions.append({
                            "label": label,
                            "prob": prob,
                            "index": int(i),
                            "is_crime_relevant": True,
                            "confidence_boost": True,  # Mark as boosted for crime relevance
                        })
                elif prob > 0.003:  # Normal threshold for non-crime actions
                    top_actions.append({
                        "label": label,
                        "prob": prob,
                        "index": int(i),
                        "is_crime_relevant": False,
                        "confidence_boost": False,
                    })
            
            # Determine clip type for temporal context
            clip_position = clip_idx / max(1, actual_clips - 1) if actual_clips > 1 else 0.5
            if clip_position < 0.25:
                clip_type = "beginning"
            elif clip_position > 0.75:
                clip_type = "end"
            else:
                clip_type = "middle"
            
            clip_data = {
                "clip_index": clip_idx,
                "clip_type": clip_type,
                "clip_position": round(clip_position, 2),
                "frame_range": {
                    "start": start_idx,
                    "end": end_idx,
                    "total_frames": num_total_frames,
                },
                "num_frames_analyzed": len(images),
                "top_actions": top_actions,
                "highest_confidence": top_actions[0]["prob"] if top_actions else 0.0,
            }
            
            clips_data.append(clip_data)
            
            # Log crime-relevant actions
            crime_relevant = [a for a in top_actions if a.get("is_crime_relevant")]
            if crime_relevant:
                crime_labels = [f"{a['label']} ({a['prob']:.3f})" for a in crime_relevant[:3]]
                logger.info(
                    f"Clip {clip_idx} ({clip_type}): frames {start_idx}-{end_idx}, "
                    f"CRIME-RELEVANT actions: {crime_labels}"
                )
            else:
                logger.debug(
                    f"Clip {clip_idx} ({clip_type}): frames {start_idx}-{end_idx}, "
                    f"top actions: {[a['label'] for a in top_actions[:3]]}"
                )
        
        return clips_data
        
    except Exception as e:
        logger.error(f"Error in action recognition: {e}")
        import traceback
        traceback.print_exc()
        return []