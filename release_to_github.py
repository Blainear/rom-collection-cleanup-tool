#!/usr/bin/env python3
"""
Simple GitHub Release Helper for ROM Cleanup Tool v2.0
"""

import os
import subprocess
from pathlib import Path

def main():
    """Main function to help with GitHub release"""
    
    print("🚀 ROM Cleanup Tool v2.0 - GitHub Release Helper")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("rom_cleanup_gui.py").exists():
        print("❌ Error: rom_cleanup_gui.py not found")
        print("Please run this script from the 'rom cleanup public' directory")
        return
    
    # Check if executable exists
    exe_path = Path("dist/ROM_Cleanup_Tool.exe")
    if not exe_path.exists():
        print("❌ Error: ROM_Cleanup_Tool.exe not found in dist/")
        print("Please build the executable first using: python build_exe.py")
        return
    
    print("✅ Executable found:", exe_path)
    print(f"📦 Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
    
    # Check git status
    try:
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("\n📝 Files with changes:")
            print(result.stdout)
            print("💡 Consider committing changes before release")
        else:
            print("✅ Working directory is clean")
    except subprocess.CalledProcessError:
        print("⚠️ Could not check git status")
    
    print("\n" + "=" * 50)
    print("📋 MANUAL RELEASE STEPS:")
    print("=" * 50)
    print("1. Go to: https://github.com/Blainear/rom-collection-cleanup-tool")
    print("2. Click 'Releases' in the right sidebar")
    print("3. Click 'Create a new release'")
    print("4. Set Tag version: v2.0")
    print("5. Set Release title: ROM Cleanup Tool v2.0 - Enhanced Edition")
    print("6. Copy the release description from RELEASE_NOTES.md")
    print("7. Upload the executable: dist/ROM_Cleanup_Tool.exe")
    print("8. Click 'Publish release'")
    print("\n📦 Release files:")
    print("- ROM_Cleanup_Tool.exe (13.4 MB)")
    print("- README.md (documentation)")
    print("- RELEASE_NOTES.md (detailed notes)")
    print("- requirements.txt (dependencies)")
    
    print("\n🎯 What's new in v2.0:")
    print("- ✅ Startup API Connection Check")
    print("- 🔧 Force API Check Button")
    print("- 🛑 Stop Process Button")
    print("- ⚙️ Enhanced Process Control")
    print("- 🎯 Improved Region Detection")
    
    print("\n✅ Ready for release!")

if __name__ == "__main__":
    main() 