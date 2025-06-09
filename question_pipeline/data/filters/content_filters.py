from .base_filter import IUniversalFilter, FilterCategory
from typing import Tuple, List

class CategoryFilter(IUniversalFilter):
    """Filter questions by category (truth/dare)"""
    
    def __init__(self, categories: List[str]):
        self.categories = [cat.lower() for cat in categories]
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if not self.categories:
            return query, params
        
        # Map English terms to Swedish database values
        category_conditions = []
        for category in self.categories:
            if category in ['truth', 'sanning']:
                category_conditions.append("Kort_1 = 'Sanning'")
            elif category in ['dare', 'konsekvens', 'consequence']:
                category_conditions.append("Kort_1 = 'Konsekvens'")
            else:
                # Generic category search
                category_conditions.append("LOWER(Kort_1) LIKE ?")
                params.append(f"%{category}%")
        
        if category_conditions:
            query += f" AND ({' OR '.join(category_conditions)})"
        
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
        
        # Search in question text (both languages) and official groups
        topic_conditions = []
        for topic in self.topics:
            topic_conditions.append(
                "(LOWER(Fråga_EN) LIKE ? OR LOWER(Fråga_Svenska) LIKE ? OR LOWER(Official_group) LIKE ?)"
            )
            params.extend([f"%{topic}%", f"%{topic}%", f"%{topic}%"])
        
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
            # Search in both English and Swedish question text
            keyword_conditions.append(
                "(LOWER(Fråga_EN) LIKE ? OR LOWER(Fråga_Svenska) LIKE ?)"
            )
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
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
        
        # Map English terms to Swedish database values
        exclude_conditions = []
        for category in self.excluded_categories:
            if category in ['truth', 'sanning']:
                exclude_conditions.append("Kort_1 != 'Sanning'")
            elif category in ['dare', 'konsekvens', 'consequence']:
                exclude_conditions.append("Kort_1 != 'Konsekvens'")
            else:
                # Generic category exclusion
                exclude_conditions.append("LOWER(Kort_1) NOT LIKE ?")
                params.append(f"%{category}%")
        
        if exclude_conditions:
            query += f" AND ({' AND '.join(exclude_conditions)})"
        
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.CONTENT
    
    def get_description(self) -> str:
        return f"Exclude categories: {', '.join(self.excluded_categories)}"

class LanguageFilter(IUniversalFilter):
    """Filter questions by language availability based on actual database values
    
    Database Language column values:
    - "both" for questions available in both languages
    - "SE Only" for Swedish-only questions  
    - "EN Only" for English-only questions
    """
    
    def __init__(self, language: str):
        self.language = language.lower()
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if self.language == 'en':
            # English: include "both" and "EN Only"
            query += " AND (Language = 'both' OR Language = 'EN_Only')"
        elif self.language == 'se':
            # Swedish: include "both" and "SE Only"
            query += " AND (Language = 'both' OR Language = 'SE_Only')"
        elif self.language == 'both':
            # Both: only include questions available in both languages
            query += " AND Language = 'both'"
        
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.CONTENT
    
    def get_description(self) -> str:
        return f"Language filter: {self.language}"


class ParentAppropriateFilter(IUniversalFilter):
    """Filter for parent-appropriate questions"""
    
    def __init__(self, parent_appropriate: bool = True):
        self.parent_appropriate = parent_appropriate
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if self.parent_appropriate:
            query += " AND Parent = 'ParentWorks'"
        else:
            query += " AND (Parent != 'ParentWorks' OR Parent IS NULL)"
        
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.CONTENT
    
    def get_description(self) -> str:
        return f"Parent appropriate: {self.parent_appropriate}"

class HasInfoFilter(IUniversalFilter):
    """Filter questions that have answer information"""
    
    def __init__(self, has_info: bool = True):
        self.has_info = has_info
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if self.has_info:
            query += " AND Has_Info = 1"
        else:
            query += " AND (Has_Info = 0 OR Has_Info IS NULL)"
        
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.CONTENT
    
    def get_description(self) -> str:
        return f"Has answer info: {self.has_info}"

class OfficialGroupFilter(IUniversalFilter):
    """Filter questions by official group type"""
    
    def __init__(self, groups: List[str]):
        self.groups = [group.lower() for group in groups]
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if not self.groups:
            return query, params
        
        group_conditions = []
        for group in self.groups:
            if group == 'none':
                group_conditions.append("Official_group = 'No'")
            else:
                group_conditions.append("LOWER(Official_group) LIKE ?")
                params.append(f"%{group}%")
        
        if group_conditions:
            query += f" AND ({' OR '.join(group_conditions)})"
        
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.CONTENT
    
    def get_description(self) -> str:
        return f"Official group filter: {', '.join(self.groups)}"
    
class DareFilter(IUniversalFilter):
    """Filter questions by only dare questions"""

    def __init__(self):
        pass

    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        query += " AND Kort_1 = 'Konsekvens'"
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.CONTENT
    
    def get_description(self) -> str:
        return "Dare questions only (Kort_1 = 'Konsekvens')"
    
class TruthFilter(IUniversalFilter):
    """Filter questions by only truth questions"""

    def __init__(self):
        pass

    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        query += " AND Kort_1 = 'Sanning'"
        return query, params
    
    def get_filter_type(self) -> str:
        return FilterCategory.CONTENT
    
    def get_description(self) -> str:
        return "Truth questions only (Kort_1 = 'Sanning')"
