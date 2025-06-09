from .base_filter import IUniversalFilter, FilterCategory
from typing import Tuple, List

class TruthOrDareGameModeFilter(IUniversalFilter):
    """Filter for truth or dare style games"""
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.GAME_MODE
    
    def get_description(self) -> str:
        return "Truth or dare game mode - personal and interactive questions"
