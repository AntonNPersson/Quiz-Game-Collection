# 🚀 How to Start API Server and Development Server

This guide explains how to start both the backend API server and the mobile development server for the Quiz Game Collection project.

## 📋 Prerequisites

Before starting the servers, ensure you have:

- **Python 3.7+** installed
- **Node.js 16+** and **npm** installed
- **Expo CLI** installed globally: `npm install -g @expo/cli`

## 🎯 Quick Start (Automated)

### Option 1: Simple Test Setup (Recommended)

For quick testing and Windows compatibility:

```bash
python scripts/start_simple_mobile_test.py
```

This script will:
- ✅ Check prerequisites (Node.js, npm, npx)
- ✅ Handle Windows subprocess PATH issues
- ✅ Start lightweight API server on `http://localhost:8000`
- ✅ Start Expo development server
- ✅ Display QR code for mobile testing

**To stop:** Press `Ctrl+C` in the terminal

### Option 2: Full Development Setup

For complete development environment with all features:

```bash
python scripts/setup_mobile_dev.py
```

This script will:
- ✅ Install all Python and Node.js dependencies
- ✅ Start full FastAPI server with all features
- ✅ Start Expo development server
- ✅ Provide comprehensive development instructions

**Note:** May require additional dependencies and doesn't handle Windows PATH issues

---

## 🔧 Manual Setup (Step by Step)

### Step 1: Start the Backend API Server

The backend API provides the data and game logic for the mobile app.

#### Option A: Simple API Server (Recommended)

```bash
# Navigate to backend directory
cd mobile/backend

# Start the simple API server
python simple_api.py
```

**Expected Output:**
```
Quiz Game Collection API Server
Server running on http://localhost:8000
API endpoints available:
   GET  /                    - Health check
   GET  /games/types         - Available game types
   POST /games               - Create new game
   POST /games/{id}/start    - Start game
   GET  /games/{id}/question - Get current question
   POST /games/{id}/answer   - Submit answer
   GET  /games/{id}/status   - Get game status
   DELETE /games/{id}        - End game
   GET  /stats               - Database statistics
   GET  /themes              - Available themes

Core modules available: True
Ready for mobile app connection!
```

#### Option B: Full API Server (Advanced)

```bash
# Navigate to backend directory
cd mobile/backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Start the full API server
python api.py
```

### Step 2: Start the Mobile Development Server

Open a **NEW terminal window** (keep the API server running) and start the mobile app:

```bash
# Navigate to mobile app directory
cd mobile/apps/truth-or-dare

# Install dependencies (first time only)
npm install

# Start the Expo development server
npx @expo/cli start
```

**Alternative commands:**
```bash
# Start with cache clearing
npx @expo/cli start --clear

# Start for specific platform
npx @expo/cli start --android
npx @expo/cli start --ios
npx @expo/cli start --web
```

**Expected Output:**
```
Starting Metro Bundler
› Metro waiting on exp://192.168.1.100:8081
› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)

› Press a │ open Android
› Press i │ open iOS simulator
› Press w │ open web

› Press r │ reload app
› Press m │ toggle menu
› Press d │ show developer menu
› Press shift+d │ toggle development mode

› Press ? │ show all commands
```

### Step 3: Test on Mobile Device

