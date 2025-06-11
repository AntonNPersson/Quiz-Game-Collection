# 🚀 Server Quick Reference Card

## ⚡ One-Command Startup

### Option 1: Simple Test (Recommended)
```bash
# Quick startup with Windows compatibility
python scripts/start_simple_mobile_test.py
```

### Option 2: Full Development Setup
```bash
# Complete development environment
python scripts/setup_mobile_dev.py
```

## 🔧 Manual Commands

### Backend API Server
```bash
# Start API server (http://localhost:8000)
cd mobile/backend && python simple_api.py
```

### Mobile Development Server
```bash
# Start mobile app development server
cd mobile/apps/truth-or-dare && npx @expo/cli start
```

## 📱 Mobile Testing

1. Install **Expo Go** app on your phone
2. Scan the QR code from the terminal
3. App loads automatically

## 🛠️ Common Issues & Quick Fixes

### 🔍 Run Diagnostics First
```bash
# Diagnose "system cannot find the file specified" errors
python scripts/diagnose_mobile_setup.py
```

### API Server Won't Start
```bash
cd mobile/backend
pip install -r requirements_simple.txt
python simple_api.py
```

### Mobile App Won't Start
```bash
cd mobile/apps/truth-or-dare
npm install
npx @expo/cli start --clear
```

### Port 8000 Already in Use (Windows)
```bash
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

### Port 8000 Already in Use (Mac/Linux)
```bash
lsof -ti:8000 | xargs kill -9
```

## ✅ Success Check

- API: Visit `http://localhost:8000` - should show health check
- Mobile: QR code appears in terminal
- Phone: Truth or Dare app loads in Expo Go

## 🔗 Full Documentation

For detailed instructions, see: `docs/HOW_TO_START_SERVERS.md`
