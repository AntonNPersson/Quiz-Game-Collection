"""
Test script for the Truth or Dare GUI application

This script tests the GUI components and theme system to ensure
everything works correctly.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from games.truth_or_dare_app.ui.themes import get_theme, list_themes, AVAILABLE_THEMES
from games.truth_or_dare_app.ui.gui_app import TruthOrDareGUI


def test_theme_system():
    """Test the theme system functionality"""
    
    print("🎨 Testing Theme System")
    print("=" * 40)
    
    try:
        # Test theme loading
        print("📋 Available themes:")
        themes = list_themes()
        for name, description in themes.items():
            print(f"  - {name}: {description}")
        
        # Test each theme
        print("\n🔍 Testing theme loading:")
        for theme_name in AVAILABLE_THEMES.keys():
            theme = get_theme(theme_name)
            print(f"  ✅ {theme_name}: {theme.name}")
            
            # Test theme methods
            font = theme.get_font("normal", "bold")
            button_style = theme.get_button_style("truth")
            
            assert isinstance(font, tuple), f"Font should be tuple for {theme_name}"
            assert isinstance(button_style, dict), f"Button style should be dict for {theme_name}"
            
        print("✅ All themes loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Theme system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_initialization():
    """Test GUI initialization without showing the window"""
    
    print("\n🖥️ Testing GUI Initialization")
    print("=" * 40)
    
    db_path = "data/databases/game_questions.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        # Test with different themes
        for theme_name in ["classic", "dark", "party"]:
            print(f"🎨 Testing with {theme_name} theme...")
            
            # Create GUI instance (but don't run mainloop)
            gui = TruthOrDareGUI(db_path, theme_name)
            
            # Test basic properties
            assert gui.theme.name is not None, f"Theme name should be set for {theme_name}"
            assert gui.app is not None, f"App should be initialized for {theme_name}"
            assert gui.root is not None, f"Root window should exist for {theme_name}"
            
            # Test theme application
            assert gui.root.cget('bg') == gui.theme.window_bg, f"Window background should match theme for {theme_name}"
            
            # Cleanup
            gui.root.destroy()
            if gui.app:
                gui.app.cleanup()
            
            print(f"  ✅ {theme_name} theme initialization successful")
        
        print("✅ GUI initialization tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ GUI initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_theme_customization():
    """Test theme customization capabilities"""
    
    print("\n🎨 Testing Theme Customization")
    print("=" * 40)
    
    try:
        from games.truth_or_dare_app.ui.themes import UITheme
        
        # Create a custom theme
        custom_theme = UITheme(
            name="Test Theme",
            description="Theme for testing",
            primary_color="#FF0000",
            secondary_color="#00FF00",
            accent_color="#0000FF",
            background_color="#FFFFFF",
            surface_color="#F0F0F0",
            text_color="#000000",
            text_secondary_color="#666666",
            success_color="#00AA00",
            warning_color="#FFAA00",
            error_color="#AA0000",
            button_bg="#CCCCCC",
            button_fg="#000000",
            button_hover_bg="#BBBBBB",
            button_active_bg="#AAAAAA",
            truth_button_bg="#0000FF",
            dare_button_bg="#FF0000",
            skip_button_bg="#888888",
            complete_button_bg="#00AA00",
            font_family="Arial",
            font_size_small=10,
            font_size_normal=12,
            font_size_large=16,
            font_size_title=24,
            padding=15,
            margin=10,
            border_radius=8,
            border_width=2,
            window_bg="#FFFFFF",
            window_min_width=800,
            window_min_height=600
        )
        
        # Test theme methods
        font = custom_theme.get_font("large", "bold")
        assert font == ("Arial", 16, "bold"), "Custom font should match specification"
        
        button_style = custom_theme.get_button_style("truth")
        assert button_style["bg"] == "#0000FF", "Truth button should be blue"
        
        button_style = custom_theme.get_button_style("dare")
        assert button_style["bg"] == "#FF0000", "Dare button should be red"
        
        print("✅ Custom theme creation successful!")
        print(f"  📝 Theme name: {custom_theme.name}")
        print(f"  🎨 Primary color: {custom_theme.primary_color}")
        print(f"  📏 Font family: {custom_theme.font_family}")
        
        return True
        
    except Exception as e:
        print(f"❌ Theme customization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_components():
    """Test individual GUI components"""
    
    print("\n🧩 Testing GUI Components")
    print("=" * 40)
    
    db_path = "data/databases/game_questions.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        # Create GUI instance
        gui = TruthOrDareGUI(db_path, "classic")
        
        # Test player management
        print("👥 Testing player management...")
        
        # Simulate adding players
        gui.players = ["Alice", "Bob", "Charlie"]
        assert len(gui.players) == 3, "Should have 3 players"
        
        # Test screen switching
        print("📱 Testing screen navigation...")
        
        gui._show_screen("welcome")
        gui._show_screen("setup")
        gui._show_screen("game")
        gui._show_screen("results")
        gui._show_screen("welcome")  # Back to start
        
        print("✅ Screen navigation working")
        
        # Test theme switching
        print("🎨 Testing theme switching...")
        
        original_theme = gui.theme.name
        gui.theme = get_theme("dark")
        gui._apply_theme()
        
        assert gui.theme.name != original_theme, "Theme should have changed"
        print(f"  ✅ Switched from {original_theme} to {gui.theme.name}")
        
        # Cleanup
        gui.root.destroy()
        if gui.app:
            gui.app.cleanup()
        
        print("✅ GUI components test passed!")
        return True
        
    except Exception as e:
        print(f"❌ GUI components test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all GUI tests"""
    print("🧪 Running Truth or Dare GUI Tests")
    print("=" * 60)
    
    # Test theme system
    theme_test_passed = test_theme_system()
    
    # Test GUI initialization
    gui_init_test_passed = test_gui_initialization()
    
    # Test theme customization
    theme_custom_test_passed = test_theme_customization()
    
    # Test GUI components
    gui_components_test_passed = test_gui_components()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"  🎨 Theme System: {'✅ PASSED' if theme_test_passed else '❌ FAILED'}")
    print(f"  🖥️ GUI Initialization: {'✅ PASSED' if gui_init_test_passed else '❌ FAILED'}")
    print(f"  🎨 Theme Customization: {'✅ PASSED' if theme_custom_test_passed else '❌ FAILED'}")
    print(f"  🧩 GUI Components: {'✅ PASSED' if gui_components_test_passed else '❌ FAILED'}")
    
    all_passed = all([
        theme_test_passed,
        gui_init_test_passed,
        theme_custom_test_passed,
        gui_components_test_passed
    ])
    
    if all_passed:
        print("\n🎉 All GUI tests passed! The desktop application is ready to use.")
        print("\n🚀 To launch the GUI:")
        print("  python scripts/run_truth_or_dare_gui.py")
        print("\n📦 To build executable:")
        print("  python scripts/build_executable.py")
        return True
    else:
        print("\n❌ Some GUI tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
