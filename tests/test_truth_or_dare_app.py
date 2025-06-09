"""
Test script for the Truth or Dare application

This script tests the complete Truth or Dare application to ensure
all components work together correctly.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from games.truth_or_dare_app import TruthOrDareApp


def test_truth_or_dare_app():
    """Test the Truth or Dare application"""
    
    print("🎭 Testing Truth or Dare Application")
    print("=" * 50)
    
    # Database path
    db_path = "data/databases/game_questions.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        # Create app
        print("📱 Creating Truth or Dare app...")
        app = TruthOrDareApp(db_path, default_question_count=5)
        
        # Show question stats
        print("\n📊 Question Statistics:")
        stats = app.get_question_stats()
        print(f"  📝 Total Questions: {stats['total_questions']}")
        print(f"  🎭 By Type: {stats['by_type']}")
        print(f"  📊 By Difficulty: {stats['by_difficulty']}")
        print(f"  🌶️ By Spice Level: {stats['by_spice_level']}")
        
        # Create a test game
        print("\n🎮 Creating test game...")
        players = ["Alice", "Bob", "Charlie"]
        game_id = app.create_game(
            player_names=players,
            question_count=5,
            truth_ratio=0.6,
            spice_level="mild"
        )
        print(f"  ✅ Game created: {game_id}")
        
        # Start the game
        print("\n🚀 Starting game...")
        start_result = app.start_game(game_id)
        print(f"  ✅ Game started with {start_result['total_questions']} questions")
        print(f"  👥 Players: {', '.join(start_result['players'])}")
        print(f"  👤 Current player: {start_result['current_player']}")
        
        # Play through a few questions
        print("\n🎯 Playing through questions...")
        for i in range(3):  # Play 3 questions
            # Get current question
            question_data = app.get_current_question(game_id)
            
            if question_data.get('finished', False):
                print("  🏁 Game finished early!")
                break
            
            question = question_data['question']
            current_player = question_data['current_player']
            question_type = question_data.get('question_type', 'unknown')
            
            print(f"\n  📍 Question {i+1}:")
            print(f"    👤 Player: {current_player}")
            print(f"    🎭 Type: {question_type}")
            print(f"    ❓ Question: {question.get_text()[:100]}...")
            
            # Mark as completed
            result = app.complete_question(game_id, completed=True)
            print(f"    ✅ Completed! Action: {result['action']}")
            
            if result['session_complete']:
                print("  🎉 Game completed!")
                break
        
        # Show final status
        print("\n📊 Final Game Status:")
        final_status = app.get_game_status(game_id)
        print(f"  🎮 Game ID: {final_status['game_id']}")
        print(f"  📍 Progress: {final_status['current_question_index']}/{final_status['total_questions']}")
        print(f"  📈 Completion: {final_status['progress_percentage']:.1f}%")
        print(f"  ⏱️ Duration: {final_status.get('duration', 0):.1f} seconds")
        
        # End the game
        print("\n🏁 Ending game...")
        end_result = app.end_game(game_id)
        print(f"  ✅ Game ended: {end_result['game_ended']}")
        
        # Cleanup
        app.cleanup()
        
        print("\n✅ All tests passed! Truth or Dare app is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_app_factory():
    """Test the app factory functionality"""
    
    print("\n🏭 Testing App Factory")
    print("=" * 30)
    
    db_path = "data/databases/game_questions.db"
    
    try:
        from question_pipeline.factory.app_factory import AppFactory
        
        # Test creating app with factory
        print("📱 Creating app with factory...")
        app = AppFactory.create_truth_or_dare_app(
            database_path=db_path,
            player_names=["Test1", "Test2"],
            question_count=3,
            truth_ratio=0.5,
            spice_level="mild"
        )
        
        print("  ✅ App created successfully")
        
        # Test basic functionality
        stats = app.get_question_stats()
        print(f"  📊 Questions available: {stats['total_questions']}")
        
        # Cleanup
        app.cleanup()
        
        print("✅ App Factory test passed!")
        return True
        
    except Exception as e:
        print(f"❌ App Factory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🧪 Running Truth or Dare Application Tests")
    print("=" * 60)
    
    # Test the main app
    app_test_passed = test_truth_or_dare_app()
    
    # Test the factory
    factory_test_passed = test_app_factory()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"  🎭 Truth or Dare App: {'✅ PASSED' if app_test_passed else '❌ FAILED'}")
    print(f"  🏭 App Factory: {'✅ PASSED' if factory_test_passed else '❌ FAILED'}")
    
    if app_test_passed and factory_test_passed:
        print("\n🎉 All tests passed! The system is ready to use.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
