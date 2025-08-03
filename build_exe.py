#!/usr/bin/env python3
"""
Build script to create ROM Cleanup GUI executable
"""

import subprocess
import sys
from pathlib import Path


def check_pyinstaller() -> bool:
    """Check that PyInstaller is available."""
    try:
        import PyInstaller  # noqa: F401  (imported for availability check)
        print("✓ PyInstaller found")
        return True
    except ImportError:
        print(
            "✗ PyInstaller is not installed. Please run 'pip install pyinstaller' and rerun this script."
        )
        return False

def create_executable():
    """Create the executable using PyInstaller"""
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Create single executable file
        "--windowed",                   # No console window (Windows)
        "--name", "ROM_Cleanup_Tool",   # Executable name
        "--icon", "NONE",               # No icon for now
        "--clean",                      # Clean build
        "--distpath", "dist",           # Output directory
        "--workpath", "build",          # Build directory
        "rom_cleanup_gui.py"            # Source file
    ]
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Executable built successfully!")
            
            # Check if file was created
            exe_path = Path("dist/ROM_Cleanup_Tool.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"✓ Created: {exe_path} ({size_mb:.1f} MB)")
                print("\nTo distribute:")
                print(f"  - Copy {exe_path} to target computer")
                print("  - No Python installation required on target!")
            else:
                print("✗ Executable file not found in expected location")
                
        else:
            print("✗ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except Exception as e:
        print(f"✗ Error running PyInstaller: {e}")

def main():
    print("ROM Cleanup Tool - Executable Builder")
    print("=" * 40)
    
    # Check if source file exists
    if not Path("rom_cleanup_gui.py").exists():
        print("✗ rom_cleanup_gui.py not found in current directory")
        return
        
    # Ensure PyInstaller is installed
    if not check_pyinstaller():
        return
        
    # Create executable
    create_executable()
    
    print("\nBuild process complete!")

if __name__ == "__main__":
    main()