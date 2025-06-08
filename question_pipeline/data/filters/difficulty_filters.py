from .base_filter import IUniversalFilter, FilterCategory
from typing import Tuple, List, Optional
import re

class SeriousnessLevelFilter(IUniversalFilter):
    """Filter questions by seriousness level (extracts number from Seriös field)"""
    
    def __init__(self, seriousness_levels: List[str] = None, min_level: int = None, max_level: int = None):
        """
        Args:
            seriousness_levels: List of specific levels (can be numbers or names)
            min_level: Minimum seriousness level (inclusive)
            max_level: Maximum seriousness level (inclusive)
        """
        self.min_level = min_level
        self.max_level = max_level
        self.seriousness_levels = []
        
        if seriousness_levels:
            for level in seriousness_levels:
                try:
                    self.seriousness_levels.append(int(level))
                except ValueError:
                    # Map named levels to numbers
                    level_map = {
                        'cruise': 0, 'casual': 0,
                        'fun': 1, 'light': 1,
                        'party': 2, 'social': 2,
                        'tinyserious': 2, 'moderate': 2,
                        'serious': 3, 'thoughtful': 3,
                        'deep': 4, 'profound': 4,
                        'intense': 5, 'heavy': 5
                    }
                    mapped = level_map.get(level.lower().replace(' ', ''))
                    if mapped is not None:
                        self.seriousness_levels.append(mapped)
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if not self.seriousness_levels and self.min_level is None and self.max_level is None:
            return query, params
        
        # Extract number at the end of Seriös field
        # This handles: Fun1, TinySerious2, Serious10, Deep15, etc.
        extract_number = "CAST(REGEXP_SUBSTR(Seriös, '[0-9]+$') AS UNSIGNED)"
        
        # Alternative: extract ANY number in the field (not just at the end)
        # extract_number = "CAST(REGEXP_SUBSTR(Seriös, '[0-9]+') AS UNSIGNED)"
        
        conditions = []
        
        # Handle range filtering
        if self.min_level is not None and self.max_level is not None:
            conditions.append(f"{extract_number} BETWEEN ? AND ?")
            params.extend([self.min_level, self.max_level])
        elif self.min_level is not None:
            conditions.append(f"{extract_number} >= ?")
            params.append(self.min_level)
        elif self.max_level is not None:
            conditions.append(f"{extract_number} <= ?")
            params.append(self.max_level)
        
        # Handle specific levels
        if self.seriousness_levels:
            placeholders = ','.join(['?'] * len(self.seriousness_levels))
            conditions.append(f"{extract_number} IN ({placeholders})")
            params.extend(self.seriousness_levels)
        
        if conditions:
            query += f" AND ({' OR '.join(conditions)})"
        
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
    
    def get_description(self) -> str:
        descriptions = []
        if self.min_level is not None or self.max_level is not None:
            min_val = self.min_level if self.min_level is not None else 0
            max_val = self.max_level if self.max_level is not None else 'unlimited'
            descriptions.append(f"level {min_val}-{max_val}")
        if self.seriousness_levels:
            descriptions.append(f"levels {', '.join(map(str, self.seriousness_levels))}")
        return f"Seriousness filter: {' or '.join(descriptions)}"

class SpiceLevelFilter(IUniversalFilter):
    """Filter questions by spice level (extracts number from Krydda field)"""
    
    def __init__(self, spice_levels: List[str], max_level: Optional[int] = None):
        """
        Args:
            spice_levels: List of spice levels (can be numbers or names)
            max_level: If provided, filter for levels <= this value
        """
        self.spice_levels = []
        self.max_level = max_level
        
        for level in spice_levels:
            try:
                self.spice_levels.append(int(level))
            except ValueError:
                # Map named levels to numbers
                level_map = {
                    'none': 0, 'mild': 0,
                    'medium': 2, 'moderate': 2,
                    'spicy': 3, 'hot': 4,
                    'extreme': 5, 'very spicy': 6
                }
                mapped = level_map.get(level.lower())
                if mapped is not None:
                    self.spice_levels.append(mapped)
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if not self.spice_levels and self.max_level is None:
            return query, params
        
        # Extract number at the end of Krydda field
        # This handles: SNollKrydda0, SSmidgeKrydda1, ExtremKrydda10, etc.
        extract_number = "CAST(REGEXP_SUBSTR(Krydda, '[0-9]+$') AS UNSIGNED)"
        
        if self.max_level is not None:
            # Range filter: 0 to max_level
            query += f" AND {extract_number} <= ?"
            params.append(self.max_level)
        elif self.spice_levels:
            # Specific levels filter
            placeholders = ','.join(['?'] * len(self.spice_levels))
            query += f" AND {extract_number} IN ({placeholders})"
            params.extend(self.spice_levels)
        
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
    
    def get_description(self) -> str:
        if self.max_level is not None:
            return f"Spice level filter: 0-{self.max_level}"
        return f"Spice level filter: {', '.join(map(str, self.spice_levels))}"

