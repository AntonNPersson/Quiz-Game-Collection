# Quiz Game Collection - Universal Interface Library

A powerful, schema-agnostic interface library that enables rapid development of multiple quiz game applications from a single codebase. Built for scalability, performance, and easy white-label app deployment.

## 🎯 Business Model

This project enables the creation of **multiple quiz game apps** from a single core system. Each app is essentially the same underlying technology with different filter configurations and UI themes, allowing for:

- **Rapid App Development**: New game modes in hours, not weeks
- **White-Label Publishing**: Multiple apps targeting different audiences
- **Shared Infrastructure**: One database, one codebase, many apps
- **Easy Maintenance**: Update core features across all apps simultaneously

## 🏗️ Architecture Overview

### **Universal Filter System**
The heart of the system is a polymorphic filter architecture where **every type of filtering uses the same interface**:

```python
# Single interface for ALL filtering needs
class IUniversalFilter:
    def apply_to_query(query, params) -> (query, params)
    def get_filter_type() -> str
    def get_description() -> str
```

### **Game Mode = Filter Configuration**
Each game app is just a different combination of filters:

```python
# Trivia App Configuration
TRIVIA_CONFIG = GameModeConfig(
    game_mode_filter=TriviaGameModeFilter(),
    default_filters=[DifficultyFilter("medium"), RandomOrderFilter()],
    available_filters=[CategoryFilter, DifficultyFilter, TopicFilter],
    ui_config={"theme": "blue", "show_score": True}
)

# Truth or Dare App Configuration  
TRUTH_OR_DARE_CONFIG = GameModeConfig(
    game_mode_filter=TruthOrDareGameModeFilter(),
    default_filters=[ProgressiveFilter(), BalancedFilter()],
    available_filters=[CategoryFilter, DifficultyFilter],
    ui_config={"theme": "red", "show_timer": False}
)
```

## 🎮 Planned Game Applications

Each app uses the same core but with different filter configurations:

### **📚 Ultimate Trivia**
- **Filters**: Category, Difficulty, Topic, Time Limit
- **Target**: Trivia enthusiasts, pub quiz fans
- **Features**: Scoring, leaderboards, timed rounds

### **🎭 Truth or Dare Plus**
- **Filters**: Intensity Level, Group Size, Age Rating
- **Target**: Party games, social gatherings
- **Features**: Progressive difficulty, group dynamics

### **⚡ Speed Quiz Challenge**
- **Filters**: Quick Questions, Time Pressure, Difficulty Ramp
- **Target**: Competitive players, brain training
- **Features**: Speed scoring, reaction time tracking

### **🎓 Study Buddy**
- **Filters**: Subject, Learning Level, Spaced Repetition
- **Target**: Students, educational institutions
- **Features**: Progress tracking, adaptive learning

### **🍻 Party Quiz**
- **Filters**: Fun Categories, Group Activities, Social Questions
- **Target**: Social events, party entertainment
- **Features**: Group scoring, social challenges

## 🔧 Technical Architecture

### **Data Pipeline Integration**
- **Input**: Excel/CSV files processed by separate data pipeline
- **Output**: Optimized SQLite database with indexed columns
- **Schema**: Flexible, adapts to any question structure from pipeline

### **Core Components**

#### **1. Universal Filter System** ✅ IMPLEMENTED
```
question_pipeline/data/filters/
├── base_filter.py          # IUniversalFilter interface
├── game_mode_filters.py    # TriviaGameModeFilter, etc.
├── content_filters.py      # CategoryFilter, TopicFilter, etc.
├── difficulty_filters.py   # DifficultyFilter, ComplexityFilter, etc.
├── behavior_filters.py     # RandomOrderFilter, LimitFilter, etc.
└── composite_filter.py     # CompositeFilter, FilterChain, etc.
```

#### **2. Question Repository** ✅ IMPLEMENTED
```
question_pipeline/data/repositories/
└── question_repository.py  # Connects filters to storage layer
```

#### **3. Game Engine Core** 🔄 NEXT
```
question_pipeline/core/
├── engine.py              # UniversalQuizEngine
├── session.py             # Game session management
└── scoring.py             # Scoring algorithms
```

#### **4. Game Configurations** 🔄 NEXT
```
question_pipeline/configs/
├── base_config.py         # GameModeConfig class
├── trivia_config.py       # Ultimate Trivia configuration
├── truth_dare_config.py   # Truth or Dare configuration
└── speed_quiz_config.py   # Speed Quiz configuration
```

#### **5. App Factory** 🔄 NEXT
```
question_pipeline/factory/
└── app_factory.py         # QuizAppFactory for creating apps
```

#### **6. Individual Game Apps** 🔄 FUTURE
```
games/
├── trivia_app/           # Ultimate Trivia
├── truth_dare_app/       # Truth or Dare Plus
├── speed_quiz_app/       # Speed Quiz Challenge
└── shared/               # Shared UI components
```

