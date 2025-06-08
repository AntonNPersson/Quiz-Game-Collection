from .base_filter import IUniversalFilter, FilterCategory
from typing import Tuple, List

class DifficultyFilter(IUniversalFilter):
    """Filter questions by difficulty level"""
    
    def __init__(self, difficulty: str):
        self.difficulty = difficulty.lower()
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        query += " AND LOWER(difficulty) = ?"
        params.append(self.difficulty)
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
    
    def get_description(self) -> str:
        return f"Difficulty: {self.difficulty}"

class DifficultyRangeFilter(IUniversalFilter):
    """Filter questions by difficulty range (easy, medium, hard)"""
    
    def __init__(self, min_difficulty: str, max_difficulty: str):
        # Map difficulty levels to numbers for comparison
        self.difficulty_map = {
            'easy': 1,
            'medium': 2,
            'hard': 3,
            'expert': 4
        }
        
        self.min_level = self.difficulty_map.get(min_difficulty.lower(), 1)
        self.max_level = self.difficulty_map.get(max_difficulty.lower(), 4)
        self.min_difficulty = min_difficulty.lower()
        self.max_difficulty = max_difficulty.lower()
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        # Create a CASE statement to map difficulty to numbers
        difficulty_cases = []
        valid_difficulties = []
        
        for diff, level in self.difficulty_map.items():
            if self.min_level <= level <= self.max_level:
                valid_difficulties.append(diff)
        
        if valid_difficulties:
            placeholders = ','.join(['?' for _ in valid_difficulties])
            query += f" AND LOWER(difficulty) IN ({placeholders})"
            params.extend(valid_difficulties)
        
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
    
    def get_description(self) -> str:
        return f"Difficulty range: {self.min_difficulty} to {self.max_difficulty}"

class ComplexityFilter(IUniversalFilter):
    """Filter questions by text complexity (length-based)"""
    
    def __init__(self, max_length: int = None, min_length: int = None):
        self.max_length = max_length
        self.min_length = min_length
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if self.min_length is not None:
            query += " AND LENGTH(text) >= ?"
            params.append(self.min_length)
        
        if self.max_length is not None:
            query += " AND LENGTH(text) <= ?"
            params.append(self.max_length)
        
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
    
    def get_description(self) -> str:
        if self.min_length and self.max_length:
            return f"Question length: {self.min_length}-{self.max_length} characters"
        elif self.min_length:
            return f"Question length: at least {self.min_length} characters"
        elif self.max_length:
            return f"Question length: at most {self.max_length} characters"
        else:
            return "No length restrictions"

class EasyQuestionsFilter(IUniversalFilter):
    """Convenience filter for easy questions only"""
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        query += " AND (LOWER(difficulty) = 'easy' OR difficulty IS NULL)"
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
    
    def get_description(self) -> str:
        return "Easy questions only"

class HardQuestionsFilter(IUniversalFilter):
    """Convenience filter for hard questions only"""
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        query += " AND LOWER(difficulty) IN ('hard', 'expert')"
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
    
    def get_description(self) -> str:
        return "Hard questions only"
