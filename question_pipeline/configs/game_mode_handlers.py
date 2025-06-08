"""
Game mode handlers implementing specific logic for each game type
"""

import random
import time
from typing import List, Dict, Any
from ..core.engine import IGameModeHandler, GameMode, GameSession
from ..objects.question import Question


class TriviaGameModeHandler(IGameModeHandler):
    """Handler for Trivia game mode"""
    
    def get_mode(self) -> GameMode:
        return GameMode.TRIVIA
    
    def prepare_questions(self, questions: List[Question], config: Dict[str, Any]) -> List[Question]:
        """Prepare questions for trivia mode"""
        prepared_questions = questions.copy()
        
        # Shuffle questions if enabled
        if config.get('shuffle_questions', True):
            random.shuffle(prepared_questions)
        
        # Shuffle options for each question if enabled
        if config.get('shuffle_options', True):
            for question in prepared_questions:
                if question.has_multiple_choices():
                    options = question.get_options()
                    if options and len(options) > 1:
                        # Keep track of correct answer before shuffling
                        correct_answer = question.get_correct_answer()
                        if isinstance(correct_answer, int) and 0 <= correct_answer < len(options):
                            correct_text = options[correct_answer]
                            
                            # Shuffle options
                            random.shuffle(options)
                            
                            # Update correct answer index
                            try:
                                new_correct_index = options.index(correct_text)
                                question.correct_answer = new_correct_index
                            except ValueError:
                                # If we can't find the correct answer, keep original
                                pass
        
        return prepared_questions
    
    def process_answer(self, session: GameSession, answer: Any) -> Dict[str, Any]:
        """Process answer for trivia mode"""
        current_question = session.current_question
        if not current_question:
            return {'error': 'No current question'}
        
        # Convert answer to appropriate type
        if isinstance(answer, str) and answer.isdigit():
            answer = int(answer)
        
        # Check if answer is correct
        is_correct = current_question.is_correct(str(answer))
        
        result = {
            'correct': is_correct,
            'provided_answer': answer,
            'correct_answer': current_question.get_correct_answer(),
            'question_id': current_question.id,
            'timestamp': time.time()
        }
        
        # Add explanation if available
        if hasattr(current_question, 'explanation'):
            result['explanation'] = current_question.explanation
        
        # Add options for context
        if current_question.has_multiple_choices():
            result['options'] = current_question.get_options()
        
        return result
    
    def calculate_score(self, session: GameSession, answer_result: Dict[str, Any]) -> int:
        """Calculate score for trivia answer"""
        config = session.metadata.get('config', {}).custom_settings
        
        if answer_result.get('correct', False):
            return config.get('points_per_correct', 1)
        else:
            return config.get('penalty_for_wrong', 0)
    
    def get_question_display_data(self, question: Question, session: GameSession) -> Dict[str, Any]:
        """Get display data for trivia question"""
        config = session.metadata.get('config', {}).custom_settings
        
        display_data = {
            'question': question,
            'question_number': session.current_question_index + 1,
            'total_questions': len(session.questions),
            'progress': session.progress_percentage,
            'show_options': question.has_multiple_choices(),
            'time_per_question': config.get('time_per_question', 30)
        }
        
        if question.has_multiple_choices():
            display_data['options'] = question.get_options()
        
        return display_data


class FlashcardGameModeHandler(IGameModeHandler):
    """Handler for Flashcard game mode"""
    
    def get_mode(self) -> GameMode:
        return GameMode.FLASHCARD
    
    def prepare_questions(self, questions: List[Question], config: Dict[str, Any]) -> List[Question]:
        """Prepare questions for flashcard mode"""
        prepared_questions = questions.copy()
        
        # Shuffle cards if enabled
        if config.get('shuffle_cards', True):
            random.shuffle(prepared_questions)
        
        return prepared_questions
    
    def process_answer(self, session: GameSession, answer: Any) -> Dict[str, Any]:
        """Process answer for flashcard mode (self-rating)"""
        current_question = session.current_question
        if not current_question:
            return {'error': 'No current question'}
        
        # In flashcard mode, answer is typically a self-rating
        config = session.metadata.get('config', {}).custom_settings
        rating_scale = config.get('rating_scale', ['Again', 'Hard', 'Good', 'Easy'])
        
        # Validate rating
        if answer not in rating_scale:
            return {'error': f'Invalid rating. Must be one of: {rating_scale}'}
        
        result = {
            'rating': answer,
            'question_id': current_question.id,
            'correct_answer': current_question.get_correct_answer(),
            'timestamp': time.time(),
            'self_assessed': True
        }
        
        # Determine if this card should be repeated
        repeat_card = answer in ['Again', 'Hard']
        result['repeat_card'] = repeat_card
        
        return result
    
    def calculate_score(self, session: GameSession, answer_result: Dict[str, Any]) -> int:
        """Flashcard mode doesn't use traditional scoring"""
        return 0  # No scoring in flashcard mode
    
    def get_question_display_data(self, question: Question, session: GameSession) -> Dict[str, Any]:
        """Get display data for flashcard"""
        config = session.metadata.get('config', {}).custom_settings
        
        display_data = {
            'question': question,
            'card_number': session.current_question_index + 1,
            'total_cards': len(session.questions),
            'progress': session.progress_percentage,
            'show_answer_immediately': config.get('show_answer_immediately', False),
            'rating_scale': config.get('rating_scale', ['Again', 'Hard', 'Good', 'Easy']),
            'allow_self_rating': config.get('allow_self_rating', True)
        }
        
        return display_data


