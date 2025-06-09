"""
UI Theme System for Truth or Dare App

This module provides a flexible theming system that allows easy customization
of colors, fonts, and styling across the entire application.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class UITheme:
    """
    Complete UI theme configuration
    
    This class defines all visual aspects of the application,
    making it easy to create different themes or white-label versions.
    """
    
    # Theme metadata
    name: str
    description: str
    
    # Color scheme
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str
    surface_color: str
    text_color: str
    text_secondary_color: str
    success_color: str
    warning_color: str
    error_color: str
    
    # Button colors
    button_bg: str
    button_fg: str
    button_hover_bg: str
    button_active_bg: str
    
    # Special button colors
    truth_button_bg: str
    dare_button_bg: str
    skip_button_bg: str
    complete_button_bg: str
    
    # Fonts
    font_family: str
    font_size_small: int
    font_size_normal: int
    font_size_large: int
    font_size_title: int
    
    # Layout
    padding: int
    margin: int
    border_radius: int
    border_width: int
    
    # Window settings
    window_bg: str
    window_min_width: int
    window_min_height: int
    
    def get_font(self, size: str = "normal", weight: str = "normal") -> tuple:
        """Get font tuple for tkinter"""
        size_map = {
            "small": self.font_size_small,
            "normal": self.font_size_normal,
            "large": self.font_size_large,
            "title": self.font_size_title
        }
        return (self.font_family, size_map.get(size, self.font_size_normal), weight)
    
    def get_button_style(self, button_type: str = "default") -> Dict[str, Any]:
        """Get button styling configuration"""
        base_style = {
            "font": self.get_font("normal", "bold"),
            "relief": "flat",
            "borderwidth": self.border_width,
            "padx": self.padding,
            "pady": self.padding // 2,
            "cursor": "hand2"
        }
        
        if button_type == "truth":
            base_style.update({
                "bg": self.truth_button_bg,
                "fg": self.text_color,
                "activebackground": self.button_hover_bg
            })
        elif button_type == "dare":
            base_style.update({
                "bg": self.dare_button_bg,
                "fg": self.text_color,
                "activebackground": self.button_hover_bg
            })
        elif button_type == "skip":
            base_style.update({
                "bg": self.skip_button_bg,
                "fg": self.text_color,
                "activebackground": self.button_hover_bg
            })
        elif button_type == "complete":
            base_style.update({
                "bg": self.complete_button_bg,
                "fg": self.text_color,
                "activebackground": self.button_hover_bg
            })
        else:  # default
            base_style.update({
                "bg": self.button_bg,
                "fg": self.button_fg,
                "activebackground": self.button_hover_bg
            })
        
        return base_style


# Predefined themes
TRUTH_OR_DARE_THEME = UITheme(
    name="Truth or Dare Classic",
    description="Modern classic theme with improved styling",
    
    # Colors - Updated for better contrast and modern look
    primary_color="#E53E3E",      # Red
    secondary_color="#3182CE",     # Blue
    accent_color="#805AD5",        # Purple
    background_color="#F8FAFC",    # Slightly warmer light gray
    surface_color="#FFFFFF",       # White
    text_color="#1A202C",          # Darker text for better readability
    text_secondary_color="#4A5568", # Darker medium gray
    success_color="#38A169",       # Green
    warning_color="#D69E2E",       # Orange
    error_color="#E53E3E",         # Red
    
    # Buttons - Modern flat design
    button_bg="#4299E1",           # Modern blue
    button_fg="#FFFFFF",
    button_hover_bg="#3182CE",
    button_active_bg="#2B6CB0",
    
    # Special buttons
    truth_button_bg="#3182CE",     # Blue for truth
    dare_button_bg="#E53E3E",      # Red for dare
    skip_button_bg="#718096",      # Gray for skip
    complete_button_bg="#38A169",  # Green for complete
    
    # Fonts - Larger for better readability
    font_family="Segoe UI",
    font_size_small=11,
    font_size_normal=13,
    font_size_large=18,
    font_size_title=28,
    
    # Layout - More generous spacing
    padding=20,
    margin=15,
    border_radius=12,
    border_width=0,                # Flat design
    
    # Window - Larger minimum size for better UX
    window_bg="#F8FAFC",
    window_min_width=900,
    window_min_height=700
)

DARK_THEME = UITheme(
    name="Dark Mode",
    description="Modern dark theme for night gaming",
    
    # Colors - Updated for better contrast and modern dark design
    primary_color="#FF6B6B",       # Soft red
    secondary_color="#4ECDC4",     # Teal
    accent_color="#45B7D1",        # Light blue
    background_color="#1A202C",    # Darker background
    surface_color="#2D3748",       # Darker surface
    text_color="#F7FAFC",          # Better contrast light text
    text_secondary_color="#CBD5E0", # Better contrast medium light gray
    success_color="#68D391",       # Brighter green for dark theme
    warning_color="#F6AD55",       # Brighter orange
    error_color="#FC8181",         # Softer red
    
    # Buttons - Modern dark design
    button_bg="#4299E1",           # Modern blue
    button_fg="#F7FAFC",
    button_hover_bg="#3182CE",
    button_active_bg="#2B6CB0",
    
    # Special buttons
    truth_button_bg="#4ECDC4",     # Teal for truth
    dare_button_bg="#FF6B6B",      # Soft red for dare
    skip_button_bg="#718096",      # Gray for skip
    complete_button_bg="#68D391",  # Brighter green for complete
    
    # Fonts - Larger for better readability
    font_family="Segoe UI",
    font_size_small=11,
    font_size_normal=13,
    font_size_large=18,
    font_size_title=28,
    
    # Layout - More generous spacing
    padding=20,
    margin=15,
    border_radius=12,
    border_width=0,                # Flat design
    
    # Window - Larger minimum size for better UX
    window_bg="#1A202C",
    window_min_width=900,
    window_min_height=700
)

PARTY_THEME = UITheme(
    name="Party Mode",
    description="Bright and colorful theme for parties",
    
    # Colors
    primary_color="#FF1744",       # Bright red
    secondary_color="#00BCD4",     # Cyan
    accent_color="#FF9800",        # Orange
    background_color="#FFF3E0",    # Light orange
    surface_color="#FFFFFF",       # White
    text_color="#212121",          # Dark
    text_secondary_color="#757575", # Gray
    success_color="#4CAF50",       # Green
    warning_color="#FF9800",       # Orange
    error_color="#F44336",         # Red
    
    # Buttons
    button_bg="#673AB7",           # Purple
    button_fg="#FFFFFF",
    button_hover_bg="#512DA8",
    button_active_bg="#4527A0",
    
    # Special buttons
    truth_button_bg="#00BCD4",     # Cyan for truth
    dare_button_bg="#FF1744",      # Bright red for dare
    skip_button_bg="#9E9E9E",      # Gray for skip
    complete_button_bg="#4CAF50",  # Green for complete
    
    # Fonts
    font_family="Segoe UI",
    font_size_small=11,
    font_size_normal=13,
    font_size_large=17,
    font_size_title=26,
    
    # Layout
    padding=18,
    margin=12,
    border_radius=12,
    border_width=3,
    
    # Window
    window_bg="#FFF3E0",
    window_min_width=800,
    window_min_height=600
)

# Theme registry
AVAILABLE_THEMES = {
    "classic": TRUTH_OR_DARE_THEME,
    "dark": DARK_THEME,
    "party": PARTY_THEME
}

def get_theme(theme_name: str = "classic") -> UITheme:
    """Get a theme by name"""
    return AVAILABLE_THEMES.get(theme_name, TRUTH_OR_DARE_THEME)

def list_themes() -> Dict[str, str]:
    """Get list of available themes with descriptions"""
    return {name: theme.description for name, theme in AVAILABLE_THEMES.items()}
