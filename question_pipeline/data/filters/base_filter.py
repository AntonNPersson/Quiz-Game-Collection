from abc import ABC, abstractmethod
from typing import List, Tuple

class FilterCategory:
    GAME_MODE = "game_mode"
    CONTENT = "content"
    DIFFICULTY = "difficulty"
    BEHAVIOR = "behavior"

class IUniversalFilter(ABC):
    @abstractmethod
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        pass

    @abstractmethod
    def get_filter_type(self) -> str:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    def is_compatible_with(self, other_filter: 'IUniversalFilter') -> bool:
        return True
