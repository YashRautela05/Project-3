import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(ROOT_DIR, "uploads")
MAX_FILE_SIZE = 100 * 1024 * 1024
ALLOWED_EXTENSIONS = {
    "video": [".mp4", ".avi", ".mov", ".mkv", ".webm"],
    "audio": [".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"],
}

WHISPER_MODEL = "small"
DETR_MODEL = "facebook/detr-resnet-50"
BLIP_MODEL = "Salesforce/blip-image-captioning-base"
GEMINI_MODEL = "gemini-1.5-flash"

CRIME_ANALYSIS_PROMPT = """
Analyze this video and its audio content carefully. 

**Your Task:**
1. Describe the sequence of events in the video
2. Identify if any criminal activity is occurring, such as:
   - Assault or violence
   - Theft, robbery, or snatching
   - ATM fraud or card skimming
   - Property damage or vandalism
   - Illegal weapon display or use
   - Drug-related activities
   - Harassment or stalking
   - Breaking and entering
   - Other suspicious or illegal activities

3. If criminal activity is identified:
   - Provide immediate, concise, and SAFE steps a person witnessing this should take
   - Emphasize NOT to intervene directly if there's danger
   - Suggest calling appropriate authorities (911, police, etc.)
   - Include any relevant details that would help law enforcement

4. If no criminal activity is detected:
   - State "No criminal activity detected"
   - Provide a brief description of what is happening
   - Keep the response concise and clear

**Important Safety Guidelines:**
- Always prioritize personal safety
- Do not attempt to confront dangerous situations
- Contact local authorities for real emergencies
- This analysis is for informational purposes only

**Output Format (Keep responses concise):**
- Event Description: [Brief description of what's happening]
- Criminal Activity Detected: [Yes/No]
- If Yes: [Type of crime and immediate safety steps]
- If No: [Brief description of normal activity - keep this short]
- Safety Recommendations: [Specific steps for witnesses]
"""

DATABASE_URL = "sqlite:///./crime_ai.db"
