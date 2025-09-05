#!/usr/bin/env python3
"""
Gmail RAG Assistant - Setup Script
This script helps install and verify all required dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def upgrade_pip():
    """Upgrade pip to latest version"""
    print("📦 Upgrading pip...")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
        ], check=True, capture_output=True)
        print("✅ pip upgraded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Could not upgrade pip: {e}")
        return True  # Non-critical, continue anyway

def install_core_dependencies():
    """Install core dependencies one by one"""
    print("📦 Installing core dependencies...")
    
    # Core packages that should be installed first
    core_packages = [
        'numpy>=1.21.0',
        'beautifulsoup4>=4.11.0',
        'python-dateutil>=2.8.0',
        'python-dotenv>=0.19.0',
        'requests>=2.25.0',
        'certifi>=2021.5.25'
    ]
    
    for package in core_packages:
        print(f"   Installing {package}...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}")
            return False
    
    print("✅ Core dependencies installed")
    return True

def install_ai_dependencies():
    """Install AI and ML dependencies"""
    print("🤖 Installing AI dependencies...")
    
    ai_packages = [
        'faiss-cpu>=1.7.0',
        'groq>=0.4.0',
        'langchain>=0.0.200'
    ]
    
    for package in ai_packages:
        print(f"   Installing {package}...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], check=True, capture_output=True, timeout=300)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}")
            print("   You may need to install it manually later")
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout installing {package} - continuing...")
    
    print("✅ AI dependencies installation attempted")
    return True

def install_google_dependencies():
    """Install Google API dependencies"""
    print("📧 Installing Google API dependencies...")
    
    google_packages = [
        'google-auth>=2.0.0',
        'google-auth-oauthlib>=0.4.0',
        'google-api-python-client>=2.0.0',
        'google-auth-httplib2>=0.1.0'
    ]
    
    for package in google_packages:
        print(f"   Installing {package}...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}")
            return False
    
    print("✅ Google API dependencies installed")
    return True

def install_web_dependencies():
    """Install web framework dependencies"""
    print("🌐 Installing web framework dependencies...")
    
    web_packages = [
        'Flask>=2.0.0',
        'Flask-CORS>=3.0.0'
    ]
    
    for package in web_packages:
        print(f"   Installing {package}...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}")
            return False
    
    print("✅ Web framework dependencies installed")
    return True

def install_optional_dependencies():
    """Install optional dependencies"""
    print("🔊 Installing optional dependencies...")
    
    optional_packages = [
        'pyttsx3>=2.90',
        'SpeechRecognition>=3.8.0',
        'tzlocal>=4.0',
        'chime>=0.7.0',
        'psutil>=5.8.0'
    ]
    
    for package in optional_packages:
        print(f"   Installing {package}...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Could not install {package} (optional)")
    
    print("✅ Optional dependencies installation completed")
    return True

def install_all_at_once():
    """Try installing all dependencies from requirements.txt"""
    print("📦 Attempting to install all dependencies at once...")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True, capture_output=True, timeout=600)
        print("✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Batch installation failed, trying individual packages...")
        return False
    except subprocess.TimeoutExpired:
        print("⏰ Installation timeout, trying individual packages...")
        return False

def verify_installation():
    """Verify that key packages can be imported"""
    print("🔍 Verifying installation...")
    
    test_imports = [
        ('beautifulsoup4', 'bs4'),
        ('python-dateutil', 'dateutil'),
        ('python-dotenv', 'dotenv'),
        ('requests', 'requests'),
        ('Flask', 'flask'),
        ('Flask-CORS', 'flask_cors'),
        ('google-api-python-client', 'googleapiclient'),
        ('google-auth', 'google.auth'),
        ('numpy', 'numpy')
    ]
    
    failed_imports = []
    
    for package_name, import_name in test_imports:
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name}")
            failed_imports.append(package_name)
    
    # Test optional packages
    optional_imports = [
        ('faiss-cpu', 'faiss'),
        ('groq', 'groq'),
        ('pyttsx3', 'pyttsx3'),
        ('SpeechRecognition', 'speech_recognition')
    ]
    
    print("\n🔊 Optional packages:")
    for package_name, import_name in optional_imports:
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ⚠️  {package_name} (optional)")
    
    if failed_imports:
        print(f"\n❌ Failed to verify: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ All core dependencies verified successfully!")
        return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("📧 Gmail RAG Assistant - Setup Script")
    print("   Installing Python dependencies...")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Upgrade pip
    upgrade_pip()
    
    # Try batch installation first
    if install_all_at_once():
        if verify_installation():
            print("\n🎉 Setup completed successfully!")
            print("\nNext steps:")
            print("1. Get Gmail API credentials (credentials.json)")
            print("2. Get Groq API key")
            print("3. Run: python main.py")
            return
    
    # If batch failed, try individual packages
    print("\n🔧 Installing packages individually...")
    
    success = True
    success &= install_core_dependencies()
    success &= install_google_dependencies()
    success &= install_web_dependencies()
    success &= install_ai_dependencies()
    success &= install_optional_dependencies()
    
    if success:
        print("\n🔍 Final verification...")
        if verify_installation():
            print("\n🎉 Setup completed successfully!")
            print("\nNext steps:")
            print("1. Get Gmail API credentials (credentials.json)")
            print("2. Get Groq API key")
            print("3. Run: python main.py")
        else:
            print("\n⚠️  Setup completed with some issues.")
            print("   The application may still work with core features.")
    else:
        print("\n❌ Setup encountered errors.")
        print("   Please install missing packages manually:")
        print("   pip install <package-name>")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)