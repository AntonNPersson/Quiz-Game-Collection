"""
Truth or Dare GUI Launcher

This script launches the desktop GUI application for Truth or Dare.
Provides a modern, themeable interface for playing Truth or Dare games.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from games.truth_or_dare_app.ui.gui_app import main

if __name__ == "__main__":
    main()
