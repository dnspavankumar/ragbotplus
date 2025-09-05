#!/usr/bin/env python3
"""
Gmail RAG Assistant Launch Script
This script ensures the application starts properly with all dependencies
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'PyQt6',
        'beautifulsoup4',
        'numpy',
        'faiss_cpu',
        'groq',
        'google_api_python_client',
        'pyttsx3',
        'speech_recognition'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'faiss_cpu':
                import faiss
            elif package == 'google_api_python_client':
                import googleapiclient
            elif package == 'speech_recognition':
                import speech_recognition
            else:
                __import__(package)
            print(f"✅ {package} - installed")
        except ImportError:
            print(f"❌ {package} - missing")
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(missing_packages):
    """Install missing dependencies"""
    if not missing_packages:
        return True
    
    print(f"\n🔧 Installing missing packages: {', '.join(missing_packages)}")
    
    try:
        # Use pip to install missing packages
        cmd = [sys.executable, '-m', 'pip', 'install'] + missing_packages
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("Please install them manually using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False

def check_credentials():
    """Check if required credentials files exist"""
    credentials_file = Path("credentials.json")
    
    if not credentials_file.exists():
        print("⚠️  Warning: credentials.json not found")
        print("You'll need to:")
        print("1. Go to Google Cloud Console")
        print("2. Create a new project or select existing one")
        print("3. Enable Gmail API")
        print("4. Create credentials (OAuth 2.0)")
        print("5. Download and rename to 'credentials.json'")
        print("6. Place it in the same directory as this script")
        return False
    else:
        print("✅ credentials.json found")
        return True

def check_environment():
    """Check environment setup"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠️  Warning: .env file not found")
        print("Creating .env template...")
        
        with open(".env", "w") as f:
            f.write("# Gmail RAG Assistant Environment Variables\n")
            f.write("# Get your Groq API key from: https://console.groq.com/\n")
            f.write("GROQ_API_KEY=your_groq_api_key_here\n")
            f.write("\n# Optional: Customize other settings\n")
            f.write("# GROQ_MODEL=deepseek-r1-distill-llama-70b\n")
            f.write("# TEMPERATURE=0.3\n")
        
        print("📝 Created .env template")
        print("Please edit .env and add your Groq API key")
        return False
    else:
        # Check if GROQ_API_KEY is set
        from dotenv import load_dotenv
        load_dotenv()
        
        if not os.getenv('GROQ_API_KEY'):
            print("⚠️  Warning: GROQ_API_KEY not set in .env file")
            print("Please add your Groq API key to the .env file")
            return False
        else:
            print("✅ Environment variables configured")
            return True

def main():
    """Main launch function"""
    print("🚀 Gmail RAG Assistant - Launch Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        install_choice = input(f"\nInstall missing packages? (y/n): ").lower().strip()
        if install_choice == 'y':
            if not install_dependencies(missing_packages):
                sys.exit(1)
        else:
            print("❌ Cannot proceed without required dependencies")
            sys.exit(1)
    
    # Check credentials
    print("\n🔐 Checking credentials...")
    credentials_ok = check_credentials()
    
    # Check environment
    print("\n🌍 Checking environment...")
    env_ok = check_environment()
    
    # Final check
    if not credentials_ok or not env_ok:
        print("\n⚠️  Setup incomplete. Please resolve the issues above before running.")
        input("Press Enter to continue anyway or Ctrl+C to exit...")
    
    # Launch the application
    print("\n🎯 Launching Gmail RAG Assistant...")
    print("-" * 50)
    
    try:
        # Add current directory to Python path
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        # Import and run the main application
        from main import main as app_main
        app_main()
        
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
    except Exception as e:
        print(f"\n❌ Application error: {str(e)}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()