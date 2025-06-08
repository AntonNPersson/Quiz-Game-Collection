from .base_filter import IUniversalFilter, FilterCategory
from typing import Tuple, List

class CategoryFilter(IUniversalFilter):
    """Filter questions by category"""
    
    def __init__(self, categories: List[str]):
        self.categories = [cat.lower() for cat in categories]
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if not self.categories:
            return query, params
        
        placeholders = ','.join(['?' for _ in self.categories])
        query += f" AND LOWER(category) IN ({placeholders})"
        params.extend(self.categories)
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.CONTENT
    
    def get_description(self) -> str:
        return f"Category filter: {', '.join(self.categories)}"

class TopicFilter(IUniversalFilter):
    """Filter questions by topic/subject"""
    
    def __init__(self, topics: List[str]):
        self.topics = [topic.lower() for topic in topics]
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if not self.topics:
            return query, params
        
        # Search in both category and text for topic matches
        topic_conditions = []
        for topic in self.topics:
            topic_conditions.append("(LOWER(category) LIKE ? OR LOWER(text) LIKE ?)")
            params.extend([f"%{topic}%", f"%{topic}%"])
        
        if topic_conditions:
            query += f" AND ({' OR '.join(topic_conditions)})"
        
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.CONTENT
    
    def get_description(self) -> str:
        return f"Topic filter: {', '.join(self.topics)}"

class KeywordFilter(IUniversalFilter):
    """Filter questions containing specific keywords"""
    
    def __init__(self, keywords: List[str], match_all: bool = False):
        self.keywords = [keyword.lower() for keyword in keywords]
        self.match_all = match_all  # True = AND, False = OR
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if not self.keywords:
            return query, params
        
        keyword_conditions = []
        for keyword in self.keywords:
            keyword_conditions.append("LOWER(text) LIKE ?")
            params.append(f"%{keyword}%")
        
        if keyword_conditions:
            operator = " AND " if self.match_all else " OR "
            query += f" AND ({operator.join(keyword_conditions)})"
        
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.CONTENT
    
    def get_description(self) -> str:
        operator = "all" if self.match_all else "any"
        return f"Keyword filter ({operator}): {', '.join(self.keywords)}"

class ExcludeCategoryFilter(IUniversalFilter):
    """Exclude questions from specific categories"""
    
    def __init__(self, excluded_categories: List[str]):
        self.excluded_categories = [cat.lower() for cat in excluded_categories]
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if not self.excluded_categories:
            return query, params
        
        placeholders = ','.join(['?' for _ in self.excluded_categories])
        query += f" AND LOWER(category) NOT IN ({placeholders})"
        params.extend(self.excluded_categories)
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.CONTENT
    
    def get_description(self) -> str:
        return f"Exclude categories: {', '.join(self.excluded_categories)}"
