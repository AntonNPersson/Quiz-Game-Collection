#!/usr/bin/env python3
"""
Node.js PATH Fix Script for Windows

This script helps fix the common issue where Node.js is installed
but not accessible from the command line due to PATH configuration.
"""

import os
import sys
import subprocess
import winreg
from pathlib import Path

def run_command(command, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def find_nodejs_installation():
    """Find Node.js installation paths"""
    possible_paths = [
        r"C:\Program Files\nodejs",
        r"C:\Program Files (x86)\nodejs",
        os.path.expanduser(r"~\AppData\Roaming\npm"),
        os.path.expanduser(r"~\AppData\Local\Programs\nodejs"),
    ]
    
    found_paths = []
    for path in possible_paths:
        node_exe = os.path.join(path, "node.exe")
        if os.path.exists(node_exe):
            found_paths.append(path)
            print(f"✅ Found Node.js at: {path}")
    
    return found_paths

def check_current_path():
    """Check if Node.js is in current PATH"""
    success, stdout, stderr = run_command("node --version")
    if success:
        print(f"✅ Node.js is accessible: {stdout}")
        return True
    else:
        print("❌ Node.js not found in PATH")
        return False

def get_current_path():
    """Get current system PATH"""
    try:
        # Get system PATH
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as key:
            system_path, _ = winreg.QueryValueEx(key, "Path")
        
        # Get user PATH
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                user_path, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            user_path = ""
        
        return system_path, user_path
    except Exception as e:
        print(f"Error reading PATH: {e}")
        return "", ""

def add_to_user_path(nodejs_path):
    """Add Node.js to user PATH (doesn't require admin)"""
    try:
        # Open user environment key
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                current_path, _ = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current_path = ""
            
            # Check if already in PATH
            if nodejs_path.lower() in current_path.lower():
                print(f"✅ {nodejs_path} already in user PATH")
                return True
            
            # Add to PATH
            if current_path:
                new_path = f"{current_path};{nodejs_path}"
            else:
                new_path = nodejs_path
            
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"✅ Added {nodejs_path} to user PATH")
            return True
            
    except Exception as e:
        print(f"❌ Error adding to user PATH: {e}")
        return False

def add_to_system_path(nodejs_path):
    """Add Node.js to system PATH (requires admin)"""
    try:
        # Open system environment key
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_ALL_ACCESS) as key:
            current_path, _ = winreg.QueryValueEx(key, "Path")
            
            # Check if already in PATH
            if nodejs_path.lower() in current_path.lower():
                print(f"✅ {nodejs_path} already in system PATH")
                return True
            
            # Add to PATH
            new_path = f"{current_path};{nodejs_path}"
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"✅ Added {nodejs_path} to system PATH")
            return True
            
    except PermissionError:
        print("❌ Permission denied. Run as Administrator to modify system PATH")
        return False
    except Exception as e:
        print(f"❌ Error adding to system PATH: {e}")
        return False

def set_temporary_path(nodejs_paths):
    """Set PATH for current session"""
    current_path = os.environ.get("PATH", "")
    for path in nodejs_paths:
        if path not in current_path:
            os.environ["PATH"] = f"{current_path};{path}"
            current_path = os.environ["PATH"]
    
    print("✅ Set temporary PATH for current session")

def main():
    """Main function"""
    print("🔧 Node.js PATH Fix Script")
    print("=" * 40)
    
    # Check if we're on Windows
    if os.name != 'nt':
        print("❌ This script is for Windows only")
        sys.exit(1)
    
    # Check current status
    print("\n🔍 Checking current Node.js status...")
    if check_current_path():
        print("✅ Node.js is already working! No fix needed.")
        return
    
    # Find Node.js installations
    print("\n🔍 Looking for Node.js installations...")
    nodejs_paths = find_nodejs_installation()
    
    if not nodejs_paths:
        print("❌ Node.js installation not found!")
        print("\n💡 Solutions:")
        print("1. Download and install Node.js from: https://nodejs.org/")
        print("2. Make sure to check 'Add to PATH' during installation")
        print("3. Run the installer as Administrator")
        return
    
    # Try to fix PATH
    print(f"\n🔧 Attempting to fix PATH...")
    
    for nodejs_path in nodejs_paths:
        print(f"\n📁 Working with: {nodejs_path}")
        
        # Try user PATH first (doesn't require admin)
        if add_to_user_path(nodejs_path):
            break
        
        # Try system PATH (requires admin)
        if add_to_system_path(nodejs_path):
            break
    
    # Set temporary PATH for current session
    set_temporary_path(nodejs_paths)
    
    # Test again
    print("\n🧪 Testing Node.js access...")
    success, stdout, stderr = run_command("node --version")
    
    if success:
        print(f"✅ SUCCESS! Node.js is now accessible: {stdout}")
        
        # Test npm too
        success, stdout, stderr = run_command("npm --version")
        if success:
            print(f"✅ npm is also working: {stdout}")
        
        print("\n🎉 PATH fix completed successfully!")
        print("\n📋 Next steps:")
        print("1. Close and reopen your terminal/command prompt")
        print("2. Run: python scripts/setup_mobile_dev.py")
        print("3. If it still doesn't work, restart your computer")
        
    else:
        print("❌ Node.js still not accessible")
        print("\n💡 Manual solutions:")
        print("1. Restart your terminal/command prompt")
        print("2. Restart your computer")
        print("3. Reinstall Node.js as Administrator")
        print("4. Check the troubleshooting guide: mobile/TROUBLESHOOTING.md")

if __name__ == "__main__":
    main()
