/**
 * Asset Management System for Quiz Game Collection Mobile Apps
 * 
 * This system provides dynamic asset loading, theme management, and easy
 * customization for white-label deployments. It mirrors the desktop theme
 * system but optimized for mobile platforms.
 */

import { Platform } from 'react-native';

/**
 * Asset pack structure for easy customization
 */
export const DEFAULT_ASSET_PACK = {
  // App metadata
  app: {
    name: 'Truth or Dare',
    version: '1.0.0',
    bundle_id: 'com.quizgames.truthordare',
  },
  
  // Theme configuration (mirrors desktop themes)
  themes: {
    classic: {
      name: 'Truth or Dare Classic',
      colors: {
        primary: '#E53E3E',
        secondary: '#3182CE',
        accent: '#805AD5',
        background: '#F8FAFC',
        surface: '#FFFFFF',
        text: '#1A202C',
        textSecondary: '#4A5568',
        success: '#38A169',
        warning: '#D69E2E',
        error: '#E53E3E',
        
        // Button colors
        buttonPrimary: '#4299E1',
        buttonSecondary: '#718096',
        truthButton: '#3182CE',
        dareButton: '#E53E3E',
        skipButton: '#718096',
        completeButton: '#38A169',
      },
      fonts: {
        regular: Platform.select({
          ios: 'System',
          android: 'Roboto',
        }),
        bold: Platform.select({
          ios: 'System',
          android: 'Roboto',
        }),
        sizes: {
          small: 12,
          normal: 16,
          large: 20,
          title: 28,
          header: 24,
        },
      },
      spacing: {
        xs: 4,
        sm: 8,
        md: 16,
        lg: 24,
        xl: 32,
      },
      borderRadius: {
        small: 8,
        medium: 12,
        large: 16,
      },
    },
    
    dark: {
      name: 'Dark Mode',
      colors: {
        primary: '#FF6B6B',
        secondary: '#4ECDC4',
        accent: '#45B7D1',
        background: '#1A202C',
        surface: '#2D3748',
        text: '#F7FAFC',
        textSecondary: '#CBD5E0',
        success: '#68D391',
        warning: '#F6AD55',
        error: '#FC8181',
        
        // Button colors
        buttonPrimary: '#4299E1',
        buttonSecondary: '#718096',
        truthButton: '#4ECDC4',
        dareButton: '#FF6B6B',
        skipButton: '#718096',
        completeButton: '#68D391',
      },
      fonts: {
        regular: Platform.select({
          ios: 'System',
          android: 'Roboto',
        }),
        bold: Platform.select({
          ios: 'System',
          android: 'Roboto',
        }),
        sizes: {
          small: 12,
          normal: 16,
          large: 20,
          title: 28,
          header: 24,
        },
      },
      spacing: {
        xs: 4,
        sm: 8,
        md: 16,
        lg: 24,
        xl: 32,
      },
      borderRadius: {
        small: 8,
        medium: 12,
        large: 16,
      },
    },
    
    party: {
      name: 'Party Mode',
      colors: {
        primary: '#FF1744',
        secondary: '#00BCD4',
        accent: '#FF9800',
        background: '#FFF3E0',
        surface: '#FFFFFF',
        text: '#212121',
        textSecondary: '#757575',
        success: '#4CAF50',
        warning: '#FF9800',
        error: '#F44336',
        
        // Button colors
        buttonPrimary: '#673AB7',
        buttonSecondary: '#9E9E9E',
        truthButton: '#00BCD4',
        dareButton: '#FF1744',
        skipButton: '#9E9E9E',
        completeButton: '#4CAF50',
      },
      fonts: {
        regular: Platform.select({
          ios: 'System',
          android: 'Roboto',
        }),
        bold: Platform.select({
          ios: 'System',
          android: 'Roboto',
        }),
        sizes: {
          small: 12,
          normal: 16,
          large: 20,
          title: 28,
          header: 24,
        },
      },
      spacing: {
        xs: 4,
        sm: 8,
        md: 16,
        lg: 24,
        xl: 32,
      },
      borderRadius: {
        small: 8,
        medium: 12,
        large: 16,
      },
    },
  },
  
  // Icons and images (can be overridden by asset packs)
  icons: {
    truth: '🤔',
    dare: '💪',
    skip: '⏭️',
    complete: '✅',
    settings: '⚙️',
    stats: '📊',
    players: '👥',
    question: '❓',
    trophy: '🏆',
    party: '🎉',
  },
  
  // Sounds (optional)
  sounds: {
    buttonPress: null,
    questionComplete: null,
    gameComplete: null,
  },
  
  // Animations
  animations: {
    duration: {
      fast: 200,
      normal: 300,
      slow: 500,
    },
    easing: 'ease-in-out',
  },
};

/**
 * Asset Manager class for handling themes and assets
 */
class AssetManager {
  constructor() {
    this.currentAssetPack = DEFAULT_ASSET_PACK;
    this.currentTheme = 'classic';
  }
  
  /**
   * Load a custom asset pack
   * @param {Object} assetPack - Custom asset pack configuration
   */
  loadAssetPack(assetPack) {
    this.currentAssetPack = {
      ...DEFAULT_ASSET_PACK,
      ...assetPack,
      themes: {
        ...DEFAULT_ASSET_PACK.themes,
        ...assetPack.themes,
      },
    };
  }
  
  /**
   * Set the current theme
   * @param {string} themeName - Name of the theme to use
   */
  setTheme(themeName) {
    if (this.currentAssetPack.themes[themeName]) {
      this.currentTheme = themeName;
    } else {
      console.warn(`Theme '${themeName}' not found, using default`);
      this.currentTheme = 'classic';
    }
  }
  
