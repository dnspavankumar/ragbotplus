#!/usr/bin/env python3
"""
Gmail RAG Assistant - Launcher
Chooses between PyQt6 (legacy) and Electron (modern) interface
"""

import sys
import os
from pathlib import Path

def show_interface_selection():
    """
    Show interface selection menu
    """
    print("="*60)
    print("📧 Gmail RAG Assistant")
    print("   AI-powered email assistant")
    print("="*60)
    print()
    print("Choose your interface:")
    print("  1. 🎨 Electron (Modern, Recommended)")
    print("  2. 🖥️  PyQt6 (Legacy)")
    print("  3. 🌐 Web Browser Only")
    print("  4. ❓ Help")
    print("  5. 🚪 Exit")
    print()
    
    while True:
        try:
            choice = input("Select option (1-5): ").strip()
            
            if choice == '1':
                launch_electron()
                break
            elif choice == '2':
                launch_pyqt6()
                break
            elif choice == '3':
                launch_web_only()
                break
            elif choice == '4':
                show_help()
            elif choice == '5':
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
        except EOFError:
            sys.exit(0)

def launch_electron():
    """
    Launch the Electron interface
    """
    print("\n🚀 Starting Electron interface...")
    
    try:
        # Import and run the Electron launcher
        import main_electron
        main_electron.main()
        
    except ImportError as e:
        print(f"❌ Error importing Electron launcher: {e}")
        print("   Falling back to PyQt6 interface...")
        launch_pyqt6()
    except Exception as e:
        print(f"❌ Error starting Electron interface: {e}")
        print("   Falling back to PyQt6 interface...")
        launch_pyqt6()

def launch_pyqt6():
    """
    Launch the PyQt6 interface (legacy)
    """
    print("\n🖥️  Starting PyQt6 interface...")
    
    try:
        # Import the legacy PyQt6 main
        import main_pyqt6
        exit_code = main_pyqt6.main()
        sys.exit(exit_code)
        
    except ImportError as e:
        print(f"❌ Error importing PyQt6 modules: {e}")
        print("   Please install PyQt6: pip install PyQt6")
        print("   Or use the Electron interface instead.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting PyQt6 interface: {e}")
        sys.exit(1)

def launch_web_only():
    """
    Launch web interface only
    """
    print("\n🌐 Starting web interface...")
    
    try:
        os.environ['WEB_ONLY'] = 'true'
        import main_electron
        main_electron.main()
        
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        sys.exit(1)

def show_help():
    """
    Show help information
    """
    print("\n" + "="*60)
    print("📖 Gmail RAG Assistant - Help")
    print("="*60)
    print(
        """
🎨 ELECTRON INTERFACE (Recommended)
   • Modern, responsive design
   • Better performance
   • Cross-platform compatibility
   • Built-in updates
   
   Requirements:
   - Node.js (download from nodejs.org)
   - All Python dependencies

🖥️  PYQT6 INTERFACE (Legacy)
   • Traditional desktop application
   • Native OS integration
   - May have compatibility issues
   
   Requirements:
   - PyQt6 (pip install PyQt6)
   - All Python dependencies

🌐 WEB INTERFACE
   • Browser-based access
   • No additional dependencies
   • Limited functionality

🔧 SETUP REQUIREMENTS:
   1. Python 3.8+ with pip
   2. Install dependencies: pip install -r requirements.txt
   3. Gmail API credentials (credentials.json)
   4. Groq API key (get from console.groq.com)

💡 TIPS:
   • First-time users should choose Electron interface
   • Configure API keys in Settings after startup
   • Load emails before starting to chat

🐛 TROUBLESHOOTING:
   • If Electron fails: Try web interface or install Node.js
   • If PyQt6 fails: Install PyQt6 or use Electron interface
   • For API errors: Check your internet connection and API keys

For more help, check the README.md file.
"""
    )
    print("="*60)
    input("\nPress Enter to continue...")

def detect_best_interface():
    """
    Auto-detect the best available interface
    """
    # Try to detect Node.js for Electron
    try:
        import subprocess
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Node.js detected - Electron interface available")
            return 'electron'
    except:
        pass
    
    # Try to detect PyQt6
    try:
        import PyQt6
        print("✅ PyQt6 detected - Legacy interface available")
        return 'pyqt6'
    except ImportError:
        pass
    
    # Fallback to web
    print("⚠️  No desktop interface available - using web interface")
    return 'web'

def main():
    """
    Main entry point
    """
    # Handle command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--electron', '-e']:
            launch_electron()
        elif arg in ['--pyqt6', '--pyqt', '-p']:
            launch_pyqt6()
        elif arg in ['--web', '-w']:
            launch_web_only()
        elif arg in ['--auto', '-a']:
            interface = detect_best_interface()
            if interface == 'electron':
                launch_electron()
            elif interface == 'pyqt6':
                launch_pyqt6()
            else:
                launch_web_only()
        elif arg in ['--help', '-h']:
            show_help()
            sys.exit(0)
        else:
            print(f"❌ Unknown argument: {arg}")
            print("Use --help for available options")
            sys.exit(1)
    else:
        # Interactive mode
        show_interface_selection()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0) 