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
    TruthOrDareGameModeFilter
)

# Content filters
from .content_filters import (
    CategoryFilter,
    TopicFilter,
    KeywordFilter,
    ExcludeCategoryFilter,
    OfficialGroupFilter,
    DareFilter,
    TruthFilter
)

# Difficulty filters
from .difficulty_filters import (
    DifficultyLevelFilter,
    SeriousnessLevelFilter,
    SpiceLevelFilter,
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
    TruthOrDareGameModeFilter
]

CONTENT_FILTERS = [
    CategoryFilter,
    TopicFilter,
    KeywordFilter,
    ExcludeCategoryFilter,
    OfficialGroupFilter,
    DareFilter,
    TruthFilter
]

DIFFICULTY_FILTERS = [
    DifficultyLevelFilter,
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
    'TruthOrDareGameModeFilter',
    
    # Content
    'CategoryFilter',
    'TopicFilter',
    'KeywordFilter',
    'ExcludeCategoryFilter',
    'OfficialGroupFilter',
    'DareFilter',
    'TruthFilter',
    
    # Difficulty
    'DifficultyLevelFilter',
    'SeriousnessLevelFilter',
    'SpiceLevelFilter',
    
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
