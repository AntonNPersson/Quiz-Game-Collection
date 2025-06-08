from .base_filter import IUniversalFilter, FilterCategory
from typing import Tuple, List

class TriviaGameModeFilter(IUniversalFilter):
    """Filter for trivia-style games - focuses on multiple choice questions"""
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        # Trivia games typically want multiple choice questions
        query += " AND (options IS NOT NULL OR correct_answer IS NOT NULL)"
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.GAME_MODE
    
    def get_description(self) -> str:
        return "Trivia game mode - questions with multiple choice options"

class FlashcardGameModeFilter(IUniversalFilter):
    """Filter for flashcard-style games - any question type works"""
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        # Flashcards can work with any question type
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.GAME_MODE
    
    def get_description(self) -> str:
        return "Flashcard game mode - all question types supported"

class SpeedQuizGameModeFilter(IUniversalFilter):
    """Filter for speed quiz games - quick questions only"""
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        # Speed quiz wants shorter questions for quick answers
        query += " AND LENGTH(text) <= 200"
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.GAME_MODE
    
    def get_description(self) -> str:
        return "Speed quiz mode - short questions for quick gameplay"

class TruthOrDareGameModeFilter(IUniversalFilter):
    """Filter for truth or dare style games"""
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        # Truth or dare might want specific categories
        query += " AND (category LIKE '%truth%' OR category LIKE '%dare%' OR category LIKE '%personal%')"
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.GAME_MODE
    
    def get_description(self) -> str:
        return "Truth or dare game mode - personal and interactive questions"
