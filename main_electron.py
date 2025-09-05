#!/usr/bin/env python3
"""
Gmail RAG Assistant - Electron Edition Main Launcher
This script launches both the Python backend server and the Electron frontend
"""

import os
import sys
import subprocess
import time
import threading
import signal
import json
import webbrowser
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    missing_packages = []
    # Map package install names to their import names
    required_packages = {
        'flask': 'flask',
        'flask_cors': 'flask_cors', 
        'beautifulsoup4': 'bs4',
        'python-dateutil': 'dateutil',
        'python-dotenv': 'dotenv',
        'faiss-cpu': 'faiss',
        'numpy': 'numpy',
        'pyttsx3': 'pyttsx3',
        'SpeechRecognition': 'speech_recognition',
        'tzlocal': 'tzlocal',
        'groq': 'groq',
        'langchain': 'langchain',
        'chime': 'chime',
        'google-auth-oauthlib': 'google_auth_oauthlib',
        'google-api-python-client': 'googleapiclient',
        'google-auth-httplib2': 'google_auth_httplib2',
        'psutil': 'psutil',
        'requests': 'requests'
    }
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ Missing Python packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All Python dependencies found")
    return True

def check_credentials():
    """Check if Gmail API credentials are available"""
    print("🔑 Checking Gmail credentials...")
    
    credentials_file = current_dir / 'credentials.json'
    if not credentials_file.exists():
        print("⚠️  credentials.json not found")
        print("   Please download it from Google Cloud Console and place it in the app directory")
        return False
    
    print("✅ Gmail credentials found")
    return True

def check_api_key():
    """Check if Groq API key is configured"""
    print("🔑 Checking Groq API key...")
    
    # Check .env file
    env_file = current_dir / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'GROQ_API_KEY=' in content:
                print("✅ Groq API key found in .env file")
                return True
    
    # Check environment variable
    if os.getenv('GROQ_API_KEY'):
        print("✅ Groq API key found in environment")
        return True
    
    print("⚠️  Groq API key not found")
    print("   You can set it later in the Settings page")
    return True  # Non-blocking, can be set later

def check_node_and_electron():
    """Check if Node.js and Electron are available"""
    print("🔍 Checking Node.js and Electron...")
    
    try:
        # Check Node.js with the exact same approach that worked in diagnostic
        node_found = False
        npm_found = False
        
        # Use the successful diagnostic approach - shell=True is crucial for Windows
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=10, shell=True)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                print(f"✅ Node.js found: {node_version}")
                node_found = True
            else:
                print(f"❌ Node command failed with return code: {result.returncode}")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
        except Exception as e:
            print(f"❌ Node.js check exception: {e}")
            # Try with .exe extension as fallback
            try:
                result = subprocess.run(['node.exe', '--version'], 
                                      capture_output=True, text=True, timeout=10, shell=True)
                if result.returncode == 0:
                    node_version = result.stdout.strip()
                    print(f"✅ Node.js found: {node_version}")
                    node_found = True
            except Exception as e2:
                print(f"❌ Node.exe check also failed: {e2}")
        
        if not node_found:
            print("❌ Node.js not detected")
            print("   This is unexpected since the diagnostic showed Node.js is working...")
            print("   Possible causes:")
            print("   1. Different subprocess environment")
            print("   2. Python PATH isolation")
            print("   3. Process execution context difference")
            return False
        
        # Check npm with the same successful approach
        try:
            result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True, timeout=10, shell=True)
            if result.returncode == 0:
                npm_version = result.stdout.strip()
                print(f"✅ npm found: v{npm_version}")
                npm_found = True
            else:
                print(f"❌ npm command failed with return code: {result.returncode}")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
        except Exception as e:
            print(f"❌ npm check exception: {e}")
            # Try with .cmd extension as fallback
            try:
                result = subprocess.run(['npm.cmd', '--version'], 
                                      capture_output=True, text=True, timeout=10, shell=True)
                if result.returncode == 0:
                    npm_version = result.stdout.strip()
                    print(f"✅ npm found: v{npm_version}")
                    npm_found = True
            except Exception as e2:
                print(f"❌ npm.cmd check also failed: {e2}")
        
        if not npm_found:
            print("❌ npm not detected")
            return False
        
        # Check if package.json exists
        package_json = current_dir / 'package.json'
        if not package_json.exists():
            print("❌ package.json not found")
            return False
        
        # Check if node_modules exists, if not, install dependencies
        node_modules = current_dir / 'node_modules'
        if not node_modules.exists():
            print("📦 Installing Node.js dependencies...")
            # Use the same shell=True approach that works
            install_success = False
            
            # Try npm install
            try:
                result = subprocess.run(['npm', 'install'], cwd=current_dir, 
                                      capture_output=True, text=True, timeout=300, shell=True)
                if result.returncode == 0:
                    print("✅ Node.js dependencies installed with npm")
                    install_success = True
                else:
                    print(f"❌ npm install failed: {result.stderr}")
            except Exception as e:
                print(f"❌ npm install exception: {e}")
            
            # Try npm.cmd as fallback
            if not install_success:
                try:
                    print("   Trying npm.cmd as fallback...")
                    result = subprocess.run(['npm.cmd', 'install'], cwd=current_dir, 
                                          capture_output=True, text=True, timeout=300, shell=True)
                    if result.returncode == 0:
                        print("✅ Node.js dependencies installed with npm.cmd")
                        install_success = True
                    else:
                        print(f"❌ npm.cmd install failed: {result.stderr}")
                except Exception as e:
                    print(f"❌ npm.cmd install exception: {e}")
            
            if not install_success:
                print("❌ Failed to install Node.js dependencies")
                return False
        
        return True
        
    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        print(f"❌ Node.js check failed: {e}")
        print("   Please try:")
        print("   1. Close and reopen PowerShell")
        print("   2. Run: node --version")
        print("   3. If that fails, reinstall Node.js from https://nodejs.org/")
        return False

