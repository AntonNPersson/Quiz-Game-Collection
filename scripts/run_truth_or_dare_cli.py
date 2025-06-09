"""
Quick launcher for the Truth or Dare CLI

This script provides an easy way to launch the Truth or Dare CLI application.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from games.truth_or_dare_app.cli import main

if __name__ == "__main__":
    main()
