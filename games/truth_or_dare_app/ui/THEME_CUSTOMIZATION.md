# Theme Customization Guide

This guide shows you how to easily customize the appearance of the Truth or Dare application by creating new themes or modifying existing ones.

## Quick Theme Creation

### 1. Create a New Theme

Add a new theme to `themes.py`:

```python
CUSTOM_THEME = UITheme(
    name="My Custom Theme",
    description="My personalized theme",
    
    # Main colors
    primary_color="#FF5722",        # Orange
    secondary_color="#2196F3",      # Blue
    accent_color="#4CAF50",         # Green
    background_color="#FAFAFA",     # Light gray
    surface_color="#FFFFFF",        # White
    text_color="#212121",           # Dark gray
    text_secondary_color="#757575", # Medium gray
    success_color="#4CAF50",        # Green
    warning_color="#FF9800",        # Orange
    error_color="#F44336",          # Red
    
    # Button colors
    button_bg="#607D8B",           # Blue gray
    button_fg="#FFFFFF",           # White text
    button_hover_bg="#455A64",     # Darker blue gray
    button_active_bg="#37474F",    # Even darker
    
    # Special buttons (Truth/Dare specific)
    truth_button_bg="#2196F3",     # Blue for truth
    dare_button_bg="#FF5722",      # Orange for dare
    skip_button_bg="#9E9E9E",      # Gray for skip
    complete_button_bg="#4CAF50",  # Green for complete
    
    # Typography
    font_family="Arial",           # Font family
    font_size_small=10,           # Small text
    font_size_normal=12,          # Normal text
    font_size_large=16,           # Large text
    font_size_title=24,           # Title text
    
    # Layout
    padding=15,                   # Internal spacing
    margin=10,                    # External spacing
    border_radius=8,              # Rounded corners
    border_width=2,               # Border thickness
    
    # Window
    window_bg="#FAFAFA",          # Window background
    window_min_width=800,         # Minimum width
    window_min_height=600         # Minimum height
)
```

### 2. Register Your Theme

Add it to the theme registry:

```python
AVAILABLE_THEMES = {
    "classic": TRUTH_OR_DARE_THEME,
    "dark": DARK_THEME,
    "party": PARTY_THEME,
    "custom": CUSTOM_THEME,  # Add your theme here
}
```

### 3. Use Your Theme

Launch the app with your theme:

```python
app = TruthOrDareGUI(theme_name="custom")
```

## Color Schemes

### Material Design Colors
```python
# Material Red
primary_color="#F44336"
secondary_color="#FFCDD2"

# Material Blue
primary_color="#2196F3"
secondary_color="#BBDEFB"

# Material Green
primary_color="#4CAF50"
secondary_color="#C8E6C9"
```

### Popular Color Palettes

#### Sunset Theme
```python
primary_color="#FF6B35"      # Orange
secondary_color="#F7931E"    # Yellow-orange
accent_color="#FFD23F"       # Yellow
background_color="#FFF8E1"   # Light yellow
```

#### Ocean Theme
```python
primary_color="#006064"      # Dark cyan
secondary_color="#00ACC1"    # Cyan
accent_color="#26C6DA"       # Light cyan
background_color="#E0F2F1"   # Very light cyan
```

#### Forest Theme
```python
primary_color="#2E7D32"      # Dark green
secondary_color="#4CAF50"    # Green
accent_color="#81C784"       # Light green
background_color="#E8F5E8"   # Very light green
```

## Typography Customization

### Font Options
```python
# System fonts
font_family="Segoe UI"       # Windows default
font_family="Arial"          # Cross-platform
font_family="Helvetica"      # Mac/Linux
font_family="Roboto"         # Modern

# Font sizes for different screen sizes
# Small screens (laptops)
font_size_small=9
font_size_normal=11
font_size_large=14
font_size_title=20

# Large screens (desktops)
font_size_small=11
font_size_normal=13
font_size_large=17
font_size_title=26
```

## Layout Customization

### Compact Layout
```python
padding=10
margin=8
border_radius=4
border_width=1
window_min_width=700
window_min_height=500
```

### Spacious Layout
```python
padding=20
margin=15
border_radius=12
border_width=3
window_min_width=900
window_min_height=700
```

## Button Styling

### Flat Design
```python
border_radius=0
border_width=0
```

### Rounded Design
```python
border_radius=20
border_width=2
```

### Gradient Effect (using similar colors)
```python
button_bg="#4CAF50"
button_hover_bg="#45A049"
button_active_bg="#3D8B40"
```

## Advanced Customization

### Creating Theme Variants

You can create multiple variants of a theme:

```python
def create_theme_variant(base_theme, variant_name, color_overrides):
    """Create a theme variant with color overrides"""
    theme_dict = base_theme.__dict__.copy()
    theme_dict.update(color_overrides)
    theme_dict['name'] = f"{base_theme.name} - {variant_name}"
    return UITheme(**theme_dict)

# Create a dark variant of the classic theme
CLASSIC_DARK = create_theme_variant(
    TRUTH_OR_DARE_THEME,
    "Dark",
    {
        'background_color': '#2C3E50',
        'surface_color': '#34495E',
        'text_color': '#ECF0F1',
        'window_bg': '#2C3E50'
    }
)
```

### Dynamic Theme Loading

Load themes from configuration files:

```python
import json

def load_theme_from_file(filepath):
    """Load theme from JSON file"""
    with open(filepath, 'r') as f:
        theme_data = json.load(f)
    return UITheme(**theme_data)

# Usage
custom_theme = load_theme_from_file('my_theme.json')
```

## Testing Your Theme

1. **Launch with your theme**:
   ```bash
   python scripts/run_truth_or_dare_gui.py
   ```

2. **Test all screens**:
   - Welcome screen
   - Game setup
   - Game play
   - Results screen
   - Settings dialog

3. **Check readability**:
   - Text contrast
   - Button visibility
   - Color accessibility

## Tips for Great Themes

1. **High Contrast**: Ensure text is readable against backgrounds
2. **Consistent Colors**: Use a limited color palette
3. **Accessibility**: Consider color-blind users
4. **Brand Alignment**: Match your organization's colors
5. **User Testing**: Get feedback from actual users

## Example: Creating a "Neon" Theme

```python
NEON_THEME = UITheme(
    name="Neon Nights",
    description="Bright neon theme for night parties",
    
    primary_color="#FF0080",        # Hot pink
    secondary_color="#00FFFF",      # Cyan
    accent_color="#FFFF00",         # Yellow
    background_color="#000000",     # Black
    surface_color="#1A1A1A",       # Dark gray
    text_color="#FFFFFF",           # White
    text_secondary_color="#CCCCCC", # Light gray
    success_color="#00FF00",        # Lime green
    warning_color="#FF8000",        # Orange
    error_color="#FF0040",          # Red-pink
    
    button_bg="#FF0080",
    button_fg="#FFFFFF",
    button_hover_bg="#CC0066",
    button_active_bg="#990050",
    
    truth_button_bg="#00FFFF",
    dare_button_bg="#FF0080",
    skip_button_bg="#666666",
    complete_button_bg="#00FF00",
    
    font_family="Arial Black",
    font_size_small=11,
    font_size_normal=13,
    font_size_large=17,
    font_size_title=28,
    
    padding=18,
    margin=12,
    border_radius=15,
    border_width=3,
    
    window_bg="#000000",
    window_min_width=850,
    window_min_height=650
)
```

This creates a bold, high-contrast theme perfect for party environments!
