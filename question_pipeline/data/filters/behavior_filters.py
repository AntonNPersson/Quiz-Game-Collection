from .base_filter import IUniversalFilter, FilterCategory
from typing import Tuple, List
import random

class RandomOrderFilter(IUniversalFilter):
    """Randomize the order of questions"""
    
    def __init__(self, seed: int = None):
        self.seed = seed
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        # Add random ordering to the query
        if self.seed:
            # For reproducible randomness, we can use RANDOM() with a seed
            query += " ORDER BY RANDOM()"
        else:
            query += " ORDER BY RANDOM()"
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.BEHAVIOR
    
    def get_description(self) -> str:
        return "Random question order"

class LimitFilter(IUniversalFilter):
    """Limit the number of questions returned"""
    
    def __init__(self, limit: int):
        self.limit = max(1, limit)  # Ensure at least 1 question
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        query += f" LIMIT {self.limit}"
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.BEHAVIOR
    
    def get_description(self) -> str:
        return f"Limit to {self.limit} questions"

class OffsetFilter(IUniversalFilter):
    """Skip a number of questions (for pagination)"""
    
    def __init__(self, offset: int):
        self.offset = max(0, offset)
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if self.offset > 0:
            query += f" OFFSET {self.offset}"
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.BEHAVIOR
    
    def get_description(self) -> str:
        return f"Skip first {self.offset} questions"

class TimeLimitFilter(IUniversalFilter):
    """Filter questions suitable for time-limited games"""
    
    def __init__(self, max_time_seconds: int):
        self.max_time_seconds = max_time_seconds
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        # Estimate time based on question length (rough: 1 second per 10 characters)
        estimated_max_length = self.max_time_seconds * 10
        query += " AND LENGTH(text) <= ?"
        params.append(estimated_max_length)
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.BEHAVIOR
    
    def get_description(self) -> str:
        return f"Questions suitable for {self.max_time_seconds}s time limit"

class NoRepeatFilter(IUniversalFilter):
    """Exclude questions that have been used recently"""
    
    def __init__(self, excluded_question_ids: List[int]):
        self.excluded_ids = excluded_question_ids
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if self.excluded_ids:
            placeholders = ','.join(['?' for _ in self.excluded_ids])
            query += f" AND id NOT IN ({placeholders})"
            params.extend(self.excluded_ids)
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.BEHAVIOR
    
    def get_description(self) -> str:
        return f"Exclude {len(self.excluded_ids)} recently used questions"

class ProgressiveFilter(IUniversalFilter):
    """Filter for progressive difficulty (start easy, get harder)"""
    
    def __init__(self, current_level: int = 1, max_level: int = 3):
        self.current_level = max(1, current_level)
        self.max_level = max_level
        
        # Map levels to difficulties
        self.level_to_difficulty = {
            1: ['easy'],
            2: ['easy', 'medium'],
            3: ['medium', 'hard'],
            4: ['hard', 'expert']
        }
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        difficulties = self.level_to_difficulty.get(self.current_level, ['medium'])
        
        if difficulties:
            placeholders = ','.join(['?' for _ in difficulties])
            query += f" AND LOWER(difficulty) IN ({placeholders})"
            params.extend(difficulties)
        
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.BEHAVIOR
    
    def get_description(self) -> str:
        return f"Progressive difficulty - Level {self.current_level}/{self.max_level}"

class BalancedFilter(IUniversalFilter):
    """Ensure balanced distribution across categories/difficulties"""
    
    def __init__(self, balance_by: str = "category", max_per_group: int = 5):
        self.balance_by = balance_by  # 'category' or 'difficulty'
        self.max_per_group = max_per_group
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        # This is complex to implement in pure SQL, so we'll add a note
        # that this filter might need post-processing in the repository
        # For now, we'll just add a comment to the query
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.BEHAVIOR
    
    def get_description(self) -> str:
        return f"Balanced distribution by {self.balance_by} (max {self.max_per_group} per group)"
    
    def requires_post_processing(self) -> bool:
        """Indicates this filter needs special handling in the repository"""
        return True