class SpeedQuizGameModeHandler(IGameModeHandler):
    """Handler for Speed Quiz game mode"""
    
    def get_mode(self) -> GameMode:
        return GameMode.SPEED_QUIZ
    
    def prepare_questions(self, questions: List[Question], config: Dict[str, Any]) -> List[Question]:
        """Prepare questions for speed quiz mode"""
        prepared_questions = questions.copy()
        
        # Always shuffle for unpredictability
        random.shuffle(prepared_questions)
        
        # Apply difficulty progression if enabled
        if config.get('difficulty_progression', True):
            # Sort by difficulty, then shuffle within difficulty groups
            difficulty_order = {'Easy': 1, 'Medium': 2, 'Hard': 3}
            
            def get_difficulty_score(q):
                diff = q.get_difficulty() or 'Medium'
                return difficulty_order.get(diff, 2)
            
            prepared_questions.sort(key=get_difficulty_score)
        
        return prepared_questions
    
    def process_answer(self, session: GameSession, answer: Any) -> Dict[str, Any]:
        """Process answer for speed quiz mode"""
        current_question = session.current_question
        if not current_question:
            return {'error': 'No current question'}
        
        # Convert answer to appropriate type
        if isinstance(answer, str) and answer.isdigit():
            answer = int(answer)
        
        # Check if answer is correct
        is_correct = current_question.is_correct(str(answer))
        
        # Calculate time bonus (if answer was fast)
        config = session.metadata.get('config', {}).custom_settings
        time_per_question = config.get('time_per_question', 10)
        
        # Simulate time taken (in real implementation, this would be tracked)
        time_taken = random.uniform(2, time_per_question)  # Placeholder
        speed_bonus = max(0, time_per_question - time_taken) / time_per_question
        
        result = {
            'correct': is_correct,
            'provided_answer': answer,
            'correct_answer': current_question.get_correct_answer(),
            'question_id': current_question.id,
            'time_taken': time_taken,
            'speed_bonus': speed_bonus,
            'timestamp': time.time()
        }
        
        # Check for streak bonus
        recent_answers = session.player_answers[-2:] if len(session.player_answers) >= 2 else []
        if all(ans['result'].get('correct', False) for ans in recent_answers):
            result['streak_bonus'] = True
        
        return result
    
    def calculate_score(self, session: GameSession, answer_result: Dict[str, Any]) -> int:
        """Calculate score for speed quiz answer"""
        config = session.metadata.get('config', {}).custom_settings
        
        if not answer_result.get('correct', False):
            return config.get('penalty_for_wrong', -1)
        
        base_score = 1
        
        # Apply speed bonus
        speed_multiplier = config.get('speed_bonus_multiplier', 2.0)
        speed_bonus = answer_result.get('speed_bonus', 0)
        score = base_score + (base_score * speed_bonus * speed_multiplier)
        
        # Apply streak bonus
        if answer_result.get('streak_bonus', False):
            streak_multiplier = config.get('streak_multiplier', 1.5)
            score *= streak_multiplier
        
        return int(score)
    
    def get_question_display_data(self, question: Question, session: GameSession) -> Dict[str, Any]:
        """Get display data for speed quiz question"""
        config = session.metadata.get('config', {}).custom_settings
        
        display_data = {
            'question': question,
            'question_number': session.current_question_index + 1,
            'total_questions': len(session.questions),
            'progress': session.progress_percentage,
            'time_per_question': config.get('time_per_question', 10),
            'show_timer': config.get('show_timer', True),
            'auto_advance': config.get('auto_advance', True)
        }
        
        if question.has_multiple_choices():
            display_data['options'] = question.get_options()
        
        return display_data


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
    GameMode.TRIVIA: TriviaGameModeHandler(),
    GameMode.FLASHCARD: FlashcardGameModeHandler(),
    GameMode.SPEED_QUIZ: SpeedQuizGameModeHandler(),
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
