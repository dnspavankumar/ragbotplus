#!/usr/bin/env python3
"""
Gmail RAG Assistant - Install Missing Packages
Quick script to install the specific packages that are failing
"""

import subprocess
import sys
import time

def install_package(package_name, pip_name=None):
    """Install a single package with error handling"""
    install_name = pip_name if pip_name else package_name
    print(f"📦 Installing {package_name}...")
    
    try:
        # Use --user flag to avoid permission issues
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--user', install_name
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {package_name} installed successfully")
            return True
        else:
            print(f"❌ Failed to install {package_name}")
            print(f"   Error: {result.stderr}")
            
            # Try without --user flag
            print(f"   Retrying {package_name} without --user flag...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', install_name
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ {package_name} installed successfully (retry)")
                return True
            else:
                print(f"❌ {package_name} installation failed completely")
                return False
                
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout installing {package_name}")
        return False
    except Exception as e:
        print(f"❌ Error installing {package_name}: {e}")
        return False

def test_import(package_name, import_name):
    """Test if a package can be imported"""
    try:
        __import__(import_name)
        print(f"✅ {package_name} import test passed")
        return True
    except ImportError as e:
        print(f"❌ {package_name} import test failed: {e}")
        return False

def main():
    """Install the missing packages"""
    print("=" * 60)
    print("📧 Gmail RAG Assistant - Missing Package Installer")
    print("   Installing specific packages that failed...")
    print("=" * 60)
    
    # List of packages with their pip install names and import names
    packages = [
        ("beautifulsoup4", "beautifulsoup4", "bs4"),
        ("python-dateutil", "python-dateutil", "dateutil"),
        ("python-dotenv", "python-dotenv", "dotenv"),
        ("faiss-cpu", "faiss-cpu", "faiss"),
        ("SpeechRecognition", "SpeechRecognition", "speech_recognition"),
        ("google-api-python-client", "google-api-python-client", "googleapiclient")
    ]
    
    print("🔧 First, let's upgrade pip...")
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
        ], check=True, capture_output=True)
        print("✅ pip upgraded")
    except:
        print("⚠️  Could not upgrade pip (continuing anyway)")
    
    print("\n📦 Installing missing packages...")
    
    success_count = 0
    total_count = len(packages)
    
    for display_name, pip_name, import_name in packages:
        print(f"\n--- Installing {display_name} ---")
        
        if install_package(display_name, pip_name):
            # Wait a moment then test import
            time.sleep(1)
            if test_import(display_name, import_name):
                success_count += 1
            else:
                print(f"⚠️  {display_name} installed but import failed")
        
        time.sleep(0.5)  # Small delay between installations
    
    print("\n" + "=" * 60)
    print(f"📊 Installation Summary: {success_count}/{total_count} packages successful")
    
    if success_count == total_count:
        print("🎉 All packages installed successfully!")
        print("\nYou can now run: python main.py")
    elif success_count > 0:
        print("⚠️  Some packages installed successfully, others may need manual installation")
        print("\nFor any remaining failures, try:")
        print("   pip install --upgrade <package-name>")
        print("   or")
        print("   pip install --user <package-name>")
    else:
        print("❌ No packages were installed successfully")
        print("\nTry installing manually:")
        for display_name, pip_name, _ in packages:
            print(f"   pip install {pip_name}")
    
    print("\n📧 Next steps after successful installation:")
    print("1. Get Gmail API credentials (credentials.json)")
    print("2. Get Groq API key from console.groq.com")
    print("3. Run: python main.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed with error: {e}")
        sys.exit(1)