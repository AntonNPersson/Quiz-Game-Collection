from .base_filter import IUniversalFilter, FilterCategory
from typing import Tuple, List, Optional

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
        
        # SQLite-compatible approach: use SUBSTR and INSTR to extract numbers
        # This extracts the trailing number from the Seriös field
        extract_number = """
        CAST(
            CASE 
                WHEN Seriös GLOB '*[0-9]' THEN 
                    SUBSTR(Seriös, LENGTH(Seriös) - LENGTH(LTRIM(SUBSTR(Seriös, INSTR(Seriös, '0') + CASE WHEN INSTR(Seriös, '1') > 0 AND (INSTR(Seriös, '0') = 0 OR INSTR(Seriös, '1') < INSTR(Seriös, '0')) THEN INSTR(Seriös, '1') - 1 WHEN INSTR(Seriös, '2') > 0 AND (INSTR(Seriös, '0') = 0 OR INSTR(Seriös, '2') < INSTR(Seriös, '0')) AND (INSTR(Seriös, '1') = 0 OR INSTR(Seriös, '2') < INSTR(Seriös, '1')) THEN INSTR(Seriös, '2') - 1 WHEN INSTR(Seriös, '3') > 0 AND (INSTR(Seriös, '0') = 0 OR INSTR(Seriös, '3') < INSTR(Seriös, '0')) AND (INSTR(Seriös, '1') = 0 OR INSTR(Seriös, '3') < INSTR(Seriös, '1')) AND (INSTR(Seriös, '2') = 0 OR INSTR(Seriös, '3') < INSTR(Seriös, '2')) THEN INSTR(Seriös, '3') - 1 WHEN INSTR(Seriös, '4') > 0 AND (INSTR(Seriös, '0') = 0 OR INSTR(Seriös, '4') < INSTR(Seriös, '0')) AND (INSTR(Seriös, '1') = 0 OR INSTR(Seriös, '4') < INSTR(Seriös, '1')) AND (INSTR(Seriös, '2') = 0 OR INSTR(Seriös, '4') < INSTR(Seriös, '2')) AND (INSTR(Seriös, '3') = 0 OR INSTR(Seriös, '4') < INSTR(Seriös, '3')) THEN INSTR(Seriös, '4') - 1 WHEN INSTR(Seriös, '5') > 0 AND (INSTR(Seriös, '0') = 0 OR INSTR(Seriös, '5') < INSTR(Seriös, '0')) AND (INSTR(Seriös, '1') = 0 OR INSTR(Seriös, '5') < INSTR(Seriös, '1')) AND (INSTR(Seriös, '2') = 0 OR INSTR(Seriös, '5') < INSTR(Seriös, '2')) AND (INSTR(Seriös, '3') = 0 OR INSTR(Seriös, '5') < INSTR(Seriös, '3')) AND (INSTR(Seriös, '4') = 0 OR INSTR(Seriös, '5') < INSTR(Seriös, '4')) THEN INSTR(Seriös, '5') - 1 ELSE 1 END), '0123456789')) + 1)
                ELSE 0 
            END AS INTEGER
        )
        """.strip()
        
        # Simplified approach - just check for specific patterns
        conditions = []
        
        # Handle range filtering with simple pattern matching
        if self.min_level is not None and self.max_level is not None:
            level_conditions = []
            for level in range(self.min_level, self.max_level + 1):
                level_conditions.append(f"Seriös LIKE '%{level}'")
            if level_conditions:
                conditions.append(f"({' OR '.join(level_conditions)})")
        elif self.min_level is not None:
            level_conditions = []
            for level in range(self.min_level, 10):  # Assume max 10 levels
                level_conditions.append(f"Seriös LIKE '%{level}'")
            if level_conditions:
                conditions.append(f"({' OR '.join(level_conditions)})")
        elif self.max_level is not None:
            level_conditions = []
            for level in range(0, self.max_level + 1):
                level_conditions.append(f"Seriös LIKE '%{level}'")
            if level_conditions:
                conditions.append(f"({' OR '.join(level_conditions)})")
        
        # Handle specific levels
        if self.seriousness_levels:
            level_conditions = []
            for level in self.seriousness_levels:
                level_conditions.append(f"Seriös LIKE '%{level}'")
            if level_conditions:
                conditions.append(f"({' OR '.join(level_conditions)})")
        
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
        
        # SQLite-compatible approach - use pattern matching for spice levels
        conditions = []
        
        if self.max_level is not None:
            # Range filter: 0 to max_level
            level_conditions = []
            for level in range(0, self.max_level + 1):
                level_conditions.append(f"Krydda LIKE '%{level}'")
            if level_conditions:
                conditions.append(f"({' OR '.join(level_conditions)})")
        elif self.spice_levels:
            # Specific levels filter
            level_conditions = []
            for level in self.spice_levels:
                level_conditions.append(f"Krydda LIKE '%{level}'")
            if level_conditions:
                conditions.append(f"({' OR '.join(level_conditions)})")
        
        if conditions:
            query += f" AND ({' OR '.join(conditions)})"
        
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
    
    def get_description(self) -> str:
        if self.max_level is not None:
            return f"Spice level filter: 0-{self.max_level}"
        return f"Spice level filter: {', '.join(map(str, self.spice_levels))}"

class DifficultyLevelFilter(IUniversalFilter):
    """Filter questions within a difficulty range using mapped words"""
   
    def __init__(self, min_difficulty: str, max_difficulty: str):
        self.min_difficulty = min_difficulty.lower()
        self.max_difficulty = max_difficulty.lower()
   
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        # Map difficulty names to their word equivalents
        difficulty_mapping = {
            'easy': ['easy', 'lätt'],
            'lätt': ['easy', 'lätt'],
            'medium': ['medium', 'medel'],
            'medel': ['medium', 'medel'],
            'hard': ['hard', 'svår', 'tuff'],
            'svår': ['hard', 'svår', 'tuff'],
            'tuff': ['hard', 'svår', 'tuff']
        }
       
        # Get all difficulty words that should be included
        min_words = difficulty_mapping.get(self.min_difficulty, [])
        max_words = difficulty_mapping.get(self.max_difficulty, [])
        
        # Combine and deduplicate all relevant difficulty words
        all_difficulty_words = list(set(min_words + max_words))
        
        # If we have specific difficulties, include all levels between min and max
        if self.min_difficulty in ['easy', 'lätt'] and self.max_difficulty in ['hard', 'svår', 'tuff']:
            # Include all difficulties
            all_difficulty_words = ['easy', 'lätt', 'medium', 'medel', 'hard', 'svår', 'tuff']
        elif self.min_difficulty in ['easy', 'lätt'] and self.max_difficulty in ['medium', 'medel']:
            # Include easy and medium
            all_difficulty_words = ['easy', 'lätt', 'medium', 'medel']
        elif self.min_difficulty in ['medium', 'medel'] and self.max_difficulty in ['hard', 'svår', 'tuff']:
            # Include medium and hard
            all_difficulty_words = ['medium', 'medel', 'hard', 'svår', 'tuff']
       
        # Create conditions for the mapped words
        if all_difficulty_words:
            word_conditions = []
            for word in all_difficulty_words:
                word_conditions.append(f"Cat_1_Kort_2 LIKE '%{word}%'")
            
            query += f" AND ({' OR '.join(word_conditions)})"
       
        return query, params
   
    def get_filter_type(self) -> str:
        return FilterCategory.DIFFICULTY
   
    def get_description(self) -> str:
        return f"Difficulty range: {self.min_difficulty} to {self.max_difficulty}"

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