class DifficultyLevelFilter(IUniversalFilter):
    """Filter questions within a difficulty range using numeric levels"""
    
    def __init__(self, min_difficulty: str, max_difficulty: str):
        self.min_difficulty = min_difficulty.lower()
        self.max_difficulty = max_difficulty.lower()
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        # Map difficulty names to numeric ranges
        difficulty_mapping = {
            'easy': (0, 1),
            'lätt': (0, 1),
            'medium': (2, 3),
            'medel': (2, 3),
            'hard': (4, 5),
            'svår': (4, 5),
            'tuff': (4, 5)
        }
        
        min_range = difficulty_mapping.get(self.min_difficulty, (0, 0))
        max_range = difficulty_mapping.get(self.max_difficulty, (5, 5))
        
        min_level = min_range[0]
        max_level = max_range[1]
        
        # Create conditions for the range
        range_conditions = []
        for level in range(min_level, max_level + 1):
            range_conditions.append(f"Seriös LIKE '%{level}%'")
        
        if range_conditions:
            query += f" AND ({' OR '.join(range_conditions)})"
        
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
    
    def get_description(self) -> str:
        return f"Difficulty range: {self.min_difficulty} to {self.max_difficulty}"

class FunQuestionsFilter(IUniversalFilter):
    """Filter for easy/light questions only (levels 0-1)"""
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        query += " AND (Seriös LIKE '%0%' OR Seriös LIKE '%1%')"
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
    
    def get_description(self) -> str:
        return "Easy questions only (levels 0-1)"

class SeriousQuestionsFilter(IUniversalFilter):
    """Filter for hard/serious questions only (levels 4-5)"""
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        query += " AND (Seriös LIKE '%4%' OR Seriös LIKE '%5%')"
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
    
    def get_description(self) -> str:
        return "Hard questions only (levels 4-5)"

class MediumSeriousQuestionsFilter(IUniversalFilter):
    """Filter for medium questions only (levels 2-3)"""
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        query += " AND (Seriös LIKE '%2%' OR Seriös LIKE '%3%')"
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
    
    def get_description(self) -> str:
        return "Medium questions only (levels 2-3)"

class MildSpiceFilter(IUniversalFilter):
    """Filter for mild spice questions only (level 0)"""
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        query += " AND Krydda LIKE '%0%'"
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
    
    def get_description(self) -> str:
        return "Mild spice only (level 0)"

class SpicyQuestionsFilter(IUniversalFilter):
    """Filter for spicy questions only (level 1+)"""
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        query += " AND Krydda LIKE '%1%'"
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
    
    def get_description(self) -> str:
        return "Spicy questions only (level 1+)"

class ExactSeriousnessFilter(IUniversalFilter):
    """Filter questions by exact seriousness level values"""
    
    def __init__(self, seriousness_values: List[str]):
        self.seriousness_values = seriousness_values
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if not self.seriousness_values:
            return query, params
        
        # Direct mapping to Seriös field values
        seriousness_conditions = []
        for value in self.seriousness_values:
            seriousness_conditions.append("Seriös = ?")
            params.append(value)
        
        if seriousness_conditions:
            query += f" AND ({' OR '.join(seriousness_conditions)})"
        
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
    
    def get_description(self) -> str:
        return f"Exact seriousness filter: {', '.join(self.seriousness_values)}"

# Helper function to extract numeric level from Seriös/Krydda values
def extract_numeric_level(value: str) -> int:
    """Extract numeric level from Seriös or Krydda field values"""
    if not value:
        return 0
    
    # Find all digits in the string
    import re
    numbers = re.findall(r'\d+', value)
    if numbers:
        return int(numbers[-1])  # Take the last number found
    return 0
