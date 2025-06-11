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

def run_command_with_shell(cmd, description, timeout=10):
    """Run a command with proper shell handling for Windows"""
    print(f"Testing: {description}")
    try:
        # On Windows, use shell=True to inherit PATH properly
        import platform
        use_shell = platform.system() == "Windows"
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            shell=use_shell
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            print(f"  ✅ SUCCESS: {output}")
            return True, output
        else:
            error = result.stderr.strip() or result.stdout.strip()
            print(f"  ❌ FAILED: {error}")
            return False, error
            
    except subprocess.TimeoutExpired:
        print(f"  ⏰ TIMEOUT: Command took longer than {timeout} seconds")
        return False, "Timeout"
    except FileNotFoundError as e:
        print(f"  ❌ NOT FOUND: {e}")
        return False, str(e)
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False, str(e)

def check_prerequisites():
    """Check if required tools are installed"""
    print("Checking prerequisites...")
    
    # Check Node.js
    node_ok, node_version = run_command_with_shell(["node", "--version"], "Node.js installation")
    if not node_ok:
        print("   Install Node.js from: https://nodejs.org/")
        return False
    
    # Check npm
    npm_ok, npm_version = run_command_with_shell(["npm", "--version"], "npm installation")
    if not npm_ok:
        return False
    
    # Check npx
    npx_ok, npx_version = run_command_with_shell(["npx", "--version"], "npx installation")
    if not npx_ok:
        return False
    
    # Check if Expo CLI is available
    expo_ok, expo_version = run_command_with_shell(
        ["npx", "@expo/cli", "--version"], 
        "Expo CLI availability", 
        timeout=30
    )
    if not expo_ok:
        print("⚠️  Expo CLI not installed globally, will install on first use")
    
    return True

def main():
    print("Starting Simple Mobile Test Environment")
    print("=" * 50)
    
    # Check prerequisites first
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed!")
        print("\nPlease install the missing tools and try again.")
        return False
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Ensure we're in the right directory
    os.chdir(project_root)
    
    print(f"\nWorking directory: {project_root}")
    
    # Step 1: Ensure simple app is active
    print("\n1. Setting up simple test app...")
    mobile_app_dir = project_root / "mobile" / "apps" / "truth-or-dare"
    
    if not mobile_app_dir.exists():
        print("ERROR: Mobile app directory not found!")
        return False
    
    # Copy simple app to main App.js
    simple_app = mobile_app_dir / "App-minimal.js"
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
        print("ERROR: App-minimal.js not found!")
        print("INFO: Starting main app instead")
        if main_app.exists():
            print("INFO: Using existing App.js")
        else:
            print("ERROR: Main app file not found!")
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
    
    # Step 3: Check mobile app dependencies
    print("\n3. Checking mobile app dependencies...")
    package_json = mobile_app_dir / "package.json"
    node_modules = mobile_app_dir / "node_modules"
    
    if not package_json.exists():
        print("ERROR: package.json not found in mobile app directory!")
        return False
    
    if not node_modules.exists():
        print("⚠️  node_modules not found. Installing dependencies...")
        try:
            # Use the same Windows-specific approach for npm install
            import platform
            use_shell = platform.system() == "Windows"
            
            if use_shell:
                # For Windows, use shell=True and change directory in the command
                cmd = f'cd /d "{mobile_app_dir}" && npm install'
                install_result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
            else:
                # For Unix-like systems, use cwd parameter
                install_result = subprocess.run(
                    ["npm", "install"],
                    cwd=mobile_app_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
            
            if install_result.returncode == 0:
                print("✅ Dependencies installed successfully")
            else:
                print(f"❌ Failed to install dependencies: {install_result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ npm install timed out (took more than 5 minutes)")
            return False
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    else:
        print("✅ node_modules found")
    
    # Step 4: Start mobile app
    print("\n4. Starting mobile app...")
    
    try:
        print("Starting Expo development server...")
        print(f"Working directory: {mobile_app_dir}")
        
        # On Windows, we need to use shell=True and ensure proper working directory
        import platform
        use_shell = platform.system() == "Windows"
        
        if use_shell:
            # For Windows, use shell=True and change directory in the command
            cmd = f'cd /d "{mobile_app_dir}" && npx @expo/cli start --clear'
            expo_process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        else:
            # For Unix-like systems, use cwd parameter
            expo_process = subprocess.Popen(
                ["npx", "@expo/cli", "start", "--clear"],
                cwd=mobile_app_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        # Give it a moment to start and check for immediate errors
        time.sleep(3)
        
        if expo_process.poll() is not None:
            # Process has already terminated
            stdout, stderr = expo_process.communicate()
            print(f"❌ Expo failed to start:")
            print(f"   stdout: {stdout}")
            print(f"   stderr: {stderr}")
            print(f"\n🔧 Try running manually:")
            print(f"   cd {mobile_app_dir}")
            print(f"   npx @expo/cli start")
            return False
        
        print("✅ Mobile app server starting...")
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
