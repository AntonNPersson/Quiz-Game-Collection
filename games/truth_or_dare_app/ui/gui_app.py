"""
Truth or Dare GUI Application

A modern, themeable desktop application for Truth or Dare games.
Built with tkinter for maximum compatibility and easy customization.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from typing import Optional, List, Dict, Any
from pathlib import Path

from ..app import TruthOrDareApp
from .themes import UITheme, get_theme, list_themes
from question_pipeline.data.filters.content_filters import LanguageFilter


class ModernFrame(ttk.Frame):
    """Modern styled frame with consistent padding"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(padding="20")


class ModernButton(ttk.Button):
    """Modern styled button with consistent styling"""
    def __init__(self, parent, **kwargs):
        # Set default style
        if 'style' not in kwargs:
            kwargs['style'] = 'Modern.TButton'
        super().__init__(parent, **kwargs)


class ModernLabel(ttk.Label):
    """Modern styled label"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)


class TruthOrDareGUI:
    """
    Main GUI application for Truth or Dare
    
    Features:
    - Themeable interface with multiple built-in themes
    - Player management with visual indicators
    - Question display with type-specific styling
    - Game progress tracking
    - Settings panel for customization
    """
    
    def __init__(self, database_path: str = "data/databases/game_questions.db", theme_name: str = "classic"):
        """
        Initialize the GUI application
        
        Args:
            database_path: Path to the question database
            theme_name: Name of the theme to use
        """
        self.database_path = database_path
        self.theme = get_theme(theme_name)
        self.app: Optional[TruthOrDareApp] = None
        self.current_game_id: Optional[str] = None
        
        # Initialize tkinter
        self.root = tk.Tk()
        self.root.title("Truth or Dare - Party Game")
        self.root.geometry(f"{self.theme.window_min_width}x{self.theme.window_min_height}")
        self.root.minsize(self.theme.window_min_width, self.theme.window_min_height)
        self.root.configure(bg=self.theme.window_bg)
        
        # Center window on screen
        self._center_window()
        
        # Initialize variables
        self.players: List[str] = []
        self.current_question_data: Optional[Dict[str, Any]] = None
        
        # Create UI
        self._create_widgets()
        self._apply_theme()
        
        # Initialize app
        self._initialize_app()
    
    def _center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        """Create all UI widgets"""
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main container with grid layout
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=self.theme.margin, pady=self.theme.margin)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Create different screens
        self._create_welcome_screen()
        self._create_setup_screen()
        self._create_game_screen()
        self._create_results_screen()
        
        # Show welcome screen initially
        self._show_screen("welcome")
    
    def _create_welcome_screen(self):
        """Create the welcome/main menu screen with responsive grid layout"""
        self.welcome_frame = tk.Frame(self.main_frame)
        
        # Configure grid weights for responsive scaling
        self.welcome_frame.grid_rowconfigure(0, weight=1)  # Top spacer
        self.welcome_frame.grid_rowconfigure(1, weight=0)  # Title
        self.welcome_frame.grid_rowconfigure(2, weight=0)  # Subtitle
        self.welcome_frame.grid_rowconfigure(3, weight=0)  # Buttons
        self.welcome_frame.grid_rowconfigure(4, weight=1)  # Bottom spacer
        self.welcome_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = tk.Label(
            self.welcome_frame,
            text="🎭 Truth or Dare 🎭",
            font=self.theme.get_font("title", "bold")
        )
        title_label.grid(row=1, column=0, pady=30, sticky="ew")
        
        # Subtitle
        subtitle_label = tk.Label(
            self.welcome_frame,
            text="The Ultimate Party Game",
            font=self.theme.get_font("large")
        )
        subtitle_label.grid(row=2, column=0, pady=(0, 50), sticky="ew")
        
        # Buttons frame with grid layout
        button_frame = tk.Frame(self.welcome_frame)
        button_frame.grid(row=3, column=0, pady=20, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        
        self.start_button = tk.Button(
            button_frame,
            text="🎮 Start New Game",
            command=self._show_setup,
            **self.theme.get_button_style("default")
        )
        self.start_button.grid(row=0, column=0, pady=10, ipadx=20, sticky="ew")
        
        self.settings_button = tk.Button(
            button_frame,
            text="⚙️ Settings",
            command=self._show_settings,
            **self.theme.get_button_style("default")
        )
        self.settings_button.grid(row=1, column=0, pady=10, ipadx=20, sticky="ew")
        
        self.stats_button = tk.Button(
            button_frame,
            text="📊 Statistics",
            command=self._show_stats,
            **self.theme.get_button_style("default")
        )
        self.stats_button.grid(row=2, column=0, pady=10, ipadx=20, sticky="ew")
        
        self.exit_button = tk.Button(
            button_frame,
            text="❌ Exit",
            command=self._exit_app,
            **self.theme.get_button_style("default")
        )
        self.exit_button.grid(row=3, column=0, pady=10, ipadx=20, sticky="ew")
    
    def _create_setup_screen(self):
        """Create the game setup screen with responsive grid layout"""
        self.setup_frame = tk.Frame(self.main_frame)
        
        # Configure grid weights for responsive scaling
        self.setup_frame.grid_rowconfigure(0, weight=1)  # Content area (expandable)
        self.setup_frame.grid_rowconfigure(1, weight=0)  # Button area (fixed)
        self.setup_frame.grid_columnconfigure(0, weight=1)
        
        # Create a scrollable frame for the content
        content_frame = tk.Frame(self.setup_frame)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        canvas = tk.Canvas(content_frame)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout for canvas and scrollbar
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = tk.Label(
            scrollable_frame,
            text="🎮 Game Setup",
            font=self.theme.get_font("title", "bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Players section
        players_frame = tk.LabelFrame(
            scrollable_frame,
            text="👥 Players",
            font=self.theme.get_font("large", "bold"),
            padx=self.theme.padding,
            pady=self.theme.padding
        )
        players_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Player input
        input_frame = tk.Frame(players_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="Player Name:", font=self.theme.get_font()).pack(side=tk.LEFT)
        
        self.player_entry = tk.Entry(input_frame, font=self.theme.get_font())
        self.player_entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)
        self.player_entry.bind("<Return>", lambda e: self._add_player())
        
        self.add_player_button = tk.Button(
            input_frame,
            text="➕ Add",
            command=self._add_player,
            **self.theme.get_button_style("default")
        )
        self.add_player_button.pack(side=tk.RIGHT)
        
        # Players list
        self.players_listbox = tk.Listbox(
            players_frame,
            font=self.theme.get_font(),
            height=4  # Reduced height to save space
        )
        self.players_listbox.pack(fill=tk.X, pady=5)
        
        # Remove player button
        self.remove_player_button = tk.Button(
            players_frame,
            text="➖ Remove Selected",
            command=self._remove_player,
            **self.theme.get_button_style("default")
        )
        self.remove_player_button.pack(pady=5)
        
        # Game settings
        settings_frame = tk.LabelFrame(
            scrollable_frame,
            text="⚙️ Game Settings",
            font=self.theme.get_font("large", "bold"),
            padx=self.theme.padding,
            pady=self.theme.padding
        )
        settings_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Question count
        count_frame = tk.Frame(settings_frame)
        count_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(count_frame, text="Questions:", font=self.theme.get_font()).pack(side=tk.LEFT)
        
        self.question_count_var = tk.StringVar(value="15")
        self.question_count_spinbox = tk.Spinbox(
            count_frame,
            from_=5,
            to=50,
            textvariable=self.question_count_var,
            font=self.theme.get_font(),
            width=10
        )
        self.question_count_spinbox.pack(side=tk.RIGHT)
        
        # Truth ratio
        ratio_frame = tk.Frame(settings_frame)
        ratio_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(ratio_frame, text="Truth Ratio:", font=self.theme.get_font()).pack(side=tk.LEFT)
        
        self.truth_ratio_var = tk.DoubleVar(value=0.6)
        self.truth_ratio_scale = tk.Scale(
            ratio_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.truth_ratio_var,
            font=self.theme.get_font()
        )
        self.truth_ratio_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Spice level
        spice_frame = tk.Frame(settings_frame)
        spice_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(spice_frame, text="Spice Level:", font=self.theme.get_font()).pack(side=tk.LEFT)
        
        self.spice_level_var = tk.StringVar(value="mild")
        spice_combo = ttk.Combobox(
            spice_frame,
            textvariable=self.spice_level_var,
            values=["mild", "spicy"],
            state="readonly",
            font=self.theme.get_font()
        )
        spice_combo.pack(side=tk.RIGHT)
        
        # Language selection
        language_frame = tk.Frame(settings_frame)
        language_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(language_frame, text="Language:", font=self.theme.get_font()).pack(side=tk.LEFT)
        
        self.language_var = tk.StringVar(value="en")
        language_combo = ttk.Combobox(
            language_frame,
            textvariable=self.language_var,
            values=["en", "se", "both"],
            state="readonly",
            font=self.theme.get_font()
        )
        language_combo.pack(side=tk.RIGHT)
        
        # Control buttons - ALWAYS VISIBLE at the bottom with grid layout
        button_frame = tk.Frame(self.setup_frame, bg=self.theme.window_bg)
        button_frame.grid(row=1, column=0, sticky="ew", pady=20, padx=20)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        self.back_button = tk.Button(
            button_frame,
            text="⬅️ Back to Main Menu",
            command=lambda: self._show_screen("welcome"),
            **self.theme.get_button_style("default")
        )
        self.back_button.grid(row=0, column=0, padx=10, sticky="ew")
        
        self.start_game_button = tk.Button(
            button_frame,
            text="🚀 Start Game",
            command=self._start_game,
            **self.theme.get_button_style("complete")
        )
        self.start_game_button.grid(row=0, column=1, padx=10, sticky="ew")
        
        # Store references for theme application
        self.setup_canvas = canvas
        self.setup_scrollable_frame = scrollable_frame
    
    def _create_game_screen(self):
        """Create the main game screen with responsive grid layout"""
        self.game_frame = tk.Frame(self.main_frame)
        
        # Configure grid weights for responsive scaling
        self.game_frame.grid_rowconfigure(0, weight=0)  # Header
        self.game_frame.grid_rowconfigure(1, weight=0)  # Progress bar
        self.game_frame.grid_rowconfigure(2, weight=1)  # Question (expandable)
        self.game_frame.grid_rowconfigure(3, weight=0)  # Action buttons
        self.game_frame.grid_columnconfigure(0, weight=1)
        
        # Header with game info
        header_frame = tk.Frame(self.game_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)
        
        self.progress_label = tk.Label(
            header_frame,
            text="Question 1 of 15",
            font=self.theme.get_font("large", "bold")
        )
        self.progress_label.grid(row=0, column=0, sticky="w")
        
        self.current_player_label = tk.Label(
            header_frame,
            text="Current Player: Alice",
            font=self.theme.get_font("large", "bold")
        )
        self.current_player_label.grid(row=0, column=1, sticky="e")
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.game_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Question display
        question_frame = tk.LabelFrame(
            self.game_frame,
            text="❓ Question",
            font=self.theme.get_font("large", "bold"),
            padx=self.theme.padding,
            pady=self.theme.padding
        )
        question_frame.grid(row=2, column=0, sticky="nsew", pady=10)
        question_frame.grid_rowconfigure(1, weight=1)  # Question text expandable
        question_frame.grid_columnconfigure(0, weight=1)
        
        # Question type indicator
        self.question_type_label = tk.Label(
            question_frame,
            text="🤔 TRUTH",
            font=self.theme.get_font("large", "bold")
        )
        self.question_type_label.grid(row=0, column=0, pady=(0, 10), sticky="ew")
        
        # Question text
        self.question_text = scrolledtext.ScrolledText(
            question_frame,
            font=self.theme.get_font("normal"),
            wrap=tk.WORD,
            height=8,
            state=tk.DISABLED
        )
        self.question_text.grid(row=1, column=0, sticky="nsew", pady=10)
        
        # Info button (initially hidden)
        self.info_button = tk.Button(
            question_frame,
            text="ℹ️ Show Info",
            command=self._show_question_info,
            **self.theme.get_button_style("default")
        )
        # Don't grid initially - will be shown when question has info
        
        # Action buttons
        action_frame = tk.Frame(self.game_frame)
        action_frame.grid(row=3, column=0, sticky="ew", pady=20)
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)
        action_frame.grid_columnconfigure(2, weight=0)
        
        self.complete_button = tk.Button(
            action_frame,
            text="✅ Completed",
            command=lambda: self._answer_question(True),
            **self.theme.get_button_style("complete")
        )
        self.complete_button.grid(row=0, column=0, padx=10, sticky="ew")
        
        self.skip_button = tk.Button(
            action_frame,
            text="⏭️ Skip",
            command=lambda: self._answer_question(False),
            **self.theme.get_button_style("skip")
        )
        self.skip_button.grid(row=0, column=1, padx=10, sticky="ew")
        
        self.end_game_button = tk.Button(
            action_frame,
            text="🏁 End Game",
            command=self._end_game,
            **self.theme.get_button_style("default")
        )
        self.end_game_button.grid(row=0, column=2, padx=10, sticky="e")
    
    def _create_results_screen(self):
        """Create the game results screen with responsive grid layout"""
        self.results_frame = tk.Frame(self.main_frame)
        
        # Configure grid weights for responsive scaling
        self.results_frame.grid_rowconfigure(0, weight=1)  # Top spacer
        self.results_frame.grid_rowconfigure(1, weight=0)  # Title
        self.results_frame.grid_rowconfigure(2, weight=1)  # Results (expandable)
        self.results_frame.grid_rowconfigure(3, weight=0)  # Buttons
        self.results_frame.grid_rowconfigure(4, weight=1)  # Bottom spacer
        self.results_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = tk.Label(
            self.results_frame,
            text="🏆 Game Complete!",
            font=self.theme.get_font("title", "bold")
        )
        title_label.grid(row=1, column=0, pady=30, sticky="ew")
        
        # Results display
        self.results_text = scrolledtext.ScrolledText(
            self.results_frame,
            font=self.theme.get_font("normal"),
            wrap=tk.WORD,
            height=15,
            state=tk.DISABLED
        )
        self.results_text.grid(row=2, column=0, sticky="nsew", padx=50, pady=20)
        
        # Control buttons
        button_frame = tk.Frame(self.results_frame)
        button_frame.grid(row=3, column=0, pady=30, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        self.new_game_button = tk.Button(
            button_frame,
            text="🎮 New Game",
            command=self._show_setup,
            **self.theme.get_button_style("complete")
        )
        self.new_game_button.grid(row=0, column=0, padx=10, sticky="ew")
        
        self.main_menu_button = tk.Button(
            button_frame,
            text="🏠 Main Menu",
            command=lambda: self._show_screen("welcome"),
            **self.theme.get_button_style("default")
        )
        self.main_menu_button.grid(row=0, column=1, padx=10, sticky="ew")
    
    def _apply_theme(self):
        """Apply the current theme to all widgets"""
        # Configure root window
        self.root.configure(bg=self.theme.window_bg)
        
        # Configure main frame
        self.main_frame.configure(bg=self.theme.window_bg)
        
        # Apply theme to all frames
        for frame in [self.welcome_frame, self.setup_frame, self.game_frame, self.results_frame]:
            self._apply_theme_to_frame(frame)
        
        # Apply theme to setup screen canvas and scrollable frame
        if hasattr(self, 'setup_canvas'):
            self.setup_canvas.configure(bg=self.theme.window_bg)
        if hasattr(self, 'setup_scrollable_frame'):
            self._apply_theme_to_frame(self.setup_scrollable_frame)
    
    def _apply_theme_to_frame(self, frame):
        """Recursively apply theme to a frame and its children"""
        try:
            if isinstance(frame, (tk.Frame, tk.LabelFrame)):
                frame.configure(bg=self.theme.window_bg)
                if isinstance(frame, tk.LabelFrame):
                    frame.configure(fg=self.theme.text_color)
            elif isinstance(frame, tk.Label):
                frame.configure(bg=self.theme.window_bg, fg=self.theme.text_color)
            elif isinstance(frame, (tk.Entry, tk.Listbox)):
                frame.configure(bg=self.theme.surface_color, fg=self.theme.text_color)
            elif isinstance(frame, scrolledtext.ScrolledText):
                frame.configure(bg=self.theme.surface_color, fg=self.theme.text_color)
            elif isinstance(frame, tk.Radiobutton):
                frame.configure(bg=self.theme.window_bg, fg=self.theme.text_color)
            elif isinstance(frame, tk.Scale):
                frame.configure(bg=self.theme.window_bg, fg=self.theme.text_color)
            elif isinstance(frame, tk.Spinbox):
                frame.configure(bg=self.theme.surface_color, fg=self.theme.text_color)
            # Skip widgets that don't support bg/fg options (like ttk widgets)
        except tk.TclError:
            # Some widgets don't support certain options, skip them
            pass
        
        # Recursively apply to children
        for child in frame.winfo_children():
            self._apply_theme_to_frame(child)
    
    def _show_screen(self, screen_name: str):
        """Show a specific screen and hide others"""
        # Hide all screens
        for frame in [self.welcome_frame, self.setup_frame, self.game_frame, self.results_frame]:
            frame.grid_forget()
        
        # Show requested screen with grid layout
        if screen_name == "welcome":
            self.welcome_frame.grid(row=0, column=0, sticky="nsew")
        elif screen_name == "setup":
            self.setup_frame.grid(row=0, column=0, sticky="nsew")
        elif screen_name == "game":
            self.game_frame.grid(row=0, column=0, sticky="nsew")
        elif screen_name == "results":
            self.results_frame.grid(row=0, column=0, sticky="nsew")
    
    def _initialize_app(self):
        """Initialize the Truth or Dare app"""
        try:
            self.app = TruthOrDareApp(self.database_path)
            # Load stats in background
            threading.Thread(target=self._load_stats, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize app: {e}")
    
    def _load_stats(self):
        """Load database statistics (runs in background)"""
        if self.app:
            try:
                self.stats = self.app.get_question_stats()
            except Exception as e:
                print(f"Failed to load stats: {e}")
    
    def _show_setup(self):
        """Show the game setup screen"""
        self._show_screen("setup")
        self.player_entry.focus()
    
    def _show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.theme.window_bg)
        
        # Theme selection
        theme_frame = tk.LabelFrame(
            settings_window,
            text="🎨 Theme",
            font=self.theme.get_font("large", "bold"),
            bg=self.theme.window_bg,
            fg=self.theme.text_color,
            padx=self.theme.padding,
            pady=self.theme.padding
        )
        theme_frame.pack(fill=tk.X, padx=20, pady=20)
        
        current_theme_var = tk.StringVar(value=self.theme.name)
        
        for theme_name, theme_desc in list_themes().items():
            theme_radio = tk.Radiobutton(
                theme_frame,
                text=f"{theme_desc}",
                variable=current_theme_var,
                value=theme_name,
                bg=self.theme.window_bg,
                fg=self.theme.text_color,
                font=self.theme.get_font()
            )
            theme_radio.pack(anchor=tk.W, pady=2)
        
        # Apply button
        apply_button = tk.Button(
            settings_window,
            text="✅ Apply Theme",
            command=lambda: self._change_theme(current_theme_var.get(), settings_window),
            **self.theme.get_button_style("complete")
        )
        apply_button.pack(pady=20)
    
    def _change_theme(self, theme_name: str, settings_window: tk.Toplevel):
        """Change the application theme"""
        self.theme = get_theme(theme_name)
        self._apply_theme()
        settings_window.destroy()
        messagebox.showinfo("Theme Changed", f"Theme changed to: {self.theme.name}")
    
    def _show_stats(self):
        """Show database statistics"""
        if not hasattr(self, 'stats'):
            messagebox.showinfo("Loading", "Statistics are still loading...")
            return
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Database Statistics")
        stats_window.geometry("500x400")
        stats_window.configure(bg=self.theme.window_bg)
        
        stats_text = scrolledtext.ScrolledText(
            stats_window,
            font=self.theme.get_font("normal"),
            bg=self.theme.surface_color,
            fg=self.theme.text_color,
            wrap=tk.WORD
        )
        stats_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Format statistics
        stats_content = f"""📊 Question Database Statistics