def start_python_backend():
    """Start the Python backend server"""
    print("🚀 Starting Python backend server...")
    
    try:
        # Import and start the backend server
        from backend_server import run_server
        
        # Run server in a thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(2)
        
        print("✅ Python backend server started on http://localhost:5000")
        return server_thread
        
    except Exception as e:
        print(f"❌ Failed to start Python backend: {e}")
        return None

def start_electron_frontend():
    """Start the Electron frontend"""
    print("🎨 Starting Electron frontend...")
    
    try:
        # Use the same reliable approach for starting Electron
        electron_process = None
        
        # Method 1: Try standard npm start with detailed error handling
        try:
            print("   Attempting: npm start")
            electron_process = subprocess.Popen(
                ['npm', 'start'], 
                cwd=current_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True  # Critical for Windows
            )
            
            # Give it a moment and check if it started successfully
            time.sleep(3)
            if electron_process.poll() is None:
                print("✅ Electron started successfully with npm start")
                return electron_process
            else:
                # Get the error output
                try:
                    stdout, stderr = electron_process.communicate(timeout=2)
                    print(f"❌ npm start failed:")
                    if stderr:
                        print(f"   stderr: {stderr.decode().strip()}")
                    if stdout:
                        print(f"   stdout: {stdout.decode().strip()}")
                except subprocess.TimeoutExpired:
                    electron_process.kill()
                    print("❌ npm start failed (timeout)")
                electron_process = None
                
        except Exception as e:
            print(f"❌ npm start exception: {e}")
            electron_process = None
        
        # Method 2: Try with npm.cmd for Windows
        if not electron_process:
            try:
                print("   Attempting: npm.cmd start")
                electron_process = subprocess.Popen(
                    ['npm.cmd', 'start'], 
                    cwd=current_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True
                )
                
                time.sleep(3)
                if electron_process.poll() is None:
                    print("✅ Electron started successfully with npm.cmd start")
                    return electron_process
                else:
                    try:
                        stdout, stderr = electron_process.communicate(timeout=2)
                        print(f"❌ npm.cmd start failed:")
                        if stderr:
                            print(f"   stderr: {stderr.decode().strip()}")
                        if stdout:
                            print(f"   stdout: {stdout.decode().strip()}")
                    except subprocess.TimeoutExpired:
                        electron_process.kill()
                        print("❌ npm.cmd start failed (timeout)")
                    electron_process = None
                    
            except Exception as e:
                print(f"❌ npm.cmd start exception: {e}")
                electron_process = None
        
        # Method 3: Direct electron execution
        if not electron_process:
            try:
                print("   Attempting: npx electron .")
                electron_process = subprocess.Popen(
                    ['npx', 'electron', '.'], 
                    cwd=current_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True
                )
                
                time.sleep(3)
                if electron_process.poll() is None:
                    print("✅ Electron started successfully with npx electron")
                    return electron_process
                else:
                    try:
                        stdout, stderr = electron_process.communicate(timeout=2)
                        print(f"❌ npx electron failed:")
                        if stderr:
                            print(f"   stderr: {stderr.decode().strip()}")
                        if stdout:
                            print(f"   stdout: {stdout.decode().strip()}")
                    except subprocess.TimeoutExpired:
                        electron_process.kill()
                        print("❌ npx electron failed (timeout)")
                    electron_process = None
                    
            except Exception as e:
                print(f"❌ npx electron exception: {e}")
        
        if not electron_process:
            print("❌ All Electron startup methods failed")
            print("   This could be due to:")
            print("   1. Electron not installed in node_modules")
            print("   2. Package.json script issues")
            print("   3. Windows subprocess execution context")
            print("   4. Missing dependencies")
            return None
        
        return electron_process
        
    except Exception as e:
        print(f"❌ Critical error starting Electron: {e}")
        return None

