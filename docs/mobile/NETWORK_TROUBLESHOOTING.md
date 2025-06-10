# Mobile App Network Troubleshooting

## Common Issues and Solutions

### 1. "Failed to download remote update" Error

This Java IOException typically occurs due to network connectivity issues between Expo Go and your development server.

#### Solutions to Try:

**Option A: Use Tunnel Mode (Recommended)**
```bash
cd mobile/apps/truth-or-dare
npx expo start --tunnel
```
- This creates a secure tunnel through Expo's servers
- Works with corporate firewalls and complex network setups
- May require installing ngrok globally

**Option B: Check Network Connection**
- Ensure your phone and computer are on the same WiFi network
- Disable VPN on both devices
- Try mobile hotspot if WiFi has restrictions

**Option C: Use Development Build**
```bash
cd mobile/apps/truth-or-dare
npx expo start --dev-client
```

**Option D: Clear Expo Go Cache**
- Close Expo Go completely
- Reopen and try scanning QR code again
- Or shake phone in Expo Go → "Reload"

### 2. Port Conflicts

If you see "Port 8081 is being used":
```bash
# Kill existing processes
npx expo start --port 8082
# Or
npx expo start --clear
```

### 3. Alternative Testing Methods

**Web Browser Testing:**
```bash
npx expo install react-native-web@~0.19.6 react-dom@18.2.0 @expo/webpack-config@^19.0.0
npx expo start --web
```

**Android Emulator:**
```bash
npx expo start
# Press 'a' to open Android emulator
```

### 4. Network Configuration

**Check Firewall:**
- Windows Defender may block Metro bundler
- Allow Node.js through Windows Firewall
- Port 8081 needs to be accessible

**Router Settings:**
- Some routers block device-to-device communication
- Try connecting both devices to mobile hotspot
- Check if "AP Isolation" is disabled on router

### 5. Expo Go Version

- Ensure latest Expo Go version from Play Store
- Older versions may have compatibility issues
- Try uninstalling and reinstalling Expo Go

### 6. Manual IP Connection

If QR code fails, try manual connection:
1. Note your computer's IP address (ipconfig)
2. In Expo Go, manually enter: `exp://YOUR_IP:8081`

### 7. Development Server Logs

Check terminal for specific error messages:
- Metro bundler errors
- Network binding issues
- JavaScript bundle errors

## Quick Fix Commands

```bash
# Restart everything clean
cd mobile/apps/truth-or-dare
npx expo start --clear --tunnel

# Alternative ports
npx expo start --port 8082 --tunnel

# Force reload
npx expo r
```

## Still Having Issues?

1. **Try the web version** (works in browser)
2. **Use Android emulator** instead of physical device
3. **Check corporate network restrictions**
4. **Try different WiFi network**
5. **Use mobile hotspot for testing**

The simple test app should work once network connectivity is established.
