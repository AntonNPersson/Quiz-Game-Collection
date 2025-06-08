"""
Game mode configuration classes
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..core.engine import GameMode, GameConfig
from ..data.filters.base_filter import IUniversalFilter


@dataclass
class GameModeConfig:
    """Base configuration for game modes"""
    name: str
    description: str
    default_question_count: int = 10
    supports_time_limit: bool = True
    supports_scoring: bool = True
    supports_skip: bool = False
    default_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TriviaConfig(GameModeConfig):
    """Configuration for Trivia game mode"""
    name: str = "Trivia Quiz"
    description: str = "Classic question and answer format with multiple choice options"
    default_question_count: int = 10
    supports_time_limit: bool = True
    supports_scoring: bool = True
    supports_skip: bool = False
    default_settings: Dict[str, Any] = field(default_factory=lambda: {
        'show_correct_answer': True,
        'shuffle_options': True,
        'points_per_correct': 1,
        'penalty_for_wrong': 0,
        'allow_partial_credit': False,
        'time_per_question': 30,  # seconds
        'show_explanation': True
    })


@dataclass
class FlashcardConfig(GameModeConfig):
    """Configuration for Flashcard game mode"""
    name: str = "Flashcard Study"
    description: str = "Study mode with question/answer pairs for memorization"
    default_question_count: int = 20
    supports_time_limit: bool = False
    supports_scoring: bool = False
    supports_skip: bool = True
    default_settings: Dict[str, Any] = field(default_factory=lambda: {
        'show_answer_immediately': False,
        'allow_self_rating': True,
        'repeat_incorrect': True,
        'shuffle_cards': True,
        'show_progress': True,
        'rating_scale': ['Again', 'Hard', 'Good', 'Easy'],  # Spaced repetition style
        'auto_advance': False
    })


@dataclass
class SpeedQuizConfig(GameModeConfig):
    """Configuration for Speed Quiz game mode"""
    name: str = "Speed Quiz"
    description: str = "Fast-paced quiz with time pressure and bonus points"
    default_question_count: int = 15
    supports_time_limit: bool = True
    supports_scoring: bool = True
    supports_skip: bool = False
    default_settings: Dict[str, Any] = field(default_factory=lambda: {
        'time_per_question': 10,  # seconds
        'speed_bonus_multiplier': 2.0,
        'streak_bonus': True,
        'streak_multiplier': 1.5,
        'penalty_for_wrong': -1,
        'show_timer': True,
        'auto_advance': True,
        'difficulty_progression': True  # Gets harder as you progress
    })


@dataclass
class TruthOrDareConfig(GameModeConfig):
    """Configuration for Truth or Dare game mode"""
    name: str = "Truth or Dare"
    description: str = "Party game with truth questions and dare challenges"
    default_question_count: int = 10
    supports_time_limit: bool = False
    supports_scoring: bool = False
    supports_skip: bool = True
    default_settings: Dict[str, Any] = field(default_factory=lambda: {
        'allow_player_choice': True,  # Let player choose truth or dare
        'truth_ratio': 0.6,  # 60% truth, 40% dare by default
        'difficulty_levels': ['Mild', 'Spicy', 'Wild'],
        'player_names': [],  # Will be filled by the game
        'round_robin': True,  # Rotate between players
        'skip_penalty': None,  # No penalty for skipping
        'age_appropriate': True
    })


# Configuration registry
GAME_MODE_CONFIGS = {
    GameMode.TRIVIA: TriviaConfig(),
    GameMode.FLASHCARD: FlashcardConfig(),
    GameMode.SPEED_QUIZ: SpeedQuizConfig(),
    GameMode.TRUTH_OR_DARE: TruthOrDareConfig()
}


def get_default_config(game_mode: GameMode) -> GameModeConfig:
    """
    Get default configuration for a game mode
    
    Args:
        game_mode: The game mode to get config for
        
    Returns:
        Default configuration for the game mode
        
    Raises:
        ValueError: If game mode is not supported
    """
    if game_mode not in GAME_MODE_CONFIGS:
        raise ValueError(f"No default configuration available for game mode: {game_mode.value}")
    
    return GAME_MODE_CONFIGS[game_mode]


def create_game_config(
    game_mode: GameMode,
    filters: List[IUniversalFilter] = None,
    question_count: Optional[int] = None,
    time_limit: Optional[int] = None,
    custom_settings: Dict[str, Any] = None
) -> GameConfig:
    """
    Create a GameConfig with mode-specific defaults
    
    Args:
        game_mode: The game mode
        filters: List of filters to apply
        question_count: Number of questions (uses mode default if None)
        time_limit: Time limit in seconds (uses mode default if None)
        custom_settings: Custom settings to override defaults
        
    Returns:
        Configured GameConfig instance
    """
    mode_config = get_default_config(game_mode)
    
    # Use mode defaults if not specified
    if question_count is None:
        question_count = mode_config.default_question_count
    
    # Merge custom settings with defaults
    merged_settings = mode_config.default_settings.copy()
    if custom_settings:
        merged_settings.update(custom_settings)
    
    # Create GameConfig
    return GameConfig(
        game_mode=game_mode,
        filters=filters or [],
        question_count=question_count,
        time_limit=time_limit,
        shuffle_questions=merged_settings.get('shuffle_cards', True),
        shuffle_options=merged_settings.get('shuffle_options', True),
        allow_skip=mode_config.supports_skip,
        show_correct_answer=merged_settings.get('show_correct_answer', True),
        scoring_enabled=mode_config.supports_scoring,
        custom_settings=merged_settings
    )


def validate_game_config(config: GameConfig) -> List[str]:
    """
    Validate a game configuration
    
    Args:
        config: GameConfig to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    try:
        mode_config = get_default_config(config.game_mode)
        
        # Check if time limit is supported
        if config.time_limit is not None and not mode_config.supports_time_limit:
            errors.append(f"Time limit not supported for {config.game_mode.value} mode")
        
        # Check if scoring is enabled when not supported
        if config.scoring_enabled and not mode_config.supports_scoring:
            errors.append(f"Scoring not supported for {config.game_mode.value} mode")
        
        # Validate question count
        if config.question_count <= 0:
            errors.append("Question count must be positive")
        elif config.question_count > 100:
            errors.append("Question count should not exceed 100 for performance reasons")
        
        # Mode-specific validations
        if config.game_mode == GameMode.SPEED_QUIZ:
            time_per_question = config.custom_settings.get('time_per_question', 10)
            if time_per_question < 5:
                errors.append("Speed quiz requires at least 5 seconds per question")
        
        elif config.game_mode == GameMode.TRUTH_OR_DARE:
            truth_ratio = config.custom_settings.get('truth_ratio', 0.6)
            if not 0 <= truth_ratio <= 1:
                errors.append("Truth ratio must be between 0 and 1")
        
    except ValueError as e:
        errors.append(str(e))
    
    return errors


