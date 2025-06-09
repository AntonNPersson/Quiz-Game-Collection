"""
Truth or Dare CLI Interface

Command-line interface for the Truth or Dare game application.
Provides an interactive way to play Truth or Dare games.
"""

import os
import sys
from typing import List, Optional
from pathlib import Path

from .app import TruthOrDareApp


class TruthOrDareCLI:
    """
    Command-line interface for Truth or Dare games
    
    Provides an interactive terminal-based interface for playing
    Truth or Dare with friends.
    """
    
    def __init__(self, database_path: str):
        """
        Initialize the CLI
        
        Args:
            database_path: Path to the question database
        """
        self.database_path = database_path
        self.app = None
        self.current_game_id = None
        
    def run(self):
        """Run the interactive CLI"""
        try:
            print("🎭 Welcome to Truth or Dare! 🎭")
            print("=" * 40)
            
            # Initialize app
            self.app = TruthOrDareApp(self.database_path)
            
            # Show stats
            self._show_question_stats()
            
            # Main game loop
            while True:
                if self.current_game_id is None:
                    self._main_menu()
                else:
                    self._game_menu()
                    
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for playing! Goodbye!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            if self.app:
                self.app.cleanup()
    
    def _main_menu(self):
        """Show main menu and handle selection"""
        print("\n📋 Main Menu:")
        print("1. Start New Game")
        print("2. View Question Statistics")
        print("3. Exit")
        
        choice = input("\nSelect an option (1-3): ").strip()
        
        if choice == "1":
            self._setup_new_game()
        elif choice == "2":
            self._show_question_stats()
        elif choice == "3":
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")
    
    def _setup_new_game(self):
        """Setup a new game"""
        print("\n🎮 Setting up new game...")
        
        # Get player names
        players = self._get_player_names()
        if not players:
            return
        
        # Get game settings
        settings = self._get_game_settings()
        
        try:
            # Create game
            self.current_game_id = self.app.create_game(
                player_names=players,
                question_count=settings['question_count'],
                truth_ratio=settings['truth_ratio'],
                spice_level=settings['spice_level']
            )
            
            print(f"\n✅ Game created! Game ID: {self.current_game_id}")
            print(f"👥 Players: {', '.join(players)}")
            print(f"❓ Questions: {settings['question_count']}")
            print(f"🎯 Truth ratio: {settings['truth_ratio']:.0%}")
            print(f"🌶️ Spice level: {settings['spice_level']}")
            
            # Start the game
            self._start_game()
            
        except Exception as e:
            print(f"❌ Failed to create game: {e}")
            self.current_game_id = None
    
    def _get_player_names(self) -> List[str]:
        """Get player names from user input"""
        print("\n👥 Enter player names (press Enter with empty name to finish):")
        
        players = []
        while True:
            player_name = input(f"Player {len(players) + 1}: ").strip()
            
            if not player_name:
                break
                
            if player_name in players:
                print("❌ Player name already exists. Please use a different name.")
                continue
                
            players.append(player_name)
            
            if len(players) >= 10:  # Reasonable limit
                print("ℹ️ Maximum 10 players reached.")
                break
        
        if not players:
            print("❌ At least one player is required.")
            return []
        
        return players
    
    def _get_game_settings(self) -> dict:
        """Get game settings from user input"""
        settings = {}
        
        # Question count
        while True:
            try:
                count = input("\n❓ Number of questions (default: 15): ").strip()
                if not count:
                    settings['question_count'] = 15
                    break
                count = int(count)
                if count <= 0:
                    print("❌ Number of questions must be positive.")
                    continue
                if count > 100:
                    print("❌ Maximum 100 questions allowed.")
                    continue
                settings['question_count'] = count
                break
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Truth ratio
        while True:
            try:
                ratio = input("\n🎯 Truth ratio (0.0-1.0, default: 0.6): ").strip()
                if not ratio:
                    settings['truth_ratio'] = 0.6
                    break
                ratio = float(ratio)
                if not 0.0 <= ratio <= 1.0:
                    print("❌ Truth ratio must be between 0.0 and 1.0.")
                    continue
                settings['truth_ratio'] = ratio
                break
            except ValueError:
                print("❌ Please enter a valid number between 0.0 and 1.0.")
        
        # Spice level
        print("\n🌶️ Spice level:")
        print("1. Mild (family-friendly)")
        print("2. Spicy (adult content)")
        
        while True:
            choice = input("Select spice level (1-2, default: 1): ").strip()
            if not choice or choice == "1":
                settings['spice_level'] = "mild"
                break
            elif choice == "2":
                settings['spice_level'] = "spicy"
                break
            else:
                print("❌ Please select 1 or 2.")
        
        return settings
    
    def _start_game(self):
        """Start the current game"""
        try:
            result = self.app.start_game(self.current_game_id)
            print(f"\n🎉 Game started!")
            print(f"🎮 Total questions: {result['total_questions']}")
            
        except Exception as e:
            print(f"❌ Failed to start game: {e}")
            self.current_game_id = None
    
    def _game_menu(self):
        """Show game menu and handle game actions"""
        try:
            # Get current question
            question_data = self.app.get_current_question(self.current_game_id)
            
            if question_data.get('finished', False):
                self._show_game_results()
                return
            
            # Display question
            self._display_question(question_data)
            
            # Get player action
            print("\n🎯 Actions:")
            print("1. Mark as Completed")
            print("2. Skip Question")
            print("3. View Game Status")
            print("4. End Game")
            
            choice = input("\nSelect action (1-4): ").strip()
            
            if choice == "1":
                self._complete_question(True)
            elif choice == "2":
                self._complete_question(False)
            elif choice == "3":
                self._show_game_status()
            elif choice == "4":
                self._end_current_game()
            else:
                print("❌ Invalid choice. Please select 1, 2, 3, or 4.")
                
        except Exception as e:
            print(f"❌ Game error: {e}")
            self.current_game_id = None
    
    def _display_question(self, question_data: dict):
        """Display the current question"""
        question = question_data['question']
        current_player = question_data.get('current_player', 'Unknown')
        question_num = question_data.get('question_number', 1)
        total_questions = question_data.get('total_questions', 1)
        question_type = question_data.get('question_type', 'unknown')
        
        print("\n" + "=" * 50)
        print(f"📍 Question {question_num}/{total_questions}")
        print(f"👤 Current Player: {current_player}")
        
        # Show question type with emoji
        type_emoji = "🤔" if question_type == "truth" else "💪"
        type_name = question_type.title()
        print(f"{type_emoji} Type: {type_name}")
        
        print("\n" + "-" * 50)
        print(f"❓ {question.get_text()}")
        
        # Show additional info if available
        info = question.get_info()
        if info:
            print(f"ℹ️ Info: {info}")
        
        print("-" * 50)
    
    def _complete_question(self, completed: bool):
        """Mark question as completed or skipped"""
        try:
            action = "completed" if completed else "skipped"
            result = self.app.complete_question(self.current_game_id, completed)
            
            if completed:
                print("✅ Question marked as completed!")
            else:
                print("⏭️ Question skipped!")
            
            if result['session_complete']:
                print("\n🎉 Game completed!")
                self._show_game_results()
            else:
                print(f"\n➡️ Moving to next question...")
                
        except Exception as e:
            print(f"❌ Error processing answer: {e}")
    
    def _show_game_status(self):
        """Show current game status"""
        try:
            status = self.app.get_game_status(self.current_game_id)
            
            print("\n📊 Game Status:")
            print(f"🎮 Game ID: {status['game_id']}")
            print(f"👥 Players: {', '.join(status['players'])}")
            print(f"👤 Current Player: {status['current_player']}")
            print(f"📍 Progress: {status['current_question_index']}/{status['total_questions']}")
            print(f"📈 Progress: {status['progress_percentage']:.1f}%")
            print(f"⏱️ Duration: {status.get('duration', 0):.1f} seconds")
            print(f"🎯 Truth Ratio: {status['truth_ratio']:.0%}")
            print(f"🌶️ Spice Level: {status['spice_level']}")
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
    
    def _show_game_results(self):
        """Show final game results"""
        try:
            status = self.app.get_game_status(self.current_game_id)
            
            print("\n🏆 Game Complete!")
            print("=" * 40)
            print(f"👥 Players: {', '.join(status['players'])}")
            print(f"❓ Questions Completed: {status['current_question_index']}/{status['total_questions']}")
            print(f"⏱️ Total Duration: {status.get('duration', 0):.1f} seconds")
            print(f"🎯 Truth Ratio: {status['truth_ratio']:.0%}")
            
            # End the game
            self._end_current_game()
            
        except Exception as e:
            print(f"❌ Error showing results: {e}")
            self.current_game_id = None
    
    def _end_current_game(self):
        """End the current game"""
        if self.current_game_id:
            try:
                self.app.end_game(self.current_game_id)
                print("🎮 Game ended.")
            except Exception as e:
                print(f"❌ Error ending game: {e}")
            finally:
                self.current_game_id = None
    
    def _show_question_stats(self):
        """Show question database statistics"""
        try:
            stats = self.app.get_question_stats()
            
            print("\n📊 Question Database Statistics:")
            print("=" * 40)
            print(f"📝 Total Questions: {stats['total_questions']}")
            
            print("\n🎭 By Type:")
            for q_type, count in stats['by_type'].items():
                emoji = "🤔" if q_type == "truth" else "💪" if q_type == "dare" else "❓"
                print(f"  {emoji} {q_type.title()}: {count}")
            
            print("\n📊 By Difficulty:")
            for difficulty, count in stats['by_difficulty'].items():
                emoji = "🟢" if difficulty == "Easy" else "🟡" if difficulty == "Medium" else "🔴"
                print(f"  {emoji} {difficulty}: {count}")
            
            print("\n🌶️ By Spice Level:")
            for spice, count in stats['by_spice_level'].items():
                emoji = "🟢" if spice == "Mild" else "🟡" if spice == "Spicy" else "🔴"
                print(f"  {emoji} {spice}: {count}")
                
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")


def main():
    """Main entry point for the CLI"""
    # Default database path
    default_db = "data/databases/game_questions.db"
    
    # Check if database exists
    if not os.path.exists(default_db):
        print(f"❌ Database not found: {default_db}")
        print("Please ensure the database file exists.")
        sys.exit(1)
    
    # Create and run CLI
    cli = TruthOrDareCLI(default_db)
    cli.run()


if __name__ == "__main__":
    main()
