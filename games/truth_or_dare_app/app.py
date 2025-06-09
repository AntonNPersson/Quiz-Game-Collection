"""
Truth or Dare Application

Main application class that provides a high-level interface for Truth or Dare games.
Built on top of the Quiz Game Collection framework.
"""

import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path

from question_pipeline.factory.app_factory import AppFactory, GameApp
from question_pipeline.core.engine import GameMode
from question_pipeline.data.filters.content_filters import CategoryFilter
from question_pipeline.data.filters.difficulty_filters import SpiceLevelFilter
from question_pipeline.data.filters.behavior_filters import RandomOrderFilter


class TruthOrDareApp:
    """
    High-level Truth or Dare application
    
    This class provides a simple interface for creating and managing
    Truth or Dare game sessions with sensible defaults.
    """
    
    def __init__(
        self,
        database_path: str,
        default_question_count: int = 15,
        default_spice_level: str = "mild"
    ):
        """
        Initialize the Truth or Dare application
        
        Args:
            database_path: Path to the question database
            default_question_count: Default number of questions per game
            default_spice_level: Default spice level ("mild", "spicy", etc.)
        """
        self.database_path = database_path
        self.default_question_count = default_question_count
        self.default_spice_level = default_spice_level
        
        # Create the underlying game app
        self.game_app = AppFactory.create_truth_or_dare_app(
            database_path=database_path,
            question_count=default_question_count,
            spice_level=default_spice_level,
            app_name="TruthOrDareApp"
        )
        
        # Track active games
        self.active_games: Dict[str, Dict[str, Any]] = {}
    
    def create_game(
        self,
        player_names: List[str],
        question_count: Optional[int] = None,
        truth_ratio: float = 0.6,
        spice_level: Optional[str] = None,
        game_id: Optional[str] = None
    ) -> str:
        """
        Create a new Truth or Dare game
        
        Args:
            player_names: List of player names
            question_count: Number of questions (uses default if None)
            truth_ratio: Ratio of truth to dare questions (0.0 to 1.0)
            spice_level: Spice level filter (uses default if None)
            game_id: Optional custom game ID (generates one if None)
            
        Returns:
            Game ID
        """
        if not player_names:
            raise ValueError("At least one player name is required")
        
        # Generate game ID if not provided
        if game_id is None:
            game_id = f"tod_{uuid.uuid4().hex[:8]}"
        
        # Use defaults if not specified
        if question_count is None:
            question_count = self.default_question_count
        if spice_level is None:
            spice_level = self.default_spice_level
        
        # Create custom settings for this game
        custom_settings = {
            'player_names': player_names,
            'truth_ratio': truth_ratio,
            'round_robin': True,
            'allow_player_choice': False,  # Game decides truth or dare
            'age_appropriate': True
        }
        
        # Create session
        session_id = self.game_app.create_session(
            session_id=game_id,
            question_count=question_count,
            custom_settings=custom_settings
        )
        
        # Track game info
        self.active_games[game_id] = {
            'session_id': session_id,
            'player_names': player_names,
            'current_player_index': 0,
            'question_count': question_count,
            'truth_ratio': truth_ratio,
            'spice_level': spice_level,
            'started': False
        }
        
        return game_id
    
    def start_game(self, game_id: str) -> Dict[str, Any]:
        """
        Start a Truth or Dare game
        
        Args:
            game_id: Game identifier
            
        Returns:
            Dictionary with game start info and first question
        """
        if game_id not in self.active_games:
            raise ValueError(f"Game {game_id} not found")
        
        game_info = self.active_games[game_id]
        
        # Start the session
        result = self.game_app.start_session(game_info['session_id'])
        
        # Mark as started
        game_info['started'] = True
        
        # Add game-specific info
        result.update({
            'game_id': game_id,
            'players': game_info['player_names'],
            'current_player': self._get_current_player(game_id)
        })
        
        return result
    
    def get_current_question(self, game_id: str) -> Dict[str, Any]:
        """
        Get the current question for a game
        
        Args:
            game_id: Game identifier
            
        Returns:
            Dictionary with question data and game context
        """
        if game_id not in self.active_games:
            raise ValueError(f"Game {game_id} not found")
        
        game_info = self.active_games[game_id]
        
        # Get question from game app
        question_data = self.game_app.get_current_question(game_info['session_id'])
        
        # Add game-specific context
        if not question_data.get('finished', False):
            question_data.update({
                'game_id': game_id,
                'current_player': self._get_current_player(game_id),
                'players': game_info['player_names']
            })
        
        return question_data
    
    def complete_question(self, game_id: str, completed: bool = True) -> Dict[str, Any]:
        """
        Mark the current question as completed or skipped
        
        Args:
            game_id: Game identifier
            completed: True if completed, False if skipped
            
        Returns:
            Dictionary with result and next question (if available)
        """
        if game_id not in self.active_games:
            raise ValueError(f"Game {game_id} not found")
        
        game_info = self.active_games[game_id]
        
        # Submit answer to game app
        answer = 'completed' if completed else 'skip'
        result = self.game_app.submit_answer(game_info['session_id'], answer)
        
        # Update current player for next question
        if not result['session_complete']:
            self._advance_player(game_id)
            
            # Add current player info to next question
            if 'next_question' in result:
                result['next_question'].update({
                    'current_player': self._get_current_player(game_id),
                    'players': game_info['player_names']
                })
        
        # Add game context
        result.update({
            'game_id': game_id,
            'action': 'completed' if completed else 'skipped'
        })
        
        return result
    
    def get_game_status(self, game_id: str) -> Dict[str, Any]:
        """
        Get complete status of a game
        
        Args:
            game_id: Game identifier
            
        Returns:
            Dictionary with complete game status
        """
        if game_id not in self.active_games:
            raise ValueError(f"Game {game_id} not found")
        
        game_info = self.active_games[game_id]
        
        # Get session status
        session_status = self.game_app.get_session_status(game_info['session_id'])
        
        # Add game-specific info
        session_status.update({
            'game_id': game_id,
            'players': game_info['player_names'],
            'current_player': self._get_current_player(game_id),
            'started': game_info['started'],
            'truth_ratio': game_info['truth_ratio'],
            'spice_level': game_info['spice_level']
        })
        
        return session_status
    
    def end_game(self, game_id: str) -> Dict[str, Any]:
        """
        End a game and get final results
        
        Args:
            game_id: Game identifier
            
        Returns:
            Dictionary with final game results
        """
        if game_id not in self.active_games:
            raise ValueError(f"Game {game_id} not found")
        
        game_info = self.active_games[game_id]
        
        # End session
        final_status = self.game_app.end_session(game_info['session_id'])
        
        # Remove from active games
        del self.active_games[game_id]
        
        # Add game summary
        final_status.update({
            'game_id': game_id,
            'players': game_info['player_names'],
            'game_ended': True
        })
        
        return final_status
    
    def get_active_games(self) -> List[str]:
        """Get list of active game IDs"""
        return list(self.active_games.keys())
    
    def get_question_stats(self) -> Dict[str, Any]:
        """Get statistics about available questions"""
        return self.game_app.get_question_stats()
    
    def _get_current_player(self, game_id: str) -> str:
        """Get the current player for a game"""
        game_info = self.active_games[game_id]
        player_names = game_info['player_names']
        current_index = game_info['current_player_index']
        
        if player_names and 0 <= current_index < len(player_names):
            return player_names[current_index]
        return "Unknown"
    
    def _advance_player(self, game_id: str):
        """Advance to the next player"""
        game_info = self.active_games[game_id]
        player_count = len(game_info['player_names'])
        
        if player_count > 0:
            game_info['current_player_index'] = (game_info['current_player_index'] + 1) % player_count
    
    def cleanup(self):
        """Clean up all active games and resources"""
        # End all active games
        for game_id in list(self.active_games.keys()):
            try:
                self.end_game(game_id)
            except Exception as e:
                print(f"Warning: Error ending game {game_id}: {e}")
        
        # Clean up game app
        self.game_app.cleanup()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.cleanup()


# Convenience function for quick setup
def create_truth_or_dare_app(
    database_path: str,
    **kwargs
) -> TruthOrDareApp:
    """
    Quick function to create a Truth or Dare app
    
    Args:
        database_path: Path to the question database
        **kwargs: Additional configuration options
        
    Returns:
        Configured TruthOrDareApp
    """
    return TruthOrDareApp(database_path, **kwargs)