def open_fallback_browser():
    """Open fallback web interface in browser if Electron fails"""
    print("🌐 Opening web interface in browser as fallback...")
    
    try:
        # Wait a moment for backend to be ready
        time.sleep(3)
        
        # Open browser to a simple HTML page that loads our frontend
        fallback_url = "http://localhost:5000/static/index.html"
        webbrowser.open(fallback_url)
        
        print("✅ Web interface opened in browser")
        print("   You can use the application in your web browser")
        
    except Exception as e:
        print(f"❌ Failed to open web interface: {e}")

def create_fallback_route():
    """Add a static file route to the backend server for fallback web access"""
    try:
        # This would be added to backend_server.py
        frontend_dir = current_dir / 'frontend'
        if frontend_dir.exists():
            print("📁 Frontend directory found for web fallback")
    except Exception as e:
        print(f"⚠️  Could not set up web fallback: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down Gmail RAG Assistant...")
    sys.exit(0)

def main():
    """Main application entry point"""
    print("=" * 60)
    print("📧 Gmail RAG Assistant - Electron Edition")
    print("   Modern AI-powered email assistant")
    print("=" * 60)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Pre-flight checks
    print("\n🔧 Running pre-flight checks...")
    
    # Check Python dependencies
    if not check_dependencies():
        print("\n❌ Setup incomplete. Please install missing dependencies.")
        sys.exit(1)
    
    # Check credentials (non-blocking)
    check_credentials()
    
    # Check API key (non-blocking)
    check_api_key()
    
    # Check Node.js and Electron
    electron_available = check_node_and_electron()
    
    print("\n🚀 Starting application...")
    
    # Start Python backend
    backend_thread = start_python_backend()
    if not backend_thread:
        print("❌ Failed to start backend server. Exiting.")
        sys.exit(1)
    
    # Start Electron frontend or fallback
    electron_process = None
    if electron_available:
        electron_process = start_electron_frontend()
        
        if not electron_process:
            print("⚠️  Electron failed to start, trying web fallback...")
            open_fallback_browser()
    else:
        print("⚠️  Electron not available, using web fallback...")
        print("\n📝 To use Electron interface:")
        print("   1. Install Node.js from https://nodejs.org/")
        print("   2. Restart your terminal/PowerShell")
        print("   3. Run: python main.py --electron")
        open_fallback_browser()
    
    print("\n✅ Gmail RAG Assistant is now running!")
    print("\n💡 Tips:")
    print("   • The application will open automatically")
    print("   • Configure your Groq API key in Settings")
    print("   • Load emails first, then start chatting")
    print("   • Press Ctrl+C to exit")
    
    try:
        # Keep the main process alive
        if electron_process:
            print("\n📱 Electron app is running...")
            electron_process.wait()
        else:
            print("\n🌐 Web interface is running at http://localhost:5000")
            print("   Press Ctrl+C to stop the server")
            
            # Keep backend running
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Cleanup
        if electron_process:
            try:
                electron_process.terminate()
                electron_process.wait(timeout=5)
            except:
                electron_process.kill()
        
        print("👋 Gmail RAG Assistant stopped. Goodbye!")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], cwd=current_dir, check=True, capture_output=True, text=True)
        
        print("✅ Python dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False

def show_help():
    """Show help information"""
    print("""
Gmail RAG Assistant - Electron Edition

Usage:
    python main.py [options]

Options:
    --install-deps    Install Python dependencies
    --help, -h        Show this help message
    --web-only        Start only web interface (skip Electron)
    --version         Show version information

Setup Instructions:
1. Install Python dependencies: python main.py --install-deps
2. Download credentials.json from Google Cloud Console
3. Get Groq API key from console.groq.com
4. Install Node.js from nodejs.org
5. Run the application: python main.py

For more information, visit the project documentation.
""")

if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            show_help()
            sys.exit(0)
        elif sys.argv[1] == '--install-deps':
            if install_dependencies():
                print("Dependencies installed. You can now run: python main.py")
            sys.exit(0)
        elif sys.argv[1] == '--web-only':
            print("Starting in web-only mode...")
            # Modify behavior to skip Electron
            os.environ['WEB_ONLY'] = 'true'
        elif sys.argv[1] == '--version':
            print("Gmail RAG Assistant v1.0.0 - Electron Edition")
            sys.exit(0)
    
    # Run main application
    main()