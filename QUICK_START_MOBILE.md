# 🚀 Quick Start Guide - Mobile Development

## ✅ Current Status

Your backend API is now running successfully! 🎉

- 🌐 **API Server**: http://localhost:8000 ✅ RUNNING
- 🔧 **Core Modules**: Available ✅ 
- 📱 **Ready for**: Mobile app connection

## 📱 Next Steps - Start Mobile App

### **Option 1: Use the Mobile App (Recommended)**

**1. Open a NEW terminal/command prompt**

**2. Navigate to the mobile app:**
```bash
cd mobile/apps/truth-or-dare
```

**3. Install dependencies:**
```bash
npm install
```

**4. Start the mobile development server:**
```bash
npx @expo/cli start
```

**5. Test on your phone:**
- Install "Expo Go" app from your app store
- Scan the QR code that appears
- The Truth or Dare app will load on your phone!

### **Option 2: Test the API First**

Open http://localhost:8000 in your browser to see the API working.

## 🎯 What You'll Get

### **Working Mobile App Features:**
- ✅ **Welcome Screen** - Main menu with navigation
- ✅ **Game Setup** - Add players, configure settings
- ✅ **Live Gameplay** - Real questions from your database
- ✅ **Progress Tracking** - Visual progress and player rotation
- ✅ **Theme Support** - Multiple visual themes
- ✅ **Asset Management** - Easy customization system

### **API Features Working:**
- ✅ **Game Creation** - Create new Truth or Dare sessions
- ✅ **Question Delivery** - Real questions from your database
- ✅ **Player Management** - Round-robin player rotation
- ✅ **Progress Tracking** - Game state management
- ✅ **Statistics** - Database stats and analytics

## 🎨 Asset Customization

### **Easy Theme Changes:**
Edit `mobile/shared/assets/AssetManager.js`:

```javascript
themes: {
  yourBrand: {
    colors: {
      primary: '#YOUR_COLOR',      // Change to your brand color
      secondary: '#YOUR_COLOR',    // Change to your secondary color
      background: '#YOUR_COLOR',   // Background color
      // ... customize everything
    }
  }
}
```

### **White-Label Apps:**
1. Copy `mobile/apps/truth-or-dare` to `mobile/apps/your-brand`
2. Update `package.json` with your app name
3. Load custom asset pack
4. Deploy as separate app

## 🔧 Troubleshooting

### **If mobile app fails to start:**
1. Make sure Node.js is working: `node --version`
2. Install Expo CLI: `npm install -g @expo/cli`
3. Try: `npx @expo/cli start` instead of `expo start`

### **If API connection fails:**
- Make sure the API server is still running (check the terminal)
- Try visiting http://localhost:8000 in your browser
- Check that your phone and computer are on the same network

### **If you get dependency errors:**
- Run: `npm install` in the mobile app directory
- Clear cache: `expo r -c`
- Restart the development server

## 🎉 Success Indicators

You'll know everything is working when:

1. ✅ **API Server** shows "Core modules available: True"
2. ✅ **Mobile App** shows QR code for scanning
3. ✅ **Phone App** loads the Truth or Dare welcome screen
4. ✅ **Game Creation** works and shows real questions

## 📋 Commands Summary

**Keep API running in one terminal:**
```bash
cd mobile/backend
python simple_api.py
```

**Start mobile app in another terminal:**
```bash
cd mobile/apps/truth-or-dare
npm install
expo start
```

**Test on phone:**
- Install "Expo Go" app
- Scan QR code
- Play Truth or Dare! 🎭

## 🚀 What's Next

Once you have the mobile app working:

1. **Test the full game flow** - Create game, add players, play questions
2. **Customize the theme** - Edit colors and assets to match your brand
3. **Deploy to app stores** - Follow the deployment guide
4. **Create white-label versions** - Multiple branded apps from same code

Your modular architecture is now successfully running on mobile! 📱✨
