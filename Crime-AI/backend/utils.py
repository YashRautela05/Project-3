# backend/utils.py

from __future__ import annotations

import json
from typing import Any, Dict, List


# --- Configurable label groups ----

# Expanded weapon detection
WEAPON_LABELS = {
    "knife", "gun", "pistol", "rifle", "weapon",
    "baseball bat", "bat", "scissors", "hammer", "axe",
    "sword", "machete", "crowbar"
}

# Expanded valuable items
VALUABLE_LABELS = {
    "handbag", "backpack", "suitcase", "cell phone", "laptop", 
    "wallet", "purse", "briefcase", "luggage", "bag",
    "watch", "jewelry", "tablet", "camera"
}

# Vehicle-related items for potential theft
VEHICLE_LABELS = {
    "car", "truck", "motorcycle", "bicycle", "bus", "van", "suv"
}

PERSON_LABEL = "person"

# Enhanced action keywords with more comprehensive crime patterns
ACTION_KEYWORDS = {
    "possible_property_damage": [
        "tagging graffiti", "spray painting", "vandalizing", "smashing",
        "breaking", "destroying", "damaging", "scratching"
    ],
    "possible_robbery_or_snatching": [
        "stealing", "shoplifting", "pick pocketing", "mugging",
        "robbery", "snatching", "grabbing", "taking", "theft"
    ],
    "possible_assault_or_fight": [
        "fighting", "punching", "kicking", "wrestling", "slapping",
        "strangling", "beating", "hitting", "attacking", "struggling",
        "brawling", "combat"
    ],
    "possible_weapon_incident": [
        "shooting", "firing gun", "aiming gun", "stabbing", 
        "knife fighting", "wielding", "threatening", "pointing"
    ],
    "possible_chase_or_escape": [
        "running", "chasing", "escaping", "fleeing", "pursuing",
        "sprinting", "racing"
    ],
    "possible_break_in": [
        "breaking and entering", "climbing", "opening", "forcing",
        "prying", "jimmying"
    ],
    "suspicious_behavior": [
        "lurking", "sneaking", "hiding", "creeping", "stalking",
        "loitering", "prowling"
    ],
}


