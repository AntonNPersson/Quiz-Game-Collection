"""
Truth or Dare UI Module

This module provides the graphical user interface components for the Truth or Dare application.
Includes themeable GUI components and desktop application functionality.
"""

from .themes import UITheme, get_theme, list_themes, AVAILABLE_THEMES
from .gui_app import TruthOrDareGUI

__all__ = [
    'UITheme',
    'get_theme', 
    'list_themes',
    'AVAILABLE_THEMES',
    'TruthOrDareGUI'
]
