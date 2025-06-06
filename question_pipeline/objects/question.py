from typing import List, Optional

class Question:
    """Class representing a question in a quiz or survey, containing all necessary attributes."""

    ALLOWED_ATTRIBUTES = {"options", "correct_answer", "difficulty", "category"}

    def __init__(self, id: int, text: str, validate: bool = True, **kwargs: any):
        """
        Initializes a Question instance.

        :param id: Unique identifier for the question.
        :param text: The text of the question.
        :param kwargs: Additional attributes such as options, correct answer, etc.
        """
        self.id: int = id
        self.text: str = text

        for key, value in kwargs.items():
            if key in self.ALLOWED_ATTRIBUTES:
                setattr(self, key, value)
            else:
                print(f"Warning: {key} is not a valid attribute for Question. Allowed attributes are {self.ALLOWED_ATTRIBUTES}. If you want to add a new attribute, please modify the ALLOWED_ATTRIBUTES set.")

        if validate and not self.validate():
            raise ValueError("Invalid question attributes. Please check the provided values.")

    # Core Methods
    def is_correct(self, answer: str) -> bool:
        """Checks if the provided answer is correct."""
        if hasattr(self, 'correct_answer'):
            return self.correct_answer == answer
        return False
    
    def has_multiple_choices(self) -> bool:
        """Checks if the question has multiple choice options."""
        return hasattr(self, 'options') and isinstance(self.options, list) and len(self.options) > 1
    
    # Getters/Setters
    def get_id(self) -> int:
        """Returns the unique identifier of the question."""
        return self.id
    
    def get_text(self) -> str:
        """Returns the text of the question."""
        return self.text
    
    def get_options(self) -> Optional[List[str]]:
        """Returns the options for the question if available."""
        return getattr(self, 'options', None)
    
    def get_correct_answer(self) -> Optional[str]:
        """Returns the correct answer for the question if available."""
        return getattr(self, 'correct_answer', "Unknown correct answer")
    
    def get_difficulty(self) -> Optional[str]:
        """Returns the difficulty level of the question if available."""
        return getattr(self, 'difficulty', "Medium")

    # Filter Methods
    def matches_category(self, category: str) -> bool:
        """Checks if the given category matches the objects category"""
        if hasattr(self, 'category'):
            return self.category == category
        return False
    
    def matches_difficulty(self, difficulty: str) -> bool:
        """Checks if the given difficulty matches the objects difficulty"""
        if hasattr(self, 'difficulty'):
            return self.difficulty == difficulty
        return False

    # Utility Methods
    def get_options_count(self) -> int:
        """Returns the number of options available for the question."""
        if hasattr(self, 'options') and isinstance(self.options, list):
            return len(self.options)
        else:
            print("Warning: No options available for this question.")
        return 0
    
    def validate(self) -> bool:
        """
        Validates the question's existing attributes.
        Only validates critical requirements.
        """
        # Validate required attributes
        if not self.text.strip():
            print("Error: Question text cannot be empty.")
            return False
    
        if not isinstance(self.id, int) or self.id <= 0:
            print("Error: Question ID must be a positive integer.")
            return False
        
        # Only validate critical relationships
        if hasattr(self, 'correct_answer') and hasattr(self, 'options'):
            if isinstance(self.correct_answer, int):
                if not (0 <= self.correct_answer < len(self.options)):
                    print("Error: correct_answer index is out of range for options.")
                    return False
        
        return True
    
    def to_dict(self) -> dict:
        """Converts the Question instance to a dictionary."""
        result = {"id": self.id, "text": self.text}
        for attr in self.ALLOWED_ATTRIBUTES:
            if hasattr(self, attr):
                result[attr] = getattr(self, attr)
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Question':
        """Creates a Question instance from a dictionary."""
        id = data.get("id")
        text = data.get("text")
        kwargs = {key: value for key, value in data.items() if key in cls.ALLOWED_ATTRIBUTES}
        return cls(id=id, text=text, **kwargs)
    
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
        return f"Question(id={self.id}, text='{self.text}', options={self.options}, correct_answer='{self.correct_answer}', difficulty='{self.difficulty}', category='{self.category}')"