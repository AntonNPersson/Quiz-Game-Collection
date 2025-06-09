"""
App Factory - Creates complete quiz game applications with minimal setup

This factory provides a high-level interface for creating fully configured
quiz game applications. It handles all the complex setup and wiring of
components, allowing developers to focus on game-specific logic.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Type
from pathlib import Path

from ..core.engine import GameEngine, GameMode, GameConfig
from ..data.repositories.question_repository import QuestionRepository
from ..data.storage.sqlite_storage import SQLiteStorage
from ..data.filters.base_filter import IUniversalFilter
from ..configs.game_configs import create_game_config, get_default_config
from ..configs.game_mode_handlers import register_all_handlers
from ..utils.exceptions import GameEngineError


class GameAppBuilder:
    """
    Builder class for creating game applications with fluent interface
    
    Example usage:
        app = (GameAppBuilder()
               .with_database("path/to/db.sqlite")
               .with_game_mode(GameMode.TRUTH_OR_DARE)
               .with_filters([CategoryFilter("truth")])
               .with_question_count(20)
               .build())
    """
    
    def __init__(self):
        self._database_path: Optional[str] = None
        self._game_mode: GameMode = GameMode.TRUTH_OR_DARE
        self._filters: List[IUniversalFilter] = []
        self._question_count: int = 10
        self._time_limit: Optional[int] = None
        self._custom_settings: Dict[str, Any] = {}
        self._logger_level: int = logging.INFO
        self._app_name: str = "QuizGameApp"
    
    def with_database(self, database_path: str) -> 'GameAppBuilder':
        """Set the database path"""
        self._database_path = database_path
        return self
    
    def with_game_mode(self, game_mode: GameMode) -> 'GameAppBuilder':
        """Set the game mode"""
        self._game_mode = game_mode
        return self
    
    def with_filters(self, filters: List[IUniversalFilter]) -> 'GameAppBuilder':
        """Set the filters to apply"""
        self._filters = filters
        return self
    
    def add_filter(self, filter_instance: IUniversalFilter) -> 'GameAppBuilder':
        """Add a single filter"""
        self._filters.append(filter_instance)
        return self
    
    def with_question_count(self, count: int) -> 'GameAppBuilder':
        """Set the number of questions"""
        self._question_count = count
        return self
    
    def with_time_limit(self, seconds: int) -> 'GameAppBuilder':
        """Set time limit in seconds"""
        self._time_limit = seconds
        return self
    
    def with_custom_settings(self, settings: Dict[str, Any]) -> 'GameAppBuilder':
        """Set custom game settings"""
        self._custom_settings.update(settings)
        return self
    
    def with_setting(self, key: str, value: Any) -> 'GameAppBuilder':
        """Add a single custom setting"""
        self._custom_settings[key] = value
        return self
    
    def with_logger_level(self, level: int) -> 'GameAppBuilder':
        """Set logging level"""
        self._logger_level = level
        return self
    
    def with_app_name(self, name: str) -> 'GameAppBuilder':
        """Set application name"""
        self._app_name = name
        return self
    
    def build(self) -> 'GameApp':
        """Build the complete game application"""
        if not self._database_path:
            raise ValueError("Database path must be specified")
        
        return AppFactory.create_app(
            database_path=self._database_path,
            game_mode=self._game_mode,
            filters=self._filters,
            question_count=self._question_count,
            time_limit=self._time_limit,
            custom_settings=self._custom_settings,
            logger_level=self._logger_level,
            app_name=self._app_name
        )


class GameApp:
    """
    Complete game application with all components wired together
    
    This class provides a high-level interface for running quiz games
    without needing to manage individual components.
    """
    
    def __init__(
        self,
        engine: GameEngine,
        repository: QuestionRepository,
        storage: SQLiteStorage,
        default_config: GameConfig,
        app_name: str = "QuizGameApp"
    ):
        self.engine = engine
        self.repository = repository
        self.storage = storage
        self.default_config = default_config
        self.app_name = app_name
        self.logger = logging.getLogger(f"{app_name}.GameApp")
        
        # Track active sessions for cleanup
        self._active_sessions: List[str] = []
    
    def create_session(
        self,
        session_id: str,
        config: Optional[GameConfig] = None,
        **config_overrides
    ) -> str:
        """
        Create a new game session
        
        Args:
            session_id: Unique identifier for the session
            config: Optional custom configuration (uses default if None)
            **config_overrides: Override specific config values
            
        Returns:
            Session ID
            
        Raises:
            GameEngineError: If session creation fails
        """
        # Use provided config or default
        if config is None:
            config = self.default_config
        
        # Apply any overrides
        if config_overrides:
            # Create a copy of the config with overrides
            config_dict = {
                'game_mode': config.game_mode,
                'filters': config.filters,
                'question_count': config_overrides.get('question_count', config.question_count),
                'time_limit': config_overrides.get('time_limit', config.time_limit),
                'shuffle_questions': config_overrides.get('shuffle_questions', config.shuffle_questions),
                'shuffle_options': config_overrides.get('shuffle_options', config.shuffle_options),
                'allow_skip': config_overrides.get('allow_skip', config.allow_skip),
                'show_correct_answer': config_overrides.get('show_correct_answer', config.show_correct_answer),
                'scoring_enabled': config_overrides.get('scoring_enabled', config.scoring_enabled),
                'custom_settings': {**config.custom_settings, **config_overrides.get('custom_settings', {})}
            }
            config = GameConfig(**config_dict)
        
        # Create session
        session = self.engine.create_session(session_id, config)
        self._active_sessions.append(session_id)
        
        self.logger.info(f"Created session {session_id} for {self.app_name}")
        return session_id
    
    def start_session(self, session_id: str) -> Dict[str, Any]:
        """
        Start a game session and return initial question data
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session info and first question
        """
        session = self.engine.start_session(session_id)
        question_data = self.engine.get_question_display_data(session_id)
        
        return {
            'session_started': True,
            'session_id': session_id,
            'game_mode': session.game_mode.value,
            'total_questions': len(session.questions),
            'current_question': question_data
        }
    
    def get_current_question(self, session_id: str) -> Dict[str, Any]:
        """Get current question display data"""
        return self.engine.get_question_display_data(session_id)
    
    def submit_answer(self, session_id: str, answer: Any) -> Dict[str, Any]:
        """Submit an answer and get result"""
        result = self.engine.submit_answer(session_id, answer)
        
        # Add next question data if available
        if not result['session_complete']:
            result['next_question'] = self.engine.get_question_display_data(session_id)
        
        return result
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get complete session status"""
        return self.engine.get_session_status(session_id)
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a session and get final results"""
        status = self.get_session_status(session_id)
        
        # Clean up
        self.engine.cleanup_session(session_id)
        if session_id in self._active_sessions:
            self._active_sessions.remove(session_id)
        
        self.logger.info(f"Ended session {session_id}")
        return status
    
    def get_available_filters(self) -> Dict[str, List[str]]:
        """Get information about available filters"""
        from ..data.filters import (
            GAME_MODE_FILTERS, CONTENT_FILTERS, 
            DIFFICULTY_FILTERS, BEHAVIOR_FILTERS
        )
        
        return {
            'game_mode': [f.__name__ for f in GAME_MODE_FILTERS],
            'content': [f.__name__ for f in CONTENT_FILTERS],
            'difficulty': [f.__name__ for f in DIFFICULTY_FILTERS],
            'behavior': [f.__name__ for f in BEHAVIOR_FILTERS]
        }
    
    def get_question_stats(self) -> Dict[str, Any]:
        """Get statistics about available questions"""
        # Get all questions without filters
        all_questions = self.repository.get_questions([])
        
        stats = {
            'total_questions': len(all_questions),
            'by_type': {},
            'by_difficulty': {},
            'by_spice_level': {}
        }
        
        for question in all_questions:
            # Count by type
            q_type = question.get_question_type() or 'unknown'
            stats['by_type'][q_type] = stats['by_type'].get(q_type, 0) + 1
            
            # Count by difficulty
            difficulty = question.get_difficulty() or 'unknown'
            stats['by_difficulty'][difficulty] = stats['by_difficulty'].get(difficulty, 0) + 1
            
            # Count by spice level
            spice = question.get_spice_level() or 'unknown'
            stats['by_spice_level'][spice] = stats['by_spice_level'].get(spice, 0) + 1
        
        return stats
    
    def cleanup(self):
        """Clean up all active sessions and resources"""
        for session_id in self._active_sessions.copy():
            try:
                self.engine.cleanup_session(session_id)
            except Exception as e:
                self.logger.warning(f"Error cleaning up session {session_id}: {e}")
        
        self._active_sessions.clear()
        self.logger.info(f"Cleaned up {self.app_name}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.cleanup()


class AppFactory:
    """
    Factory class for creating complete game applications
    
    This factory handles all the complex setup and configuration needed
    to create a working quiz game application.
    """
    
    @staticmethod
    def create_app(
        database_path: str,
        game_mode: GameMode = GameMode.TRUTH_OR_DARE,
        filters: List[IUniversalFilter] = None,
        question_count: int = 10,
        time_limit: Optional[int] = None,
        custom_settings: Dict[str, Any] = None,
        logger_level: int = logging.INFO,
        app_name: str = "QuizGameApp"
    ) -> GameApp:
        """
        Create a complete game application
        
        Args:
            database_path: Path to the SQLite database
            game_mode: Game mode to use
            filters: List of filters to apply
            question_count: Number of questions per session
            time_limit: Time limit in seconds (optional)
            custom_settings: Custom game settings
            logger_level: Logging level
            app_name: Name for the application
            
        Returns:
            Configured GameApp instance
            
        Raises:
            FileNotFoundError: If database file doesn't exist
            GameEngineError: If setup fails
        """
        # Setup logging
        logging.basicConfig(level=logger_level)
        logger = logging.getLogger(f"{app_name}.Factory")
        
        try:
            # Validate database path
            if not os.path.exists(database_path):
                raise FileNotFoundError(f"Database file not found: {database_path}")
            
            # Create storage layer
            storage = SQLiteStorage(database_path)
            
            # Create repository
            repository = QuestionRepository(storage)
            
            # Create game engine
            engine = GameEngine(repository)
            
            # Register game mode handlers
            register_all_handlers(engine)
            
            # Create default configuration
            default_config = create_game_config(
                game_mode=game_mode,
                filters=filters or [],
                question_count=question_count,
                time_limit=time_limit,
                custom_settings=custom_settings or {}
            )
            
            # Create and return the app
            app = GameApp(
                engine=engine,
                repository=repository,
                storage=storage,
                default_config=default_config,
                app_name=app_name
            )
            
            logger.info(f"Created {app_name} with {game_mode.value} mode")
            return app
            
        except Exception as e:
            logger.error(f"Failed to create {app_name}: {e}")
            raise GameEngineError(f"App creation failed: {e}")
    
    @staticmethod
    def create_truth_or_dare_app(
        database_path: str,
        player_names: List[str] = None,
        question_count: int = 15,
        truth_ratio: float = 0.6,
        spice_level: str = "mild",
        app_name: str = "TruthOrDareApp"
    ) -> GameApp:
        """
        Create a Truth or Dare application with sensible defaults
        
        Args:
            database_path: Path to the SQLite database
            player_names: List of player names for round-robin
            question_count: Number of questions per session
            truth_ratio: Ratio of truth to dare questions (0.0 to 1.0)
            spice_level: Spice level filter ("mild", "spicy", etc.)
            app_name: Name for the application
            
        Returns:
            Configured GameApp for Truth or Dare
        """
        from ..data.filters.content_filters import TruthFilter, DareFilter
        from ..data.filters.difficulty_filters import SpiceLevelFilter
        from ..data.filters.behavior_filters import RandomOrderFilter
        
        # Create appropriate filters
        filters = [RandomOrderFilter()]
        
        # Add spice level filter if specified
        if spice_level and spice_level.lower() != "any":
            filters.append(SpiceLevelFilter([spice_level]))
        
        # Custom settings for Truth or Dare
        custom_settings = {
            'truth_ratio': truth_ratio,
            'player_names': player_names or [],
            'round_robin': bool(player_names),
            'allow_player_choice': True,
            'age_appropriate': True
        }
        
        return AppFactory.create_app(
            database_path=database_path,
            game_mode=GameMode.TRUTH_OR_DARE,
            filters=filters,
            question_count=question_count,
            custom_settings=custom_settings,
            app_name=app_name
        )
    
    @staticmethod
    def get_builder() -> GameAppBuilder:
        """Get a new GameAppBuilder instance"""
        return GameAppBuilder()


# Convenience function for quick app creation
def create_quick_app(database_path: str, **kwargs) -> GameApp:
    """
    Quick function to create a game app with minimal setup
    
    Args:
        database_path: Path to database
        **kwargs: Additional configuration options
        
    Returns:
        Configured GameApp
    """
    return AppFactory.create_app(database_path, **kwargs)
