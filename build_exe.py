#!/usr/bin/env python3
"""
Build script for creating Dobby AI Rephraser EXE
This script uses PyInstaller to create a standalone executable
"""

import os
import sys
import shutil
import subprocess

def check_requirements():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed")

def build_exe():
    """Build the EXE file"""
    print("\n🔨 Building Dobby AI Rephraser EXE...")
    
    # PyInstaller command with all options - use Python module approach
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # Single file executable
        "--windowed",          # No console window
        "--name", "DobbyAI-Rephraser",
        "--add-data", "dobby_logo.png;.",
        "--add-data", "button_icon.png;.",
        "--hidden-import", "pynput.keyboard._win32",
        "--hidden-import", "pynput.mouse._win32",
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui", 
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "PyQt6.QtWidgets.QSystemTrayIcon",
        "--hidden-import", "PyQt6.QtWidgets.QMenu",
        "--hidden-import", "PyQt6.QtWidgets.QAction",
        "--clean",             # Clean PyInstaller cache
        "--noconfirm",         # Replace output directory without asking
        "dobby_qt.py"
    ]
    
    # Add icon if available
    if os.path.exists("dobby_icon.ico"):
        cmd.insert(-1, "--icon")
        cmd.insert(-1, "dobby_icon.ico")
    
    try:
        subprocess.check_call(cmd)
        print("✅ Build successful!")
        
        # Move EXE to root directory
        if os.path.exists("dist/DobbyAI-Rephraser.exe"):
            shutil.move("dist/DobbyAI-Rephraser.exe", "DobbyAI-Rephraser.exe")
            print("✅ EXE moved to root directory")
            
            # Clean up build files
            if os.path.exists("build"):
                shutil.rmtree("build")
            if os.path.exists("dist"):
                shutil.rmtree("dist")
            if os.path.exists("DobbyAI-Rephraser.spec"):
                os.remove("DobbyAI-Rephraser.spec")
            print("✅ Build files cleaned up")
            
            print(f"\n🎉 Success! EXE created: DobbyAI-Rephraser.exe ({os.path.getsize('DobbyAI-Rephraser.exe') / 1024 / 1024:.1f} MB)")
        else:
            print("❌ EXE file not found in dist directory")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)

def create_icon():
    """Create a simple icon if none exists"""
    if not os.path.exists("dobby_icon.ico"):
        print("ℹ️  No icon file found. You can add dobby_icon.ico for a custom icon.")

if __name__ == "__main__":
    print("🔥 Dobby AI Rephraser - EXE Builder")
    print("=====================================\n")
    
    check_requirements()
    create_icon()
    build_exe()
    
    print("\n📦 Package contents:")
    print("- DobbyAI-Rephraser.exe (standalone executable)")
    print("- No Python installation required")
    print("- No dependencies needed")
    print("\n✅ Ready for distribution!")