## 🚀 Development Workflow

### **Adding a New Game Mode**
1. **Create filter configuration** (5 minutes)
2. **Design UI theme** (optional)
3. **Use app factory** to generate app
4. **Deploy as separate app**

### **Cross-Platform Deployment**
- **Python/Desktop**: Direct library usage
- **Web**: FastAPI wrapper + React frontend
- **Mobile**: React Native with API calls
- **All platforms use the same filter interfaces**

## 📊 Performance Benefits

### **Database-Level Filtering**
- Filters operate at SQL level for maximum performance
- No object creation overhead for bulk operations
- Optimized queries with proper indexing

### **Lazy Object Creation**
```python
# Fast: Raw data for analytics
raw_questions = repository.get_questions_raw(filters)

# Convenient: Objects when needed for game logic  
question_objects = repository.get_questions(filters)
```

## 🎯 Key Advantages

### **For Development**
- ✅ **Single Interface**: All filtering uses `IUniversalFilter`
- ✅ **Rapid Prototyping**: New game mode = new configuration
- ✅ **Type Safety**: Strong typing with polymorphic design
- ✅ **Easy Testing**: Mock interfaces for unit tests

### **For Business**
- ✅ **Multiple Revenue Streams**: Many apps from one codebase
- ✅ **Fast Time-to-Market**: New apps in days, not months
- ✅ **Reduced Maintenance**: Fix once, benefit everywhere
- ✅ **Scalable Architecture**: Add features to all apps simultaneously

### **For Users**
- ✅ **Consistent Experience**: Same quality across all apps
- ✅ **High Performance**: Database-optimized filtering
- ✅ **Rich Functionality**: Advanced filtering and game mechanics

## 🛠️ Current Status

- ✅ **Universal Filter System**: Complete and tested
- ✅ **Question Repository**: Complete with validation
- ✅ **Database Integration**: SQLite with migrations
- ✅ **Game Engine Core**: Complete with session management
- ✅ **App Factory**: Complete with builder pattern
- ✅ **Game Configurations**: Complete for Truth or Dare
- ✅ **First Game App**: Truth or Dare app fully functional
- ✅ **CLI Interface**: Interactive command-line gameplay
- ✅ **Comprehensive Testing**: All components validated

## 🎮 **TRUTH OR DARE APP - READY TO PLAY!**

The first complete game application is now available:

### **Features Implemented:**
- 🎭 **Complete Truth or Dare Game**: 4,020 questions (1,745 Truth + 2,275 Dare)
- 👥 **Player Management**: Round-robin player rotation system
- 🎯 **Smart Filtering**: Spice level, difficulty, and question type filtering
- 🎮 **Session Management**: Full game lifecycle (create, start, play, end)
- 📊 **Statistics**: Real-time game progress and database analytics
- 🖥️ **CLI Interface**: Interactive terminal-based gameplay
- 🏗️ **Programmatic API**: Full API for integration into other apps

### **How to Play:**
```bash
# Launch the interactive CLI
python scripts/run_truth_or_dare_cli.py

# Run comprehensive tests
python tests/test_truth_or_dare_app.py
```

### **Programmatic Usage:**
```python
from games.truth_or_dare_app import TruthOrDareApp

# Create and configure game
app = TruthOrDareApp("data/databases/game_questions.db")
game_id = app.create_game(
    player_names=["Alice", "Bob", "Charlie"],
    question_count=15,
    truth_ratio=0.6,
    spice_level="mild"
)

# Play the game
app.start_game(game_id)
question_data = app.get_current_question(game_id)
result = app.complete_question(game_id, completed=True)
```

## 📈 Roadmap

### **Phase 1: Core Engine** ✅ COMPLETE
- [x] Universal Filter System
- [x] Question Repository  
- [x] Game Engine Core
- [x] App Factory
- [x] Game Configurations

### **Phase 2: First Apps** ✅ TRUTH OR DARE COMPLETE
- [x] **Truth or Dare app** - Fully functional with CLI
- [ ] Ultimate Trivia app
- [ ] Speed Quiz app

### **Phase 3: Platform Expansion**
- [ ] Web API layer
- [ ] React frontend
- [ ] Mobile app adapters
- [ ] Desktop packaging

### **Phase 4: Advanced Features**
- [ ] Real-time multiplayer
- [ ] Cloud synchronization
- [ ] Analytics dashboard
- [ ] A/B testing framework

## 📄 License

This project is licensed under Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) - see the [LICENSE](LICENSE) file for details.

**Personal and educational use only. Commercial use prohibited.**

---

*Built for rapid quiz game development with enterprise-grade architecture and consumer-friendly deployment.*
