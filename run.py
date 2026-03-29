"""
🚀 ONE-CLICK LAUNCHER
====================
Runs backend + opens frontend automatically
"""

import subprocess
import time
import webbrowser
import os
import sys

def check_requirements():
    """Check if required packages are installed"""
    required = ['fastapi', 'uvicorn', 'transformers', 'torch']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n💡 Install them with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def check_model():
    """Check if model exists"""
    model_path = "./abuse_detector_model2"
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found at: {model_path}")
        print("\n💡 Make sure your model folder is in the same directory as this script")
        print("   Expected structure:")
        print("   ├── run.py")
        print("   ├── backend.py")
        print("   ├── frontend.html")
        print("   └── abuse_detector_model2/")
        print("       ├── config.json")
        print("       ├── pytorch_model.bin")
        print("       └── ...")
        return False
    
    return True

def main():
    print("="*70)
    print("🚀 ABUSE DETECTION APP - LAUNCHER")
    print("="*70)
    
    # Check requirements
    print("\n1️⃣ Checking requirements...")
    if not check_requirements():
        sys.exit(1)
    print("   ✅ All packages installed")
    
    # Check model
    print("\n2️⃣ Checking model...")
    if not check_model():
        sys.exit(1)
    print("   ✅ Model found")
    
    # Start backend
    print("\n3️⃣ Starting backend API...")
    print("   📍 URL: http://localhost:8000")
    print("   📖 API Docs: http://localhost:8000/docs")
    print("   🎨 Frontend: http://localhost:8000/app")
    
    try:
        # Run backend
        subprocess.run([sys.executable, "backend.py"])
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        print("="*70)

if __name__ == "__main__":
    main()
