# backend/motion_analyzer.py
"""
Motion and movement pattern analysis for crime detection.
Analyzes frame-to-frame changes to detect suspicious movements.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class MotionAnalyzer:
    """
    Analyzes motion patterns in video to detect:
    - Sudden movements (potential violence, running, fleeing)
    - Chase sequences
    - Erratic behavior
    - Directional movement patterns
    """
    
    def __init__(self):
        self.motion_threshold = 30.0  # Threshold for significant motion
        self.sudden_movement_threshold = 50.0  # Threshold for very sudden movements
    
    def analyze_motion_patterns(self, frames: List[Path]) -> Dict[str, Any]:
        """
        Analyze motion patterns across frames.
        Returns motion intensity, sudden movements, and movement trends.
        """
        if len(frames) < 2:
            return {"analyzed": False, "reason": "Insufficient frames"}
        
        logger.info(f"Analyzing motion patterns across {len(frames)} frames...")
        
        motion_scores = []
        sudden_movements = []
        prev_frame = None
        
        for idx, frame_path in enumerate(frames[:50]):  # Analyze first 50 frames
            try:
                current_frame = cv2.imread(str(frame_path), cv2.IMREAD_GRAYSCALE)
                if current_frame is None:
                    continue
                
                # Resize for faster processing
                current_frame = cv2.resize(current_frame, (320, 240))
                
                if prev_frame is not None:
                    # Calculate frame difference
                    motion_score = self._calculate_motion_score(prev_frame, current_frame)
                    motion_scores.append(motion_score)
                    
                    # Detect sudden movements
                    if motion_score > self.sudden_movement_threshold:
                        sudden_movements.append({
                            "frame_index": idx,
                            "motion_intensity": motion_score,
                            "timestamp": f"{idx}s",
                        })
                
                prev_frame = current_frame
                
            except Exception as e:
                logger.error(f"Error processing frame {frame_path}: {e}")
                continue
        
        if not motion_scores:
            return {"analyzed": False, "reason": "No motion data"}
        
        # Calculate statistics
        avg_motion = np.mean(motion_scores)
        max_motion = np.max(motion_scores)
        motion_variance = np.var(motion_scores)
        
        # Detect patterns
        motion_pattern = self._classify_motion_pattern(avg_motion, motion_variance, sudden_movements)
        
        # Detect running/chase sequences
        chase_sequences = self._detect_chase_sequences(motion_scores)
        
        logger.info(f"Motion analysis complete: {motion_pattern['category']} - {len(sudden_movements)} sudden movements")
        
        return {
            "analyzed": True,
            "average_motion": float(avg_motion),
            "max_motion": float(max_motion),
            "motion_variance": float(motion_variance),
            "motion_pattern": motion_pattern,
            "sudden_movements": sudden_movements,
            "chase_sequences": chase_sequences,
            "frames_analyzed": len(motion_scores),
        }
    
    def _calculate_motion_score(self, prev_frame: np.ndarray, current_frame: np.ndarray) -> float:
        """
        Calculate motion score between two frames using frame differencing.
        """
        # Frame difference
        diff = cv2.absdiff(prev_frame, current_frame)
        
        # Threshold to get binary motion mask
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        
        # Calculate percentage of changed pixels
        motion_pixels = np.sum(thresh > 0)
        total_pixels = thresh.shape[0] * thresh.shape[1]
        motion_percentage = (motion_pixels / total_pixels) * 100
        
        return motion_percentage
    
    def _classify_motion_pattern(
        self,
        avg_motion: float,
        variance: float,
        sudden_movements: List[Dict]
    ) -> Dict[str, Any]:
        """
        Classify overall motion pattern.
        """
        if len(sudden_movements) > 3:
            if avg_motion > 25:
                return {
                    "category": "chaotic_high_motion",
                    "description": "High chaotic motion with multiple sudden movements (possible chase, fight, panic)",
                    "crime_relevance": "high",
                    "confidence": 0.85,
                }
            else:
                return {
                    "category": "erratic_movement",
                    "description": "Erratic motion patterns (possible suspicious behavior)",
                    "crime_relevance": "medium",
                    "confidence": 0.70,
                }
        
        elif avg_motion > 30:
            return {
                "category": "high_activity",
                "description": "High overall motion (possible running, chase, or violent activity)",
                "crime_relevance": "medium",
                "confidence": 0.75,
            }
        
        elif avg_motion > 15:
            return {
                "category": "moderate_activity",
                "description": "Moderate motion (normal activity or walking)",
                "crime_relevance": "low",
                "confidence": 0.50,
            }
        
        elif variance > 50:
            return {
                "category": "intermittent_activity",
                "description": "Sporadic bursts of activity (possible lurking or waiting behavior)",
                "crime_relevance": "medium",
                "confidence": 0.65,
            }
        
        else:
            return {
                "category": "low_activity",
                "description": "Low motion (static scene or loitering)",
                "crime_relevance": "low",
                "confidence": 0.40,
            }
    
    def _detect_chase_sequences(self, motion_scores: List[float]) -> List[Dict[str, Any]]:
        """
        Detect sustained high-motion sequences that might indicate chases.
        """
        chase_sequences = []
        in_chase = False
        chase_start = 0
        chase_duration = 0
        
        for idx, score in enumerate(motion_scores):
            if score > 35:  # High sustained motion
                if not in_chase:
                    in_chase = True
                    chase_start = idx
                    chase_duration = 1
                else:
                    chase_duration += 1
            else:
                if in_chase and chase_duration >= 3:  # Sustained for at least 3 frames
                    chase_sequences.append({
                        "start_frame": chase_start,
                        "duration_frames": chase_duration,
                        "avg_intensity": float(np.mean(motion_scores[chase_start:chase_start + chase_duration])),
                        "description": f"High-motion sequence suggesting chase or rapid movement",
                    })
                in_chase = False
                chase_duration = 0
        
        # Check final sequence
        if in_chase and chase_duration >= 3:
            chase_sequences.append({
                "start_frame": chase_start,
                "duration_frames": chase_duration,
                "avg_intensity": float(np.mean(motion_scores[chase_start:chase_start + chase_duration])),
                "description": f"High-motion sequence suggesting chase or rapid movement",
            })
        
        return chase_sequences


def integrate_motion_analysis(frames: List[Path]) -> Dict[str, Any]:
    """
    Convenience function to run motion analysis.
    """
    analyzer = MotionAnalyzer()
    return analyzer.analyze_motion_patterns(frames)
