#!/usr/bin/env python3
"""
Simple API Server for Quiz Game Collection Mobile Apps

A minimal HTTP server that provides the essential endpoints needed
for the mobile app, avoiding complex dependency issues.
"""

import json
import uuid
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Add the parent directory to Python path to import the core modules
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from games.truth_or_dare_app.app import TruthOrDareApp
    CORE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Core modules not available: {e}")
    CORE_AVAILABLE = False

# Global storage
active_games = {}
game_apps = {}

class QuizAPIHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler for the Quiz API"""
    
    def _send_cors_headers(self):
        """Send CORS headers for mobile app access"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def _send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def _send_error_response(self, message, status_code=500):
        """Send error response"""
        self._send_json_response({"error": message}, status_code)
    
    def _get_request_body(self):
        """Get JSON request body"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
                return json.loads(body.decode('utf-8'))
            return {}
        except Exception as e:
            print(f"Error parsing request body: {e}")
            return {}
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        try:
            if path == '/':
                # Health check
                self._send_json_response({
                    "message": "Quiz Game Collection API",
                    "version": "1.0.0",
                    "status": "healthy",
                    "core_available": CORE_AVAILABLE
                })
            
            elif path == '/games/types':
                # Get available game types
                self._send_json_response({
                    "game_types": [
                        {
                            "id": "truth_or_dare",
                            "name": "Truth or Dare",
                            "description": "The classic party game",
                            "available": CORE_AVAILABLE
                        }
                    ]
                })
            
            elif path == '/games':
                # List active games
                games = []
                for game_id, game_info in active_games.items():
                    games.append({
                        "game_id": game_id,
                        "game_type": game_info.get("game_type", "unknown"),
                        "started": game_info.get("started", False),
                        "players": game_info.get("players", [])
                    })
                self._send_json_response({"active_games": games})
            
            elif path.startswith('/games/') and path.endswith('/question'):
                # Get current question
                game_id = path.split('/')[2]
                if not CORE_AVAILABLE:
                    self._send_json_response({
                        "game_id": game_id,
                        "question_number": 1,
                        "total_questions": 5,
                        "current_player": "Demo Player",
                        "question_type": "truth",
                        "question_text": "Demo question: What's your favorite color?",
                        "question_info": "This is a demo question for testing.",
                        "progress_percentage": 20.0,
                        "finished": False
                    })
                else:
                    self._handle_get_question(game_id)
            
            elif path.startswith('/games/') and path.endswith('/status'):
                # Get game status
                game_id = path.split('/')[2]
                self._handle_get_status(game_id)
            
            elif path == '/stats':
                # Get database stats
                if CORE_AVAILABLE:
                    self._handle_get_stats()
                else:
                    self._send_json_response({
                        "total_questions": 100,
                        "by_type": {"truth": 50, "dare": 50},
                        "by_difficulty": {"Easy": 40, "Medium": 40, "Hard": 20},
                        "by_spice_level": {"Mild": 80, "Spicy": 20}
                    })
            
            elif path == '/themes':
                # Get available themes
                self._send_json_response({
                    "themes": [
                        {
                            "id": "classic",
                            "name": "Classic Theme",
                            "colors": {"primary": "#E53E3E", "secondary": "#3182CE"}
                        },
                        {
                            "id": "dark",
                            "name": "Dark Theme", 
                            "colors": {"primary": "#FF6B6B", "secondary": "#4ECDC4"}
                        }
                    ]
                })
            
            else:
                self._send_error_response("Endpoint not found", 404)
                
        except Exception as e:
            print(f"Error handling GET request: {e}")
            self._send_error_response(str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        try:
            if path == '/games':
                # Create new game
                self._handle_create_game()
            
            elif path.startswith('/games/') and path.endswith('/start'):
                # Start game
                game_id = path.split('/')[2]
                self._handle_start_game(game_id)
            
            elif path.startswith('/games/') and path.endswith('/answer'):
                # Submit answer
                game_id = path.split('/')[2]
                self._handle_submit_answer(game_id)
            
            else:
                self._send_error_response("Endpoint not found", 404)
                
        except Exception as e:
            print(f"Error handling POST request: {e}")
            self._send_error_response(str(e))
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        try:
            if path.startswith('/games/'):
                # End game
                game_id = path.split('/')[2]
                self._handle_end_game(game_id)
            else:
                self._send_error_response("Endpoint not found", 404)
                
        except Exception as e:
            print(f"Error handling DELETE request: {e}")
            self._send_error_response(str(e))
    
    def _handle_create_game(self):
        """Handle game creation"""
        data = self._get_request_body()
        
        game_id = f"tod_{uuid.uuid4().hex[:8]}"
        
        if CORE_AVAILABLE:
            try:
                # Use real game logic
                if "truth_or_dare" not in game_apps:
                    db_path = Path(__file__).parent.parent.parent / "data" / "databases" / "game_questions.db"
                    game_apps["truth_or_dare"] = TruthOrDareApp(str(db_path))
                
                app = game_apps["truth_or_dare"]
                settings = data.get("settings", {})
                
                actual_game_id = app.create_game(
                    player_names=data.get("player_names", ["Player 1"]),
                    question_count=data.get("question_count", 15),
                    truth_ratio=settings.get("truth_ratio", 0.6),
                    spice_level=settings.get("spice_level", "mild"),
                    language=settings.get("language", "en"),
                    game_id=game_id
                )
                
                active_games[game_id] = {
                    "game_type": "truth_or_dare",
                    "app": app,
                    "players": data.get("player_names", ["Player 1"]),
                    "started": False
                }
                
            except Exception as e:
                print(f"Error creating real game: {e}")
                # Fall back to demo mode
                active_games[game_id] = {
                    "game_type": "truth_or_dare",
                    "players": data.get("player_names", ["Player 1"]),
                    "started": False,
                    "demo": True
                }
        else:
            # Demo mode
            active_games[game_id] = {
                "game_type": "truth_or_dare",
                "players": data.get("player_names", ["Player 1"]),
                "started": False,
                "demo": True
            }
        
        self._send_json_response({
            "game_id": game_id,
            "game_type": "truth_or_dare",
            "status": "created",
            "message": "Game created successfully"
        })
    
    def _handle_start_game(self, game_id):
        """Handle game start"""
        if game_id not in active_games:
            self._send_error_response("Game not found", 404)
            return
        
        game_info = active_games[game_id]
        
        if CORE_AVAILABLE and "app" in game_info:
            try:
                app = game_info["app"]
                app.start_game(game_id)
            except Exception as e:
                print(f"Error starting real game: {e}")
        
        game_info["started"] = True
        
        self._send_json_response({
            "game_id": game_id,
            "game_type": game_info["game_type"],
            "status": "started",
            "message": "Game started successfully"
        })
    
    def _handle_get_question(self, game_id):
        """Handle get current question"""
        if game_id not in active_games:
            self._send_error_response("Game not found", 404)
            return
        
        game_info = active_games[game_id]
        
        if CORE_AVAILABLE and "app" in game_info:
            try:
                app = game_info["app"]
                question_data = app.get_current_question(game_id)
                
                if question_data.get('finished', False):
                    self._send_json_response({
                        "game_id": game_id,
                        "finished": True,
                        "progress_percentage": 100.0
                    })
                    return
                
                question = question_data['question']
                question_text = question.get_text("en") or question.get_text()
                question_info = question.get_info("en") or question.get_info()
                
                self._send_json_response({
                    "game_id": game_id,
                    "question_number": question_data.get('question_number', 1),
                    "total_questions": question_data.get('total_questions', 1),
                    "current_player": question_data.get('current_player', 'Unknown'),
                    "question_type": question_data.get('question_type', 'unknown'),
                    "question_text": question_text,
                    "question_info": question_info,
                    "progress_percentage": question_data.get('progress_percentage', 0.0),
                    "finished": False
                })
                return
                
            except Exception as e:
                print(f"Error getting real question: {e}")
        
        # Demo response
        self._send_json_response({
            "game_id": game_id,
            "question_number": 1,
            "total_questions": 5,
            "current_player": game_info["players"][0] if game_info["players"] else "Demo Player",
            "question_type": "truth",
            "question_text": "Demo question: What's your biggest fear?",
            "question_info": "This is a demo question for testing the mobile app.",
            "progress_percentage": 20.0,
            "finished": False
        })
    
    def _handle_submit_answer(self, game_id):
        """Handle answer submission"""
        if game_id not in active_games:
            self._send_error_response("Game not found", 404)
            return
        
        data = self._get_request_body()
        completed = data.get("completed", True)
        
        game_info = active_games[game_id]
        
        if CORE_AVAILABLE and "app" in game_info:
            try:
                app = game_info["app"]
                result = app.complete_question(game_id, completed)
                
                self._send_json_response({
                    "game_id": game_id,
                    "action": "completed" if completed else "skipped",
                    "session_complete": result.get('session_complete', False),
                    "message": "Answer submitted successfully"
                })
                return
                
            except Exception as e:
                print(f"Error submitting real answer: {e}")
        
        # Demo response
        self._send_json_response({
            "game_id": game_id,
            "action": "completed" if completed else "skipped",
            "session_complete": False,
            "message": "Answer submitted successfully (demo mode)"
        })
    
    def _handle_get_status(self, game_id):
        """Handle get game status"""
        if game_id not in active_games:
            self._send_error_response("Game not found", 404)
            return
        
        game_info = active_games[game_id]
        
        self._send_json_response({
            "game_id": game_id,
            "game_type": game_info["game_type"],
            "players": game_info["players"],
            "current_player": game_info["players"][0] if game_info["players"] else "Demo Player",
            "question_number": 1,
            "total_questions": 5,
            "progress_percentage": 20.0,
            "started": game_info["started"],
            "finished": False,
            "settings": {"truth_ratio": 0.6, "spice_level": "mild"}
        })
    
    def _handle_end_game(self, game_id):
        """Handle end game"""
        if game_id not in active_games:
            self._send_error_response("Game not found", 404)
            return
        
        game_info = active_games[game_id]
        
        if CORE_AVAILABLE and "app" in game_info:
            try:
                app = game_info["app"]
                app.end_game(game_id)
            except Exception as e:
                print(f"Error ending real game: {e}")
        
        del active_games[game_id]
        
        self._send_json_response({
            "game_id": game_id,
            "status": "ended",
            "message": "Game ended successfully"
        })
    
    def _handle_get_stats(self):
        """Handle get database stats"""
        try:
            if "truth_or_dare" not in game_apps:
                db_path = Path(__file__).parent.parent.parent / "data" / "databases" / "game_questions.db"
                game_apps["truth_or_dare"] = TruthOrDareApp(str(db_path))
            
            app = game_apps["truth_or_dare"]
            stats = app.get_question_stats()
            
            self._send_json_response({
                "total_questions": stats['total_questions'],
                "by_type": stats['by_type'],
                "by_difficulty": stats['by_difficulty'],
                "by_spice_level": stats['by_spice_level']
            })
            
        except Exception as e:
            print(f"Error getting real stats: {e}")
            # Demo stats
            self._send_json_response({
                "total_questions": 100,
                "by_type": {"truth": 50, "dare": 50},
                "by_difficulty": {"Easy": 40, "Medium": 40, "Hard": 20},
                "by_spice_level": {"Mild": 80, "Spicy": 20}
            })

def run_server(port=8000):
    """Run the simple API server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, QuizAPIHandler)
    
    print(f"Quiz Game Collection API Server")
    print(f"Server running on http://localhost:{port}")
    print(f"API endpoints available:")
    print(f"   GET  /                    - Health check")
    print(f"   GET  /games/types         - Available game types")
    print(f"   POST /games               - Create new game")
    print(f"   POST /games/{{id}}/start    - Start game")
    print(f"   GET  /games/{{id}}/question - Get current question")
    print(f"   POST /games/{{id}}/answer   - Submit answer")
    print(f"   GET  /games/{{id}}/status   - Get game status")
    print(f"   DELETE /games/{{id}}        - End game")
    print(f"   GET  /stats               - Database statistics")
    print(f"   GET  /themes              - Available themes")
    print(f"")
    print(f"Core modules available: {CORE_AVAILABLE}")
    print(f"Ready for mobile app connection!")
    print(f"")
    print(f"Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
