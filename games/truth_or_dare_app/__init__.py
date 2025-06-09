"""
Truth or Dare Game Application

A complete Truth or Dare game built using the Quiz Game Collection framework.
This application demonstrates how to use the framework to create a specific
game type with custom logic and user interface.
"""

from .app import TruthOrDareApp
from .cli import TruthOrDareCLI

__all__ = [
    'TruthOrDareApp',
    'TruthOrDareCLI'
]
