# Troubleshooting Guide - Mobile Development Setup

## 🔧 Common Issues and Solutions

### **Issue: "Node.js not found" after installation**

This is a common Windows issue where Node.js is installed but not added to the system PATH.

#### **Solution 1: Restart Terminal/Command Prompt**
```bash
# Close all terminal windows and reopen
# Then try:
node --version
npm --version
```

#### **Solution 2: Check Installation Location**
Node.js is usually installed in one of these locations:
- `C:\Program Files\nodejs\`
- `C:\Program Files (x86)\nodejs\`
- `%APPDATA%\npm\` (for user installation)

#### **Solution 3: Add Node.js to PATH (Windows)**

**Method A: Using System Properties**
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Click "Environment Variables"
3. Under "System Variables", find and select "Path"
4. Click "Edit" → "New"
5. Add the Node.js installation path (usually `C:\Program Files\nodejs\`)
6. Click "OK" on all dialogs
7. **Restart your terminal/command prompt**

**Method B: Using Command Prompt (as Administrator)**
```cmd
# Check where Node.js is installed
where node

# If found, add to PATH temporarily
set PATH=%PATH%;C:\Program Files\nodejs\

# Or permanently (requires admin)
setx PATH "%PATH%;C:\Program Files\nodejs\" /M
```

**Method C: Using PowerShell (as Administrator)**
```powershell
# Check current PATH
$env:PATH

# Add Node.js to PATH permanently
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\nodejs\", "Machine")
```

#### **Solution 4: Reinstall Node.js with PATH option**
1. Download Node.js from https://nodejs.org/
2. Run installer as Administrator
3. **Make sure "Add to PATH" is checked during installation**
4. Complete installation
5. Restart terminal

#### **Solution 5: Use Node Version Manager (Recommended)**
```bash
# Install nvm-windows from: https://github.com/coreybutler/nvm-windows
# Then install Node.js through nvm:
nvm install 18.17.0
nvm use 18.17.0
```

### **Verification Steps**
After fixing PATH, verify installation:
```bash
# These should all work:
node --version          # Should show v18.x.x or similar
npm --version           # Should show 9.x.x or similar
npx --version           # Should show 9.x.x or similar
```

---

## 🐛 Other Common Issues

### **Issue: Python not found**
```bash
# Try these commands:
python --version
python3 --version
py --version

# If none work, install Python from python.org
# Make sure to check "Add Python to PATH" during installation
```

### **Issue: pip not found**
```bash
# Try:
pip --version
python -m pip --version

# If not found, reinstall Python with pip included
```

### **Issue: Permission denied errors**
```bash
# On Windows, run Command Prompt as Administrator
# On macOS/Linux, use sudo:
sudo npm install -g @expo/cli
```

### **Issue: Expo CLI installation fails**
```bash
# Clear npm cache first:
npm cache clean --force

# Then install:
npm install -g @expo/cli

# Alternative: Use npx instead of global install
npx @expo/cli --version
```

### **Issue: FastAPI dependencies fail to install**
```bash
# Upgrade pip first:
python -m pip install --upgrade pip

# Then install requirements:
pip install -r mobile/backend/requirements.txt

# If still fails, try:
pip install --user -r mobile/backend/requirements.txt
```

### **Issue: Port 8000 already in use**
```bash
# Find what's using port 8000:
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID):
taskkill /PID <PID> /F

# Or use a different port in the API:
uvicorn api:app --host 0.0.0.0 --port 8001
```

### **Issue: Database not found**
```bash
# Make sure you're in the right directory:
cd Quiz-Game-Collection

# Check if database exists:
ls data/databases/game_questions.db

# If not found, you may need to run your data pipeline first
```

---

## 🔍 Diagnostic Commands

Run these to check your environment:

```bash
# System info
echo $PATH                    # Linux/macOS
echo %PATH%                   # Windows

# Node.js ecosystem
node --version
npm --version
npx --version
npm config get prefix

# Python ecosystem
python --version
pip --version
which python                  # Linux/macOS
where python                  # Windows

# Check if tools are accessible
expo --version
git --version
```

---

## 🚀 Alternative Setup Methods

### **Method 1: Manual Setup (if script fails)**
```bash
# 1. Setup backend
cd mobile/backend
pip install -r requirements.txt
python api.py &

# 2. Setup mobile app
cd ../apps/truth-or-dare
npm install
expo start
```

### **Method 2: Docker Setup (Advanced)**
```bash
# If you have Docker installed:
cd mobile/backend
docker build -t quiz-api .
docker run -p 8000:8000 quiz-api
```

### **Method 3: Use Online Development Environment**
- **Replit**: Upload your code to replit.com
- **CodeSandbox**: Use codesandbox.io for React Native development
- **Expo Snack**: Use snack.expo.dev for quick testing

---

## 📞 Getting Help

If you're still having issues:

1. **Check the error message carefully** - it usually tells you what's wrong
2. **Try running commands individually** instead of the setup script
3. **Restart your terminal/computer** after installing software
4. **Run as Administrator** if you get permission errors
5. **Check antivirus software** - it might be blocking installations

### **Useful Resources**
- Node.js Installation: https://nodejs.org/
- Expo Documentation: https://docs.expo.dev/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- React Native Setup: https://reactnative.dev/docs/environment-setup

---

## 🔧 Environment-Specific Notes

### **Windows**
- Use Command Prompt or PowerShell as Administrator
- Check Windows Defender/antivirus settings
- Use backslashes in paths: `C:\Program Files\nodejs\`

### **macOS**
- May need to install Xcode Command Line Tools: `xcode-select --install`
- Use Homebrew for easier package management: `brew install node`

### **Linux**
- Use your distribution's package manager
- May need to install build tools: `sudo apt-get install build-essential`

The most common issue is PATH configuration, so focus on that first!
