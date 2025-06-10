#!/usr/bin/env python3
"""
Mobile Development Setup Script for Quiz Game Collection

This script helps set up the mobile development environment and starts
the necessary services for mobile app development.
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    success, stdout, stderr = run_command("python --version")
    if success:
        print(f"✅ Python: {stdout.strip()}")
    else:
        print("❌ Python not found")
        return False
    
    # Check Node.js
    success, stdout, stderr = run_command("node --version")
    if success:
        print(f"✅ Node.js: {stdout.strip()}")
    else:
        print("❌ Node.js not found. Please install Node.js 16+")
        return False
    
    # Check npm
    success, stdout, stderr = run_command("npm --version")
    if success:
        print(f"✅ npm: {stdout.strip()}")
    else:
        print("❌ npm not found")
        return False
    
    # Check if Expo CLI is installed
    success, stdout, stderr = run_command("expo --version")
    if success:
        print(f"✅ Expo CLI: {stdout.strip()}")
    else:
        print("⚠️  Expo CLI not found. Installing...")
        success, stdout, stderr = run_command("npm install -g @expo/cli")
        if success:
            print("✅ Expo CLI installed")
        else:
            print("❌ Failed to install Expo CLI")
            return False
    
    return True

def setup_backend():
    """Set up the FastAPI backend"""
    print("\n🔧 Setting up FastAPI backend...")
    
    backend_dir = Path(__file__).parent.parent / "mobile" / "backend"
    
    # Check if requirements.txt exists
    requirements_file = backend_dir / "requirements.txt"
    if not requirements_file.exists():
        print("❌ Backend requirements.txt not found")
        return False
    
    # Install Python dependencies
    print("📦 Installing Python dependencies...")
    success, stdout, stderr = run_command(
        f"pip install -r {requirements_file}",
        cwd=backend_dir
    )
    
    if success:
        print("✅ Backend dependencies installed")
        return True
    else:
        print(f"❌ Failed to install backend dependencies: {stderr}")
        return False

def setup_mobile_app():
    """Set up the mobile app"""
    print("\n📱 Setting up mobile app...")
    
    app_dir = Path(__file__).parent.parent / "mobile" / "apps" / "truth-or-dare"
    
    # Check if package.json exists
    package_file = app_dir / "package.json"
    if not package_file.exists():
        print("❌ Mobile app package.json not found")
        return False
    
    # Install Node.js dependencies
    print("📦 Installing Node.js dependencies...")
    success, stdout, stderr = run_command("npm install", cwd=app_dir)
    
    if success:
        print("✅ Mobile app dependencies installed")
        return True
    else:
        print(f"❌ Failed to install mobile app dependencies: {stderr}")
        return False

def start_backend_server():
    """Start the FastAPI backend server"""
    print("\n🚀 Starting FastAPI backend server...")
    
    backend_dir = Path(__file__).parent.parent / "mobile" / "backend"
    api_file = backend_dir / "api.py"
    
    if not api_file.exists():
        print("❌ Backend API file not found")
        return None
    
    # Start the server in a separate process
    try:
        process = subprocess.Popen(
            ["python", "api.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(3)
        
        # Check if it's still running
        if process.poll() is None:
            print("✅ Backend server started on http://localhost:8000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Backend server failed to start: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")
        return None

def start_mobile_dev_server():
    """Start the Expo development server"""
    print("\n📱 Starting Expo development server...")
    
    app_dir = Path(__file__).parent.parent / "mobile" / "apps" / "truth-or-dare"
    
    try:
        process = subprocess.Popen(
            ["expo", "start"],
            cwd=app_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ Expo development server starting...")
        print("📱 Use the Expo Go app on your phone to scan the QR code")
        print("🔗 Or press 'a' for Android emulator, 'i' for iOS simulator")
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start Expo server: {e}")
        return None

def check_database():
    """Check if the database exists"""
    print("\n🗄️  Checking database...")
    
    db_path = Path(__file__).parent.parent / "data" / "databases" / "game_questions.db"
    
    if db_path.exists():
        print(f"✅ Database found: {db_path}")
        return True
    else:
        print(f"❌ Database not found: {db_path}")
        print("Please ensure you have the question database set up.")
        return False

def print_instructions():
    """Print development instructions"""
    print("\n" + "="*60)
    print("🎉 MOBILE DEVELOPMENT SETUP COMPLETE!")
    print("="*60)
    print()
    print("📋 NEXT STEPS:")
    print()
    print("1. 🌐 Backend API is running at: http://localhost:8000")
    print("   - Test it: http://localhost:8000/docs")
    print()
    print("2. 📱 Mobile app development server is starting...")
    print("   - Install 'Expo Go' app on your phone")
    print("   - Scan the QR code to test on your device")
    print("   - Or use Android/iOS emulator")
    print()
    print("3. 🔧 Development workflow:")
    print("   - Edit files in mobile/apps/truth-or-dare/")
    print("   - Changes will hot-reload automatically")
    print("   - Backend changes require server restart")
    print()
    print("4. 📚 Useful commands:")
    print("   - expo start --android  (Android emulator)")
    print("   - expo start --ios      (iOS simulator)")
    print("   - expo start --web      (Web browser)")
    print()
    print("5. 🎨 Asset customization:")
    print("   - Edit mobile/shared/assets/AssetManager.js")
    print("   - Create custom asset packs for white-label apps")
    print()
    print("📖 For detailed deployment info, see mobile/DEPLOYMENT.md")
    print()
    print("Press Ctrl+C to stop all servers")
    print("="*60)

def main():
    """Main setup function"""
    print("🎮 Quiz Game Collection - Mobile Development Setup")
    print("="*60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please install missing tools.")
        sys.exit(1)
    
    # Check database
    if not check_database():
        print("\n⚠️  Database not found, but continuing setup...")
    
    # Setup backend
    if not setup_backend():
        print("\n❌ Backend setup failed.")
        sys.exit(1)
    
    # Setup mobile app
    if not setup_mobile_app():
        print("\n❌ Mobile app setup failed.")
        sys.exit(1)
    
    # Start backend server
    backend_process = start_backend_server()
    if not backend_process:
        print("\n❌ Failed to start backend server.")
        sys.exit(1)
    
    # Start mobile development server
    mobile_process = start_mobile_dev_server()
    if not mobile_process:
        print("\n❌ Failed to start mobile development server.")
        if backend_process:
            backend_process.terminate()
        sys.exit(1)
    
    # Print instructions
    print_instructions()
    
    # Keep running until interrupted
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        
        if backend_process:
            backend_process.terminate()
            print("✅ Backend server stopped")
        
        if mobile_process:
            mobile_process.terminate()
            print("✅ Mobile development server stopped")
        
        print("👋 Development environment stopped. Happy coding!")

if __name__ == "__main__":
    main()
