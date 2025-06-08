"""
Game Engine Core - Central orchestrator for quiz game logic
"""

from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
from abc import ABC, abstractmethod

from ..data.filters.base_filter import IUniversalFilter
from ..data.repositories.question_repository import QuestionRepository
from ..objects.question import Question
from ..utils.exceptions import GameEngineError


class GameState(Enum):
    """Possible states of a game session"""
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABORTED = "aborted"


class GameMode(Enum):
    """Supported game modes"""
    TRIVIA = "trivia"
    FLASHCARD = "flashcard"
    SPEED_QUIZ = "speed_quiz"
    TRUTH_OR_DARE = "truth_or_dare"
    CUSTOM = "custom"


@dataclass
class GameSession:
    """Represents an active game session"""
    session_id: str
    game_mode: GameMode
    state: GameState = GameState.INITIALIZED
    questions: List[Question] = field(default_factory=list)
    current_question_index: int = 0
    score: int = 0
    max_score: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    player_answers: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def current_question(self) -> Optional[Question]:
        """Get the current question"""
        if 0 <= self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    @property
    def is_finished(self) -> bool:
        """Check if all questions have been answered"""
        return self.current_question_index >= len(self.questions)
    
    @property
    def progress_percentage(self) -> float:
        """Get completion percentage"""
        if not self.questions:
            return 0.0
        return (self.current_question_index / len(self.questions)) * 100
    
    @property
    def duration(self) -> Optional[float]:
        """Get session duration in seconds"""
        if self.start_time:
            end = self.end_time or time.time()
            return end - self.start_time
        return None


class IGameModeHandler(ABC):
    """Interface for game mode specific logic"""
    
    @abstractmethod
    def get_mode(self) -> GameMode:
        """Get the game mode this handler supports"""
        pass
    
    @abstractmethod
    def prepare_questions(self, questions: List[Question], config: Dict[str, Any]) -> List[Question]:
        """Prepare questions for this game mode"""
        pass
    
    @abstractmethod
    def process_answer(self, session: GameSession, answer: Any) -> Dict[str, Any]:
        """Process a player's answer and return result"""
        pass
    
    @abstractmethod
    def calculate_score(self, session: GameSession, answer_result: Dict[str, Any]) -> int:
        """Calculate score for an answer"""
        pass
    
    @abstractmethod
    def get_question_display_data(self, question: Question, session: GameSession) -> Dict[str, Any]:
        """Get data needed to display a question in this mode"""
        pass


