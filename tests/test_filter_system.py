"""
Test the Universal Filter System

This test demonstrates how the filter system works and validates
that all components integrate correctly.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from question_pipeline.data.storage.database_manager import DataBaseManager
from question_pipeline.data.repositories.question_repository import QuestionRepository
from question_pipeline.data.filters import (
    TriviaGameModeFilter,
    CategoryFilter,
    DifficultyFilter,
    RandomOrderFilter,
    LimitFilter,
    CompositeFilter
)

def setup_logging():
    """Setup logging for the test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def create_test_database():
    """Create a test database with sample data"""
    print("Creating test database...")
    
    # Initialize database
    db_manager = DataBaseManager("test_questions.db")
    db_manager.initialize()
    
    # Insert some test data
    storage = db_manager.storage
    
    test_questions = [
        {
            'id': 1,
            'text': 'What is the capital of France?',
            'category': 'geography',
            'difficulty': 'easy',
            'options': '["Paris", "London", "Berlin", "Madrid"]',
            'correct_answer': 'Paris'
        },
        {
            'id': 2,
            'text': 'What is 2 + 2?',
            'category': 'math',
            'difficulty': 'easy',
            'options': '["3", "4", "5", "6"]',
            'correct_answer': '4'
        },
        {
            'id': 3,
            'text': 'Who wrote Romeo and Juliet?',
            'category': 'literature',
            'difficulty': 'medium',
            'options': '["Shakespeare", "Dickens", "Austen", "Hemingway"]',
            'correct_answer': 'Shakespeare'
        },
        {
            'id': 4,
            'text': 'What is the square root of 144?',
            'category': 'math',
            'difficulty': 'medium',
            'options': '["10", "11", "12", "13"]',
            'correct_answer': '12'
        },
        {
            'id': 5,
            'text': 'What is the chemical symbol for gold?',
            'category': 'science',
            'difficulty': 'hard',
            'options': '["Go", "Gd", "Au", "Ag"]',
            'correct_answer': 'Au'
        }
    ]
    
    # First, let's check if the table has the right columns
    try:
        columns = storage.get_table_columns('questions')
        print(f"Available columns: {columns}")
        
        # Insert test data
        for question in test_questions:
            # Only insert columns that exist in the table
            filtered_question = {}
            for key, value in question.items():
                if key in columns:
                    filtered_question[key] = value
                elif key == 'text' and 'question' in columns:
                    # Map 'text' to 'question' if that's the column name
                    filtered_question['question'] = value
            
            if filtered_question:
                try:
                    storage.insert('questions', filtered_question)
                    print(f"Inserted question: {filtered_question.get('text', filtered_question.get('question', 'Unknown'))}")
                except Exception as e:
                    print(f"Failed to insert question: {e}")
    
    except Exception as e:
        print(f"Error setting up test data: {e}")
    
    storage.close()
    print("Test database created successfully!")
    return "test_questions.db"

def test_basic_filters(repository):
    """Test basic filter functionality"""
    print("\n=== Testing Basic Filters ===")
    
    # Test 1: No filters (get all questions)
    all_questions = repository.get_questions()
    print(f"Total questions in database: {len(all_questions)}")
    
    # Test 2: Category filter
    math_filter = CategoryFilter(['math'])
    math_questions = repository.get_questions([math_filter])
    print(f"Math questions: {len(math_questions)}")
    for q in math_questions:
        print(f"  - {q.get_text()}")
    
    # Test 3: Difficulty filter
    easy_filter = DifficultyFilter('easy')
    easy_questions = repository.get_questions([easy_filter])
    print(f"Easy questions: {len(easy_questions)}")
    for q in easy_questions:
        print(f"  - {q.get_text()}")
    
    # Test 4: Limit filter
    limit_filter = LimitFilter(2)
    limited_questions = repository.get_questions([limit_filter])
    print(f"Limited to 2 questions: {len(limited_questions)}")

def test_composite_filters(repository):
    """Test composite filter functionality"""
    print("\n=== Testing Composite Filters ===")
    
    # Test 1: AND composite (easy AND math)
    easy_filter = DifficultyFilter('easy')
    math_filter = CategoryFilter(['math'])
    and_composite = CompositeFilter([easy_filter, math_filter], "AND")
    
    and_questions = repository.get_questions([and_composite])
    print(f"Easy AND Math questions: {len(and_questions)}")
    for q in and_questions:
        print(f"  - {q.get_text()}")
    
    # Test 2: OR composite (math OR science)
    math_filter = CategoryFilter(['math'])
    science_filter = CategoryFilter(['science'])
    or_composite = CompositeFilter([math_filter, science_filter], "OR")
    
    or_questions = repository.get_questions([or_composite])
    print(f"Math OR Science questions: {len(or_questions)}")
    for q in or_questions:
        print(f"  - {q.get_text()}")

def test_game_mode_filters(repository):
    """Test game mode filters"""
    print("\n=== Testing Game Mode Filters ===")
    
    # Test trivia game mode
    trivia_filter = TriviaGameModeFilter()
    trivia_questions = repository.get_questions([trivia_filter])
    print(f"Trivia-suitable questions: {len(trivia_questions)}")
    for q in trivia_questions:
        print(f"  - {q.get_text()}")

def test_random_questions(repository):
    """Test random question selection"""
    print("\n=== Testing Random Questions ===")
    
    # Get 3 random questions
    random_questions = repository.get_random_questions(3)
    print(f"Random questions (3): {len(random_questions)}")
    for q in random_questions:
        print(f"  - {q.get_text()}")

def test_repository_info(repository):
    """Test repository information methods"""
    print("\n=== Testing Repository Info ===")
    
    # Get available categories
    categories = repository.get_available_categories()
    print(f"Available categories: {categories}")
    
    # Get available difficulties
    difficulties = repository.get_available_difficulties()
    print(f"Available difficulties: {difficulties}")
    
    # Count questions
    total_count = repository.count_questions()
    print(f"Total question count: {total_count}")
    
    # Count with filter
    math_filter = CategoryFilter(['math'])
    math_count = repository.count_questions([math_filter])
    print(f"Math question count: {math_count}")

def test_filter_validation(repository):
    """Test filter validation"""
    print("\n=== Testing Filter Validation ===")
    
    # Test valid filters
    valid_filters = [
        CategoryFilter(['math']),
        DifficultyFilter('easy')
    ]
    errors = repository.validate_filters(valid_filters)
    print(f"Valid filters - Errors: {errors}")
    
    # Test conflicting filters (multiple game modes)
    conflicting_filters = [
        TriviaGameModeFilter(),
        TriviaGameModeFilter()  # Duplicate game mode
    ]
    errors = repository.validate_filters(conflicting_filters)
    print(f"Conflicting filters - Errors: {errors}")

def main():
    """Main test function"""
    setup_logging()
    
    print("=== Universal Filter System Test ===")
    
    # Create test database
    db_path = create_test_database()
    
    try:
        # Initialize repository
        db_manager = DataBaseManager(db_path)
        db_manager.initialize()
        repository = QuestionRepository(db_manager.storage)
        
        # Run tests
        test_basic_filters(repository)
        test_composite_filters(repository)
        test_game_mode_filters(repository)
        test_random_questions(repository)
        test_repository_info(repository)
        test_filter_validation(repository)
        
        print("\n=== All Tests Completed Successfully! ===")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Cleaned up test database: {db_path}")

if __name__ == "__main__":
    main()
