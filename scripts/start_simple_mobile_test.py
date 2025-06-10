#!/usr/bin/env python3
"""
Simple Mobile Test Startup Script

This script starts both the backend API and mobile app with the simple test version
to avoid interruptions and test basic functionality.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    print("Starting Simple Mobile Test Environment")
    print("=" * 50)
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Ensure we're in the right directory
    os.chdir(project_root)
    
    print(f"Working directory: {project_root}")
    
    # Step 1: Ensure simple app is active
    print("\n1. Setting up simple test app...")
    mobile_app_dir = project_root / "mobile" / "apps" / "truth-or-dare"
    
    if not mobile_app_dir.exists():
        print("ERROR: Mobile app directory not found!")
        return False
    
    # Copy simple app to main App.js
    simple_app = mobile_app_dir / "App-simple.js"
    main_app = mobile_app_dir / "App.js"
    
    if simple_app.exists():
        try:
            import shutil
            shutil.copy2(simple_app, main_app)
            print("SUCCESS: Simple test app activated")
        except Exception as e:
            print(f"ERROR: Failed to copy simple app: {e}")
            return False
    else:
        print("ERROR: App-simple.js not found!")
        return False
    
    # Step 2: Start backend API
    print("\n2. Starting backend API server...")
    backend_dir = project_root / "mobile" / "backend"
    
    try:
        print("Starting API on http://localhost:8000")
        api_process = subprocess.Popen(
            [sys.executable, "simple_api.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        if api_process.poll() is None:
            print("SUCCESS: Backend API started successfully")
        else:
            stdout, stderr = api_process.communicate()
            print(f"ERROR: Backend failed to start: {stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: Error starting backend: {e}")
        return False
    
    # Step 3: Start mobile app
    print("\n3. Starting mobile app...")
    
    try:
        print("Starting Expo development server...")
        
        # Start Expo without tunnel to avoid complications
        expo_process = subprocess.Popen(
            ["npx", "@expo/cli", "start", "--clear"],
            cwd=mobile_app_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("SUCCESS: Mobile app server starting...")
        print("\nNext Steps:")
        print("1. Wait for QR code to appear in the terminal")
        print("2. Install 'Expo Go' app on your phone")
        print("3. Scan the QR code with Expo Go")
        print("4. You should see: 'Truth or Dare - Mobile App Test'")
        print("\nManual Commands (if needed):")
        print(f"   Backend: cd {backend_dir} && python simple_api.py")
        print(f"   Mobile:  cd {mobile_app_dir} && npx @expo/cli start")
        
        # Keep processes running
        try:
            print("\nServers running... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
                
                # Check if processes are still running
                if api_process.poll() is not None:
                    print("ERROR: Backend API stopped unexpectedly")
                    break
                    
                if expo_process.poll() is not None:
                    print("ERROR: Mobile app server stopped unexpectedly")
                    break
                    
        except KeyboardInterrupt:
            print("\nStopping servers...")
            
            # Stop processes
            try:
                api_process.terminate()
                expo_process.terminate()
                
                # Wait for clean shutdown
                api_process.wait(timeout=5)
                expo_process.wait(timeout=5)
                
                print("SUCCESS: Servers stopped cleanly")
                
            except subprocess.TimeoutExpired:
                print("WARNING: Force killing processes...")
                api_process.kill()
                expo_process.kill()
                
    except Exception as e:
        print(f"ERROR: Error starting mobile app: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nERROR: Failed to start mobile test environment")
        sys.exit(1)
