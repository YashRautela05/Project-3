# 🤖 Gemini API Integration Guide

## Overview
Complete integration of Google Gemini 1.5 Flash for intelligent crime analysis with legal and safety guidance.

---

## What Gemini Provides

### 1. **Intelligent Analysis**
- Human-readable crime description
- Crime type classification
- Severity assessment with confidence levels
- Evidence summary from AI detections

### 2. **Legal Information** 🏛️
- **Indian Penal Code (IPC) sections** applicable to detected crimes
- **Offense descriptions**
- **Potential punishments** (imprisonment duration, fines)
- **Severity factors** (aggravating/mitigating circumstances)

### 3. **Safety Guidance** 🛡️
- **How to stay safe** (6-8 actionable points)
- **Immediate actions** (what to do RIGHT NOW)
- Situation-specific advice based on severity
- Bystander safety vs intervention guidance

### 4. **Reporting Assistance** 📞
- Should you report? (Yes/No)
- Urgency level (immediate/high/normal/low)
- Who to contact (Police/Emergency/Security)
- What information to provide

---

## Setup Instructions

### Step 1: Get Gemini API Key

1. Visit https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

### Step 2: Add to Environment

**Option A: Using docker-compose.yml**
```yaml
services:
  worker:
    environment:
      - GOOGLE_API_KEY=your_api_key_here
```

**Option B: Using .env file**
```bash
# .env
GOOGLE_API_KEY=your_api_key_here
```

Then reference in docker-compose.yml:
```yaml
services:
  worker:
    env_file:
      - .env
```

### Step 3: Rebuild Containers

```bash
docker-compose down
docker-compose build
docker-compose up -d
```

### Step 4: Verify Installation

```bash
# Check if API key is set
docker exec crime_ai_worker env | grep GOOGLE_API_KEY

# Check if package is installed
docker exec crime_ai_worker pip show google-generativeai
```

---

## Response Structure

### Full Gemini Output

```json
{
  "gemini_output": {
    "description": "A violent altercation was detected involving two individuals...",
    
    "crime_detected": true,
    
    "crime_type": "assault",
    
    "severity": "high",
    
    "confidence_level": "high",
    
    "evidence_summary": [
      "Physical violence detected with high confidence (87%)",
      "Multiple punching and kicking actions recognized",
      "Two persons involved in sustained physical altercation",
      "High-intensity motion patterns indicating struggle"
    ],
    
    "safety_recommendations": [
      "Do NOT intervene directly in physical altercations",
      "Call law enforcement immediately (911 or local police)",
      "Move to a safe distance from the incident",
      "If nearby, alert building security or other authorities",
      "Preserve video evidence on secure device"
    ],
    
    "legal_information": {
      "ipc_sections": [
        {
          "section": "IPC 323",
          "offense": "Voluntarily causing hurt",
          "punishment": "Imprisonment up to 1 year, or fine up to ₹1000, or both"
        },
        {
          "section": "IPC 325",
          "offense": "Voluntarily causing grievous hurt",
          "punishment": "Imprisonment up to 7 years and liable to fine"
        }
      ],
      "possible_punishment": "Based on the severity of injuries and circumstances, the accused could face imprisonment ranging from 1 to 7 years. If weapons were involved or if the assault resulted in serious injuries, charges under IPC 324 (hurt with dangerous weapons) could also apply, increasing the sentence.",
      "severity_factors": [
        "Use of weapons increases severity",
        "Extent of injuries caused",
        "Whether assault was premeditated",
        "Number of attackers vs victims",
        "Age and vulnerability of victim"
      ]
    },
    
    "how_to_stay_safe": [
      "Maintain at least 10-15 feet distance from any physical altercation",
      "Do not attempt to separate fighting individuals",
      "If indoors, exit to a secure location immediately",
      "Call emergency services (911/112) and provide location details",
      "Document incident with video/photos only if safe to do so",
      "Alert others in the area to evacuate or stay clear",
      "Identify yourself to authorities as a witness only if safe",
      "Do not post video on social media before reporting to police"
    ],
    
    "immediate_actions": [
      "Call police immediately (dial 100 in India or 911)",
      "Move to safe location away from the incident",
      "If someone is injured, call ambulance (dial 108/102 in India)",
      "Do NOT engage with the individuals involved",
      "Secure the video footage on your device"
    ],
    
    "reporting_guidance": {
      "should_report": true,
      "urgency": "immediate",
      "who_to_contact": "Local police station or dial 100 (India) / 911 (US)",
      "what_to_report": "Time and location of incident, number of people involved, nature of violence observed, whether weapons were visible, if anyone appeared injured, and that you have video evidence"
    },
    
    "disclaimer": "This analysis is generated by automated AI systems analyzing video footage. While our AI models (YOLOv8x object detection, MoViNet A2 action recognition, and Google Gemini analysis) are highly accurate, this should not be considered definitive proof of criminal activity. Legal determinations should only be made by qualified law enforcement and judicial authorities. Always prioritize your personal safety and consult with legal professionals for official assessments."
  }
}
```

