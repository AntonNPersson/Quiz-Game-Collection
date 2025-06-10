#!/usr/bin/env python3
"""
Manual Mobile Setup Script - Bypasses Rust dependency issues

This script manually installs only the essential dependencies needed
for the mobile backend, avoiding the Rust compilation issues.
"""

import os
import sys
import subprocess
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

def install_package(package):
    """Install a single package"""
    print(f"📦 Installing {package}...")
    success, stdout, stderr = run_command(f"pip install {package}")
    if success:
        print(f"✅ {package} installed successfully")
        return True
    else:
        print(f"❌ Failed to install {package}: {stderr}")
        return False

def main():
    """Main setup function"""
    print("🔧 Manual Mobile Setup - Avoiding Rust Dependencies")
    print("=" * 60)
    
    # Essential packages only
    essential_packages = [
        "fastapi==0.100.0",
        "uvicorn==0.23.0", 
        "pydantic==2.0.0",
        "python-multipart==0.0.5"
    ]
    
    print("\n📦 Installing essential packages individually...")
    
    failed_packages = []
    for package in essential_packages:
        if not install_package(package):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n❌ Failed to install: {', '.join(failed_packages)}")
        print("\n💡 Try installing manually:")
        for package in failed_packages:
            print(f"   pip install {package}")
        return False
    
    print("\n✅ All essential packages installed!")
    
    # Test FastAPI import
    print("\n🧪 Testing FastAPI import...")
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ All imports successful!")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Setup mobile app
    print("\n📱 Setting up mobile app...")
    app_dir = Path(__file__).parent.parent / "mobile" / "apps" / "truth-or-dare"
    
    if not app_dir.exists():
        print(f"❌ Mobile app directory not found: {app_dir}")
        return False
    
    print("📦 Installing Node.js dependencies...")
    success, stdout, stderr = run_command("npm install", cwd=app_dir)
    
    if success:
        print("✅ Mobile app dependencies installed!")
    else:
        print(f"❌ Failed to install mobile dependencies: {stderr}")
        return False
    
    # Start backend manually
    print("\n🚀 Starting backend server...")
    backend_dir = Path(__file__).parent.parent / "mobile" / "backend"
    
    print(f"📁 Backend directory: {backend_dir}")
    print("🌐 Starting FastAPI server on http://localhost:8000")
    print("📱 In another terminal, run: cd mobile/apps/truth-or-dare && expo start")
    print("\n💡 Manual commands:")
    print(f"   cd {backend_dir}")
    print("   python api.py")
    print()
    print(f"   cd {app_dir}")
    print("   expo start")
    
    # Try to start the backend
    try:
        print("\n🔄 Attempting to start backend...")
        process = subprocess.Popen(
            ["python", "api.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        import time
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Backend server started successfully!")
            print("🌐 API available at: http://localhost:8000")
            print("📖 API docs at: http://localhost:8000/docs")
            print("\nPress Ctrl+C to stop the server")
            
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
                process.terminate()
                print("✅ Server stopped")
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start: {stderr}")
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Try the manual commands above.")
        sys.exit(1)
    else:
        print("\n🎉 Setup completed successfully!")