  /**
   * Get the current theme configuration
   * @returns {Object} Current theme configuration
   */
  getTheme() {
    return this.currentAssetPack.themes[this.currentTheme];
  }
  
  /**
   * Get app metadata
   * @returns {Object} App metadata
   */
  getAppInfo() {
    return this.currentAssetPack.app;
  }
  
  /**
   * Get icon by name
   * @param {string} iconName - Name of the icon
   * @returns {string} Icon character or null
   */
  getIcon(iconName) {
    return this.currentAssetPack.icons[iconName] || null;
  }
  
  /**
   * Get sound by name
   * @param {string} soundName - Name of the sound
   * @returns {string|null} Sound file path or null
   */
  getSound(soundName) {
    return this.currentAssetPack.sounds[soundName] || null;
  }
  
  /**
   * Get animation configuration
   * @returns {Object} Animation configuration
   */
  getAnimations() {
    return this.currentAssetPack.animations;
  }
  
  /**
   * Get available themes
   * @returns {Array} Array of theme names and descriptions
   */
  getAvailableThemes() {
    return Object.keys(this.currentAssetPack.themes).map(key => ({
      id: key,
      name: this.currentAssetPack.themes[key].name,
      colors: this.currentAssetPack.themes[key].colors,
    }));
  }
  
  /**
   * Create a style object for React Native components
   * @param {Object} styleConfig - Style configuration
   * @returns {Object} React Native style object
   */
  createStyle(styleConfig) {
    const theme = this.getTheme();
    const style = {};
    
    // Apply colors
    if (styleConfig.backgroundColor) {
      style.backgroundColor = theme.colors[styleConfig.backgroundColor] || styleConfig.backgroundColor;
    }
    if (styleConfig.color) {
      style.color = theme.colors[styleConfig.color] || styleConfig.color;
    }
    if (styleConfig.borderColor) {
      style.borderColor = theme.colors[styleConfig.borderColor] || styleConfig.borderColor;
    }
    
    // Apply spacing
    if (styleConfig.padding) {
      style.padding = theme.spacing[styleConfig.padding] || styleConfig.padding;
    }
    if (styleConfig.margin) {
      style.margin = theme.spacing[styleConfig.margin] || styleConfig.margin;
    }
    
    // Apply border radius
    if (styleConfig.borderRadius) {
      style.borderRadius = theme.borderRadius[styleConfig.borderRadius] || styleConfig.borderRadius;
    }
    
    // Apply fonts
    if (styleConfig.fontSize) {
      style.fontSize = theme.fonts.sizes[styleConfig.fontSize] || styleConfig.fontSize;
    }
    if (styleConfig.fontFamily) {
      style.fontFamily = theme.fonts[styleConfig.fontFamily] || styleConfig.fontFamily;
    }
    
    return style;
  }
  
  /**
   * Get button style for specific button type
   * @param {string} buttonType - Type of button (primary, truth, dare, etc.)
   * @returns {Object} Button style configuration
   */
  getButtonStyle(buttonType = 'primary') {
    const theme = this.getTheme();
    const baseStyle = {
      paddingHorizontal: theme.spacing.md,
      paddingVertical: theme.spacing.sm,
      borderRadius: theme.borderRadius.medium,
      alignItems: 'center',
      justifyContent: 'center',
    };
    
    switch (buttonType) {
      case 'truth':
        return {
          ...baseStyle,
          backgroundColor: theme.colors.truthButton,
        };
      case 'dare':
        return {
          ...baseStyle,
          backgroundColor: theme.colors.dareButton,
        };
      case 'skip':
        return {
          ...baseStyle,
          backgroundColor: theme.colors.skipButton,
        };
      case 'complete':
        return {
          ...baseStyle,
          backgroundColor: theme.colors.completeButton,
        };
      case 'secondary':
        return {
          ...baseStyle,
          backgroundColor: theme.colors.buttonSecondary,
        };
      default: // primary
        return {
          ...baseStyle,
          backgroundColor: theme.colors.buttonPrimary,
        };
    }
  }
  
  /**
   * Get text style for specific text type
   * @param {string} textType - Type of text (title, header, normal, etc.)
   * @param {Object} options - Additional style options
   * @returns {Object} Text style configuration
   */
  getTextStyle(textType = 'normal', options = {}) {
    const theme = this.getTheme();
    const baseStyle = {
      fontFamily: theme.fonts.regular,
      color: theme.colors.text,
    };
    
    switch (textType) {
      case 'title':
        return {
          ...baseStyle,
          fontSize: theme.fonts.sizes.title,
          fontFamily: theme.fonts.bold,
          fontWeight: 'bold',
          ...options,
        };
      case 'header':
        return {
          ...baseStyle,
          fontSize: theme.fonts.sizes.header,
          fontFamily: theme.fonts.bold,
          fontWeight: 'bold',
          ...options,
        };
      case 'large':
        return {
          ...baseStyle,
          fontSize: theme.fonts.sizes.large,
          ...options,
        };
      case 'small':
        return {
          ...baseStyle,
          fontSize: theme.fonts.sizes.small,
          color: theme.colors.textSecondary,
          ...options,
        };
      default: // normal
        return {
          ...baseStyle,
          fontSize: theme.fonts.sizes.normal,
          ...options,
        };
    }
  }
}

// Export singleton instance
export const assetManager = new AssetManager();

// Export utility functions
export const getTheme = () => assetManager.getTheme();
export const setTheme = (themeName) => assetManager.setTheme(themeName);
export const getIcon = (iconName) => assetManager.getIcon(iconName);
export const getButtonStyle = (buttonType) => assetManager.getButtonStyle(buttonType);
export const getTextStyle = (textType, options) => assetManager.getTextStyle(textType, options);
export const createStyle = (styleConfig) => assetManager.createStyle(styleConfig);

export default assetManager;
