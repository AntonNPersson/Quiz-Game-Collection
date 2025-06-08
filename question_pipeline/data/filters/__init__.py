"""
Universal Filter System for Quiz Game Collection

This module provides a comprehensive filtering system that works with a single
interface (IUniversalFilter) to handle all types of question filtering needs.

Filter Categories:
- Game Mode: Defines the type of game (trivia, flashcard, speed quiz, etc.)
- Content: Filters by category, topic, keywords
- Difficulty: Filters by difficulty level, complexity
- Behavior: Controls game mechanics (random order, limits, time constraints)
- Composite: Combines multiple filters with logic operators
"""

# Base filter interface
from .base_filter import IUniversalFilter, FilterCategory

# Game mode filters
from .game_mode_filters import (
    TriviaGameModeFilter,
    FlashcardGameModeFilter,
    SpeedQuizGameModeFilter,
    TruthOrDareGameModeFilter
)

# Content filters
from .content_filters import (
    CategoryFilter,
    TopicFilter,
    KeywordFilter,
    ExcludeCategoryFilter
)

# Difficulty filters
from .difficulty_filters import (
    DifficultyFilter,
    DifficultyRangeFilter,
    ComplexityFilter,
    EasyQuestionsFilter,
    HardQuestionsFilter
)

# Behavior filters
from .behavior_filters import (
    RandomOrderFilter,
    LimitFilter,
    OffsetFilter,
    TimeLimitFilter,
    NoRepeatFilter,
    ProgressiveFilter,
    BalancedFilter
)

# Composite filters
from .composite_filter import (
    CompositeFilter,
    FilterChain,
    ConditionalFilter
)

# Convenience collections
GAME_MODE_FILTERS = [
    TriviaGameModeFilter,
    FlashcardGameModeFilter,
    SpeedQuizGameModeFilter,
    TruthOrDareGameModeFilter
]

CONTENT_FILTERS = [
    CategoryFilter,
    TopicFilter,
    KeywordFilter,
    ExcludeCategoryFilter
]

DIFFICULTY_FILTERS = [
    DifficultyFilter,
    DifficultyRangeFilter,
    ComplexityFilter,
    EasyQuestionsFilter,
    HardQuestionsFilter
]

BEHAVIOR_FILTERS = [
    RandomOrderFilter,
    LimitFilter,
    OffsetFilter,
    TimeLimitFilter,
    NoRepeatFilter,
    ProgressiveFilter,
    BalancedFilter
]

ALL_FILTERS = (
    GAME_MODE_FILTERS + 
    CONTENT_FILTERS + 
    DIFFICULTY_FILTERS + 
    BEHAVIOR_FILTERS + 
    [CompositeFilter, FilterChain, ConditionalFilter]
)

__all__ = [
    # Base
    'IUniversalFilter',
    'FilterCategory',
    
    # Game Mode
    'TriviaGameModeFilter',
    'FlashcardGameModeFilter', 
    'SpeedQuizGameModeFilter',
    'TruthOrDareGameModeFilter',
    
    # Content
    'CategoryFilter',
    'TopicFilter',
    'KeywordFilter',
    'ExcludeCategoryFilter',
    
    # Difficulty
    'DifficultyFilter',
    'DifficultyRangeFilter',
    'ComplexityFilter',
    'EasyQuestionsFilter',
    'HardQuestionsFilter',
    
    # Behavior
    'RandomOrderFilter',
    'LimitFilter',
    'OffsetFilter',
    'TimeLimitFilter',
    'NoRepeatFilter',
    'ProgressiveFilter',
    'BalancedFilter',
    
    # Composite
    'CompositeFilter',
    'FilterChain',
    'ConditionalFilter',
    
    # Collections
    'GAME_MODE_FILTERS',
    'CONTENT_FILTERS',
    'DIFFICULTY_FILTERS',
    'BEHAVIOR_FILTERS',
    'ALL_FILTERS'
]
