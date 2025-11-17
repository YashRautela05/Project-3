# backend/crime_analyzer.py
"""
Advanced crime pattern analysis module.
Focuses specifically on detecting unlawful activities with high precision.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CrimePatternAnalyzer:
    """
    Analyzes detection and action results to identify specific crime patterns.
    Uses sophisticated algorithms to reduce false positives and increase accuracy.
    """
    
    def __init__(self):
        # Crime severity weights (0-1 scale)
        self.severity_weights = {
            "weapon_threat": 1.0,
            "violent_assault": 0.95,
            "armed_robbery": 0.90,
            "physical_fight": 0.85,
            "theft_in_progress": 0.80,
            "vandalism": 0.70,
            "suspicious_activity": 0.60,
            "trespassing": 0.50,
        }
        
        # High-risk action patterns (keyword matching)
        self.violence_keywords = [
            'punch', 'hit', 'kick', 'beat', 'attack', 'assault', 'fight',
            'slap', 'strangle', 'choke', 'tackle', 'headbutt', 'combat'
        ]
        
        self.weapon_keywords = [
            'shoot', 'stab', 'aim', 'point', 'wield', 'brandish', 
            'threaten', 'fire', 'swing', 'strike with'
        ]
        
        self.theft_keywords = [
            'steal', 'snatch', 'grab', 'rob', 'shoplift', 'pickpocket',
            'burglar', 'loot', 'pilfer', 'take', 'swipe'
        ]
        
        self.vandalism_keywords = [
            'smash', 'break', 'destroy', 'damage', 'vandal', 'graffiti',
            'spray paint', 'shatter', 'demolish'
        ]
    
    def analyze_weapon_threat(
        self, 
        detections: List[Dict[str, Any]], 
        actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze weapon presence and assess threat level.
        Returns detailed threat assessment.
        """
        weapon_frames = []
        person_weapon_proximity = []
        weapon_actions = []
        
        for frame_info in detections:
            frame_idx = frame_info.get("frame_index", 0)
            objects = frame_info.get("objects", [])
            
            weapons = [obj for obj in objects if self._is_weapon(obj["label"])]
            persons = [obj for obj in objects if obj["label"].lower() == "person"]
            
            if weapons:
                weapon_frames.append({
                    "frame_index": frame_idx,
                    "frame_name": frame_info.get("frame"),
                    "weapon_count": len(weapons),
                    "person_count": len(persons),
                    "weapons": [{"type": w["label"], "confidence": w["conf"]} for w in weapons],
                })
                
                # Calculate proximity between weapons and persons
                if persons and weapons:
                    for weapon in weapons:
                        min_distance = float('inf')
                        for person in persons:
                            dist = self._calculate_bbox_distance(weapon["bbox"], person["bbox"])
                            min_distance = min(min_distance, dist)
                        
                        person_weapon_proximity.append({
                            "frame_index": frame_idx,
                            "distance": min_distance,
                            "weapon_type": weapon["label"],
                        })
        
        # Check for weapon-related actions
        if actions:
            for clip in actions:
                for action in clip.get("top_actions", []):
                    label = action["label"].lower()
                    if any(kw in label for kw in self.weapon_keywords):
                        weapon_actions.append({
                            "action": action["label"],
                            "confidence": action["prob"],
                            "clip_index": clip.get("clip_index"),
                            "clip_type": clip.get("clip_type"),
                        })
        
        # Calculate threat level
        threat_level = self._calculate_threat_level(
            len(weapon_frames),
            person_weapon_proximity,
            weapon_actions
        )
        
        return {
            "detected": len(weapon_frames) > 0,
            "threat_level": threat_level,
            "weapon_frames": weapon_frames,
            "proximity_alerts": [p for p in person_weapon_proximity if p["distance"] < 200],
            "weapon_actions": weapon_actions,
            "assessment": self._generate_weapon_assessment(threat_level, weapon_frames, weapon_actions),
        }
    
    def analyze_violence_intensity(
        self,
        actions: List[Dict[str, Any]],
        detections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze violent actions and calculate intensity score.
        """
        violent_actions = []
        multi_person_frames = 0
        
        # Identify violent actions
        if actions:
            for clip in actions:
                for action in clip.get("top_actions", []):
                    label = action["label"].lower()
                    prob = action["prob"]
                    
                    if any(kw in label for kw in self.violence_keywords):
                        # Calculate intensity based on probability and keyword severity
                        intensity = self._calculate_violence_intensity(label, prob)
                        violent_actions.append({
                            "action": action["label"],
                            "confidence": prob,
                            "intensity": intensity,
                            "clip_index": clip.get("clip_index"),
                            "clip_type": clip.get("clip_type"),
                        })
        
        # Check for multi-person scenarios (fights)
        for frame_info in detections:
            objects = frame_info.get("objects", [])
            person_count = sum(1 for obj in objects if obj["label"].lower() == "person")
            if person_count >= 2:
                multi_person_frames += 1
        
        # Calculate overall violence score
        violence_score = self._calculate_violence_score(
            violent_actions,
            multi_person_frames,
            len(detections)
        )
        
        return {
            "detected": len(violent_actions) > 0,
            "violence_score": violence_score,
            "intensity_level": self._get_intensity_level(violence_score),
            "violent_actions": sorted(violent_actions, key=lambda x: x["intensity"], reverse=True),
            "multi_person_frame_ratio": multi_person_frames / max(1, len(detections)),
            "assessment": self._generate_violence_assessment(violence_score, violent_actions),
        }
    
    def analyze_theft_patterns(
        self,
        detections: List[Dict[str, Any]],
        actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect theft and robbery patterns.
        """
        theft_indicators = []
        valuable_disappearance = []
        
        # Track valuables across frames
        valuable_labels = {
            "handbag", "backpack", "suitcase", "cell phone", "laptop",
            "wallet", "purse", "briefcase", "watch", "bag"
        }
        
        valuable_timeline = {}
        for frame_info in detections:
            frame_idx = frame_info.get("frame_index", 0)
            objects = frame_info.get("objects", [])
            
            for obj in objects:
                label = obj["label"].lower()
                if label in valuable_labels:
                    if label not in valuable_timeline:
                        valuable_timeline[label] = []
                    valuable_timeline[label].append(frame_idx)
        
        # Detect sudden disappearance (potential theft)
        total_frames = len(detections)
        for label, frames in valuable_timeline.items():
            if len(frames) < total_frames * 0.3 and len(frames) >= 2:
                # Item appears then disappears
                first_seen = min(frames)
                last_seen = max(frames)
                duration = last_seen - first_seen
                
                if duration < total_frames * 0.5:  # Disappears within first half
                    valuable_disappearance.append({
                        "item": label,
                        "first_seen": first_seen,
                        "last_seen": last_seen,
                        "duration_ratio": duration / total_frames,
                        "suspicion_score": 0.8 if duration < total_frames * 0.2 else 0.6,
                    })
        
        # Check for theft-related actions
        theft_actions = []
        if actions:
            for clip in actions:
                for action in clip.get("top_actions", []):
                    label = action["label"].lower()
                    if any(kw in label for kw in self.theft_keywords):
                        theft_actions.append({
                            "action": action["label"],
                            "confidence": action["prob"],
                            "clip_index": clip.get("clip_index"),
                        })
        
        # Calculate theft probability
        theft_probability = self._calculate_theft_probability(
            valuable_disappearance,
            theft_actions
        )
        
        return {
            "detected": len(valuable_disappearance) > 0 or len(theft_actions) > 0,
            "theft_probability": theft_probability,
            "valuable_disappearances": valuable_disappearance,
            "theft_actions": theft_actions,
            "assessment": self._generate_theft_assessment(theft_probability, valuable_disappearance, theft_actions),
        }
    
    def analyze_suspicious_behavior(
        self,
        detections: List[Dict[str, Any]],
        actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Identify suspicious behavior patterns.
        """
        suspicious_patterns = []
        
        # Pattern 1: Loitering (same person/people in many frames without clear activity)
        total_frames = len(detections)
        person_presence = sum(
            1 for frame in detections 
            if any(obj["label"].lower() == "person" for obj in frame.get("objects", []))
        )
        person_ratio = person_presence / max(1, total_frames)
        
        if person_ratio > 0.8:  # Person present in 80%+ of frames
            suspicious_patterns.append({
                "type": "possible_loitering",
                "confidence": min(0.7, person_ratio * 0.8),
                "details": f"Person present in {person_ratio*100:.1f}% of frames",
            })
        
        # Pattern 2: Suspicious actions
        suspicious_keywords = ['lurk', 'sneak', 'hide', 'creep', 'stalk', 'prowl', 'loiter']
        if actions:
            for clip in actions:
                for action in clip.get("top_actions", []):
                    label = action["label"].lower()
                    if any(kw in label for kw in suspicious_keywords):
                        suspicious_patterns.append({
                            "type": "suspicious_action",
                            "action": action["label"],
                            "confidence": action["prob"],
                            "clip_index": clip.get("clip_index"),
                        })
        
        # Pattern 3: Multiple people with no clear legitimate activity
        multi_person_static_frames = 0
        for frame_info in detections:
            objects = frame_info.get("objects", [])
            person_count = sum(1 for obj in objects if obj["label"].lower() == "person")
            if person_count >= 3:
                multi_person_static_frames += 1
        
        if multi_person_static_frames > total_frames * 0.5:
            suspicious_patterns.append({
                "type": "group_loitering",
                "confidence": 0.65,
                "details": f"Multiple people present in {multi_person_static_frames} frames",
            })
        
        suspicion_score = len(suspicious_patterns) * 0.25
        
        return {
            "detected": len(suspicious_patterns) > 0,
            "suspicion_score": min(1.0, suspicion_score),
            "patterns": suspicious_patterns,
            "assessment": self._generate_suspicion_assessment(suspicious_patterns),
        }
    
    def generate_crime_report(
        self,
        detections: List[Dict[str, Any]],
        actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive crime analysis report.
        """
        logger.info("Generating comprehensive crime analysis report...")
        
        # Run all analyses
        weapon_threat = self.analyze_weapon_threat(detections, actions)
        violence = self.analyze_violence_intensity(actions, detections)
        theft = self.analyze_theft_patterns(detections, actions)
        suspicious = self.analyze_suspicious_behavior(detections, actions)
        
        # Determine overall crime likelihood
        crime_indicators = []
        overall_severity = "safe"
        
        if weapon_threat["detected"]:
            crime_indicators.append({
                "type": "weapon_threat",
                "severity": weapon_threat["threat_level"],
                "confidence": 0.9,
            })
        
        if violence["detected"] and violence["violence_score"] > 0.5:
            crime_indicators.append({
                "type": "violent_assault",
                "severity": violence["intensity_level"],
                "confidence": violence["violence_score"],
            })
        
        if theft["detected"] and theft["theft_probability"] > 0.4:
            crime_indicators.append({
                "type": "theft_or_robbery",
                "severity": "high" if theft["theft_probability"] > 0.7 else "medium",
                "confidence": theft["theft_probability"],
            })
        
        if suspicious["detected"] and suspicious["suspicion_score"] > 0.5:
            crime_indicators.append({
                "type": "suspicious_activity",
                "severity": "medium",
                "confidence": suspicious["suspicion_score"],
            })
        
        # Determine overall severity
        if crime_indicators:
            max_severity = max(
                ind.get("confidence", 0) * self.severity_weights.get(ind["type"], 0.5)
                for ind in crime_indicators
            )
            
            if max_severity > 0.8:
                overall_severity = "critical"
            elif max_severity > 0.6:
                overall_severity = "high"
            elif max_severity > 0.4:
                overall_severity = "medium"
            else:
                overall_severity = "low"
        
        return {
            "overall_severity": overall_severity,
            "crime_detected": len(crime_indicators) > 0,
            "crime_indicators": crime_indicators,
            "weapon_threat_analysis": weapon_threat,
            "violence_analysis": violence,
            "theft_analysis": theft,
            "suspicious_behavior_analysis": suspicious,
            "recommendation": self._generate_recommendation(overall_severity, crime_indicators),
        }
    
    # Helper methods
    
    def _is_weapon(self, label: str) -> bool:
        """
        Check if object is a weapon or potential weapon.
        EXPANDED to catch more weapon-like objects.
        """
        weapon_labels = {
            # Obvious weapons
            "knife", "gun", "pistol", "rifle", "weapon", "firearm",
            # Blunt objects
            "baseball bat", "bat", "hammer", "axe", "crowbar", "stick",
            # Bladed objects  
            "scissors", "sword", "machete", "blade", "razor",
            # Other potential weapons
            "bottle", "chain", "pipe", "wrench", "club", "baton"
        }
        label_lower = label.lower()
        return any(weapon in label_lower for weapon in weapon_labels)
    
    def _calculate_bbox_distance(self, bbox1: List[float], bbox2: List[float]) -> float:
        """Calculate distance between two bounding box centers."""
        center1 = [(bbox1[0] + bbox1[2]) / 2, (bbox1[1] + bbox1[3]) / 2]
        center2 = [(bbox2[0] + bbox2[2]) / 2, (bbox2[1] + bbox2[3]) / 2]
        return np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
    
    def _calculate_threat_level(
        self,
        weapon_frame_count: int,
        proximity_data: List[Dict],
        weapon_actions: List[Dict]
    ) -> str:
        """
        Calculate weapon threat level with LOWER thresholds.
        """
        if weapon_frame_count == 0:
            return "none"
        
        # Check for very close proximity (INCREASED threshold to catch more)
        close_proximity = sum(1 for p in proximity_data if p["distance"] < 300)  # Increased from 150
        moderate_proximity = sum(1 for p in proximity_data if p["distance"] < 500)  # New tier
        
        # CRITICAL: Any weapon close to person OR any weapon action
        if close_proximity > 0 or len(weapon_actions) > 0:
            return "critical"
        # HIGH: Weapon in moderate proximity OR detected in multiple frames
        elif moderate_proximity > 0 or weapon_frame_count > 2:  # Lowered from 3
            return "high"
        # MEDIUM: Any weapon detected
        else:
            return "medium"
    
    def _calculate_violence_intensity(self, action_label: str, probability: float) -> float:
        """
        Calculate violence intensity score for an action.
        LOWERED thresholds to catch more violence.
        """
        action_lower = action_label.lower()
        
        # EXTREME violence keywords
        extreme_violence = ['shoot', 'stab', 'strangle', 'choke', 'murder', 'kill']
        # HIGH violence keywords  
        high_violence = ['punch', 'kick', 'beat', 'hit', 'slap', 'headbutt', 'attack', 'assault']
        # MEDIUM violence keywords
        medium_violence = ['fight', 'wrestle', 'tackle', 'shove', 'push', 'grab']
        
        base_score = probability
        
        if any(kw in action_lower for kw in extreme_violence):
            return min(1.0, base_score * 2.0)  # Massive boost for extreme violence
        elif any(kw in action_lower for kw in high_violence):
            return min(1.0, base_score * 1.5)
        elif any(kw in action_lower for kw in medium_violence):
            return min(1.0, base_score * 1.2)  # Increased from base
        else:
            return base_score * 0.8
    
    def _calculate_violence_score(
        self,
        violent_actions: List[Dict],
        multi_person_frames: int,
        total_frames: int
    ) -> float:
        """Calculate overall violence score."""
        if not violent_actions:
            return 0.0
        
        avg_intensity = np.mean([a["intensity"] for a in violent_actions])
        action_count_factor = min(1.0, len(violent_actions) * 0.2)
        multi_person_factor = multi_person_frames / max(1, total_frames)
        
        return min(1.0, avg_intensity * 0.5 + action_count_factor * 0.3 + multi_person_factor * 0.2)
    
    def _get_intensity_level(self, score: float) -> str:
        """
        Convert violence score to intensity level.
        LOWERED thresholds to be more sensitive.
        """
        if score > 0.6:  # Lowered from 0.75
            return "extreme"
        elif score > 0.35:  # Lowered from 0.5
            return "high"
        elif score > 0.15:  # Lowered from 0.25
            return "moderate"
        else:
            return "low"
    
    def _calculate_theft_probability(
        self,
        disappearances: List[Dict],
        theft_actions: List[Dict]
    ) -> float:
        """Calculate probability of theft."""
        if not disappearances and not theft_actions:
            return 0.0
        
        disappearance_score = sum(d["suspicion_score"] for d in disappearances) / max(1, len(disappearances) or 1)
        action_score = sum(a["confidence"] for a in theft_actions) / max(1, len(theft_actions) or 1)
        
        if disappearances and theft_actions:
            return min(1.0, (disappearance_score + action_score) / 2 * 1.2)  # Boost when both present
        elif disappearances:
            return disappearance_score * 0.8
        else:
            return action_score * 0.7
    
    def _generate_weapon_assessment(self, threat_level: str, frames: List, actions: List) -> str:
        """Generate weapon threat assessment text."""
        if threat_level == "critical":
            return "CRITICAL: Weapon detected in close proximity to persons. Immediate threat to safety."
        elif threat_level == "high":
            return "HIGH: Weapon detected in multiple frames. Potential threat situation."
        elif threat_level == "medium":
            return "MEDIUM: Weapon-like object detected. Monitor situation."
        else:
            return "No significant weapon threat detected."
    
    def _generate_violence_assessment(self, score: float, actions: List) -> str:
        """Generate violence assessment text."""
        if score > 0.75:
            return f"EXTREME violence detected: {len(actions)} violent actions identified. Immediate intervention required."
        elif score > 0.5:
            return f"HIGH violence detected: {len(actions)} violent actions. Serious assault in progress."
        elif score > 0.25:
            return f"MODERATE violence: {len(actions)} potentially violent actions detected."
        else:
            return "Low or no violence detected."
    
    def _generate_theft_assessment(self, probability: float, disappearances: List, actions: List) -> str:
        """Generate theft assessment text."""
        if probability > 0.7:
            return f"HIGH probability of theft: {len(disappearances)} items disappeared, {len(actions)} theft-related actions."
        elif probability > 0.4:
            return f"MODERATE theft risk: Suspicious patterns detected."
        else:
            return "Low theft risk."
    
    def _generate_suspicion_assessment(self, patterns: List) -> str:
        """Generate suspicious behavior assessment."""
        if len(patterns) >= 3:
            return f"HIGHLY suspicious: {len(patterns)} suspicious patterns detected."
        elif len(patterns) >= 1:
            return f"Suspicious activity detected: {patterns[0]['type']}"
        else:
            return "No suspicious behavior detected."
    
    def _generate_recommendation(self, severity: str, indicators: List) -> str:
        """Generate safety recommendation."""
        if severity == "critical":
            return ("⚠️ CRITICAL ALERT: Immediate danger detected. "
                   "Call emergency services (911/112) immediately. "
                   "Do NOT intervene directly. Evacuate to safe location.")
        elif severity == "high":
            return ("🚨 HIGH ALERT: Serious criminal activity detected. "
                   "Contact law enforcement immediately. "
                   "Keep safe distance and observe from secure location.")
        elif severity == "medium":
            return ("⚠️ CAUTION: Suspicious activity detected. "
                   "Monitor situation closely. Contact security or police if activity escalates.")
        elif severity == "low":
            return ("ℹ️ LOW RISK: Minor concerning activity. Continue monitoring.")
        else:
            return ("✅ SAFE: No significant unlawful activity detected.")