---

## Example Responses by Severity

### CRITICAL Severity

```json
{
  "crime_type": "armed_assault",
  "severity": "critical",
  "immediate_actions": [
    "⚠️ CALL 911/112 IMMEDIATELY - Active weapon threat",
    "EVACUATE the area immediately if nearby",
    "DO NOT approach or attempt to intervene",
    "Alert others to danger and help them evacuate",
    "Take cover if unable to evacuate"
  ],
  "legal_information": {
    "ipc_sections": [
      {
        "section": "IPC 307",
        "offense": "Attempt to murder",
        "punishment": "Imprisonment up to 10 years and fine; if hurt caused, imprisonment for life"
      }
    ]
  }
}
```

### HIGH Severity

```json
{
  "crime_type": "robbery",
  "severity": "high",
  "immediate_actions": [
    "Call police immediately (dial 100/911)",
    "Monitor situation from safe distance",
    "Do not confront individuals",
    "Note descriptions of suspects if safe",
    "Preserve video evidence"
  ],
  "legal_information": {
    "ipc_sections": [
      {
        "section": "IPC 392",
        "offense": "Robbery",
        "punishment": "Rigorous imprisonment up to 10 years and fine"
      }
    ]
  }
}
```

### MEDIUM Severity

```json
{
  "crime_type": "vandalism",
  "severity": "medium",
  "immediate_actions": [
    "Continue monitoring the situation",
    "Contact security or building management",
    "Document additional details if safe",
    "Report to police if activity continues"
  ],
  "legal_information": {
    "ipc_sections": [
      {
        "section": "IPC 427",
        "offense": "Mischief causing damage",
        "punishment": "Imprisonment up to 2 years, or fine, or both"
      }
    ]
  }
}
```

### SAFE (No Crime)

```json
{
  "crime_type": "none",
  "severity": "safe",
  "description": "Normal activity detected. No criminal behavior or threats identified in the video footage.",
  "immediate_actions": [
    "No action required",
    "Continue normal activities"
  ],
  "legal_information": {
    "ipc_sections": []
  }
}
```

---

## Fallback Behavior

### When Gemini is NOT Available:

**Scenarios:**
- No `GOOGLE_API_KEY` set
- API key invalid/expired
- Network error
- Quota exceeded
- Package not installed

**Fallback Response:**
```json
{
  "gemini_output": {
    "description": "Automated analysis generated (Gemini unavailable)",
    "crime_detected": true/false,
    "crime_type": "...",
    "severity": "...",
    "evidence": ["Basic evidence from AI"],
    "safety_recommendations": ["Generic safety advice"],
    "ipc_suggestions": [{"section": "...", "reason": "..."}],
    "disclaimer": "..."
  }
}
```

**Note:** Fallback still includes:
- Basic IPC section suggestions
- Safety recommendations based on severity
- Evidence from AI analysis
- Structured crime classification

