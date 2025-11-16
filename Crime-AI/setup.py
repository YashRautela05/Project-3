#!/usr/bin/env python3
"""
Setup script for Crime-AI project
This script helps users configure the project and get started
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "fastapi", "uvicorn", "celery", "redis", "whisper", 
        "opencv-python", "torch", "transformers", "PIL", 
        "numpy", "ffmpeg-python", "google-generativeai"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n📦 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def setup_environment():
    """Set up environment variables"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("🔧 Creating .env file...")
    
    env_content = """# Google Gemini API Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: Redis Configuration (if not using default)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Optional: Server Configuration
HOST=0.0.0.0
PORT=8000
"""
    
    try:
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("📝 Please edit .env file and add your Gemini API key")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_redis():
    """Check if Redis is accessible"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
        return True
    except Exception as e:
        print("❌ Redis is not running")
        print("📋 To start Redis:")
        print("  - Windows: redis-server")
        print("  - macOS: brew services start redis")
        print("  - Linux: sudo systemctl start redis")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["uploads", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    print("🎯 Crime-AI Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return
    
    print("\n📦 Checking dependencies...")
    # if not check_dependencies():
    #     print("\n❌ Please install missing dependencies first")
    #     return 
    
    print("\n📁 Creating directories...")
    create_directories()
    
    print("\n🔧 Setting up environment...")
    setup_environment()
    
    print("\n🔍 Checking Redis...")
    check_redis()
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your Gemini API key")
    print("2. Start Redis server")
    print("3. Run: python start.py")
    print("4. Visit: http://localhost:8000")

if __name__ == "__main__":
    main() 