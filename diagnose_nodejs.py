#!/usr/bin/env python3
"""
Node.js Diagnostic Script
Quick script to diagnose Node.js installation and PATH issues
"""

import subprocess
import sys
import os
from pathlib import Path

def test_command(command, description):
    """Test a command and report results"""
    print(f"Testing {description}...")
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10, shell=True)
        if result.returncode == 0:
            output = result.stdout.strip()
            print(f"  ✅ SUCCESS: {output}")
            return True
        else:
            print(f"  ❌ FAILED: Return code {result.returncode}")
            if result.stderr:
                print(f"     Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  ❌ EXCEPTION: {e}")
        return False

def check_path_variable():
    """Check PATH variable for Node.js"""
    print("\nChecking PATH variable...")
    path_var = os.environ.get('PATH', '')
    
    # Look for Node.js in common installation paths
    node_paths = []
    for path_entry in path_var.split(os.pathsep):
        if 'node' in path_entry.lower():
            node_paths.append(path_entry)
    
    if node_paths:
        print("  ✅ Found Node.js related paths:")
        for path in node_paths:
            print(f"     {path}")
    else:
        print("  ⚠️  No Node.js paths found in PATH")
    
    return len(node_paths) > 0

def find_node_installations():
    """Try to find Node.js installations"""
    print("\nLooking for Node.js installations...")
    
    # Common installation paths on Windows
    common_paths = [
        Path(os.environ.get('PROGRAMFILES', '')) / 'nodejs',
        Path(os.environ.get('PROGRAMFILES(X86)', '')) / 'nodejs',
        Path(os.environ.get('APPDATA', '')) / 'npm',
        Path(os.environ.get('USERPROFILE', '')) / 'AppData' / 'Roaming' / 'npm',
    ]
    
    found_installations = []
    
    for path in common_paths:
        if path.exists():
            node_exe = path / 'node.exe'
            npm_exe = path / 'npm.cmd'
            
            if node_exe.exists():
                print(f"  ✅ Found Node.js at: {node_exe}")
                found_installations.append(str(path))
            
            if npm_exe.exists():
                print(f"  ✅ Found npm at: {npm_exe}")
    
    return found_installations

def main():
    """Main diagnostic function"""
    print("=" * 60)
    print("🔍 Node.js Diagnostic Tool")
    print("   Checking Node.js installation and PATH issues")
    print("=" * 60)
    
    # Test various Node.js commands
    tests = [
        (['node', '--version'], 'node --version'),
        (['node.exe', '--version'], 'node.exe --version'),
        (['npm', '--version'], 'npm --version'),
        (['npm.cmd', '--version'], 'npm.cmd --version'),
        (['npx', '--version'], 'npx --version'),
        (['npx.cmd', '--version'], 'npx.cmd --version'),
    ]
    
    results = []
    for command, description in tests:
        success = test_command(command, description)
        results.append((description, success))
    
    # Check PATH
    path_ok = check_path_variable()
    
    # Find installations
    installations = find_node_installations()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    successful_tests = [desc for desc, success in results if success]
    failed_tests = [desc for desc, success in results if not success]
    
    if successful_tests:
        print("✅ Working commands:")
        for test in successful_tests:
            print(f"   - {test}")
    
    if failed_tests:
        print("❌ Failed commands:")
        for test in failed_tests:
            print(f"   - {test}")
    
    print(f"\nPATH contains Node.js: {'✅ Yes' if path_ok else '❌ No'}")
    print(f"Found {len(installations)} Node.js installation(s)")
    
    # Recommendations
    print("\n🔧 RECOMMENDATIONS:")
    
    if not any(success for _, success in results):
        print("❌ Node.js not working at all:")
        print("   1. Download Node.js from https://nodejs.org/")
        print("   2. Install with 'Add to PATH' option checked")
        print("   3. Restart PowerShell/Command Prompt")
        print("   4. Run this diagnostic again")
    
    elif any(success for _, success in results):
        print("✅ Node.js is partially working:")
        print("   1. Close and reopen PowerShell/Command Prompt")
        print("   2. Try running the application again")
        
        if not path_ok:
            print("   3. Node.js might need to be added to PATH manually")
    
    print("\n🚀 NEXT STEPS:")
    print("   After following recommendations, run:")
    print("   python main.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Diagnostic cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Diagnostic failed: {e}")
        sys.exit(1)