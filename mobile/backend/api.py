"""
FastAPI Backend for Quiz Game Collection Mobile Apps

This API server exposes the Python core functionality as REST endpoints,
allowing mobile apps to access all game features while maintaining the
modular architecture and universal filter system.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import os
import sys
from pathlib import Path

# Add the parent directory to Python path to import the core modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from games.truth_or_dare_app.app import TruthOrDareApp
from question_pipeline.factory.app_factory import AppFactory

app = FastAPI(
    title="Quiz Game Collection API",
    description="REST API for the modular quiz game system",
    version="1.0.0"
)

# Configure CORS for mobile apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for active games and apps
active_games: Dict[str, Dict[str, Any]] = {}
game_apps: Dict[str, Any] = {}

# Database path configuration
DATABASE_PATH = "data/databases/game_questions.db"

# Pydantic models for API requests/responses
class GameCreateRequest(BaseModel):
    game_type: str  # "truth_or_dare", "trivia", etc.
    player_names: List[str]
    question_count: Optional[int] = 15
    settings: Optional[Dict[str, Any]] = {}

class GameResponse(BaseModel):
    game_id: str
    game_type: str
    status: str
    message: Optional[str] = None

class QuestionResponse(BaseModel):
    game_id: str
    question_number: int
    total_questions: int
    current_player: str
    question_type: str
    question_text: str
    question_info: Optional[str] = None
    progress_percentage: float
    finished: bool = False

class AnswerRequest(BaseModel):
    completed: bool

class GameStatusResponse(BaseModel):
    game_id: str
    game_type: str
    players: List[str]
    current_player: str
    question_number: int
    total_questions: int
    progress_percentage: float
    started: bool
    finished: bool
    settings: Dict[str, Any]

class StatsResponse(BaseModel):
    total_questions: int
    by_type: Dict[str, int]
    by_difficulty: Dict[str, int]
    by_spice_level: Dict[str, int]

# Helper functions
def get_database_path() -> str:
    """Get the absolute path to the database"""
    current_dir = Path(__file__).parent.parent.parent
    db_path = current_dir / DATABASE_PATH
    if not db_path.exists():
        raise HTTPException(status_code=500, detail=f"Database not found: {db_path}")
    return str(db_path)

def get_or_create_app(game_type: str):
    """Get or create a game app instance"""
    if game_type not in game_apps:
        db_path = get_database_path()
        
        if game_type == "truth_or_dare":
            game_apps[game_type] = TruthOrDareApp(db_path)
        else:
            # For future game types, use the factory
            raise HTTPException(status_code=400, detail=f"Game type '{game_type}' not yet supported")
    
    return game_apps[game_type]

# API Endpoints

@app.get("/")
async def root():
    """API health check"""
    return {"message": "Quiz Game Collection API", "version": "1.0.0", "status": "healthy"}

@app.get("/games/types")
async def get_game_types():
    """Get available game types"""
    return {
        "game_types": [
            {
                "id": "truth_or_dare",
                "name": "Truth or Dare",
                "description": "The classic party game with truth questions and dare challenges",
                "available": True
            },
            {
                "id": "trivia",
                "name": "Ultimate Trivia",
                "description": "Test your knowledge with trivia questions",
                "available": False  # Future implementation
            },
            {
                "id": "speed_quiz",
                "name": "Speed Quiz Challenge",
                "description": "Fast-paced quiz with time pressure",
                "available": False  # Future implementation
            }
        ]
    }

@app.post("/games", response_model=GameResponse)
async def create_game(request: GameCreateRequest):
    """Create a new game session"""
    try:
        game_app = get_or_create_app(request.game_type)
        
        # Generate unique game ID
        game_id = f"{request.game_type}_{uuid.uuid4().hex[:8]}"
        
        # Create game with settings
        if request.game_type == "truth_or_dare":
            settings = request.settings or {}
            actual_game_id = game_app.create_game(
                player_names=request.player_names,
                question_count=request.question_count,
                truth_ratio=settings.get("truth_ratio", 0.6),
                spice_level=settings.get("spice_level", "mild"),
                language=settings.get("language", "en"),
                game_id=game_id
            )
        else:
            raise HTTPException(status_code=400, detail=f"Game type '{request.game_type}' not supported")
        
        # Store game info
        active_games[game_id] = {
            "game_type": request.game_type,
            "app": game_app,
            "created": True,
            "started": False
        }
        
        return GameResponse(
            game_id=game_id,
            game_type=request.game_type,
            status="created",
            message="Game created successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/games/{game_id}/start", response_model=GameResponse)
async def start_game(game_id: str):
    """Start a game session"""
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        game_info = active_games[game_id]
        game_app = game_info["app"]
        
        # Start the game
        result = game_app.start_game(game_id)
        game_info["started"] = True
        
        return GameResponse(
            game_id=game_id,
            game_type=game_info["game_type"],
            status="started",
            message="Game started successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/games/{game_id}/question", response_model=QuestionResponse)
async def get_current_question(game_id: str):
    """Get the current question for a game"""
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        game_info = active_games[game_id]
        game_app = game_info["app"]
        
        question_data = game_app.get_current_question(game_id)
        
        if question_data.get('finished', False):
            return QuestionResponse(
                game_id=game_id,
                question_number=question_data.get('question_number', 0),
                total_questions=question_data.get('total_questions', 0),
                current_player="",
                question_type="",
                question_text="",
                progress_percentage=100.0,
                finished=True
            )
        
        question = question_data['question']
        
        # Get question text (handle language selection)
        question_text = question.get_text("en") or question.get_text()
        question_info = question.get_info("en") or question.get_info()
        
        return QuestionResponse(
            game_id=game_id,
            question_number=question_data.get('question_number', 1),
            total_questions=question_data.get('total_questions', 1),
            current_player=question_data.get('current_player', 'Unknown'),
            question_type=question_data.get('question_type', 'unknown'),
            question_text=question_text,
            question_info=question_info,
            progress_percentage=question_data.get('progress_percentage', 0.0),
            finished=False
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/games/{game_id}/answer")
async def submit_answer(game_id: str, answer: AnswerRequest):
    """Submit an answer for the current question"""
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        game_info = active_games[game_id]
        game_app = game_info["app"]
        
        result = game_app.complete_question(game_id, answer.completed)
        
        return {
            "game_id": game_id,
            "action": "completed" if answer.completed else "skipped",
            "session_complete": result.get('session_complete', False),
            "message": "Answer submitted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/games/{game_id}/status", response_model=GameStatusResponse)
async def get_game_status(game_id: str):
    """Get complete game status"""
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        game_info = active_games[game_id]
        game_app = game_info["app"]
        
        status = game_app.get_game_status(game_id)
        
        return GameStatusResponse(
            game_id=game_id,
            game_type=game_info["game_type"],
            players=status.get('players', []),
            current_player=status.get('current_player', 'Unknown'),
            question_number=status.get('current_question_index', 0),
            total_questions=status.get('total_questions', 0),
            progress_percentage=status.get('progress_percentage', 0.0),
            started=status.get('started', False),
            finished=status.get('session_complete', False),
            settings={
                "truth_ratio": status.get('truth_ratio', 0.6),
                "spice_level": status.get('spice_level', 'mild')
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/games/{game_id}")
async def end_game(game_id: str):
    """End a game session"""
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        game_info = active_games[game_id]
        game_app = game_info["app"]
        
        # End the game
        final_status = game_app.end_game(game_id)
        
        # Remove from active games
        del active_games[game_id]
        
        return {
            "game_id": game_id,
            "status": "ended",
            "message": "Game ended successfully",
            "final_stats": final_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/games")
async def list_active_games():
    """List all active games"""
    games = []
    for game_id, game_info in active_games.items():
        try:
            status = game_info["app"].get_game_status(game_id)
            games.append({
                "game_id": game_id,
                "game_type": game_info["game_type"],
                "started": game_info["started"],
                "players": status.get('players', []),
                "progress": status.get('progress_percentage', 0.0)
            })
        except:
            # Skip games with errors
            continue
    
    return {"active_games": games}

@app.get("/stats", response_model=StatsResponse)
async def get_database_stats():
    """Get database statistics"""
    try:
        # Use Truth or Dare app to get stats (all games use same database)
        game_app = get_or_create_app("truth_or_dare")
        stats = game_app.get_question_stats()
        
        return StatsResponse(
            total_questions=stats['total_questions'],
            by_type=stats['by_type'],
            by_difficulty=stats['by_difficulty'],
            by_spice_level=stats['by_spice_level']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/themes")
async def get_available_themes():
    """Get available UI themes"""
    return {
        "themes": [
            {
                "id": "classic",
                "name": "Truth or Dare Classic",
                "description": "Modern classic theme with improved styling",
                "colors": {
                    "primary": "#E53E3E",
                    "secondary": "#3182CE",
                    "background": "#F8FAFC",
                    "surface": "#FFFFFF",
                    "text": "#1A202C"
                }
            },
            {
                "id": "dark",
                "name": "Dark Mode",
                "description": "Modern dark theme for night gaming",
                "colors": {
                    "primary": "#FF6B6B",
                    "secondary": "#4ECDC4",
                    "background": "#1A202C",
                    "surface": "#2D3748",
                    "text": "#F7FAFC"
                }
            },
            {
                "id": "party",
                "name": "Party Mode",
                "description": "Bright and colorful theme for parties",
                "colors": {
                    "primary": "#FF1744",
                    "secondary": "#00BCD4",
                    "background": "#FFF3E0",
                    "surface": "#FFFFFF",
                    "text": "#212121"
                }
            }
        ]
    }

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    for game_id in list(active_games.keys()):
        try:
            game_info = active_games[game_id]
            game_app = game_info["app"]
            game_app.end_game(game_id)
        except:
            pass
    
    # Clean up game apps
    for app in game_apps.values():
        try:
            app.cleanup()
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
