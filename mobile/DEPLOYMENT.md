# Mobile Deployment Guide - Quiz Game Collection

This guide covers deploying the mobile apps and backend API for the Quiz Game Collection.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile Apps   │    │   FastAPI       │    │   Python Core   │
│   (React Native)│◄──►│   Backend       │◄──►│   (Desktop App) │
│                 │    │                 │    │                 │
│ • Truth or Dare │    │ • REST API      │    │ • Filter System │
│ • Future Games  │    │ • Game Sessions │    │ • Question DB   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

### For Backend Development
- Python 3.8+
- Your existing Quiz Game Collection project
- FastAPI and dependencies (see `mobile/backend/requirements.txt`)

### For Mobile Development
- Node.js 16+
- Expo CLI: `npm install -g @expo/cli`
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)

## Backend Deployment

### 1. Local Development

```bash
# Navigate to backend directory
cd mobile/backend

# Install dependencies
pip install -r requirements.txt

# Start development server
python api.py
```

The API will be available at `http://localhost:8000`

### 2. Production Deployment

#### Option A: Simple Cloud Deployment (Heroku, Railway, etc.)

Create `mobile/backend/Procfile`:
```
web: gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

Create `mobile/backend/runtime.txt`:
```
python-3.11.0
```

#### Option B: Docker Deployment

Create `mobile/backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy database from parent directory
COPY ../../data/databases/game_questions.db data/databases/

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Option C: VPS Deployment

```bash
# On your server
git clone your-repo
cd Quiz-Game-Collection/mobile/backend

# Install dependencies
pip install -r requirements.txt

# Run with gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 3. Environment Configuration

Update `mobile/shared/api/GameAPI.js`:
```javascript
const API_CONFIG = {
  baseURL: __DEV__ ? 'http://localhost:8000' : 'https://your-api-domain.com',
  timeout: 10000,
  retries: 3,
};
```

## Mobile App Deployment

### 1. Setup Development Environment

```bash
# Navigate to Truth or Dare app
cd mobile/apps/truth-or-dare

# Install dependencies
npm install

# Start development server
expo start
```

### 2. Testing on Devices

#### Android
```bash
# Connect Android device or start emulator
expo start --android
```

#### iOS (macOS only)
```bash
# Connect iOS device or start simulator
expo start --ios
```

### 3. Building for Production

#### Android APK (Development Build)
```bash
# Build APK
expo build:android

# Or for newer Expo versions
eas build --platform android
```

#### iOS App (Development Build)
```bash
# Build iOS app
expo build:ios

# Or for newer Expo versions
eas build --platform ios
```

### 4. App Store Deployment

#### Google Play Store
1. Build signed APK/AAB
2. Create Google Play Console account
3. Upload app bundle
4. Fill out store listing
5. Submit for review

#### Apple App Store
1. Build signed IPA
2. Create Apple Developer account
3. Upload to App Store Connect
4. Fill out app information
5. Submit for review

## Asset Pack Customization

### Creating Custom Asset Packs

```javascript
// custom-asset-pack.js
export const CUSTOM_ASSET_PACK = {
  app: {
    name: 'Your Custom Game',
    version: '1.0.0',
    bundle_id: 'com.yourcompany.customgame',
  },
  themes: {
    custom: {
      name: 'Custom Theme',
      colors: {
        primary: '#YOUR_COLOR',
        secondary: '#YOUR_COLOR',
        // ... other colors
      },
      // ... other theme properties
    },
  },
  icons: {
    // Custom icons
  },
};

// In your app
import { assetManager } from '../shared/assets/AssetManager';
import { CUSTOM_ASSET_PACK } from './custom-asset-pack';

assetManager.loadAssetPack(CUSTOM_ASSET_PACK);
```

### White-Label Deployment

1. **Create new app directory**:
   ```bash
   cp -r mobile/apps/truth-or-dare mobile/apps/your-custom-game
   ```

2. **Update package.json**:
   ```json
   {
     "name": "your-custom-game",
     "version": "1.0.0",
     "description": "Your custom game description"
   }
   ```

3. **Update app.json**:
   ```json
   {
     "expo": {
       "name": "Your Custom Game",
       "slug": "your-custom-game",
       "version": "1.0.0",
       "orientation": "portrait",
       "icon": "./assets/icon.png",
       "splash": {
         "image": "./assets/splash.png"
       },
       "android": {
         "package": "com.yourcompany.customgame"
       },
       "ios": {
         "bundleIdentifier": "com.yourcompany.customgame"
       }
     }
   }
   ```

4. **Load custom asset pack**:
   ```javascript
   // In App.js
   import { CUSTOM_ASSET_PACK } from './assets/custom-asset-pack';
   
   useEffect(() => {
     assetManager.loadAssetPack(CUSTOM_ASSET_PACK);
   }, []);
   ```

## Monitoring and Analytics

### Backend Monitoring
```python
# Add to api.py
import logging
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.2f}s")
    return response
```

### Mobile Analytics
```javascript
// Add analytics tracking
import * as Analytics from 'expo-analytics';

// Track game events
Analytics.track('game_started', {
  game_type: 'truth_or_dare',
  player_count: players.length,
});
```

## Scaling Considerations

### Backend Scaling
- Use Redis for session storage
- Implement database connection pooling
- Add rate limiting
- Use CDN for static assets

### Mobile App Optimization
- Implement offline mode
- Add caching for API responses
- Optimize bundle size
- Use code splitting

## Security

### Backend Security
```python
# Add security headers
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)

# Add rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/games")
@limiter.limit("10/minute")
async def get_games(request: Request):
    # ... endpoint logic
```

### Mobile Security
- Use HTTPS only
- Implement certificate pinning
- Validate all API responses
- Store sensitive data securely

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check network connectivity
   - Verify API URL configuration
   - Check CORS settings

2. **Build Failures**
   - Clear Expo cache: `expo r -c`
   - Update dependencies: `npm update`
   - Check platform-specific requirements

3. **Performance Issues**
   - Enable Hermes (Android)
   - Optimize images and assets
   - Use FlatList for large lists
   - Implement proper state management

### Debug Commands

```bash
# Clear Expo cache
expo r -c

# Check bundle size
expo bundle-size

# Debug Android
expo start --android --dev-client

# Debug iOS
expo start --ios --dev-client
```

## Support

For deployment issues:
1. Check the logs for specific error messages
2. Verify all environment variables are set
3. Test API endpoints manually
4. Check mobile app configuration

The modular architecture ensures that each component can be deployed and scaled independently, making it easy to maintain and update your quiz game collection.
