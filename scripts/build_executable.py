"""
Desktop Packaging Script for Truth or Dare

This script creates a standalone executable for the Truth or Dare application
using PyInstaller. The executable will include all dependencies and can be
distributed without requiring Python installation.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller is available")
        return True
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def create_spec_file():
    """Create PyInstaller spec file for customization"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['scripts/run_truth_or_dare_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/databases/game_questions.db', 'data/databases/'),
        ('games/truth_or_dare_app/ui/themes.py', 'games/truth_or_dare_app/ui/'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'threading',
        'sqlite3',
        'games.truth_or_dare_app.app',
        'games.truth_or_dare_app.ui.themes',
        'games.truth_or_dare_app.ui.gui_app',
        'question_pipeline.factory.app_factory',
        'question_pipeline.core.engine',
        'question_pipeline.data.repositories.question_repository',
        'question_pipeline.data.storage.sqlite_storage',
        'question_pipeline.data.filters.base_filter',
        'question_pipeline.data.filters.content_filters',
        'question_pipeline.data.filters.difficulty_filters',
        'question_pipeline.data.filters.behavior_filters',
        'question_pipeline.objects.question',
        'question_pipeline.configs.game_configs',
        'question_pipeline.configs.game_mode_handlers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TruthOrDare',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)
'''
    
    with open('TruthOrDare.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created TruthOrDare.spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    try:
        # Build using spec file
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "TruthOrDare.spec"
        ])
        
        print("✅ Executable built successfully!")
        print("📁 Executable location: dist/TruthOrDare.exe")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_installer_script():
    """Create a simple installer script"""
    installer_content = '''@echo off
echo Installing Truth or Dare...

REM Create application directory
if not exist "%USERPROFILE%\\TruthOrDare" mkdir "%USERPROFILE%\\TruthOrDare"

REM Copy executable
copy "TruthOrDare.exe" "%USERPROFILE%\\TruthOrDare\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Truth or Dare.lnk'); $Shortcut.TargetPath = '%USERPROFILE%\\TruthOrDare\\TruthOrDare.exe'; $Shortcut.Save()"

REM Create start menu shortcut
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Truth or Dare" mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Truth or Dare"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Truth or Dare\\Truth or Dare.lnk'); $Shortcut.TargetPath = '%USERPROFILE%\\TruthOrDare\\TruthOrDare.exe'; $Shortcut.Save()"

echo Installation complete!
echo You can now run Truth or Dare from your desktop or start menu.
pause
'''
    
    with open('dist/install.bat', 'w') as f:
        f.write(installer_content)
    
    print("✅ Created installer script: dist/install.bat")

def create_readme():
    """Create README for the distribution"""
    readme_content = '''# Truth or Dare - Desktop Application

## Installation

1. Run `install.bat` to install the application
2. Or simply run `TruthOrDare.exe` directly

## Features

- 🎭 Complete Truth or Dare game with 4,020+ questions
- 👥 Player management with round-robin rotation
- 🎨 Multiple themes (Classic, Dark Mode, Party Mode)
- 📊 Question statistics and filtering
- 🎮 Full game session management

## System Requirements

- Windows 10 or later
- No additional software required (standalone executable)

## How to Play

1. Launch the application
2. Add player names
3. Configure game settings (questions, truth ratio, spice level)
4. Start playing!

## Themes

Switch between themes in Settings:
- **Classic**: Traditional red and blue theme
- **Dark Mode**: Dark theme for night gaming
- **Party Mode**: Bright and colorful theme

## Support

For issues or questions, please refer to the project documentation.

---

Built with the Quiz Game Collection framework.
'''
    
    with open('dist/README.txt', 'w') as f:
        f.write(readme_content)
    
    print("✅ Created README.txt")

def main():
    """Main build process"""
    print("🎭 Truth or Dare - Desktop Packaging")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('data/databases/game_questions.db'):
        print("❌ Database not found. Please run from project root directory.")
        return False
    
    # Check PyInstaller
    if not check_pyinstaller():
        return False
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if not build_executable():
        return False
    
    # Create additional files
    create_installer_script()
    create_readme()
    
    print("\n🎉 Packaging complete!")
    print("📦 Distribution files:")
    print("  - dist/TruthOrDare.exe (main executable)")
    print("  - dist/install.bat (installer script)")
    print("  - dist/README.txt (user documentation)")
    print("\n💡 To distribute:")
    print("  1. Zip the entire 'dist' folder")
    print("  2. Users can run install.bat or TruthOrDare.exe directly")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