---

## Monitoring Gemini Usage

### Check Logs

```bash
# Real-time logs
docker-compose logs -f crime_ai_worker | grep -i gemini

# Look for:
# - "Calling Gemini API..."
# - "Gemini response received"
# - "Gemini API error: ..."
# - "Using fallback response"
```

### Verify API Calls

```bash
# Check if Gemini is being called
docker-compose logs crime_ai_worker | grep "Calling Gemini"

# Check for errors
docker-compose logs crime_ai_worker | grep "Gemini API error"
```

---

## Cost Considerations

### Gemini 1.5 Flash Pricing

**Free Tier:**
- 15 requests per minute
- 1 million requests per day
- Sufficient for most surveillance use cases

**Paid Tier:**
- Much higher quotas
- $0.00001875 per 1K characters input
- Very affordable for this use case

### Typical Usage

**Per video analysis:**
- Input: ~2-5K characters (analysis data)
- Output: ~1-3K characters (Gemini response)
- Cost: <$0.0001 per video

**For 1000 videos/month:**
- Cost: <$0.10/month (essentially free)

---

## Troubleshooting

### Issue: "Using fallback response"

**Cause:** Gemini API not available

**Solutions:**
1. Check API key is set:
   ```bash
   docker exec crime_ai_worker env | grep GOOGLE_API_KEY
   ```

2. Verify API key is valid:
   - Go to https://makersuite.google.com/app/apikey
   - Check key status

3. Check package installed:
   ```bash
   docker exec crime_ai_worker pip show google-generativeai
   ```

4. Rebuild if package missing:
   ```bash
   docker-compose build
   ```

### Issue: "API quota exceeded"

**Cause:** Too many requests

**Solutions:**
1. Wait for quota reset (usually per minute)
2. Upgrade to paid tier
3. System will use fallback automatically

### Issue: Generic responses

**Check:**
- Is `legal_information` populated?
- Does `how_to_stay_safe` have specific advice?
- Is `description` detailed or generic?

**If generic:**
- Gemini may not be responding
- Check logs for API errors
- Verify API key

---

## Best Practices

### 1. **Always Set API Key in Production**
- Real Gemini responses are much better
- Legal information is more accurate
- Safety advice is situation-specific

### 2. **Monitor Quota Usage**
- Check Gemini console for usage
- Set up alerts for quota limits
- Plan for growth

### 3. **Handle Errors Gracefully**
- System falls back automatically
- Users still get useful information
- No processing failures

### 4. **Keep Responses Cached**
- Redis caches video results
- Avoids duplicate Gemini calls
- Saves quota and money

### 5. **Review Gemini Output**
- Periodically check quality
- Verify legal information accuracy
- Update prompts if needed

---

## Privacy & Security

### Data Sent to Gemini:
- ✅ Structured analysis results (objects, actions, events)
- ✅ Crime pattern analysis summaries
- ✅ Motion analysis data
- ❌ NO video frames
- ❌ NO personal identifying information
- ❌ NO raw video data

### Data Retention:
- Gemini processes request then discards
- No long-term storage by Google
- Your video stays on your server
- Results cached in your Redis

---

## Future Enhancements

### Possible Additions:
1. **Multiple Gemini Models** (Pro vs Flash)
2. **Custom Legal Frameworks** (other countries)
3. **Multilingual Responses**
4. **Detailed Evidence Chains**
5. **Witness Statement Generation**

---

## Summary

✅ **Real Gemini API integration**
✅ **Legal punishment details** (IPC sections)
✅ **Safety recommendations** (how to stay safe)
✅ **Reporting guidance** (who to call, what to say)
✅ **Fallback system** (works without API key)
✅ **Privacy-focused** (no video sent to Gemini)
✅ **Cost-effective** (<$0.0001 per video)

Your Crime-AI system now provides **comprehensive legal and safety guidance** for every detected incident! 🚀