def get_recommended_filters(game_mode: GameMode) -> List[str]:
    """
    Get recommended filter types for a game mode
    
    Args:
        game_mode: The game mode
        
    Returns:
        List of recommended filter descriptions
    """
    recommendations = {
        GameMode.TRIVIA: [
            "Use CategoryFilter to focus on specific topics",
            "Use DifficultyFilter to match player skill level", 
            "Use RandomOrderFilter for variety",
            "Consider LimitFilter to control session length"
        ],
        GameMode.FLASHCARD: [
            "Use CategoryFilter to study specific subjects",
            "Use DifficultyRangeFilter for progressive learning",
            "Avoid RandomOrderFilter for structured learning",
            "Use NoRepeatFilter to avoid duplicate cards"
        ],
        GameMode.SPEED_QUIZ: [
            "Use EasyQuestionsFilter for faster gameplay",
            "Use RandomOrderFilter for unpredictability",
            "Use LimitFilter for timed sessions",
            "Consider ProgressiveFilter for increasing difficulty"
        ],
        GameMode.TRUTH_OR_DARE: [
            "Use CategoryFilter to match party theme",
            "Use appropriate difficulty filters for group comfort level",
            "Use RandomOrderFilter for spontaneity",
            "Consider ExcludeCategoryFilter to avoid sensitive topics"
        ]
    }
    
    return recommendations.get(game_mode, [])
