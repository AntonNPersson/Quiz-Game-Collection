from typing import List, Optional, Dict, Any
import json

class Question:
    """Class representing a question in a quiz or survey, adapted for the Swedish/English game database."""

    # Updated allowed attributes based on the actual database schema
    ALLOWED_ATTRIBUTES = {
        # Core question content
        "text_en", "text_se", "text",  # Question text in different languages
        "info_en", "info_se", "info",  # Answer/info text
        "has_info",  # Boolean indicating if question has an answer
        
        # Question classification
        "question_type",  # "truth" or "dare" (mapped from Kort_1)
        "category",  # General category
        "difficulty",  # Mapped from Seriös field
        "spice_level",  # Mapped from Krydda field
        "language",  # Language availability
        
        # Game mechanics
        "who_involve",  # Who needs to be involved
        "official_group",  # Official question group
        "parent_appropriate",  # If suitable for parents
        "sensitive_subject",  # If it's a sensitive topic
        
        # Media and interaction
        "picture_link_sound",  # Media attachments
        "punish_and_or_reward",  # If question involves punishment/reward
        "move_video_phone",  # Movement/video requirements
        
        # Traditional quiz attributes (for compatibility)
        "options", "correct_answer"
    }

    def __init__(self, id: int, text: str, validate: bool = True, **kwargs: Any):
        """
        Initializes a Question instance.

        :param id: Unique identifier for the question (can be row index)
        :param text: The text of the question (primary language)
        :param kwargs: Additional attributes from the database
        """
        self.id: int = id
        self.text: str = text

        # Set attributes from kwargs
        for key, value in kwargs.items():
            if key in self.ALLOWED_ATTRIBUTES:
                setattr(self, key, value)
            else:
                print(f"Warning: {key} is not a valid attribute for Question. Allowed attributes are {self.ALLOWED_ATTRIBUTES}.")

        if validate and not self.validate():
            raise ValueError("Invalid question attributes. Please check the provided values.")

    # Core Methods
    def is_correct(self, answer: str) -> bool:
        """Checks if the provided answer is correct."""
        # For traditional quiz questions with correct_answer
        if hasattr(self, 'correct_answer'):
            return str(self.correct_answer) == str(answer)
        
        # For truth/dare questions, there's no "correct" answer
        return False
    
    def has_multiple_choices(self) -> bool:
        """Checks if the question has multiple choice options."""
        return hasattr(self, 'options') and isinstance(self.options, list) and len(self.options) > 1
    
    def has_answer_info(self) -> bool:
        """Checks if the question has answer information."""
        return getattr(self, 'has_info', False) or hasattr(self, 'info') or hasattr(self, 'info_en') or hasattr(self, 'info_se')
    
    def is_truth_question(self) -> bool:
        """Checks if this is a truth question."""
        return getattr(self, 'question_type', '').lower() == 'truth'
    
    def is_dare_question(self) -> bool:
        """Checks if this is a dare/consequence question."""
        return getattr(self, 'question_type', '').lower() in ['dare', 'consequence']
    
    # Getters/Setters
    def get_id(self) -> int:
        """Returns the unique identifier of the question."""
        return self.id
    
    def get_text(self, language: str = None) -> str:
        """Returns the text of the question in the specified language."""
        if language == 'en' and hasattr(self, 'text_en') and self.text_en:
            return self.text_en
        elif language == 'se' and hasattr(self, 'text_se') and self.text_se:
            return self.text_se
        return self.text
    
    def get_info(self, language: str = None) -> Optional[str]:
        """Returns the answer/info for the question in the specified language."""
        if language == 'en' and hasattr(self, 'info_en') and self.info_en:
            return self.info_en
        elif language == 'se' and hasattr(self, 'info_se') and self.info_se:
            return self.info_se
        elif hasattr(self, 'info') and self.info:
            return self.info
        return None
    
    def get_options(self) -> Optional[List[str]]:
        """Returns the options for the question if available."""
        return getattr(self, 'options', None)
    
    def get_correct_answer(self) -> Optional[str]:
        """Returns the correct answer for the question if available."""
        if hasattr(self, 'correct_answer'):
            return str(self.correct_answer)
        # For questions with info, return the info as the "answer"
        return self.get_info()
    
    def get_difficulty(self) -> Optional[str]:
        """Returns the difficulty level of the question."""
        return getattr(self, 'difficulty', None)
    
    def get_question_type(self) -> Optional[str]:
        """Returns the type of question (truth/dare)."""
        return getattr(self, 'question_type', None)
    
    def get_spice_level(self) -> Optional[str]:
        """Returns the spice level of the question."""
        return getattr(self, 'spice_level', None)

    # Filter Methods
    def matches_category(self, category: str) -> bool:
        """Checks if the given category matches the question's category or type."""
        if hasattr(self, 'category') and self.category:
            return self.category.lower() == category.lower()
        # Also check question type
        question_type = self.get_question_type()
        if question_type:
            return question_type.lower() == category.lower()
        return False
    
    def matches_difficulty(self, difficulty: str) -> bool:
        """Checks if the given difficulty matches the question's difficulty."""
        if hasattr(self, 'difficulty') and self.difficulty:
            return self.difficulty.lower() == difficulty.lower()
        return False
    
    def matches_spice_level(self, spice_level: str) -> bool:
        """Checks if the given spice level matches the question's spice level."""
        if hasattr(self, 'spice_level') and self.spice_level:
            return self.spice_level.lower() == spice_level.lower()
        return False
    
    def matches_language(self, language: str) -> bool:
        """Checks if the question supports the given language."""
        if hasattr(self, 'language'):
            lang = self.language.lower()
            if language.lower() == 'en':
                return 'en' in lang or 'both' in lang
            elif language.lower() == 'se':
                return 'se' in lang or 'both' in lang
        return True  # Default to true if no language restriction

    # Utility Methods
    def get_options_count(self) -> int:
        """Returns the number of options available for the question."""
        if hasattr(self, 'options') and isinstance(self.options, list):
            return len(self.options)
        return 0
    
    def validate(self) -> bool:
        """
        Validates the question's existing attributes.
        Only validates critical requirements.
        """
        # Validate required attributes
        if not self.text or not self.text.strip():
            print("Error: Question text cannot be empty.")
            return False
    
        if not isinstance(self.id, int) or self.id < 0:
            print("Error: Question ID must be a non-negative integer.")
            return False
        
        # Validate question type if present
        if hasattr(self, 'question_type') and self.question_type:
            valid_types = ['truth', 'dare', 'consequence', 'trivia']
            if self.question_type.lower() not in valid_types:
                print(f"Warning: Unusual question type: {self.question_type}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts the Question instance to a dictionary."""
        result = {"id": self.id, "text": self.text}
        for attr in self.ALLOWED_ATTRIBUTES:
            if hasattr(self, attr):
                value = getattr(self, attr)
                # Handle special serialization cases
                if isinstance(value, (list, dict)):
                    result[attr] = value
                else:
                    result[attr] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Question':
        """Creates a Question instance from a dictionary."""
        id_val = data.get("id", 0)
        text = data.get("text", "")
        kwargs = {key: value for key, value in data.items() 
                 if key in cls.ALLOWED_ATTRIBUTES and key not in ["id", "text"]}
        return cls(id=id_val, text=text, **kwargs)
    
    @classmethod
    def from_database_row(cls, row_data: Dict[str, Any], row_id: int = None) -> 'Question':
        """
        Creates a Question instance from a database row.
        Maps the Swedish/English database schema to our Question object.
        """
        # Use provided row_id or try to get from data
        question_id = row_id if row_id is not None else row_data.get('id', 0)
        
        # Determine primary text (prefer English, fallback to Swedish)
        text = row_data.get('Fråga_EN') or row_data.get('Fråga_Svenska', '')
        
        # Map database fields to our attributes
        kwargs = {}
        
        # Text in different languages
        if row_data.get('Fråga_EN'):
            kwargs['text_en'] = row_data['Fråga_EN']
        if row_data.get('Fråga_Svenska'):
            kwargs['text_se'] = row_data['Fråga_Svenska']
        
        # Answer/info fields
        if row_data.get('Info_EN'):
            kwargs['info_en'] = row_data['Info_EN']
        if row_data.get('Info_SE'):
            kwargs['info_se'] = row_data['Info_SE']
        if row_data.get('Info'):
            kwargs['info'] = row_data['Info']
        if row_data.get('Has_Info') is not None:
            kwargs['has_info'] = bool(row_data['Has_Info'])
        
        # Question classification
        if row_data.get('Kort_1'):
            # Map Swedish terms to English
            kort_1 = row_data['Kort_1'].lower()
            if kort_1 == 'sanning':
                kwargs['question_type'] = 'truth'
                kwargs['category'] = 'truth'
            elif kort_1 == 'konsekvens':
                kwargs['question_type'] = 'dare'
                kwargs['category'] = 'dare'
            else:
                kwargs['question_type'] = kort_1
                kwargs['category'] = kort_1
        
        # Difficulty mapping (Seriös field)
        if row_data.get('Seriös'):
            kwargs['difficulty'] = cls._map_difficulty(row_data['Seriös'])
        
        # Spice level mapping (Krydda field)
        if row_data.get('Krydda'):
            kwargs['spice_level'] = cls._map_spice_level(row_data['Krydda'])
        
        # Other fields
        if row_data.get('Language'):
            kwargs['language'] = row_data['Language']
        if row_data.get('Who_involve'):
            kwargs['who_involve'] = row_data['Who_involve']
        if row_data.get('Official_group'):
            kwargs['official_group'] = row_data['Official_group']
        if row_data.get('Parent'):
            kwargs['parent_appropriate'] = row_data['Parent'] == 'ParentWorks'
        if row_data.get('Sensitive_subject'):
            kwargs['sensitive_subject'] = row_data['Sensitive_subject']
        if row_data.get('Picture_link_sound'):
            kwargs['picture_link_sound'] = row_data['Picture_link_sound']
        if row_data.get('Punish_and_or_reward'):
            kwargs['punish_and_or_reward'] = row_data['Punish_and_or_reward'] == 'Yes'
        if row_data.get('Move_video_phone'):
            kwargs['move_video_phone'] = row_data['Move_video_phone']
        
        return cls(id=question_id, text=text, **kwargs)
    
    @staticmethod
    def _map_difficulty(serios_value: str) -> str:
        """Map Swedish difficulty values to standardized difficulty levels based on numeric progression."""
        if not serios_value:
            return 'Medium'  # Default
        
        # Extract numeric level from the Seriös field
        import re
        numbers = re.findall(r'\d+', serios_value)
        if numbers:
            level = int(numbers[-1])  # Take the last number found
            if level <= 1:
                return 'Easy'
            elif level <= 3:
                return 'Medium'
            else:
                return 'Hard'
        
        return 'Medium'  # Default
    
    @staticmethod
    def _map_spice_level(krydda_value: str) -> str:
        """Map Swedish spice level values to standardized spice levels based on numeric progression."""
        if not krydda_value:
            return 'Mild'  # Default
        
        # Extract numeric level from the Krydda field
        import re
        numbers = re.findall(r'\d+', krydda_value)
        if numbers:
            level = int(numbers[-1])  # Take the last number found
            if level == 0:
                return 'Mild'
            elif level == 1:
                return 'Spicy'
            else:
                return 'Very Spicy'  # For future extensibility
        
        return 'Mild'  # Default
    
    def __eq__(self, value):
        """Checks if two Question instances are equal based on their id."""
        if isinstance(value, Question):
            return self.id == value.id
        return False
    
    def __hash__(self):
        """Returns a hash based on the question's id."""
        return hash(self.id)

    def __repr__(self) -> str:
        """Returns a string representation of the Question instance."""
        question_type = getattr(self, 'question_type', 'unknown')
        difficulty = getattr(self, 'difficulty', 'unknown')
        spice = getattr(self, 'spice_level', 'unknown')
        return f"Question(id={self.id}, type='{question_type}', difficulty='{difficulty}', spice='{spice}', text='{self.text[:50]}...')"
