#!/usr/bin/env python3
"""
Mobile Setup Diagnostic Script

This script diagnoses common issues with the mobile development setup
and provides specific solutions for "system cannot find the file specified" errors.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, description, timeout=10):
    """Run a command and return the result with error handling"""
    print(f"Testing: {description}")
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            shell=(platform.system() == "Windows")
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

def check_system_info():
    """Check basic system information"""
    print("=" * 60)
    print("SYSTEM INFORMATION")
    print("=" * 60)
    
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    
    # Check PATH
    path_env = os.environ.get('PATH', '')
    print(f"PATH contains {len(path_env.split(os.pathsep))} directories")
    
    # Check if common directories are in PATH
    common_paths = [
        "C:\\Program Files\\nodejs",
        "C:\\Users\\%USERNAME%\\AppData\\Roaming\\npm",
        "/usr/local/bin",
        "/usr/bin"
    ]
    
    print("\nPATH Analysis:")
    for path in common_paths:
        expanded_path = os.path.expandvars(path)
        if expanded_path in path_env:
            print(f"  ✅ {expanded_path} - Found in PATH")
        else:
            print(f"  ❌ {expanded_path} - Not in PATH")

def check_node_ecosystem():
    """Check Node.js ecosystem"""
    print("\n" + "=" * 60)
    print("NODE.JS ECOSYSTEM")
    print("=" * 60)
    
    # Test Node.js
    node_ok, node_version = run_command(["node", "--version"], "Node.js installation")
    
    # Test npm
    npm_ok, npm_version = run_command(["npm", "--version"], "npm installation")
    
    # Test npx
    npx_ok, npx_version = run_command(["npx", "--version"], "npx installation")
    
    # Test npm global directory
    if npm_ok:
        npm_global_ok, npm_global_path = run_command(
            ["npm", "config", "get", "prefix"], 
            "npm global directory"
        )
        if npm_global_ok:
            print(f"  📁 Global npm directory: {npm_global_path}")
    
    # Test Expo CLI availability
    expo_ok, expo_version = run_command(
        ["npx", "@expo/cli", "--version"], 
        "Expo CLI availability", 
        timeout=30
    )
    
    return {
        'node': node_ok,
        'npm': npm_ok,
        'npx': npx_ok,
        'expo': expo_ok
    }

def check_project_structure():
    """Check project structure"""
    print("\n" + "=" * 60)
    print("PROJECT STRUCTURE")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")
    
    # Check key directories and files
    key_paths = [
        "mobile",
        "mobile/backend",
        "mobile/backend/simple_api.py",
        "mobile/apps",
        "mobile/apps/truth-or-dare",
        "mobile/apps/truth-or-dare/package.json",
        "mobile/apps/truth-or-dare/App.js",
        "mobile/apps/truth-or-dare/App-minimal.js",
        "mobile/apps/truth-or-dare/node_modules"
    ]
    
    for path_str in key_paths:
        path = project_root / path_str
        if path.exists():
            if path.is_file():
                size = path.stat().st_size
                print(f"  ✅ {path_str} (file, {size} bytes)")
            else:
                try:
                    items = len(list(path.iterdir()))
                    print(f"  ✅ {path_str} (directory, {items} items)")
                except PermissionError:
                    print(f"  ✅ {path_str} (directory, permission denied)")
        else:
            print(f"  ❌ {path_str} - Missing")

def check_mobile_dependencies():
    """Check mobile app dependencies"""
    print("\n" + "=" * 60)
    print("MOBILE APP DEPENDENCIES")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    mobile_app_dir = project_root / "mobile" / "apps" / "truth-or-dare"
    
    if not mobile_app_dir.exists():
        print("❌ Mobile app directory not found!")
        return False
    
    # Check package.json
    package_json = mobile_app_dir / "package.json"
    if package_json.exists():
        print("✅ package.json found")
        try:
            import json
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            print(f"  📦 App name: {package_data.get('name', 'Unknown')}")
            print(f"  📦 Version: {package_data.get('version', 'Unknown')}")
            
            # Check dependencies
            deps = package_data.get('dependencies', {})
            dev_deps = package_data.get('devDependencies', {})
            print(f"  📦 Dependencies: {len(deps)}")
            print(f"  📦 Dev Dependencies: {len(dev_deps)}")
            
        except Exception as e:
            print(f"  ❌ Error reading package.json: {e}")
    else:
        print("❌ package.json not found")
        return False
    
    # Check node_modules
    node_modules = mobile_app_dir / "node_modules"
    if node_modules.exists():
        try:
            modules = len(list(node_modules.iterdir()))
            print(f"✅ node_modules found ({modules} modules)")
        except:
            print("✅ node_modules found (unable to count)")
    else:
        print("❌ node_modules not found - need to run 'npm install'")
    
    return True

def provide_solutions(results):
    """Provide specific solutions based on diagnostic results"""
    print("\n" + "=" * 60)
    print("RECOMMENDED SOLUTIONS")
    print("=" * 60)
    
    if not results['node']:
        print("\n🔧 INSTALL NODE.JS:")
        print("   1. Go to https://nodejs.org/")
        print("   2. Download the LTS version")
        print("   3. Run the installer")
        print("   4. Restart your terminal/command prompt")
        print("   5. Run this diagnostic script again")
        return
    
    if not results['npm']:
        print("\n🔧 FIX NPM:")
        print("   npm should come with Node.js. Try:")
        print("   1. Reinstall Node.js from https://nodejs.org/")
        print("   2. Or run: npm install -g npm@latest")
        return
    
    if not results['npx']:
        print("\n🔧 FIX NPX:")
        print("   npx should come with npm 5.2+. Try:")
        print("   1. Update npm: npm install -g npm@latest")
        print("   2. Or install npx: npm install -g npx")
        return
    
    if not results['expo']:
        print("\n🔧 INSTALL EXPO CLI:")
        print("   Run: npm install -g @expo/cli")
        print("   Or use npx (no global install needed)")
        
    print("\n🔧 COMMON WINDOWS FIXES:")
    print("   1. Run Command Prompt as Administrator")
    print("   2. Add Node.js to PATH manually:")
    print("      - Add C:\\Program Files\\nodejs to PATH")
    print("      - Add %APPDATA%\\npm to PATH")
    print("   3. Restart terminal after PATH changes")
    
    print("\n🔧 MOBILE APP SETUP:")
    print("   1. Navigate to mobile app directory:")
    print("      cd mobile/apps/truth-or-dare")
    print("   2. Install dependencies:")
    print("      npm install")
    print("   3. Start the development server:")
    print("      npx @expo/cli start")
    
    print("\n🔧 ALTERNATIVE COMMANDS:")
    print("   If 'npx @expo/cli' doesn't work, try:")
    print("   - expo start (if globally installed)")
    print("   - npm start (uses package.json scripts)")
    print("   - yarn start (if using Yarn)")

def main():
    """Main diagnostic function"""
    print("Mobile Development Setup Diagnostic")
    print("This script will help identify why mobile app startup is failing")
    
    # Run all checks
    check_system_info()
    results = check_node_ecosystem()
    check_project_structure()
    check_mobile_dependencies()
    provide_solutions(results)
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
    print("If you're still having issues after following the solutions:")
    print("1. Copy the output above")
    print("2. Check the troubleshooting documentation")
    print("3. Try the manual setup commands")

if __name__ == "__main__":
    main()
