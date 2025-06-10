# Mobile Port - Quiz Game Collection

This directory contains the mobile application ports for the Quiz Game Collection, built with React Native and Expo for maximum compatibility and ease of deployment.

## Architecture

The mobile apps follow the same modular architecture as the desktop version:

```
mobile/
├── shared/                 # Shared components and utilities
│   ├── api/               # API client for Python backend
│   ├── components/        # Reusable UI components
│   ├── themes/           # Theme system (mirrors desktop themes)
│   ├── assets/           # Asset management system
│   └── utils/            # Utility functions
├── apps/                  # Individual game apps
│   ├── truth-or-dare/    # Truth or Dare mobile app
│   ├── trivia/           # Trivia mobile app (future)
│   └── speed-quiz/       # Speed Quiz mobile app (future)
└── backend/              # Python API server
    ├── api.py            # FastAPI server
    ├── models/           # API models
    └── routes/           # API routes
```

## Key Features

### 1. **Universal API Layer**
- FastAPI backend that exposes your Python core as REST endpoints
- Maintains all filtering capabilities
- Session management for mobile clients
- Real-time game state synchronization

### 2. **Modular Mobile Apps**
- Each game type is a separate React Native app
- Shared components and utilities
- Easy white-label deployment
- Platform-specific optimizations

### 3. **Asset Management System**
- Dynamic theme loading
- Asset pack support
- Easy customization for different markets
- Automatic resource optimization

### 4. **Cross-Platform Compatibility**
- Single codebase for Android and iOS
- Native performance with React Native
- Expo for easy deployment and updates

## Development Workflow

1. **Backend Setup**: Python FastAPI server exposes your core logic
2. **Mobile Development**: React Native apps consume the API
3. **Asset Management**: Dynamic loading of themes and assets
4. **Deployment**: Expo for easy app store deployment

## Getting Started

See individual app directories for specific setup instructions.