def _count_objects_by_label(objects: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for obj in objects:
        label = str(obj.get("label", "")).lower()
        counts[label] = counts.get(label, 0) + 1
    return counts


def evaluate_unlawful_events(
    detections: List[Dict[str, Any]],
    actions: List[Dict[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
    """
    Build a list of 'events' using both:
      - frame-level YOLO detections
      - clip-level MoViNet action predictions

    Enhanced with more sophisticated pattern detection and severity scoring.
    This function is deliberately heuristic + conservative; it *suggests*
    suspicious patterns, not definitive crimes.
    """
    events: List[Dict[str, Any]] = []

    # --- 1. Events based on per-frame object detections (YOLO) ---

    total_frames = len(detections)
    person_frames = []
    weapon_frames = []
    valuable_frames = []
    vehicle_frames = []

    for frame_info in detections:
        frame_name = frame_info.get("frame")
        frame_idx = frame_info.get("frame_index", 0)
        objs = frame_info.get("objects", [])

        counts = _count_objects_by_label(objs)

        # Track objects across frames
        if counts.get(PERSON_LABEL, 0) > 0:
            person_frames.append(frame_idx)
        
        # weapon-like object in frame
        weapon_labels_in_frame = [lbl for lbl in counts if lbl in WEAPON_LABELS]
        if weapon_labels_in_frame:
            weapon_frames.append(frame_idx)
            # Calculate severity based on weapon type and person presence
            has_persons = counts.get(PERSON_LABEL, 0) > 0
            severity = 0.9 if has_persons else 0.7
            
            events.append({
                "type": "weapon_like_object_detected",
                "frame": frame_name,
                "frame_index": frame_idx,
                "confidence": severity,
                "severity": "critical" if has_persons else "high",
                "source": "object_detection",
                "details": {
                    "weapon_labels": weapon_labels_in_frame,
                    "counts": {lbl: counts[lbl] for lbl in weapon_labels_in_frame},
                    "persons_present": counts.get(PERSON_LABEL, 0),
                },
            })

        # Valuable items detection
        valuable_labels_in_frame = [lbl for lbl in counts if lbl in VALUABLE_LABELS]
        if valuable_labels_in_frame:
            valuable_frames.append(frame_idx)
            person_count = counts.get(PERSON_LABEL, 0)
            
            # High-value scenario: multiple persons + valuables (potential theft)
            if person_count >= 2:
                events.append({
                    "type": "valuable_items_with_multiple_persons",
                    "frame": frame_name,
                    "frame_index": frame_idx,
                    "confidence": 0.6,
                    "severity": "medium",
                    "source": "object_detection",
                    "details": {
                        "valuable_labels": valuable_labels_in_frame,
                        "persons_count": person_count,
                        "items_count": sum(counts[lbl] for lbl in valuable_labels_in_frame),
                    },
                })

        # Vehicle-related events
        vehicle_labels_in_frame = [lbl for lbl in counts if lbl in VEHICLE_LABELS]
        if vehicle_labels_in_frame and counts.get(PERSON_LABEL, 0) > 0:
            vehicle_frames.append(frame_idx)

        # crowd activity (many persons visible) - LOWERED threshold
        person_count = counts.get(PERSON_LABEL, 0)
        if person_count >= 3:  # Lowered from 5 to catch smaller groups
            events.append({
                "type": "crowd_activity",
                "frame": frame_name,
                "frame_index": frame_idx,
                "confidence": min(0.8, 0.4 + person_count * 0.05),
                "severity": "low" if person_count < 7 else "medium",  # Adjusted threshold
                "source": "object_detection",
                "details": {
                    "persons_visible": person_count,
                },
            })

    # --- Temporal Pattern Analysis ---
    
    # LOWERED THRESHOLD: Weapon even in single frame is critical
    if len(weapon_frames) >= 1:  # Changed from >= 2
        events.append({
            "type": "weapon_persistent_presence" if len(weapon_frames) >= 2 else "weapon_detected",
            "confidence": 0.90 if len(weapon_frames) >= 2 else 0.75,
            "severity": "critical",
            "source": "temporal_analysis",
            "details": {
                "frames_with_weapon": len(weapon_frames),
                "total_frames": total_frames,
                "persistence_ratio": len(weapon_frames) / max(1, total_frames),
            },
        })

    # Sudden appearance/disappearance of valuables (potential theft)
    if len(valuable_frames) > 0:
        first_valuable = min(valuable_frames)
        last_valuable = max(valuable_frames)
        
        if last_valuable - first_valuable < total_frames * 0.3:  # Items disappear quickly
            events.append({
                "type": "valuable_items_sudden_change",
                "confidence": 0.65,
                "severity": "medium",
                "source": "temporal_analysis",
                "details": {
                    "first_appearance": first_valuable,
                    "last_appearance": last_valuable,
                    "duration_ratio": (last_valuable - first_valuable) / max(1, total_frames),
                },
            })

    # --- 2. Events based on action recognition (MoViNet) ---

    if actions:
        for clip in actions:
            clip_index = clip.get("clip_index", 0)
            clip_type = clip.get("clip_type", "unknown")
            top_actions = clip.get("top_actions", [])

            for act in top_actions:
                label = str(act.get("label", "")).lower()
                prob = float(act.get("prob", 0.0))
                is_crime_relevant = act.get("is_crime_relevant", False)

                # ULTRA LOW thresholds - we MUST catch criminal activity!
                if is_crime_relevant:
                    min_prob = 0.001  # Nearly zero threshold for crime-relevant
                else:
                    min_prob = 0.08  # Lowered from 0.15
                
                if prob < min_prob:
                    continue

                # Match against expanded action keywords
                for event_type, keywords in ACTION_KEYWORDS.items():
                    if any(kw in label for kw in keywords):
                        # AGGRESSIVE severity assignment
                        if "weapon" in event_type or "assault" in event_type:
                            severity = "critical" if prob > 0.1 else "high"  # Lowered from 0.3
                        elif "robbery" in event_type or "break_in" in event_type:
                            severity = "high" if prob > 0.05 else "medium"  # Lowered from 0.2
                        elif "chase" in event_type or "fight" in event_type:
                            severity = "high" if prob > 0.05 else "medium"  # New
                        else:
                            severity = "medium" if prob > 0.05 else "low"  # Lowered from 0.15
                        
                        events.append({
                            "type": event_type,
                            "source": "action_recognition",
                            "confidence": prob,
                            "severity": severity,
                            "details": {
                                "label": act.get("label"),
                                "prob": prob,
                                "clip_index": clip_index,
                                "clip_type": clip_type,
                                "is_crime_relevant": is_crime_relevant,
                            },
                        })

    # --- 3. Cross-modal correlation (combine object + action) ---
    
    # Weapon + Fight action = High severity incident
    weapon_events = [e for e in events if "weapon" in e.get("type", "")]
    fight_events = [e for e in events if "assault" in e.get("type", "") or "fight" in e.get("type", "")]
    
    if weapon_events and fight_events:
        events.append({
            "type": "armed_conflict_detected",
            "confidence": 0.9,
            "severity": "critical",
            "source": "cross_modal_correlation",
            "details": {
                "weapon_detections": len(weapon_events),
                "fight_actions": len(fight_events),
                "correlation": "weapons detected during violent actions",
            },
        })

    return events


# --- Gemini API Integration for Crime Analysis ----

def call_gemini(summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    REAL Gemini API integration for comprehensive crime analysis.
    
    Sends complete analysis data to Gemini and gets:
    - Human-readable description
    - Crime type classification
    - Severity assessment
    - Evidence summary
    - Safety recommendations
    - Legal punishment information (IPC sections)
    - How to stay safe
    
    Returns structured response with all information.
    """
    import os
    
    # Get API key from environment
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    if not GOOGLE_API_KEY:
        # Fallback to structured response if no API key
        return _generate_fallback_response(summary)
    
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Extract key information
        crime_report = summary.get("crime_report", {})
        motion_analysis = summary.get("motion_analysis", {})
        detections = summary.get("detections", [])
        actions = summary.get("actions", [])
        events = summary.get("events", [])
        
        severity = crime_report.get("overall_severity", "unknown")
        crime_detected = crime_report.get("crime_detected", False)
        indicators = crime_report.get("crime_indicators", [])
        
        # Build comprehensive prompt
        prompt = f"""You are an expert crime analyst and legal advisor reviewing automated video surveillance results.

ANALYSIS DATA:
==============

**Severity Level**: {severity.upper()}
**Crime Detected**: {"YES" if crime_detected else "NO"}
**Number of Crime Indicators**: {len(indicators)}

**Crime Indicators:**
{_format_indicators(indicators)}

**Weapon Threat Analysis:**
{_format_weapon_analysis(crime_report.get("weapon_threat_analysis", {}))}

**Violence Analysis:**
{_format_violence_analysis(crime_report.get("violence_analysis", {}))}

**Theft Analysis:**
{_format_theft_analysis(crime_report.get("theft_analysis", {}))}

**Suspicious Behavior:**
{_format_suspicious_behavior(crime_report.get("suspicious_behavior_analysis", {}))}

**Objects Detected**: {_format_detections_summary(detections)}

**Actions Recognized**: {_format_actions_summary(actions)}

**Motion Patterns**: {_format_motion_summary(motion_analysis)}

YOUR TASK:
==========
Provide a comprehensive analysis in JSON format with the following structure:

{{
  "description": "Clear, factual 3-5 sentence description of what is happening in the video",
  
  "crime_detected": true/false,
  
  "crime_type": "One of: assault, armed_assault, robbery, theft, vandalism, fight, weapon_threat, suspicious_activity, none",
  
  "severity": "critical/high/medium/low/safe",
  
  "confidence_level": "very_high/high/medium/low (based on evidence strength)",
  
  "evidence_summary": [
    "List 3-5 specific pieces of evidence from the analysis"
  ],
  
  "safety_recommendations": [
    "List 4-6 specific safety steps based on severity"
  ],
  
  "legal_information": {{
    "ipc_sections": [
      {{"section": "IPC XXX", "offense": "description", "punishment": "details"}}
    ],
    "possible_punishment": "Detailed explanation of potential legal consequences",
    "severity_factors": ["Factors that increase/decrease punishment"]
  }},
  
  "how_to_stay_safe": [
    "Specific actionable safety advice (6-8 points)"
  ],
  
  "immediate_actions": [
    "What to do RIGHT NOW based on severity (3-5 points)"
  ],
  
  "reporting_guidance": {{
    "should_report": true/false,
    "urgency": "immediate/high/normal/low",
    "who_to_contact": "Police/Security/etc",
    "what_to_report": "Specific information to provide"
  }},
  
  "disclaimer": "Legal disclaimer about automated analysis"
}}

IMPORTANT GUIDELINES:
- Be specific and actionable
- For CRITICAL/HIGH severity: emphasize IMMEDIATE safety (call 911/112, evacuate, do NOT intervene)
- For punishment: cite actual Indian Penal Code sections when applicable
- For safety advice: be practical and situation-specific
- Include both immediate and long-term safety measures
- Mention evidence preservation (video, documentation)
- Consider bystander safety vs intervention risks

Generate ONLY valid JSON, no other text."""

        # Call Gemini API
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Extract JSON from response (remove markdown if present)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        gemini_response = json.loads(response_text)
        
        return gemini_response
        
    except ImportError:
        # google-generativeai not installed
        import logging
        logging.warning("google-generativeai not installed. Using fallback response.")
        return _generate_fallback_response(summary)
    except Exception as e:
        import logging
        logging.error(f"Gemini API error: {e}")
        return _generate_fallback_response(summary)


def _format_indicators(indicators: List[Dict]) -> str:
    """Format crime indicators for prompt."""
    if not indicators:
        return "None"
    return "\n".join([
        f"  - {ind.get('type', 'unknown')}: {ind.get('severity', 'unknown')} severity "
        f"(confidence: {ind.get('confidence', 0):.2f})"
        for ind in indicators[:10]  # Limit to top 10
    ])


def _format_weapon_analysis(weapon_data: Dict) -> str:
    """Format weapon analysis for prompt."""
    if not weapon_data.get("detected"):
        return "No weapons detected"
    return f"""Detected: YES
Threat Level: {weapon_data.get('threat_level', 'unknown').upper()}
Weapon Frames: {len(weapon_data.get('weapon_frames', []))}
Proximity Alerts: {len(weapon_data.get('proximity_alerts', []))}
Assessment: {weapon_data.get('assessment', 'N/A')}"""


def _format_violence_analysis(violence_data: Dict) -> str:
    """Format violence analysis for prompt."""
    if not violence_data.get("detected"):
        return "No violence detected"
    return f"""Detected: YES
Intensity Level: {violence_data.get('intensity_level', 'unknown').upper()}
Violence Score: {violence_data.get('violence_score', 0):.2f}
Violent Actions: {len(violence_data.get('violent_actions', []))}
Assessment: {violence_data.get('assessment', 'N/A')}"""


def _format_theft_analysis(theft_data: Dict) -> str:
    """Format theft analysis for prompt."""
    if not theft_data.get("detected"):
        return "No theft detected"
    return f"""Detected: YES
Theft Probability: {theft_data.get('theft_probability', 0)*100:.0f}%
Item Disappearances: {len(theft_data.get('disappearances', []))}
Assessment: {theft_data.get('assessment', 'N/A')}"""


def _format_suspicious_behavior(suspicious_data: Dict) -> str:
    """Format suspicious behavior for prompt."""
    patterns = suspicious_data.get("patterns", [])
    if not patterns:
        return "No suspicious patterns detected"
    return f"""Patterns Found: {len(patterns)}
Types: {', '.join([p.get('type', 'unknown') for p in patterns[:5]])}"""


def _format_detections_summary(detections: List[Dict]) -> str:
    """Summarize object detections."""
    all_labels = []
    for det in detections:
        all_labels.extend([obj.get("label") for obj in det.get("objects", [])])
    
    if not all_labels:
        return "None"
    
    from collections import Counter
    counts = Counter(all_labels)
    top_objects = counts.most_common(10)
    return ", ".join([f"{label} ({count})" for label, count in top_objects])


def _format_actions_summary(actions: List[Dict]) -> str:
    """Summarize recognized actions."""
    if not actions:
        return "None"
    
    all_actions = []
    for clip in actions:
        top_actions = clip.get("top_actions", [])[:3]  # Top 3 per clip
        all_actions.extend([a.get("label") for a in top_actions])
    
    if not all_actions:
        return "None"
    
    return ", ".join(all_actions[:10])  # Limit to 10


def _format_motion_summary(motion_data: Dict) -> str:
    """Format motion analysis summary."""
    if not motion_data.get("analyzed"):
        return "Not analyzed"
    
    pattern = motion_data.get("motion_pattern", {})
    return f"{pattern.get('category', 'unknown')} - {pattern.get('description', 'N/A')}"


def _generate_fallback_response(summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate fallback response when Gemini API is unavailable.
    Uses the existing logic from previous implementation.
    """
    # Extract key information from crime report if available
    crime_report = summary.get("crime_report", {})
    motion_analysis = summary.get("motion_analysis", {})
    
    severity = crime_report.get("overall_severity", "unknown")
    crime_detected = crime_report.get("crime_detected", False)
    indicators = crime_report.get("crime_indicators", [])
    
    # Build enhanced prompt with crime context
    crime_context = ""
    if crime_detected:
        crime_context = "\n\n**IMPORTANT CRIME ANALYSIS RESULTS:**\n"
        crime_context += f"- Overall Severity: {severity.upper()}\n"
        crime_context += f"- Crime Indicators Detected: {len(indicators)}\n"
        for ind in indicators:
            crime_context += f"  * {ind['type']}: {ind['severity']} severity (confidence: {ind['confidence']:.2f})\n"
        
        # Add specific analysis details
        weapon_analysis = crime_report.get("weapon_threat_analysis", {})
        if weapon_analysis.get("detected"):
            crime_context += f"\n- Weapon Threat: {weapon_analysis.get('threat_level', 'unknown').upper()}\n"
            crime_context += f"  {weapon_analysis.get('assessment', '')}\n"
        
        violence_analysis = crime_report.get("violence_analysis", {})
        if violence_analysis.get("detected"):
            crime_context += f"\n- Violence Detected: {violence_analysis.get('intensity_level', 'unknown').upper()}\n"
            crime_context += f"  {violence_analysis.get('assessment', '')}\n"
        
        theft_analysis = crime_report.get("theft_analysis", {})
        if theft_analysis.get("detected"):
            crime_context += f"\n- Theft Probability: {theft_analysis.get('theft_probability', 0)*100:.0f}%\n"
            crime_context += f"  {theft_analysis.get('assessment', '')}\n"
    
    # Add motion analysis context
    motion_context = ""
    if motion_analysis.get("analyzed"):
        motion_pattern = motion_analysis.get("motion_pattern", {})
        if motion_pattern.get("crime_relevance") in ["high", "medium"]:
            motion_context = f"\n\n**MOTION ANALYSIS:**\n"
            motion_context += f"- Pattern: {motion_pattern.get('category', 'unknown')}\n"
            motion_context += f"- Description: {motion_pattern.get('description', '')}\n"
            
            sudden_movements = motion_analysis.get("sudden_movements", [])
            if sudden_movements:
                motion_context += f"- Sudden Movements: {len(sudden_movements)} detected\n"
    
    prompt = (
        "You are an expert crime analysis assistant reviewing automated video surveillance results.\n\n"
        "You are given comprehensive analysis data from multiple AI models including:\n"
        "- Object detection (persons, weapons, valuables, vehicles)\n"
        "- Action recognition (fighting, stealing, vandalism, etc.)\n"
        "- Crime pattern analysis (weapon threats, violence, theft patterns)\n"
        "- Motion analysis (sudden movements, chase sequences)\n"
        "- Event detection (suspicious activities, temporal patterns)\n\n"
        f"{crime_context}"
        f"{motion_context}\n\n"
        "**Your Tasks:**\n"
        "1. Provide a clear, factual description (3-5 sentences) of what is happening in the video based on the analysis.\n"
        "2. If criminal activity is detected:\n"
        "   - Specify the type of crime (assault, theft, vandalism, etc.)\n"
        "   - Note severity level and confidence\n"
        "   - List specific evidence (weapons seen, violent actions, theft patterns)\n"
        "3. If the severity is HIGH or CRITICAL:\n"
        "   - Provide IMMEDIATE safety recommendations\n"
        "   - Emphasize NOT to intervene directly if dangerous\n"
        "   - Recommend calling emergency services (911/112)\n"
        "4. If the severity is MEDIUM or LOW:\n"
        "   - Suggest appropriate response (monitor, contact security, etc.)\n"
        "5. If NO criminal activity detected:\n"
        "   - State clearly that the scene appears safe\n"
        "   - Briefly describe what is happening\n\n"
        "6. Add appropriate Indian Penal Code (IPC) sections if relevant.\n"
        "7. Include a disclaimer about automated analysis.\n\n"
        f"**Input Analysis Data:**\n{json.dumps(summary, indent=2)}\n\n"
        "**Output Format (JSON):**\n"
        "{\n"
        '  "description": "Clear description of the scene and activities",\n'
        '  "crime_detected": true/false,\n'
        '  "crime_type": "assault/theft/vandalism/none/etc",\n'
        '  "severity": "critical/high/medium/low/safe",\n'
        '  "evidence": ["list of specific evidence"],\n'
        '  "safety_recommendations": ["immediate steps to take"],\n'
        '  "ipc_suggestions": [{"section": "IPC 307", "reason": "attempt to murder"}],\n'
        '  "disclaimer": "standard disclaimer text"\n'
        "}\n"
    )

    # TODO: Replace with actual Gemini API call
    # For now, return structured response based on crime analysis
    
    if crime_detected:
        evidence = []
        if crime_report.get("weapon_threat_analysis", {}).get("detected"):
            evidence.append("Weapon detected in video")
        if crime_report.get("violence_analysis", {}).get("detected"):
            evidence.append(f"Violent actions detected with {crime_report['violence_analysis']['intensity_level']} intensity")
        if crime_report.get("theft_analysis", {}).get("detected"):
            evidence.append(f"Theft patterns detected with {crime_report['theft_analysis']['theft_probability']*100:.0f}% probability")
        
        recommendations = []
        if severity == "critical":
            recommendations = [
                "⚠️ IMMEDIATE ACTION REQUIRED",
                "Call emergency services (911/112) immediately",
                "Do NOT intervene directly - maintain safe distance",
                "Evacuate to a secure location if nearby",
                "Preserve any evidence and provide video to authorities"
            ]
        elif severity == "high":
            recommendations = [
                "Contact law enforcement immediately",
                "Monitor situation from safe distance",
                "Do not confront individuals involved",
                "Alert security personnel if available",
                "Document additional observations safely"
            ]
        else:
            recommendations = [
                "Continue monitoring the situation",
                "Contact security or local police if activity escalates",
                "Keep safe distance from the area",
                "Document time and location of incident"
            ]
        
        return {
            "description": f"Automated analysis has detected potential criminal activity with {severity} severity. "
                          f"{len(indicators)} crime indicators were identified through multi-modal AI analysis. "
                          f"This includes object detection, action recognition, and behavioral pattern analysis.",
            "crime_detected": True,
            "crime_type": indicators[0]["type"] if indicators else "unknown",
            "severity": severity,
            "evidence": evidence,
            "safety_recommendations": recommendations,
            "ipc_suggestions": _get_ipc_suggestions(indicators),
            "disclaimer": (
                "This analysis is generated by automated AI systems (YOLOv8x, MoViNet A2, and specialized "
                "crime pattern analyzers). While these systems are highly accurate, this is not definitive "
                "proof of criminal activity and should not replace human judgment or legal proceedings. "
                "Always consult law enforcement and legal professionals for official assessments."
            ),
        }
    else:
        return {
            "description": (
                "Automated video analysis using advanced AI models (YOLOv8x object detection, "
                "MoViNet A2 action recognition, motion analysis) has been completed. "
                "No significant criminal activity or unlawful behavior was detected in this video. "
                "The scene appears to show normal, lawful activity."
            ),
            "crime_detected": False,
            "crime_type": "none",
            "severity": "safe",
            "evidence": [],
            "safety_recommendations": ["No immediate action required", "Continue normal activities"],
            "ipc_suggestions": [],
            "disclaimer": (
                "This analysis is generated by automated AI systems. The absence of detected "
                "criminal activity does not guarantee that no crime occurred, as AI systems have "
                "limitations. Human review and judgment should be used for final assessments."
            ),
        }


def _get_ipc_suggestions(indicators: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Suggest relevant IPC sections based on crime indicators.
    """
    ipc_suggestions = []
    
    for indicator in indicators:
        crime_type = indicator.get("type", "")
        
        if "weapon" in crime_type:
            ipc_suggestions.append({
                "section": "IPC 307",
                "reason": "Attempt to murder (if weapon used against person)"
            })
            ipc_suggestions.append({
                "section": "IPC 506",
                "reason": "Criminal intimidation with weapon"
            })
        
        if "assault" in crime_type or "violent" in crime_type:
            ipc_suggestions.append({
                "section": "IPC 323",
                "reason": "Voluntarily causing hurt"
            })
            ipc_suggestions.append({
                "section": "IPC 325",
                "reason": "Voluntarily causing grievous hurt"
            })
        
        if "robbery" in crime_type or "theft" in crime_type:
            ipc_suggestions.append({
                "section": "IPC 379",
                "reason": "Theft"
            })
            ipc_suggestions.append({
                "section": "IPC 392",
                "reason": "Robbery"
            })
        
        if "vandal" in crime_type or "damage" in crime_type:
            ipc_suggestions.append({
                "section": "IPC 427",
                "reason": "Mischief causing damage"
            })
    
    # Remove duplicates
    seen = set()
    unique_suggestions = []
    for suggestion in ipc_suggestions:
        key = suggestion["section"]
        if key not in seen:
            seen.add(key)
            unique_suggestions.append(suggestion)
    
    return unique_suggestions
