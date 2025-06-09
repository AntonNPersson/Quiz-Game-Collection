"""
Game mode handlers implementing specific logic for each game type
"""

import random
import time
from typing import List, Dict, Any
from ..core.engine import IGameModeHandler, GameMode, GameSession
from ..objects.question import Question


class TruthOrDareGameModeHandler(IGameModeHandler):
    """Handler for Truth or Dare game mode"""
    
    def get_mode(self) -> GameMode:
        return GameMode.TRUTH_OR_DARE
    
    def prepare_questions(self, questions: List[Question], config: Dict[str, Any]) -> List[Question]:
        """Prepare questions for truth or dare mode"""
        prepared_questions = questions.copy()
        
        # Shuffle for randomness
        random.shuffle(prepared_questions)
        
        # Apply truth/dare ratio if specified
        truth_ratio = config.get('truth_ratio', 0.6)
        if 'category' in [q.category for q in prepared_questions if hasattr(q, 'category')]:
            # Separate truth and dare questions
            truth_questions = [q for q in prepared_questions if getattr(q, 'category', '').lower() == 'truth']
            dare_questions = [q for q in prepared_questions if getattr(q, 'category', '').lower() == 'dare']
            
            # Calculate desired counts
            total_count = len(prepared_questions)
            truth_count = int(total_count * truth_ratio)
            dare_count = total_count - truth_count
            
            # Select questions according to ratio
            selected_questions = []
            selected_questions.extend(truth_questions[:truth_count])
            selected_questions.extend(dare_questions[:dare_count])
            
            # Fill remaining slots if needed
            remaining = total_count - len(selected_questions)
            if remaining > 0:
                remaining_questions = [q for q in prepared_questions if q not in selected_questions]
                selected_questions.extend(remaining_questions[:remaining])
            
            prepared_questions = selected_questions
            random.shuffle(prepared_questions)
        
        return prepared_questions
    
    def process_answer(self, session: GameSession, answer: Any) -> Dict[str, Any]:
        """Process answer for truth or dare mode"""
        current_question = session.current_question
        if not current_question:
            return {'error': 'No current question'}
        
        # In truth or dare, answer is typically completion status
        result = {
            'completed': answer in ['completed', 'done', True, 1],
            'skipped': answer in ['skip', 'skipped', 'pass'],
            'question_id': current_question.id,
            'question_type': getattr(current_question, 'category', 'unknown'),
            'timestamp': time.time()
        }
        
        return result
    
    def calculate_score(self, session: GameSession, answer_result: Dict[str, Any]) -> int:
        """Truth or dare mode doesn't use traditional scoring"""
        return 0  # No scoring in truth or dare mode
    
    def get_question_display_data(self, question: Question, session: GameSession) -> Dict[str, Any]:
        """Get display data for truth or dare question"""
        config = session.metadata.get('config', {}).custom_settings
        
        question_type = getattr(question, 'category', 'truth').lower()
        
        display_data = {
            'question': question,
            'question_number': session.current_question_index + 1,
            'total_questions': len(session.questions),
            'progress': session.progress_percentage,
            'question_type': question_type,
            'allow_skip': config.get('skip_penalty', None) is None,
            'player_names': config.get('player_names', []),
            'round_robin': config.get('round_robin', True)
        }
        
        # Determine current player if round robin is enabled
        if config.get('round_robin', True) and config.get('player_names'):
            player_names = config['player_names']
            current_player_index = session.current_question_index % len(player_names)
            display_data['current_player'] = player_names[current_player_index]
        
        return display_data


# Registry of all handlers
GAME_MODE_HANDLERS = {
    GameMode.TRUTH_OR_DARE: TruthOrDareGameModeHandler()
}


def get_handler(game_mode: GameMode) -> IGameModeHandler:
    """
    Get handler for a specific game mode
    
    Args:
        game_mode: The game mode
        
    Returns:
        Handler instance for the game mode
        
    Raises:
        ValueError: If no handler is available for the game mode
    """
    if game_mode not in GAME_MODE_HANDLERS:
        raise ValueError(f"No handler available for game mode: {game_mode.value}")
    
    return GAME_MODE_HANDLERS[game_mode]


def register_all_handlers(game_engine):
    """
    Register all built-in game mode handlers with a game engine
    
    Args:
        game_engine: GameEngine instance to register handlers with
    """
    for handler in GAME_MODE_HANDLERS.values():
        game_engine.register_mode_handler(handler)
