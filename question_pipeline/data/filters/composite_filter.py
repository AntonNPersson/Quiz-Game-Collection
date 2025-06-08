from .base_filter import IUniversalFilter, FilterCategory
from typing import Tuple, List

class CompositeFilter(IUniversalFilter):
    """Combines multiple filters with AND/OR logic"""
    
    def __init__(self, filters: List[IUniversalFilter], operator: str = "AND"):
        self.filters = filters
        self.operator = operator.upper()
        
        if self.operator not in ["AND", "OR"]:
            raise ValueError("Operator must be 'AND' or 'OR'")
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        if not self.filters:
            return query, params
        
        # Apply each filter sequentially to build up the query
        current_query = query
        current_params = params.copy()
        
        for filter_obj in self.filters:
            current_query, current_params = filter_obj.apply_to_query(current_query, current_params)
        
        return current_query, current_params
    
    def get_filter_type(self) -> str:
        # Return the most specific type, or "composite" if mixed
        filter_types = [f.get_filter_type() for f in self.filters]
        unique_types = set(filter_types)
        
        if len(unique_types) == 1:
            return list(unique_types)[0]
        else:
            return "composite"
    
    def get_description(self) -> str:
        if not self.filters:
            return "Empty composite filter"
        
        descriptions = [f.get_description() for f in self.filters]
        return f" {self.operator} ".join(descriptions)
    
    def is_compatible_with(self, other_filter: 'IUniversalFilter') -> bool:
        # Check if all our filters are compatible with the other filter
        return all(f.is_compatible_with(other_filter) for f in self.filters)
    
    def add_filter(self, filter_obj: IUniversalFilter):
        """Add another filter to this composite"""
        self.filters.append(filter_obj)
    
    def remove_filter(self, filter_obj: IUniversalFilter):
        """Remove a filter from this composite"""
        if filter_obj in self.filters:
            self.filters.remove(filter_obj)
    
    def get_filters_by_type(self, filter_type: str) -> List[IUniversalFilter]:
        """Get all filters of a specific type"""
        return [f for f in self.filters if f.get_filter_type() == filter_type]
    
    def has_filter_type(self, filter_type: str) -> bool:
        """Check if this composite contains any filters of the given type"""
        return any(f.get_filter_type() == filter_type for f in self.filters)

class FilterChain(IUniversalFilter):
    """Applies filters in sequence (each filter operates on the result of the previous)"""
    
    def __init__(self, filters: List[IUniversalFilter]):
        self.filters = filters
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        # Apply filters sequentially
        current_query = query
        current_params = params.copy()
        
        for filter_obj in self.filters:
            current_query, current_params = filter_obj.apply_to_query(current_query, current_params)
        
        return current_query, current_params
    
    def get_filter_type(self) -> str:
        return "chain"
    
    def get_description(self) -> str:
        if not self.filters:
            return "Empty filter chain"
        
        descriptions = [f.get_description() for f in self.filters]
        return " → ".join(descriptions)

class ConditionalFilter(IUniversalFilter):
    """Applies different filters based on conditions"""
    
    def __init__(self, condition_func, true_filter: IUniversalFilter, false_filter: IUniversalFilter = None):
        self.condition_func = condition_func
        self.true_filter = true_filter
        self.false_filter = false_filter
    
    def apply_to_query(self, query: str, params: list) -> Tuple[str, List]:
        # Evaluate condition (this would need context passed in somehow)
        # For now, we'll just apply the true filter
        if self.condition_func():
            return self.true_filter.apply_to_query(query, params)
        elif self.false_filter:
            return self.false_filter.apply_to_query(query, params)
        else:
            return query, params
    
    def get_filter_type(self) -> str:
        return "conditional"
    
    def get_description(self) -> str:
        desc = f"If condition: {self.true_filter.get_description()}"
        if self.false_filter:
            desc += f" Else: {self.false_filter.get_description()}"
        return desc