📝 Total Questions: {self.stats['total_questions']}

🎭 By Type:
"""
        for q_type, count in self.stats['by_type'].items():
            emoji = "🤔" if q_type == "truth" else "💪"
            stats_content += f"  {emoji} {q_type.title()}: {count}\n"
        
        stats_content += f"""
📊 By Difficulty:
"""
        for difficulty, count in self.stats['by_difficulty'].items():
            emoji = "🟢" if difficulty == "Easy" else "🟡" if difficulty == "Medium" else "🔴"
            stats_content += f"  {emoji} {difficulty}: {count}\n"
        
        stats_content += f"""
🌶️ By Spice Level:
"""
        for spice, count in self.stats['by_spice_level'].items():
            emoji = "🟢" if spice == "Mild" else "🟡"
            stats_content += f"  {emoji} {spice}: {count}\n"
        
        stats_text.insert(tk.END, stats_content)
        stats_text.configure(state=tk.DISABLED)
    
    def _add_player(self):
        """Add a player to the game"""
        player_name = self.player_entry.get().strip()
        if player_name and player_name not in self.players:
            self.players.append(player_name)
            self.players_listbox.insert(tk.END, player_name)
            self.player_entry.delete(0, tk.END)
        elif player_name in self.players:
            messagebox.showwarning("Duplicate Player", "This player is already in the game!")
    
    def _remove_player(self):
        """Remove selected player from the game"""
        selection = self.players_listbox.curselection()
        if selection:
            index = selection[0]
            player_name = self.players[index]
            self.players.remove(player_name)
            self.players_listbox.delete(index)
    
    def _start_game(self):
        """Start a new game with current settings"""
        if len(self.players) < 1:
            messagebox.showwarning("No Players", "Please add at least one player!")
            return
        
        try:
            # Create game with language filtering
            self.current_game_id = self.app.create_game(
                player_names=self.players,
                question_count=int(self.question_count_var.get()),
                truth_ratio=self.truth_ratio_var.get(),
                spice_level=self.spice_level_var.get(),
                language=self.language_var.get()
            )
            
            # Start game
            self.app.start_game(self.current_game_id)
            
            # Show game screen
            self._show_screen("game")
            self._update_game_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start game: {e}")
    
    def _update_game_display(self):
        """Update the game display with current question"""
        if not self.current_game_id:
            return
        
        try:
            # Get current question
            self.current_question_data = self.app.get_current_question(self.current_game_id)
            
            if self.current_question_data.get('finished', False):
                self._show_game_results()
                return
            
            question = self.current_question_data['question']
            question_num = self.current_question_data.get('question_number', 1)
            total_questions = self.current_question_data.get('total_questions', 1)
            current_player = self.current_question_data.get('current_player', 'Unknown')
            question_type = self.current_question_data.get('question_type', 'unknown')
            
            # Update progress
            progress = (question_num / total_questions) * 100
            self.progress_var.set(progress)
            self.progress_label.config(text=f"Question {question_num} of {total_questions}")
            self.current_player_label.config(text=f"Current Player: {current_player}")
            
            # Update question type
            if question_type == "truth":
                self.question_type_label.config(text="🤔 TRUTH", fg=self.theme.truth_button_bg)
            else:
                self.question_type_label.config(text="💪 DARE", fg=self.theme.dare_button_bg)
            
            # Update question text (without info)
            self.question_text.config(state=tk.NORMAL)
            self.question_text.delete(1.0, tk.END)
            
            # Get question text in appropriate language
            selected_language = getattr(self, 'language_var', tk.StringVar(value="en")).get()
            if selected_language == "en":
                question_text = question.get_text("en") or question.get_text()
            elif selected_language == "se":
                question_text = question.get_text("se") or question.get_text()
            else:
                question_text = question.get_text()
            
            self.question_text.insert(tk.END, question_text)
            self.question_text.config(state=tk.DISABLED)
            
            # Show/hide info button based on whether question has info
            info = question.get_info()
            if info and info.strip():
                self.info_button.grid(row=2, column=0, pady=10, sticky="ew")
                self.info_button.config(text="ℹ️ Show Info")
            else:
                self.info_button.grid_forget()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update display: {e}")
    
    def _show_question_info(self):
        """Show or hide question info"""
        if not self.current_question_data:
            return
        
        question = self.current_question_data['question']
        selected_language = getattr(self, 'language_var', tk.StringVar(value="en")).get()
        
        # Get info in appropriate language
        if selected_language == "en":
            info = question.get_info("en") or question.get_info()
        elif selected_language == "se":
            info = question.get_info("se") or question.get_info()
        else:
            info = question.get_info()
        
        if not info:
            return
        
        # Check if info is already shown
        current_text = self.question_text.get(1.0, tk.END)
        if "ℹ️ Info:" in current_text:
            # Hide info
            self.question_text.config(state=tk.NORMAL)
            lines = current_text.split('\n')
            # Remove info lines
            filtered_lines = []
            skip_next = False
            for line in lines:
                if "ℹ️ Info:" in line:
                    skip_next = True
                    continue
                if skip_next and line.strip():
                    continue
                if skip_next and not line.strip():
                    skip_next = False
                    continue
                filtered_lines.append(line)
            
            self.question_text.delete(1.0, tk.END)
            self.question_text.insert(tk.END, '\n'.join(filtered_lines).rstrip())
            self.question_text.config(state=tk.DISABLED)
            self.info_button.config(text="ℹ️ Show Info")
        else:
            # Show info
            self.question_text.config(state=tk.NORMAL)
            self.question_text.insert(tk.END, f"\n\nℹ️ Info: {info}")
            self.question_text.config(state=tk.DISABLED)
            self.info_button.config(text="ℹ️ Hide Info")
    
    def _answer_question(self, completed: bool):
        """Process answer and move to next question"""
        if not self.current_game_id:
            return
        
        try:
            result = self.app.complete_question(self.current_game_id, completed)
            
            if result['session_complete']:
                self._show_game_results()
            else:
                self._update_game_display()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process answer: {e}")
    
    def _end_game(self):
        """End the current game early"""
        if messagebox.askyesno("End Game", "Are you sure you want to end the game?"):
            self._show_game_results()
    
    def _show_game_results(self):
        """Show the game results screen"""
        if not self.current_game_id:
            return
        
        try:
            # Get final status
            status = self.app.get_game_status(self.current_game_id)
            
            # Format results
            results_content = f"""🏆 Game Complete!