1. **Install Expo Go** on your mobile device:
   - [Android: Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
   - [iOS: App Store](https://apps.apple.com/app/expo-go/id982107779)

2. **Scan the QR Code:**
   - **Android:** Open Expo Go app and scan the QR code
   - **iOS:** Open Camera app and scan the QR code, then tap the notification

3. **Verify Connection:**
   - The app should load showing "Truth or Dare" welcome screen
   - You should be able to create games and get questions

---

## 🌐 API Endpoints Reference

Once the API server is running on `http://localhost:8000`, these endpoints are available:

### Health Check
```http
GET http://localhost:8000/
```

### Game Management
```http
# Get available game types
GET http://localhost:8000/games/types

# Create new game
POST http://localhost:8000/games
Content-Type: application/json
{
  "player_names": ["Alice", "Bob"],
  "question_count": 15,
  "settings": {
    "truth_ratio": 0.6,
    "spice_level": "mild"
  }
}

# Start game
POST http://localhost:8000/games/{game_id}/start

# Get current question
GET http://localhost:8000/games/{game_id}/question

# Submit answer
POST http://localhost:8000/games/{game_id}/answer
Content-Type: application/json
{
  "completed": true
}

# End game
DELETE http://localhost:8000/games/{game_id}
```

### Statistics
```http
# Get database statistics
GET http://localhost:8000/stats

# Get available themes
GET http://localhost:8000/themes
```

---

## 🛠️ Troubleshooting

### 🔍 Diagnostic Tool

If you're experiencing "system cannot find the file specified" or other startup errors, run the diagnostic script first:

```bash
python scripts/diagnose_mobile_setup.py
```

This script will:
- ✅ Check if Node.js, npm, and npx are installed and working
- ✅ Verify project structure and dependencies
- ✅ Test Expo CLI availability
- ✅ Provide specific solutions for your system

### Backend API Issues

**Problem:** `ModuleNotFoundError` when starting API
```bash
# Solution: Install dependencies
cd mobile/backend
pip install -r requirements_simple.txt
```

**Problem:** Port 8000 already in use
```bash
# Solution: Kill existing process or use different port
# Kill process on port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Kill process on port 8000 (Mac/Linux)
lsof -ti:8000 | xargs kill -9
```

**Problem:** Core modules not available
- This is normal - the API will work in demo mode
- For full functionality, ensure the main project dependencies are installed

### Mobile Development Server Issues

**Problem:** "System cannot find the file specified" on Windows
- **Cause**: Python subprocess can't find npm/npx from project root
- **Solution**: The updated script now handles this automatically by using `shell=True` on Windows
- **Manual fix**: Always run commands from the mobile app directory:
  ```bash
  cd mobile/apps/truth-or-dare
  npx @expo/cli start
  ```

**Problem:** Expo CLI not found
```bash
# Solution: Install Expo CLI globally
npm install -g @expo/cli
```

**Problem:** Metro bundler fails to start
```bash
# Solution: Clear cache and restart
cd mobile/apps/truth-or-dare
npx @expo/cli start --clear
```

**Problem:** Can't connect to development server
- Ensure your phone and computer are on the same WiFi network
- Try restarting the development server
- Check firewall settings

**Problem:** Dependencies not installed
```bash
# Solution: Install dependencies
cd mobile/apps/truth-or-dare
npm install
```

**Problem:** Commands work manually but fail in script
- **Cause**: Windows PATH inheritance issues in Python subprocess
- **Solution**: Use the diagnostic script to identify the issue:
  ```bash
  python scripts/diagnose_mobile_setup.py
  ```

### Network Connection Issues

**Problem:** Mobile app can't reach API server
1. Check that API server is running on `http://localhost:8000`
2. Ensure phone and computer are on same network
3. Try accessing `http://YOUR_COMPUTER_IP:8000` from phone browser
4. Check firewall settings

**Problem:** QR code not scanning
- Ensure good lighting when scanning
- Try typing the URL manually in Expo Go
- Use the tunnel option: `npx @expo/cli start --tunnel`

---

## 📱 Development Workflow

### Typical Development Session

1. **Start Backend API:**
   ```bash
   cd mobile/backend
   python simple_api.py
   ```

2. **Start Mobile App (new terminal):**
   ```bash
   cd mobile/apps/truth-or-dare
   npx @expo/cli start
   ```

3. **Test on Device:**
   - Scan QR code with Expo Go
   - Test app functionality
   - Make code changes (auto-reloads)

4. **Stop Servers:**
   - Press `Ctrl+C` in both terminals

### Making Changes

- **Backend Changes:** Restart the API server (`Ctrl+C` then `python simple_api.py`)
- **Mobile Changes:** The app auto-reloads when you save files
- **Force Reload:** Shake device or press `r` in Expo CLI

---

## 🔧 Advanced Configuration

### Custom API Port

To run the API on a different port:

```bash
# Edit simple_api.py and change the port
python simple_api.py
# Or modify the run_server() call at the bottom
```

### Custom Mobile Configuration

Edit `mobile/apps/truth-or-dare/app.json` to customize:
- App name and description
- Icons and splash screens
- Permissions and features

### Environment Variables

Create `.env` files for different environments:

```bash
# mobile/backend/.env
API_PORT=8000
DEBUG=true
DATABASE_PATH=../../data/databases/game_questions.db
```

---

## 📋 Commands Summary

### Essential Commands

```bash
# Start API server
cd mobile/backend && python simple_api.py

# Start mobile development server
cd mobile/apps/truth-or-dare && npx @expo/cli start

# Install mobile dependencies
cd mobile/apps/truth-or-dare && npm install

# Clear mobile cache
cd mobile/apps/truth-or-dare && npx @expo/cli start --clear

# Automated startup (both servers)
python scripts/start_simple_mobile_test.py
```

### Useful Development Commands

```bash
# Check API health
curl http://localhost:8000/

# View API stats
curl http://localhost:8000/stats

# Test mobile app on web
cd mobile/apps/truth-or-dare && npx @expo/cli start --web

# Build mobile app for production
cd mobile/apps/truth-or-dare && npx @expo/cli build
```

---

## ✅ Success Indicators

You'll know everything is working correctly when:

1. **API Server Shows:**
   ```
   Server running on http://localhost:8000
   Core modules available: True
   Ready for mobile app connection!
   ```

2. **Mobile Server Shows:**
   ```
   Metro waiting on exp://192.168.1.100:8081
   Scan the QR code above with Expo Go
   ```

3. **Mobile App Loads:**
   - Welcome screen appears
   - Can create new games
   - Questions load from API
   - Game flow works end-to-end

4. **API Responds:**
   - `http://localhost:8000/` shows health check
   - `http://localhost:8000/stats` shows database statistics

---

## 🎉 Next Steps

Once both servers are running successfully:

1. **Test the full game flow** - Create games, add players, play questions
2. **Customize the mobile app** - Edit themes, colors, and branding
3. **Explore the API** - Test different endpoints and game configurations
4. **Deploy to production** - Follow the deployment guides for app stores

Your Quiz Game Collection is now running with both backend API and mobile development servers! 🚀📱