@dataclass
class GameConfig:
    """Configuration for a game session"""
    game_mode: GameMode
    filters: List[IUniversalFilter] = field(default_factory=list)
    question_count: int = 10
    time_limit: Optional[int] = None  # seconds
    shuffle_questions: bool = True
    shuffle_options: bool = True
    allow_skip: bool = False
    show_correct_answer: bool = True
    scoring_enabled: bool = True
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class GameEngine:
    """
    Core game engine that orchestrates quiz games
    
    This is the central component that:
    - Manages game sessions
    - Coordinates between filters, repositories, and game modes
    - Handles game state and flow
    - Provides a unified interface for all game types
    """
    
    def __init__(self, question_repository: QuestionRepository):
        self.repository = question_repository
        self.logger = logging.getLogger(__name__)
        
        # Active sessions
        self.active_sessions: Dict[str, GameSession] = {}
        
        # Game mode handlers
        self.mode_handlers: Dict[GameMode, IGameModeHandler] = {}
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = {
            'session_started': [],
            'question_answered': [],
            'session_completed': [],
            'session_aborted': [],
            'score_updated': []
        }
    
    def register_mode_handler(self, handler: IGameModeHandler):
        """Register a game mode handler"""
        mode = handler.get_mode()
        self.mode_handlers[mode] = handler
        self.logger.info(f"Registered handler for game mode: {mode.value}")
    
    def register_event_callback(self, event: str, callback: Callable):
        """Register a callback for game events"""
        if event in self.event_callbacks:
            self.event_callbacks[event].append(callback)
        else:
            self.logger.warning(f"Unknown event type: {event}")
    
    def create_session(self, session_id: str, config: GameConfig) -> GameSession:
        """
        Create a new game session
        
        Args:
            session_id: Unique identifier for the session
            config: Game configuration
            
        Returns:
            Created GameSession
            
        Raises:
            GameEngineError: If session creation fails
        """
        try:
            # Validate configuration
            self._validate_config(config)
            
            # Check if session already exists
            if session_id in self.active_sessions:
                raise GameEngineError(f"Session {session_id} already exists")
            
            # Get questions based on filters
            questions = self._get_questions_for_session(config)
            
            if not questions:
                raise GameEngineError("No questions found matching the specified criteria")
            
            # Create session
            session = GameSession(
                session_id=session_id,
                game_mode=config.game_mode,
                questions=questions,
                max_score=len(questions),
                metadata={
                    'config': config,
                    'question_count': len(questions),
                    'filters_applied': [f.get_description() for f in config.filters]
                }
            )
            
            # Store session
            self.active_sessions[session_id] = session
            
            self.logger.info(f"Created session {session_id} with {len(questions)} questions")
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to create session {session_id}: {e}")
            raise GameEngineError(f"Session creation failed: {e}")
    
    def start_session(self, session_id: str) -> GameSession:
        """
        Start a game session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Started GameSession
            
        Raises:
            GameEngineError: If session cannot be started
        """
        session = self._get_session(session_id)
        
        if session.state != GameState.INITIALIZED:
            raise GameEngineError(f"Session {session_id} cannot be started from state {session.state.value}")
        
        session.state = GameState.RUNNING
        session.start_time = time.time()
        
        # Trigger event
        self._trigger_event('session_started', session)
        
        self.logger.info(f"Started session {session_id}")
        return session
    
    def get_current_question(self, session_id: str) -> Optional[Question]:
        """
        Get the current question for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Current Question or None if session is finished
        """
        session = self._get_session(session_id)
        return session.current_question
    
    def get_question_display_data(self, session_id: str) -> Dict[str, Any]:
        """
        Get data needed to display the current question
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with display data
        """
        session = self._get_session(session_id)
        current_question = session.current_question
        
        if not current_question:
            return {'finished': True, 'session': session}
        
        # Get mode-specific display data
        handler = self.mode_handlers.get(session.game_mode)
        if handler:
            display_data = handler.get_question_display_data(current_question, session)
        else:
            # Default display data
            display_data = {
                'question': current_question,
                'question_number': session.current_question_index + 1,
                'total_questions': len(session.questions),
                'progress': session.progress_percentage
            }
        
        # Add session info
        display_data.update({
            'session_id': session_id,
            'game_mode': session.game_mode.value,
            'score': session.score,
            'max_score': session.max_score
        })
        
        return display_data
    
    def submit_answer(self, session_id: str, answer: Any) -> Dict[str, Any]:
        """
        Submit an answer for the current question
        
        Args:
            session_id: Session identifier
            answer: Player's answer
            
        Returns:
            Dictionary with answer result and feedback
            
        Raises:
            GameEngineError: If answer cannot be processed
        """
        session = self._get_session(session_id)
        
        if session.state != GameState.RUNNING:
            raise GameEngineError(f"Cannot submit answer for session in state {session.state.value}")
        
        if session.is_finished:
            raise GameEngineError("Session is already completed")
        
        current_question = session.current_question
        if not current_question:
            raise GameEngineError("No current question available")
        
        try:
            # Process answer using mode-specific handler
            handler = self.mode_handlers.get(session.game_mode)
            if handler:
                answer_result = handler.process_answer(session, answer)
                score_delta = handler.calculate_score(session, answer_result)
            else:
                # Default answer processing
                answer_result = self._default_process_answer(current_question, answer)
                score_delta = 1 if answer_result.get('correct', False) else 0
            
            # Update session
            session.player_answers.append({
                'question_id': current_question.id,
                'question_index': session.current_question_index,
                'answer': answer,
                'result': answer_result,
                'timestamp': time.time()
            })
            
            session.score += score_delta
            session.current_question_index += 1
            
            # Check if session is complete
            if session.is_finished:
                self._complete_session(session)
            
            # Trigger events
            self._trigger_event('question_answered', session, answer_result)
            if score_delta > 0:
                self._trigger_event('score_updated', session, session.score)
            
            self.logger.debug(f"Answer submitted for session {session_id}: {answer_result}")
            
            return {
                'result': answer_result,
                'score_delta': score_delta,
                'total_score': session.score,
                'session_complete': session.is_finished,
                'next_question_available': not session.is_finished
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process answer for session {session_id}: {e}")
            raise GameEngineError(f"Answer processing failed: {e}")
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get current status of a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session status
        """
        session = self._get_session(session_id)
        
        return {
            'session_id': session_id,
            'state': session.state.value,
            'game_mode': session.game_mode.value,
            'current_question_index': session.current_question_index,
            'total_questions': len(session.questions),
            'score': session.score,
            'max_score': session.max_score,
            'progress_percentage': session.progress_percentage,
            'duration': session.duration,
            'is_finished': session.is_finished,
            'metadata': session.metadata
        }
    
    def pause_session(self, session_id: str) -> GameSession:
        """Pause a running session"""
        session = self._get_session(session_id)
        
        if session.state != GameState.RUNNING:
            raise GameEngineError(f"Cannot pause session in state {session.state.value}")
        
        session.state = GameState.PAUSED
        self.logger.info(f"Paused session {session_id}")
        return session
    
    def resume_session(self, session_id: str) -> GameSession:
        """Resume a paused session"""
        session = self._get_session(session_id)
        
        if session.state != GameState.PAUSED:
            raise GameEngineError(f"Cannot resume session in state {session.state.value}")
        
        session.state = GameState.RUNNING
        self.logger.info(f"Resumed session {session_id}")
        return session
    
    def abort_session(self, session_id: str) -> GameSession:
        """Abort a session"""
        session = self._get_session(session_id)
        
        session.state = GameState.ABORTED
        session.end_time = time.time()
        
        # Trigger event
        self._trigger_event('session_aborted', session)
        
        self.logger.info(f"Aborted session {session_id}")
        return session
    
    def cleanup_session(self, session_id: str):
        """Remove a session from active sessions"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            self.logger.info(f"Cleaned up session {session_id}")
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.active_sessions.keys())
    
    def _get_session(self, session_id: str) -> GameSession:
        """Get session by ID or raise error"""
        if session_id not in self.active_sessions:
            raise GameEngineError(f"Session {session_id} not found")
        return self.active_sessions[session_id]
    
    def _validate_config(self, config: GameConfig):
        """Validate game configuration"""
        if config.question_count <= 0:
            raise GameEngineError("Question count must be positive")
        
        if config.time_limit is not None and config.time_limit <= 0:
            raise GameEngineError("Time limit must be positive")
        
        if config.game_mode not in self.mode_handlers and config.game_mode != GameMode.CUSTOM:
            self.logger.warning(f"No handler registered for game mode {config.game_mode.value}")
    
    def _get_questions_for_session(self, config: GameConfig) -> List[Question]:
        """Get questions based on configuration"""
        # Add limit filter if not already present
        from ..data.filters.behavior_filters import LimitFilter
        
        filters = config.filters.copy()
        
        # Check if limit filter already exists
        has_limit = any('limit' in f.get_description().lower() for f in filters)
        if not has_limit:
            filters.append(LimitFilter(config.question_count))
        
        # Get questions from repository
        questions = self.repository.get_questions(filters)
        
        # Apply game mode specific preparation
        handler = self.mode_handlers.get(config.game_mode)
        if handler:
            questions = handler.prepare_questions(questions, config.custom_settings)
        
        return questions
    
    def _default_process_answer(self, question: Question, answer: Any) -> Dict[str, Any]:
        """Default answer processing logic"""
        is_correct = question.is_correct(str(answer))
        
        return {
            'correct': is_correct,
            'provided_answer': answer,
            'correct_answer': question.get_correct_answer(),
            'explanation': None
        }
    
    def _complete_session(self, session: GameSession):
        """Mark session as completed"""
        session.state = GameState.COMPLETED
        session.end_time = time.time()
        
        # Trigger event
        self._trigger_event('session_completed', session)
        
        self.logger.info(f"Completed session {session.session_id} - Score: {session.score}/{session.max_score}")
    
    def _trigger_event(self, event: str, *args):
        """Trigger event callbacks"""
        if event in self.event_callbacks:
            for callback in self.event_callbacks[event]:
                try:
                    callback(*args)
                except Exception as e:
                    self.logger.error(f"Error in event callback for {event}: {e}")
