from typing import List, Dict, Any, Optional
from ..storage.sqlite_storage import SQLiteStorage
from ..filters.base_filter import IUniversalFilter, FilterCategory
from ...objects.question import Question
import logging

class QuestionRepository:
    """Repository for accessing questions with universal filter support"""
    
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage
        self.logger = logging.getLogger(__name__)
    
    def get_questions_raw(self, filters: List[IUniversalFilter] = None, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get raw question data (as dictionaries) with filters applied
        
        Args:
            filters: List of filters to apply
            limit: Maximum number of questions to return
            
        Returns:
            List of question dictionaries
        """
        try:
            # Start with base query - use the actual table name
            query = "SELECT rowid, * FROM game_questions WHERE 1=1"
            params = []
            
            # Apply filters
            if filters:
                query, params = self._apply_filters(query, params, filters)
            
            # Add limit if specified and not already added by a filter
            if limit and "LIMIT" not in query.upper():
                query += f" LIMIT {limit}"
            
            self.logger.debug(f"Executing query: {query} with params: {params}")
            
            # Execute query and convert to dictionaries
            rows = self.storage.fetch_all(query, tuple(params))
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Error fetching raw questions: {e}")
            raise
    
    def get_questions(self, filters: List[IUniversalFilter] = None, limit: int = None) -> List[Question]:
        """
        Get Question objects with filters applied
        
        Args:
            filters: List of filters to apply
            limit: Maximum number of questions to return
            
        Returns:
            List of Question objects
        """
        try:
            raw_data = self.get_questions_raw(filters, limit)
            questions = []
            
            for row_data in raw_data:
                try:
                    # Convert raw data to Question object
                    question = self._dict_to_question(row_data)
                    questions.append(question)
                except Exception as e:
                    self.logger.warning(f"Failed to convert row to Question: {e}, row: {row_data}")
                    continue
            
            self.logger.info(f"Retrieved {len(questions)} questions")
            return questions
            
        except Exception as e:
            self.logger.error(f"Error fetching questions: {e}")
            raise
    
    def count_questions(self, filters: List[IUniversalFilter] = None) -> int:
        """
        Count questions matching the given filters
        
        Args:
            filters: List of filters to apply
            
        Returns:
            Number of matching questions
        """
        try:
            # Start with count query - use the actual table name
            query = "SELECT COUNT(*) as count FROM game_questions WHERE 1=1"
            params = []
            
            # Apply filters (excluding LIMIT, OFFSET, ORDER BY)
            if filters:
                content_filters = [f for f in filters if not self._is_result_modifier_filter(f)]
                query, params = self._apply_filters(query, params, content_filters)
            
            self.logger.debug(f"Executing count query: {query} with params: {params}")
            
            result = self.storage.fetch_one(query, tuple(params))
            count = result['count'] if result else 0
            
            self.logger.debug(f"Question count: {count}")
            return count
            
        except Exception as e:
            self.logger.error(f"Error counting questions: {e}")
            raise
    
    def get_random_questions(self, count: int, filters: List[IUniversalFilter] = None) -> List[Question]:
        """
        Get random questions with filters applied
        
        Args:
            count: Number of questions to return
            filters: List of filters to apply
            
        Returns:
            List of random Question objects
        """
        from ..filters.behavior_filters import RandomOrderFilter, LimitFilter
        
        # Add random order and limit filters
        random_filters = filters.copy() if filters else []
        random_filters.extend([
            RandomOrderFilter(),
            LimitFilter(count)
        ])
        
        return self.get_questions(random_filters)
    
    def get_available_categories(self, filters: List[IUniversalFilter] = None) -> List[str]:
        """
        Get list of available categories (optionally filtered)
        
        Args:
            filters: List of filters to apply
            
        Returns:
            List of category names
        """
        try:
            query = "SELECT DISTINCT category FROM questions WHERE 1=1 AND category IS NOT NULL"
            params = []
            
            # Apply filters (excluding category filters to avoid circular logic)
            if filters:
                non_category_filters = [f for f in filters if f.get_filter_type() != FilterCategory.CONTENT or 'category' not in f.get_description().lower()]
                query, params = self._apply_filters(query, params, non_category_filters)
            
            query += " ORDER BY category"
            
            rows = self.storage.fetch_all(query, tuple(params))
            categories = [row['category'] for row in rows if row['category']]
            
            self.logger.debug(f"Available categories: {categories}")
            return categories
            
        except Exception as e:
            self.logger.error(f"Error fetching categories: {e}")
            return []
    
    def get_available_difficulties(self, filters: List[IUniversalFilter] = None) -> List[str]:
        """
        Get list of available difficulty levels (optionally filtered)
        
        Args:
            filters: List of filters to apply
            
        Returns:
            List of difficulty levels
        """
        try:
            query = "SELECT DISTINCT difficulty FROM questions WHERE 1=1 AND difficulty IS NOT NULL"
            params = []
            
            # Apply filters (excluding difficulty filters)
            if filters:
                non_difficulty_filters = [f for f in filters if f.get_filter_type() != FilterCategory.DIFFICULTY]
                query, params = self._apply_filters(query, params, non_difficulty_filters)
            
            query += " ORDER BY difficulty"
            
            rows = self.storage.fetch_all(query, tuple(params))
            difficulties = [row['difficulty'] for row in rows if row['difficulty']]
            
            self.logger.debug(f"Available difficulties: {difficulties}")
            return difficulties
            
        except Exception as e:
            self.logger.error(f"Error fetching difficulties: {e}")
            return []
    
    def _apply_filters(self, query: str, params: List, filters: List[IUniversalFilter]) -> tuple[str, List]:
        """Apply a list of filters to a query"""
        current_query = query
        current_params = params.copy()
        
        # Group filters by type for better SQL generation
        filter_groups = self._group_filters_by_type(filters)
        
        # Apply filters in a logical order
        for filter_type in [FilterCategory.GAME_MODE, FilterCategory.CONTENT, FilterCategory.DIFFICULTY, FilterCategory.BEHAVIOR]:
            if filter_type in filter_groups:
                for filter_obj in filter_groups[filter_type]:
                    try:
                        current_query, current_params = filter_obj.apply_to_query(current_query, current_params)
                    except Exception as e:
                        self.logger.warning(f"Failed to apply filter {filter_obj.get_description()}: {e}")
                        continue
        
        # Apply any remaining filters (composite, etc.)
        remaining_filters = [f for f in filters if f.get_filter_type() not in [FilterCategory.GAME_MODE, FilterCategory.CONTENT, FilterCategory.DIFFICULTY, FilterCategory.BEHAVIOR]]
        for filter_obj in remaining_filters:
            try:
                current_query, current_params = filter_obj.apply_to_query(current_query, current_params)
            except Exception as e:
                self.logger.warning(f"Failed to apply filter {filter_obj.get_description()}: {e}")
                continue
        
        return current_query, current_params
    
    def _group_filters_by_type(self, filters: List[IUniversalFilter]) -> Dict[str, List[IUniversalFilter]]:
        """Group filters by their type"""
        groups = {}
        for filter_obj in filters:
            filter_type = filter_obj.get_filter_type()
            if filter_type not in groups:
                groups[filter_type] = []
            groups[filter_type].append(filter_obj)
        return groups
    
    def _is_result_modifier_filter(self, filter_obj: IUniversalFilter) -> bool:
        """Check if filter modifies result set (LIMIT, OFFSET, ORDER BY) rather than filtering content"""
        filter_desc = filter_obj.get_description().lower()
        return any(keyword in filter_desc for keyword in ['limit', 'offset', 'random', 'order'])
    
    def _dict_to_question(self, row_data: Dict[str, Any]) -> Question:
        """Convert a database row dictionary to a Question object"""
        # Use the new from_database_row method that handles the Swedish/English schema
        row_id = row_data.get('rowid', 0)
        return Question.from_database_row(row_data, row_id)
    
    def validate_filters(self, filters: List[IUniversalFilter]) -> List[str]:
        """
        Validate a list of filters and return any error messages
        
        Args:
            filters: List of filters to validate
            
        Returns:
            List of error messages (empty if all valid)
        """
        errors = []
        
        if not filters:
            return errors
        
        # Check for conflicting filters
        filter_types = [f.get_filter_type() for f in filters]
        
        # Check for multiple game mode filters
        game_mode_count = filter_types.count(FilterCategory.GAME_MODE)
        if game_mode_count > 1:
            errors.append("Multiple game mode filters detected - only one game mode should be active")
        
        # Check filter compatibility
        for i, filter1 in enumerate(filters):
            for j, filter2 in enumerate(filters[i+1:], i+1):
                if not filter1.is_compatible_with(filter2):
                    errors.append(f"Incompatible filters: {filter1.get_description()} and {filter2.get_description()}")
        
        return errors