👥 Players: {', '.join(status['players'])}
❓ Questions Completed: {status['current_question_index']}/{status['total_questions']}
📈 Completion: {status['progress_percentage']:.1f}%
⏱️ Duration: {status.get('duration', 0):.1f} seconds
🎯 Truth Ratio: {status['truth_ratio']:.0%}
🌶️ Spice Level: {status['spice_level']}

Thanks for playing Truth or Dare! 🎉
"""
            
            # Update results display
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, results_content)
            self.results_text.config(state=tk.DISABLED)
            
            # End the game
            self.app.end_game(self.current_game_id)
            self.current_game_id = None
            
            # Show results screen
            self._show_screen("results")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show results: {e}")
    
    def _exit_app(self):
        """Exit the application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            if self.app:
                self.app.cleanup()
            self.root.quit()
    
    def run(self):
        """Start the GUI application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self._exit_app)
            self.root.mainloop()
        except KeyboardInterrupt:
            self._exit_app()


def main():
    """Main entry point for the GUI application"""
    import sys
    import os
    
    # Default database path
    database_path = "data/databases/game_questions.db"
    
    # Check if database exists
    if not os.path.exists(database_path):
        print(f"❌ Database not found: {database_path}")
        print("Please ensure the database file exists.")
        sys.exit(1)
    
    # Create and run GUI
    app = TruthOrDareGUI(database_path)
    app.run()


if __name__ == "__main__":
    main()
