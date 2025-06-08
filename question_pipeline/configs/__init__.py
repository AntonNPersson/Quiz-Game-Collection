"""
Game mode configurations and handlers
"""

from .game_mode_handlers import (
    TriviaGameModeHandler,
    FlashcardGameModeHandler,
    SpeedQuizGameModeHandler,
    TruthOrDareGameModeHandler
)

from .game_configs import (
    GameModeConfig,
    TriviaConfig,
    FlashcardConfig,
    SpeedQuizConfig,
    TruthOrDareConfig,
    get_default_config
)

__all__ = [
    'TriviaGameModeHandler',
    'FlashcardGameModeHandler', 
    'SpeedQuizGameModeHandler',
    'TruthOrDareGameModeHandler',
    'GameModeConfig',
    'TriviaConfig',
    'FlashcardConfig',
    'SpeedQuizConfig',
    'TruthOrDareConfig',
    'get_default_config'
]
