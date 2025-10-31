from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input
from textual.reactive import reactive
from textual.screen import Screen
from rich.text import Text
import time
import random
import json
from pathlib import Path
from enum import Enum


class GameState(Enum):
    """Game state machine."""
    USER_SETUP = "user_setup"  # First-time user creation
    USER_SELECT = "user_select"  # User selection screen
    MENU = "menu"          # Main menu, can use all menu controls
    READY = "ready"        # Ready to start, waiting for first keystroke
    IN_TEST = "in_test"    # Actively typing
    COMPLETE = "complete"  # Test finished, showing results


PHRASES = [
    "The quick brown fox jumps over the lazy dog",
    "Pack my box with five dozen liquor jugs",
    "How vexingly quick daft zebras jump",
    "Sphinx of black quartz, judge my vow",
    "Two driven jocks help fax my big quiz",
    "Five quacking zephyrs jolt my wax bed",
    "The five boxing wizards jump quickly",
    "Jackdaws love my big sphinx of quartz",
    "My girl wove six dozen plaid jackets before she quit",
    "Sixty zippers were quickly picked from the woven jute bag",
    "A quick movement of the enemy will jeopardize six gunboats",
    "All questions asked by five watch experts amazed the judge",
    "Back in June we delivered oxygen equipment of the same size",
    "A mad boxer shot a quick, gloved jab to the jaw of his dizzy opponent",
    "The job requires extra pluck and zeal from every young wage earner",
    "We promptly judged antique ivory buckles for the next prize",
    "A large fawn jumped quickly over white zinc boxes",
    "Six big devils from Japan quickly forgot how to waltz",
]


PARAGRAPHS = [
    "The art of typing quickly and accurately is a skill that takes time to develop. With consistent practice and focus, anyone can improve their typing speed. The key is to maintain proper hand position and avoid looking at the keyboard. Over time, muscle memory will develop and typing will become second nature. Remember to take breaks and stretch your hands regularly.",

    "Programming is not just about writing code, it is about solving problems creatively. Every algorithm you write represents a unique solution to a challenge. The best programmers are those who can think logically and break down complex problems into smaller, manageable pieces. Always strive to write clean, readable code that others can understand and maintain.",

    "The ocean is a vast and mysterious place, covering more than seventy percent of our planet's surface. Deep beneath the waves lie unexplored ecosystems teeming with life. From tiny plankton to massive whales, the ocean supports an incredible diversity of species. Scientists continue to discover new creatures in the darkest depths, reminding us how much we still have to learn about our world.",

    "Coffee has become an essential part of modern culture, fueling millions of people each day. The journey from bean to cup involves careful cultivation, harvesting, roasting, and brewing. Different regions produce beans with unique flavor profiles, from fruity Ethiopian varieties to rich Colombian blends. Whether you prefer it black or with milk, coffee brings people together and provides a moment of comfort.",

    "Reading books opens windows to new worlds and perspectives we might never otherwise encounter. Through literature, we can experience different time periods, cultures, and ways of thinking. A good book can make us laugh, cry, or see the world in a completely new light. In our digital age, the timeless pleasure of turning pages and getting lost in a story remains irreplaceable.",

    "Exercise is crucial for maintaining both physical and mental health throughout our lives. Regular physical activity strengthens muscles, improves cardiovascular health, and releases endorphins that boost mood. You don't need expensive equipment or a gym membership to stay active. Simple activities like walking, stretching, or bodyweight exercises can make a significant difference in how you feel each day.",
]


THEMES = [
    {
        "name": "Dark",
        "correct": "green bold",
        "incorrect": "white bold on red",
        "pending": "dim",
        "cursor": "black on yellow bold",
        "complete": "green"
    },
    {
        "name": "Light",
        "correct": "blue bold",
        "incorrect": "white bold on dark_red",
        "pending": "grey50",
        "cursor": "white on blue bold",
        "complete": "blue"
    },
    {
        "name": "Ocean",
        "correct": "cyan bold",
        "incorrect": "yellow bold on dark_blue",
        "pending": "blue dim",
        "cursor": "black on bright_cyan bold",
        "complete": "cyan"
    },
    {
        "name": "Retro",
        "correct": "bright_green bold",
        "incorrect": "black bold on bright_yellow",
        "pending": "green dim",
        "cursor": "black on bright_green bold",
        "complete": "bright_green"
    },
]


class UsernameScreen(Screen):
    """Screen for entering username."""

    CSS = """
    UsernameScreen {
        align: center middle;
        background: $surface;
    }

    #username-title {
        width: 60;
        text-align: center;
        margin: 1;
        padding: 1;
        color: $accent;
    }

    #username-input {
        width: 60;
        margin: 1;
        border: solid $primary;
    }

    #username-hint {
        width: 60;
        text-align: center;
        margin: 1;
        color: $text-muted;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the username input screen."""
        yield Static("[bold cyan]Enter Your Username[/bold cyan]", id="username-title")
        yield Input(placeholder="Type your name and press Enter...", id="username-input")
        yield Static("[dim]Press ESC to skip[/dim]", id="username-hint")

    def on_mount(self) -> None:
        """Focus the input when the screen is shown."""
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle username submission."""
        username = event.value.strip()
        if username:
            self.dismiss(username)

    def on_key(self, event) -> None:
        """Handle escape key to dismiss without username."""
        if event.key == "escape":
            event.prevent_default()
            event.stop()
            self.dismiss(None)


class UserMenuScreen(Screen):
    """Screen for user management."""

    def __init__(self, current_user, user_data):
        super().__init__()
        self.current_user = current_user
        self.user_data = user_data

    CSS = """
    UserMenuScreen {
        align: center middle;
    }

    #user-menu-container {
        width: 80;
        height: auto;
        padding: 2 4;
        background: $surface;
        border: thick $primary;
    }

    #user-menu-title {
        text-align: center;
        margin-bottom: 1;
        color: $accent;
    }

    #user-list {
        margin: 1 0;
        padding: 1;
    }

    #user-menu-actions {
        text-align: center;
        margin-top: 1;
        color: $text-muted;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the user menu screen."""
        yield Static("", id="user-menu-container")

    def on_mount(self) -> None:
        """Build the user menu display."""
        self.update_menu()

    def update_menu(self) -> None:
        """Update the user menu display."""
        container = self.query_one("#user-menu-container", Static)

        content = Text()

        # Header with ASCII art
        content.append("╔═══════════════════════════════════════════════════════════════════╗\n", style="cyan bold")
        content.append("║                                                                   ║\n", style="cyan bold")
        content.append("║                    ", style="cyan bold")
        content.append("USER MANAGEMENT", style="bold cyan")
        content.append("                                ║\n", style="cyan bold")
        content.append("║                                                                   ║\n", style="cyan bold")
        content.append("╚═══════════════════════════════════════════════════════════════════╝\n", style="cyan bold")
        content.append("\n")

        if self.user_data:
            # Current user display
            content.append("┌─────────────────────────────────────────────────────────────────┐\n", style="green")
            content.append("│  ", style="green")
            content.append("CURRENT USER", style="bold green")
            content.append("                                                     │\n", style="green")
            content.append("└─────────────────────────────────────────────────────────────────┘\n", style="green")
            content.append("\n    ► ", style="green bold")
            content.append(f"{self.current_user or 'None'}\n\n", style="green bold")

            # All users list
            content.append("╔═══════════════════════════════════════════════════════════════════╗\n", style="yellow")
            content.append("║  ", style="yellow")
            content.append("ALL USERS", style="bold yellow")
            content.append("                                                        ║\n", style="yellow")
            content.append("╚═══════════════════════════════════════════════════════════════════╝\n", style="yellow")
            content.append("\n")

            for i, username in enumerate(sorted(self.user_data.keys()), 1):
                is_current = username == self.current_user

                if is_current:
                    content.append("  ► ", style="green bold")
                    content.append(f"{i}. ", style="green bold")
                    content.append(f"{username}", style="green bold")
                    content.append("  (active)", style="green dim")
                    content.append("\n")
                else:
                    content.append("    ", style="dim")
                    content.append(f"{i}. ", style="cyan bold")
                    content.append(f"{username}\n", style="white")
        else:
            content.append("┌─────────────────────────────────────────────────────────────────┐\n", style="dim")
            content.append("│  ", style="dim")
            content.append("No users found. Create a user to get started!", style="dim italic")
            content.append("              │\n", style="dim")
            content.append("└─────────────────────────────────────────────────────────────────┘", style="dim")

        content.append("\n")

        # Actions menu
        content.append("╔═══════════════════════════════════════════════════════════════════╗\n", style="magenta")
        content.append("║  ", style="magenta")
        content.append("ACTIONS", style="bold magenta")
        content.append("                                                          ║\n", style="magenta")
        content.append("╚═══════════════════════════════════════════════════════════════════╝\n", style="magenta")
        content.append("\n")

        content.append("  ┌────────────────────────────────────────────────────────────┐\n", style="dim")
        content.append("  │  ", style="dim")
        content.append("1-9", style="cyan bold")
        content.append("  Switch to user by number", style="white")
        content.append("                            │\n", style="dim")
        content.append("  ├────────────────────────────────────────────────────────────┤\n", style="dim")
        content.append("  │  ", style="dim")
        content.append("C", style="green bold")
        content.append("    Create new user", style="white")
        content.append("                                       │\n", style="dim")
        content.append("  ├────────────────────────────────────────────────────────────┤\n", style="dim")
        content.append("  │  ", style="dim")
        content.append("D", style="red bold")
        content.append("    Delete current user", style="white")
        content.append("                                  │\n", style="dim")
        content.append("  ├────────────────────────────────────────────────────────────┤\n", style="dim")
        content.append("  │  ", style="dim")
        content.append("ESC", style="yellow bold")
        content.append("  Back to game", style="white")
        content.append("                                          │\n", style="dim")
        content.append("  └────────────────────────────────────────────────────────────┘", style="dim")

        container.update(content)

    async def on_key(self, event) -> None:
        """Handle key presses in user menu."""
        if event.key == "escape":
            event.prevent_default()
            event.stop()
            self.dismiss({"action": "back", "user": self.current_user})
        elif event.key == "c":
            # Create new user
            username = await self.app.push_screen_wait(UsernameScreen())
            if username and username not in self.user_data:
                self.user_data[username] = {
                    "tests_completed": 0,
                    "total_wpm": 0.0,
                    "best_wpm": 0,
                    "total_accuracy": 0.0,
                    "best_accuracy": 0.0
                }
                self.current_user = username
                self.update_menu()
        elif event.key == "d":
            # Delete current user
            if self.current_user and self.current_user in self.user_data:
                del self.user_data[self.current_user]
                self.current_user = None
                self.update_menu()
        elif event.key.isdigit():
            # Switch to user by number
            num = int(event.key)
            users = sorted(self.user_data.keys())
            if 1 <= num <= len(users):
                self.current_user = users[num - 1]
                self.update_menu()
                # Small delay to show selection
                await self.app.run_worker(self.delayed_dismiss())

    async def delayed_dismiss(self):
        """Dismiss after a short delay."""
        import asyncio
        await asyncio.sleep(0.5)
        self.dismiss({"action": "switch", "user": self.current_user})


class StatsScreen(Screen):
    """Screen for displaying personal stats and leaderboard."""

    def __init__(self, current_user, user_data):
        super().__init__()
        self.current_user = current_user
        self.user_data = user_data

    CSS = """
    StatsScreen {
        align: center middle;
    }

    #stats-container {
        width: 80;
        height: auto;
        padding: 2 4;
        background: $surface;
        border: thick $primary;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the stats screen."""
        yield Static("", id="stats-container")

    def on_mount(self) -> None:
        """Build the stats display."""
        self.update_stats()

    def update_stats(self) -> None:
        """Update the stats display."""
        container = self.query_one("#stats-container", Static)

        content = Text()

        # Header with ASCII art
        content.append("╔═══════════════════════════════════════════════════════════════════╗\n", style="cyan bold")
        content.append("║                                                                   ║\n", style="cyan bold")
        content.append("║              ", style="cyan bold")
        content.append("STATISTICS & LEADERBOARD", style="bold cyan")
        content.append("                             ║\n", style="cyan bold")
        content.append("║                                                                   ║\n", style="cyan bold")
        content.append("╚═══════════════════════════════════════════════════════════════════╝\n", style="cyan bold")
        content.append("\n")

        # Personal stats
        if self.current_user and self.current_user in self.user_data:
            user = self.user_data[self.current_user]

            content.append("┌─────────────────────────────────────────────────────────────────┐\n", style="yellow")
            content.append("│  ", style="yellow")
            content.append(f"YOUR STATS - {self.current_user.upper()}", style="bold yellow")

            # Pad to align right border
            padding = 63 - len(self.current_user) - 14
            content.append(" " * padding, style="yellow")
            content.append("│\n", style="yellow")
            content.append("└─────────────────────────────────────────────────────────────────┘\n", style="yellow")
            content.append("\n")

            tests = user["tests_completed"]

            # Tests completed
            content.append("    📊 ", style="bold")
            content.append("Tests Completed: ", style="bold white")
            content.append(f"{tests}\n", style="green bold")

            if tests > 0:
                avg_wpm = user["total_wpm"] / tests
                avg_accuracy = user["total_accuracy"] / tests

                content.append("\n")

                # WPM Stats box
                content.append("    ┌───────────────────────────────┐\n", style="dim")
                content.append("    │ ", style="dim")
                content.append("⚡ TYPING SPEED (WPM)", style="bold cyan")
                content.append("       │\n", style="dim")
                content.append("    ├───────────────────────────────┤\n", style="dim")
                content.append("    │  Average: ", style="dim")
                content.append(f"{avg_wpm:6.1f}", style="green")
                content.append("             │\n", style="dim")
                content.append("    │  Best:    ", style="dim")
                content.append(f"{user['best_wpm']:6d}", style="green bold")

                # Add stars for best WPM
                if user['best_wpm'] >= 80:
                    content.append("  ★★★", style="yellow bold")
                    content.append("      │\n", style="dim")
                elif user['best_wpm'] >= 60:
                    content.append("  ★★", style="yellow bold")
                    content.append("       │\n", style="dim")
                elif user['best_wpm'] >= 40:
                    content.append("  ★", style="yellow bold")
                    content.append("        │\n", style="dim")
                else:
                    content.append("             │\n", style="dim")

                content.append("    └───────────────────────────────┘\n", style="dim")
                content.append("\n")

                # Accuracy Stats box
                content.append("    ┌───────────────────────────────┐\n", style="dim")
                content.append("    │ ", style="dim")
                content.append("✓ ACCURACY (%)", style="bold magenta")
                content.append("              │\n", style="dim")
                content.append("    ├───────────────────────────────┤\n", style="dim")
                content.append("    │  Average: ", style="dim")
                content.append(f"{avg_accuracy:6.1f}%", style="green")
                content.append("           │\n", style="dim")
                content.append("    │  Best:    ", style="dim")
                content.append(f"{user['best_accuracy']:6.1f}%", style="green bold")
                content.append("           │\n", style="dim")
                content.append("    └───────────────────────────────┘\n", style="dim")
            else:
                content.append("\n    ")
                content.append("No tests completed yet. Start typing to build your stats!", style="dim italic")
                content.append("\n")
        else:
            content.append("No user selected.\n", style="dim")

        content.append("\n")

        # Leaderboard
        content.append("╔═══════════════════════════════════════════════════════════════════╗\n", style="yellow bold")
        content.append("║  ", style="yellow bold")
        content.append("LEADERBOARD - TOP 5 BY BEST WPM", style="bold yellow")
        content.append("                                ║\n", style="yellow bold")
        content.append("╚═══════════════════════════════════════════════════════════════════╝\n", style="yellow bold")
        content.append("\n")

        if self.user_data:
            # Sort by best WPM descending
            sorted_users = sorted(
                self.user_data.items(),
                key=lambda x: x[1]["best_wpm"],
                reverse=True
            )[:5]

            for i, (username, stats) in enumerate(sorted_users, 1):
                is_current = username == self.current_user

                # Rank indicator with medals
                if i == 1:
                    rank_style = "yellow bold"
                    rank_icon = "🥇"
                elif i == 2:
                    rank_style = "white bold"
                    rank_icon = "🥈"
                elif i == 3:
                    rank_style = "#cd7f32 bold"  # Bronze color
                    rank_icon = "🥉"
                else:
                    rank_style = "dim"
                    rank_icon = "  "

                # Highlight current user
                name_style = "green bold" if is_current else "white"

                content.append("  ", style="dim")
                content.append(f"{rank_icon} ", style=rank_style)
                content.append(f"#{i}", style=rank_style)
                content.append("  ", style="dim")

                # Username with marker for current user
                if is_current:
                    content.append("► ", style="green bold")
                else:
                    content.append("  ", style="dim")

                content.append(f"{username:20}", style=name_style)
                content.append("  │  ", style="dim")
                content.append(f"WPM: {stats['best_wpm']:3d}", style=name_style)
                content.append("  │  ", style="dim")
                content.append(f"Acc: {stats['best_accuracy']:5.1f}%", style=name_style)
                content.append("  │  ", style="dim")
                content.append(f"Tests: {stats['tests_completed']}\n", style="dim")

                # Add separator between entries except after last
                if i < len(sorted_users):
                    content.append("  " + "─" * 63 + "\n", style="dim")
        else:
            content.append("  No users found. Create a user to start tracking stats!\n", style="dim italic")

        content.append("\n")
        content.append("┌─────────────────────────────────────────────────────────────────┐\n", style="dim")
        content.append("│  Press ", style="dim")
        content.append("ESC", style="cyan bold")
        content.append(" to return to game", style="dim")
        content.append("                                        │\n", style="dim")
        content.append("└─────────────────────────────────────────────────────────────────┘", style="dim")

        container.update(content)

    def on_key(self, event) -> None:
        """Handle key presses in stats screen."""
        if event.key == "escape":
            event.prevent_default()
            event.stop()
            self.dismiss()


class TypingGame(App):
    """A terminal typing speed game."""

    CSS = """
    Screen {
        align: center middle;
    }

    #instructions {
        width: 100%;
        content-align: center middle;
        text-align: center;
        padding: 0 2;
        margin: 1 0;
    }

    #theme-notification {
        width: 100%;
        content-align: center middle;
        text-align: center;
        padding: 0;
        color: yellow;
    }

    #live-stats {
        width: 100%;
        content-align: center middle;
        text-align: center;
        padding: 1 2;
        margin: 0 0 1 0;
    }

    #completed-lines {
        width: 100%;
        content-align: center middle;
        text-align: center;
        padding: 0 2;
        margin: 0 0 1 0;
    }

    #current-line-bordered {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-align: center;
        border: solid $accent;
        padding: 1 2;
        margin: 0;
    }

    #preview-lines {
        width: 100%;
        content-align: center middle;
        text-align: center;
        padding: 0 2;
        margin: 1 0 0 0;
    }

    #completion-message {
        width: 100%;
        content-align: center middle;
        text-align: center;
        padding: 0 2;
        margin: 1 0;
        color: green;
    }
    """

    # Reactive attributes
    game_state = reactive(GameState.MENU)  # Current game state
    target_text = reactive("")
    typed_text = reactive("")
    completed = reactive(False)
    cursor_visible = reactive(True)
    start_time = reactive(0.0)
    elapsed_time = reactive(0.0)
    accuracy = reactive(0.0)
    mistakes = reactive(0)
    theme_index = reactive(0)
    theme_notification = reactive("")

    # Game mode attributes
    game_mode = reactive(None)  # None, "30sec", "30word", "unlimited"
    current_line_index = reactive(0)
    lines_completed = reactive(0)
    total_chars_typed = reactive(0)
    total_words_typed = reactive(0)
    countdown_remaining = reactive(30.0)  # for 30-second mode

    # User management
    current_user = reactive(None)  # Current username
    user_data = reactive({})  # Dictionary of all user data
    user_data_file = Path("users.json")
    show_user_menu = reactive(False)
    show_stats_menu = reactive(False)
    awaiting_username = reactive(False)

    # Track which character positions have had mistakes
    mistake_positions = set()

    # Live stats tracking
    current_streak = reactive(0)
    best_streak = reactive(0)
    live_wpm = reactive(0.0)
    live_accuracy = reactive(0.0)

    # Store lines and paragraph
    current_lines = []
    current_paragraph = ""

    # Store completed lines history: list of (target_text, typed_text, mistake_positions_set)
    completed_lines_history = []

    # Text library attributes
    phrases = []
    paragraphs = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Static("Type the text below:", id="instructions")
        yield Static("", id="theme-notification")
        yield Static("", id="live-stats")
        yield Static("", id="completed-lines")
        yield Static("", id="current-line-bordered")
        yield Static("", id="preview-lines")
        yield Static("", id="completion-message")
        yield Footer()

    def split_into_lines(self, paragraph: str, max_words_per_line: int = 10) -> list:
        """Split a paragraph into lines with approximately max_words_per_line words each."""
        words = paragraph.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            if len(current_line) >= max_words_per_line:
                lines.append(" ".join(current_line))
                current_line = []

        # Add any remaining words
        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def load_texts(self) -> None:
        """Load practice texts from external file with fallback to defaults."""
        texts_file = Path("texts.json")

        # Try to load from external file
        if texts_file.exists():
            try:
                with open(texts_file, "r") as f:
                    data = json.load(f)
                    loaded_phrases = data.get("phrases", [])
                    loaded_paragraphs = data.get("paragraphs", [])

                    # Only use loaded data if both lists are non-empty
                    if loaded_phrases and loaded_paragraphs:
                        self.phrases = loaded_phrases
                        self.paragraphs = loaded_paragraphs
                        return
            except (json.JSONDecodeError, IOError, KeyError):
                # If file is corrupted or invalid, fall back to defaults
                pass

        # Fallback to default texts if file doesn't exist or loading failed
        self.phrases = PHRASES
        self.paragraphs = PARAGRAPHS

    def on_mount(self) -> None:
        """Set up the app after mounting."""
        self.title = "Typing Speed Game"
        self.sub_title = "U Users | S Stats | TAB Theme | ESC Quit"
        # Load practice texts from file
        self.load_texts()
        # Load user data
        self.load_user_data()

        # Set up cursor blinking (every 0.5 seconds)
        self.set_interval(0.5, self.toggle_cursor)

        # Run startup flow as a worker to allow push_screen_wait
        self.run_worker(self.startup_flow())

    async def startup_flow(self) -> None:
        """Handle startup flow for user setup/selection."""
        # Startup flow: Check if users exist and route to appropriate state
        if len(self.user_data) == 0:
            # No users exist - force create first user
            await self.force_create_first_user()
        elif self.current_user is None:
            # Users exist but no current_user selected - show user selection
            await self.force_user_selection()
        else:
            # Current user exists - go to main menu
            self.game_state = GameState.MENU

        self.update_display()

    def load_user_data(self) -> None:
        """Load user data from JSON file."""
        if self.user_data_file.exists():
            try:
                with open(self.user_data_file, "r") as f:
                    data = json.load(f)
                    self.current_user = data.get("current_user")
                    self.user_data = data.get("users", {})
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, start fresh
                self.current_user = None
                self.user_data = {}
        else:
            self.current_user = None
            self.user_data = {}

    def save_user_data(self) -> None:
        """Save user data to JSON file."""
        data = {
            "current_user": self.current_user,
            "users": self.user_data
        }
        try:
            with open(self.user_data_file, "w") as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't save

    async def force_create_first_user(self) -> None:
        """Force user creation on first startup when no users exist."""
        self.game_state = GameState.USER_SETUP
        self.update_display()

        # Show username screen and wait for input
        username = await self.push_screen_wait(UsernameScreen())

        if username:
            # Create user and set as current
            self.create_user(username)
            self.current_user = username
            self.save_user_data()
            self.game_state = GameState.MENU
        else:
            # User cancelled - retry
            await self.force_create_first_user()

    async def force_user_selection(self) -> None:
        """Force user selection when users exist but no current_user is set."""
        self.game_state = GameState.USER_SELECT
        self.update_display()

        # Show user menu screen
        result = await self.push_screen_wait(UserMenuScreen(self.current_user, self.user_data))

        if result and result.get("user"):
            # User selected
            self.current_user = result.get("user")
            self.save_user_data()
            self.game_state = GameState.MENU
        else:
            # No user selected - retry
            await self.force_user_selection()

    async def prompt_username(self) -> None:
        """Show username prompt and create new user if needed."""
        username = await self.push_screen_wait(UsernameScreen())
        if username:
            self.create_user(username)
            self.current_user = username
            self.save_user_data()

    def create_user(self, username: str) -> None:
        """Create a new user entry in user_data."""
        if username not in self.user_data:
            self.user_data[username] = {
                "tests_completed": 0,
                "total_wpm": 0.0,
                "best_wpm": 0,
                "total_accuracy": 0.0,
                "best_accuracy": 0.0
            }

    def update_user_stats(self, wpm: int, accuracy: float) -> None:
        """Update current user's stats after completing a test."""
        if not self.current_user:
            return

        # Ensure user exists
        if self.current_user not in self.user_data:
            self.create_user(self.current_user)

        user = self.user_data[self.current_user]
        user["tests_completed"] += 1
        user["total_wpm"] += wpm
        user["total_accuracy"] += accuracy

        # Update best scores
        if wpm > user["best_wpm"]:
            user["best_wpm"] = wpm
        if accuracy > user["best_accuracy"]:
            user["best_accuracy"] = accuracy

        self.save_user_data()

    def toggle_cursor(self) -> None:
        """Toggle cursor visibility for blinking effect."""
        self.cursor_visible = not self.cursor_visible
        self.update_display()

    def create_ascii_title(self, theme) -> Text:
        """Create ASCII art title with theme colors."""
        title = Text()
        title.append("╔═══════════════════════════════════════════════════════════════════════╗\n", style=theme["correct"])
        title.append("║                                                                       ║\n", style=theme["correct"])
        title.append("║     ████████╗██╗   ██╗██████╗ ██╗███╗   ██╗ ██████╗                 ║\n", style=theme["complete"])
        title.append("║     ╚══██╔══╝╚██╗ ██╔╝██╔══██╗██║████╗  ██║██╔════╝                 ║\n", style=theme["complete"])
        title.append("║        ██║    ╚████╔╝ ██████╔╝██║██╔██╗ ██║██║  ███╗                ║\n", style=theme["complete"])
        title.append("║        ██║     ╚██╔╝  ██╔═══╝ ██║██║╚██╗██║██║   ██║                ║\n", style=theme["complete"])
        title.append("║        ██║      ██║   ██║     ██║██║ ╚████║╚██████╔╝                ║\n", style=theme["complete"])
        title.append("║        ╚═╝      ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝                 ║\n", style=theme["complete"])
        title.append("║                                                                       ║\n", style=theme["correct"])
        title.append("║          ██████╗  █████╗ ███╗   ███╗███████╗                        ║\n", style=theme["complete"])
        title.append("║         ██╔════╝ ██╔══██╗████╗ ████║██╔════╝                        ║\n", style=theme["complete"])
        title.append("║         ██║  ███╗███████║██╔████╔██║█████╗                          ║\n", style=theme["complete"])
        title.append("║         ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝                          ║\n", style=theme["complete"])
        title.append("║         ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗                        ║\n", style=theme["complete"])
        title.append("║          ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝                        ║\n", style=theme["complete"])
        title.append("║                                                                       ║\n", style=theme["correct"])
        title.append("╚═══════════════════════════════════════════════════════════════════════╝\n", style=theme["correct"])
        return title

    def create_progress_bar(self, progress: float, width: int = 50, theme=None) -> Text:
        """Create a progress bar visualization with block characters."""
        if theme is None:
            theme = THEMES[self.theme_index]

        filled = int(progress * width)
        empty = width - filled

        bar = Text()
        bar.append("▐", style=theme["complete"])
        bar.append("█" * filled, style=theme["complete"])
        bar.append("░" * empty, style="dim")
        bar.append("▌", style=theme["complete"])
        bar.append(f" {progress * 100:.0f}%", style="bold")

        return bar

    def update_display(self) -> None:
        """Update the display with current state."""
        # Get current theme
        theme = THEMES[self.theme_index]

        instructions = self.query_one("#instructions", Static)
        completed_lines_container = self.query_one("#completed-lines", Static)
        current_line_container = self.query_one("#current-line-bordered", Static)
        preview_lines_container = self.query_one("#preview-lines", Static)
        live_stats_container = self.query_one("#live-stats", Static)

        # Update live stats display (only show during IN_TEST)
        if self.game_state == GameState.IN_TEST and self.start_time > 0:
            stats_text = Text()
            stats_text.append("┌────────────────────────────────────────────────────────────────┐\n", style="cyan dim")
            stats_text.append("│ ", style="cyan dim")
            stats_text.append("WPM: ", style="bold yellow")
            stats_text.append(f"{self.live_wpm:.1f}", style="green bold")
            stats_text.append(" │ ", style="cyan dim")
            stats_text.append("Accuracy: ", style="bold cyan")
            stats_text.append(f"{self.live_accuracy:.1f}%", style="green bold")
            stats_text.append(" │ ", style="cyan dim")
            stats_text.append("Streak: ", style="bold magenta")
            stats_text.append(f"{self.current_streak}", style="green bold")
            stats_text.append(" (Best: ", style="dim")
            stats_text.append(f"{self.best_streak}", style="yellow bold")
            stats_text.append(")", style="dim")

            # Pad to align the right border (internal width is 64)
            current_content = f"WPM: {self.live_wpm:.1f} │ Accuracy: {self.live_accuracy:.1f}% │ Streak: {self.current_streak} (Best: {self.best_streak})"
            padding = max(0, 63 - len(current_content))
            stats_text.append(" " * padding, style="cyan dim")
            stats_text.append("│\n", style="cyan dim")
            stats_text.append("└────────────────────────────────────────────────────────────────┘", style="cyan dim")
            live_stats_container.update(stats_text)
        else:
            # Clear live stats when not in IN_TEST state
            live_stats_container.update("")

        # User setup screen (USER_SETUP state)
        if self.game_state == GameState.USER_SETUP:
            instructions.update("[bold cyan]Welcome to Typing Speed Game![/bold cyan]")
            setup_text = Text()
            setup_text.append("\n┌─────────────────────────────────────────────────────────────┐\n", style=theme["correct"])
            setup_text.append("│  ", style=theme["correct"])
            setup_text.append("To get started, please enter your username.", style="bold")
            setup_text.append("              │\n", style=theme["correct"])
            setup_text.append("└─────────────────────────────────────────────────────────────┘\n", style=theme["correct"])
            setup_text.append("\nType your username and press ", style="white")
            setup_text.append("ENTER", style="green bold")
            setup_text.append(" to continue.\n", style="white")
            current_line_container.update(setup_text)

            # Clear other containers
            completed_lines_container.update("")
            preview_lines_container.update("")
            completion_msg = self.query_one("#completion-message", Static)
            completion_msg.update("")
            return

        # User selection screen (USER_SELECT state)
        if self.game_state == GameState.USER_SELECT:
            instructions.update("[bold cyan]Select Your User[/bold cyan]")
            select_text = Text()
            select_text.append("\n┌─────────────────────────────────────────────────────────────┐\n", style=theme["correct"])
            select_text.append("│  ", style=theme["correct"])
            select_text.append("Available users:", style="bold yellow")
            select_text.append("                                           │\n", style=theme["correct"])
            select_text.append("└─────────────────────────────────────────────────────────────┘\n", style=theme["correct"])
            select_text.append("\n")

            for i, username in enumerate(sorted(self.user_data.keys()), 1):
                select_text.append("  ► ", style="cyan bold")
                select_text.append(f"{i}. ", style="cyan bold")
                select_text.append(f"{username}\n", style="green")

            select_text.append("\n" + "─" * 61 + "\n", style="dim")
            select_text.append("Press ", style="white")
            select_text.append("1-9", style="cyan bold")
            select_text.append(" to select a user, or ", style="white")
            select_text.append("C", style="cyan bold")
            select_text.append(" to create a new user.\n", style="white")
            current_line_container.update(select_text)

            # Clear other containers
            completed_lines_container.update("")
            preview_lines_container.update("")
            completion_msg = self.query_one("#completion-message", Static)
            completion_msg.update("")
            return

        # Mode selection screen (MENU state)
        if self.game_state == GameState.MENU:
            if self.game_mode is None:
                # No mode selected - show mode selection menu with ASCII title
                instructions.update("")  # Clear instructions for title
                mode_text = Text()

                # Add ASCII title
                mode_text.append(self.create_ascii_title(theme))
                mode_text.append("\n")

                # Mode selection with decorative boxes
                mode_text.append("╔════════════════════════════════════════════════════════════════════╗\n", style=theme["correct"])
                mode_text.append("║  ", style=theme["correct"])
                mode_text.append("SELECT YOUR CHALLENGE", style="bold cyan")
                mode_text.append("                                             ║\n", style=theme["correct"])
                mode_text.append("╚════════════════════════════════════════════════════════════════════╝\n", style=theme["correct"])
                mode_text.append("\n")

                mode_text.append("  ┌────────────────────────────────────────────────────────────┐\n", style="green")
                mode_text.append("  │ ", style="green")
                mode_text.append("1", style="bold green")
                mode_text.append(" ► ", style="green")
                mode_text.append("30-Second Challenge", style="bold green")
                mode_text.append("                                  │\n", style="green")
                mode_text.append("  │   ", style="green")
                mode_text.append("⚡ Race against time! Type as many words as possible.", style="white")
                mode_text.append("    │\n", style="green")
                mode_text.append("  └────────────────────────────────────────────────────────────┘\n", style="green")
                mode_text.append("\n")

                mode_text.append("  ┌────────────────────────────────────────────────────────────┐\n", style="yellow")
                mode_text.append("  │ ", style="yellow")
                mode_text.append("2", style="bold yellow")
                mode_text.append(" ► ", style="yellow")
                mode_text.append("30-Word Sprint", style="bold yellow")
                mode_text.append("                                       │\n", style="yellow")
                mode_text.append("  │   ", style="yellow")
                mode_text.append("🏃 Complete 30 words as fast as you can!", style="white")
                mode_text.append("                │\n", style="yellow")
                mode_text.append("  └────────────────────────────────────────────────────────────┘\n", style="yellow")
                mode_text.append("\n")

                mode_text.append("  ┌────────────────────────────────────────────────────────────┐\n", style="blue")
                mode_text.append("  │ ", style="blue")
                mode_text.append("3", style="bold blue")
                mode_text.append(" ► ", style="blue")
                mode_text.append("Unlimited Practice", style="bold blue")
                mode_text.append("                                   │\n", style="blue")
                mode_text.append("  │   ", style="blue")
                mode_text.append("📚 Practice at your own pace. No pressure!", style="white")
                mode_text.append("              │\n", style="blue")
                mode_text.append("  └────────────────────────────────────────────────────────────┘\n", style="blue")

                current_line_container.update(mode_text)
            else:
                # Mode selected - show ready up prompt with decorative frame
                mode_names = {"30sec": "30-Second Challenge", "30word": "30-Word Sprint", "unlimited": "Unlimited Practice"}
                mode_colors = {"30sec": "green", "30word": "yellow", "unlimited": "blue"}
                mode_icons = {"30sec": "⚡", "30word": "🏃", "unlimited": "📚"}
                mode_name = mode_names.get(self.game_mode, self.game_mode)
                mode_color = mode_colors.get(self.game_mode, "white")
                mode_icon = mode_icons.get(self.game_mode, "►")

                instructions.update("")
                mode_text = Text(justify="center")
                mode_text.append("\n")
                mode_text.append("╔════════════════════════════════════════════════════════════════════╗\n", style=mode_color)
                mode_text.append("║  ", style=mode_color)
                mode_text.append("MODE SELECTED", style=f"bold {mode_color}")
                mode_text.append("                                                     ║\n", style=mode_color)
                mode_text.append("╠════════════════════════════════════════════════════════════════════╣\n", style=mode_color)
                mode_text.append("║                                                                    ║\n", style=mode_color)
                mode_text.append("║", style=mode_color)

                # Center the mode name within the box
                mode_display = f"{mode_icon} {mode_name}"
                mode_padding_total = 68 - len(mode_display)  # 68 is internal width
                mode_padding_left = mode_padding_total // 2
                mode_padding_right = mode_padding_total - mode_padding_left

                mode_text.append(" " * mode_padding_left, style=mode_color)
                mode_text.append(mode_display, style=f"bold {mode_color}")
                mode_text.append(" " * mode_padding_right, style=mode_color)
                mode_text.append("║\n", style=mode_color)
                mode_text.append("║                                                                    ║\n", style=mode_color)
                mode_text.append("╚════════════════════════════════════════════════════════════════════╝\n", style=mode_color)
                mode_text.append("\n")

                mode_text.append("┌──────────────────────────────────────────────┐\n", style="cyan")
                mode_text.append("│  Press ", style="cyan")
                mode_text.append("ENTER", style="green bold")
                mode_text.append(" to ready up and start typing  │\n", style="cyan")
                mode_text.append("└──────────────────────────────────────────────┘\n", style="cyan")
                mode_text.append("\n")

                instruction_line = Text(justify="center")
                instruction_line.append("Press ", style="dim")
                instruction_line.append("1/2/3", style="cyan bold")
                instruction_line.append(" to select a different mode", style="dim")
                mode_text.append(instruction_line)
                mode_text.append("\n")

                current_line_container.update(mode_text)

            # Clear other containers
            completed_lines_container.update("")
            preview_lines_container.update("")
            completion_msg = self.query_one("#completion-message", Static)
            completion_msg.update("")
            return

        # READY state - show ready indicator with visual frame
        if self.game_state == GameState.READY:
            ready_text = Text()
            ready_text.append("\n╔════════════════════════════════════════════════════════════════════╗\n", style="green bold")
            ready_text.append("║                                                                    ║\n", style="green bold")
            ready_text.append("║              ", style="green bold")
            ready_text.append("✓ READY! START TYPING WHEN READY...", style="green bold")
            ready_text.append("                   ║\n", style="green bold")
            ready_text.append("║                                                                    ║\n", style="green bold")
            ready_text.append("╚════════════════════════════════════════════════════════════════════╝\n", style="green bold")
            instructions.update(ready_text)
        # IN_TEST state - show progress indicator
        elif self.game_state == GameState.IN_TEST:
            test_header = Text()
            test_header.append("┌─────────────────────────────────────────────────────────────────┐\n", style=theme["complete"])
            test_header.append("│  ", style=theme["complete"])
            test_header.append("⌨  TYPING IN PROGRESS...", style="bold yellow")
            test_header.append("                                       │\n", style=theme["complete"])
            test_header.append("└─────────────────────────────────────────────────────────────────┘", style=theme["complete"])
            instructions.update(test_header)
        # COMPLETE state - show completion banner
        elif self.game_state == GameState.COMPLETE:
            complete_text = Text()
            complete_text.append("\n╔════════════════════════════════════════════════════════════════════╗\n", style=theme["complete"])
            complete_text.append("║                                                                    ║\n", style=theme["complete"])
            # Center "★ ★ ★  COMPLETE!  ★ ★ ★" - it's 23 chars, box internal width is 68
            banner_text = "★ ★ ★  COMPLETE!  ★ ★ ★"
            banner_padding_left = (68 - len(banner_text)) // 2
            banner_padding_right = 68 - len(banner_text) - banner_padding_left
            complete_text.append("║", style=theme["complete"])
            complete_text.append(" " * banner_padding_left, style=theme["complete"])
            complete_text.append(banner_text, style=f"bold {theme['complete']}")
            complete_text.append(" " * banner_padding_right, style=theme["complete"])
            complete_text.append("║\n", style=theme["complete"])
            complete_text.append("║                                                                    ║\n", style=theme["complete"])
            complete_text.append("╚════════════════════════════════════════════════════════════════════╝\n", style=theme["complete"])
            instructions.update(complete_text)

        # Show completed text in COMPLETE state, hide in other special states
        if self.game_state == GameState.COMPLETE:
            # Show all completed/attempted lines with color coding (not dimmed)
            completed_display = Text()
            for target_text, typed_text, mistake_pos in self.completed_lines_history:
                for i, char in enumerate(target_text):
                    if i < len(typed_text):
                        if typed_text[i] == char:
                            # Correct character
                            completed_display.append(char, style=theme['correct'])
                        else:
                            # Incorrect character
                            completed_display.append(char, style=theme['incorrect'])
                    else:
                        # Not typed (shouldn't happen in completed lines, but handle it)
                        completed_display.append(char, style=theme['pending'])
                completed_display.append("\n")

            completed_lines_container.update(completed_display)
            current_line_container.update("")

            # Show remaining untyped lines from the paragraph in preview area (dimmed)
            preview_display = Text()
            if self.current_lines:
                # Find which line index we stopped at
                lines_typed = len(self.completed_lines_history)
                # Show any remaining lines that weren't reached
                for i in range(lines_typed, len(self.current_lines)):
                    preview_display.append(self.current_lines[i], style="dim")
                    if i < len(self.current_lines) - 1:
                        preview_display.append("\n")

            preview_lines_container.update(preview_display)
        else:
            # Render completed lines with dimmed color coding
            completed_display = Text()
            for target_text, typed_text, mistake_pos in self.completed_lines_history:
                # No manual indent - let CSS padding handle alignment
                for i, char in enumerate(target_text):
                    if i < len(typed_text):
                        if typed_text[i] == char:
                            # Correct character - dimmed version
                            completed_display.append(char, style=f"{theme['correct']} dim")
                        else:
                            # Incorrect character - dimmed version
                            completed_display.append(char, style=f"{theme['incorrect']} dim")
                    else:
                        completed_display.append(char, style="dim")
                completed_display.append("\n")

            completed_lines_container.update(completed_display)

            # Show current line with color-coding and cursor in bordered container
            current_display = Text()
            current_line_text = self.target_text
            cursor_pos = len(self.typed_text)

            # No manual indentation - let CSS padding handle alignment
            for i, char in enumerate(current_line_text):
                is_cursor_position = i == cursor_pos and self.cursor_visible and not self.completed

                if i < len(self.typed_text):
                    if self.typed_text[i] == char:
                        current_display.append(char, style=theme["correct"])
                    else:
                        current_display.append(char, style=theme["incorrect"])
                elif is_cursor_position:
                    current_display.append(char, style=theme["cursor"])
                else:
                    current_display.append(char, style=theme["pending"])

            current_line_container.update(current_display)

            # Show preview lines (next 1-2 lines) - dimmed
            preview_display = Text()
            preview_count = 0
            for i in range(self.current_line_index + 1, len(self.current_lines)):
                if preview_count >= 2:  # Show max 2 preview lines
                    break
                # No manual indent - let CSS padding handle alignment
                preview_display.append(self.current_lines[i], style="dim")
                if i < len(self.current_lines) - 1 and preview_count < 1:
                    preview_display.append("\n")
                preview_count += 1

            preview_lines_container.update(preview_display)

        # Update theme notification
        theme_notif = self.query_one("#theme-notification", Static)
        theme_notif.update(self.theme_notification)

        # Update completion message and stats based on state
        completion_msg = self.query_one("#completion-message", Static)

        if self.game_state == GameState.READY:
            # Show ready state controls with decorative frame
            ready_controls = Text()
            ready_controls.append("\n")
            ready_controls.append("        ┌────────────────────────────────────────────┐\n", style="cyan")
            ready_controls.append("        │  ", style="cyan")
            ready_controls.append("Start typing to begin", style="bold green")
            ready_controls.append(" | Press ", style="white")
            ready_controls.append("ENTER", style="yellow bold")
            ready_controls.append(" to cancel  │\n", style="white")
            ready_controls.append("        └────────────────────────────────────────────┘\n", style="cyan")
            completion_msg.update(ready_controls)
        elif self.game_state == GameState.IN_TEST:
            # Show stats during gameplay with progress bar
            stats_display = Text()
            stats_display.append("\n")

            if self.start_time > 0:
                if self.game_mode == "30sec":
                    # Show countdown progress bar
                    progress = (30.0 - self.countdown_remaining) / 30.0
                    stats_display.append("  Time: ", style="bold yellow")
                    stats_display.append(self.create_progress_bar(progress, width=40, theme=theme))
                    stats_display.append(f"  {self.countdown_remaining:.1f}s left\n", style="yellow")
                    stats_display.append(f"  Words Typed: ", style="bold")
                    stats_display.append(f"{self.total_words_typed}", style="green bold")
                    stats_display.append(f"  │  Characters: {self.total_chars_typed}", style="dim")
                elif self.game_mode == "30word":
                    # Show word completion progress
                    progress = self.total_words_typed / 30.0
                    words_left = 30 - self.total_words_typed
                    stats_display.append("  Progress: ", style="bold yellow")
                    stats_display.append(self.create_progress_bar(progress, width=40, theme=theme))
                    stats_display.append(f"  {words_left} words left\n", style="yellow")
                    stats_display.append(f"  Time Elapsed: ", style="bold")
                    stats_display.append(f"{self.elapsed_time:.1f}s", style="cyan bold")
                else:  # unlimited
                    # Show elapsed time and words - NO progress bar for unlimited mode
                    if len(self.current_lines) > 0:
                        total_lines = len(self.current_lines)
                        lines_done = self.current_line_index
                        stats_display.append(f"  Lines: ", style="bold yellow")
                        stats_display.append(f"{lines_done}/{total_lines}", style="yellow bold")
                        stats_display.append(f"  │  ", style="dim")
                    stats_display.append(f"Time: ", style="bold")
                    stats_display.append(f"{self.elapsed_time:.1f}s", style="cyan bold")
                    stats_display.append(f"  │  Words: ", style="bold")
                    stats_display.append(f"{self.total_words_typed}", style="green bold")

                stats_display.append("\n\n")
                stats_display.append("  " + "─" * 60 + "\n", style="dim")
                stats_display.append("  Press ", style="dim")
                stats_display.append("ESC", style="yellow bold")
                stats_display.append(" to cancel test", style="dim")
            else:
                stats_display.append("  " + "─" * 60 + "\n", style="dim")
                stats_display.append("  Press ", style="dim")
                stats_display.append("ESC", style="yellow bold")
                stats_display.append(" to cancel", style="dim")

            completion_msg.update(stats_display)
        elif self.game_state == GameState.COMPLETE:
            # Calculate final WPM and accuracy with decorative results display
            if self.game_mode == "30sec":
                words = self.total_chars_typed / 5
                minutes = 0.5  # 30 seconds = 0.5 minutes
            elif self.game_mode == "30word":
                words = 30
                minutes = self.elapsed_time / 60
            else:  # unlimited
                words = self.total_chars_typed / 5
                minutes = self.elapsed_time / 60 if self.elapsed_time > 0 else 1

            wpm = int(words / minutes) if minutes > 0 else 0

            results_display = Text()
            results_display.append("\n")

            # Create perfect rectangle box - 67 spaces between borders
            border_width = 67

            results_display.append("╔" + "═" * border_width + "╗\n", style=theme["complete"])
            results_display.append("║" + " " * border_width + "║\n", style=theme["complete"])

            # Center "FINAL RESULTS" - it's 13 chars
            title_text = "FINAL RESULTS"
            title_padding_left = (border_width - len(title_text)) // 2
            title_padding_right = border_width - len(title_text) - title_padding_left
            results_display.append("║", style=theme["complete"])
            results_display.append(" " * title_padding_left, style=theme["complete"])
            results_display.append(title_text, style=f"bold {theme['complete']}")
            results_display.append(" " * title_padding_right, style=theme["complete"])
            results_display.append("║\n", style=theme["complete"])

            results_display.append("║" + " " * border_width + "║\n", style=theme["complete"])
            results_display.append("╠" + "═" * border_width + "╣\n", style=theme["complete"])
            results_display.append("║" + " " * border_width + "║\n", style=theme["complete"])

            # WPM line - left-align with 2-space margin
            wpm_label = "Words Per Minute:"
            wpm_value = f"{wpm}"
            if wpm >= 80:
                wpm_stars = "  ***"
            elif wpm >= 60:
                wpm_stars = "  **"
            elif wpm >= 40:
                wpm_stars = "  *"
            else:
                wpm_stars = ""

            # Build WPM line: 2 spaces + label + 2 spaces + value + stars
            wpm_line_content = f"  {wpm_label}  {wpm_value}{wpm_stars}"
            wpm_padding = border_width - len(wpm_line_content)
            results_display.append("║", style=theme["complete"])
            results_display.append("  ", style=theme["complete"])
            results_display.append(wpm_label, style="bold yellow")
            results_display.append(f"  {wpm_value}", style=f"bold {theme['complete']}")
            if wpm_stars:
                results_display.append(wpm_stars, style="yellow bold")
            results_display.append(" " * wpm_padding, style=theme["complete"])
            results_display.append("║\n", style=theme["complete"])

            # Accuracy line - left-align with 2-space margin
            acc_label = "Accuracy:"
            acc_value = f"{self.accuracy:.1f}%"

            acc_line_content = f"  {acc_label}          {acc_value}"
            acc_padding = border_width - len(acc_line_content)
            results_display.append("║", style=theme["complete"])
            results_display.append("  ", style=theme["complete"])
            results_display.append(acc_label, style="bold cyan")
            results_display.append(f"          {acc_value}", style=f"bold {theme['complete']}")
            results_display.append(" " * acc_padding, style=theme["complete"])
            results_display.append("║\n", style=theme["complete"])

            results_display.append("║" + " " * border_width + "║\n", style=theme["complete"])
            results_display.append("╚" + "═" * border_width + "╝\n", style=theme["complete"])
            results_display.append("\n")
            # Action menu with proper alignment - 61 chars internal width
            results_display.append("  ┌─────────────────────────────────────────────────────────────┐\n", style="dim")
            results_display.append("  │  ", style="dim")
            results_display.append("N", style="green bold")
            results_display.append(" New  │  ", style="dim")
            results_display.append("R", style="yellow bold")
            results_display.append(" Retry  │  ", style="dim")
            results_display.append("U", style="cyan bold")
            results_display.append(" Users  │  ", style="dim")
            results_display.append("S", style="magenta bold")
            results_display.append(" Stats  │  ", style="dim")
            results_display.append("ESC", style="red bold")
            results_display.append(" Menu     │\n", style="dim")
            results_display.append("  └─────────────────────────────────────────────────────────────┘", style="dim")

            completion_msg.update(results_display)
        else:
            completion_msg.update("")

    def on_key(self, event) -> None:
        """Handle key press events based on current game state."""

        # ===== MENU State =====
        if self.game_state == GameState.MENU:
            # Mode selection
            if event.key == "1":
                event.prevent_default()
                event.stop()
                self.start_mode("30sec")
                return
            elif event.key == "2":
                event.prevent_default()
                event.stop()
                self.start_mode("30word")
                return
            elif event.key == "3":
                event.prevent_default()
                event.stop()
                self.start_mode("unlimited")
                return
            # Theme switching
            elif event.key == "tab":
                event.prevent_default()
                event.stop()
                self.cycle_theme()
                return
            # User management
            elif event.key == "u":
                event.prevent_default()
                event.stop()
                self.run_worker(self.show_user_menu())
                return
            # Stats view
            elif event.key == "s":
                event.prevent_default()
                event.stop()
                self.run_worker(self.show_stats())
                return
            # Enter key to ready up (only if mode is selected)
            elif event.key == "enter" and self.game_mode is not None:
                event.prevent_default()
                event.stop()
                self.ready_up()
                return
            # ESC to quit app from menu
            elif event.key == "escape":
                event.prevent_default()
                event.stop()
                self.exit()
                return
            return

        # ===== READY State =====
        elif self.game_state == GameState.READY:
            # ENTER to cancel and go back to menu (un-ready)
            if event.key == "enter":
                event.prevent_default()
                event.stop()
                self.cancel_ready()
                return
            # Theme switching
            elif event.key == "tab":
                event.prevent_default()
                event.stop()
                self.cycle_theme()
                return
            # Any printable character starts the test
            elif event.key == "space":
                event.prevent_default()
                event.stop()
                self.game_state = GameState.IN_TEST
                self.run_worker(self.handle_character(" "))
                return
            else:
                # Handle special characters
                char_map = {
                    "period": ".",
                    "full_stop": ".",
                    "comma": ",",
                    "exclamation_mark": "!",
                    "question_mark": "?",
                    "colon": ":",
                    "semicolon": ";",
                    "apostrophe": "'",
                    "quotation_mark": '"',
                    "hyphen": "-",
                    "minus": "-",
                    "underscore": "_",
                    "slash": "/",
                    "backslash": "\\",
                    "left_parenthesis": "(",
                    "right_parenthesis": ")",
                    "left_square_bracket": "[",
                    "right_square_bracket": "]",
                    "at": "@",
                    "number_sign": "#",
                    "dollar_sign": "$",
                    "percent_sign": "%",
                    "ampersand": "&",
                    "asterisk": "*",
                    "plus": "+",
                    "equals": "=",
                }

                if event.key in char_map:
                    event.prevent_default()
                    event.stop()
                    self.game_state = GameState.IN_TEST
                    self.run_worker(self.handle_character(char_map[event.key]))
                    return
                elif len(event.key) == 1:
                    # Regular single character - start test
                    event.prevent_default()
                    event.stop()
                    self.game_state = GameState.IN_TEST
                    self.run_worker(self.handle_character(event.key))
                    return
            return

        # ===== IN_TEST State =====
        elif self.game_state == GameState.IN_TEST:
            # ESC to cancel test
            if event.key == "escape":
                event.prevent_default()
                event.stop()
                self.cancel_test()
                return
            # Typing
            elif event.key == "backspace":
                event.prevent_default()
                event.stop()
                if self.typed_text:
                    self.typed_text = self.typed_text[:-1]
                    self.update_display()
                return
            elif event.key == "space":
                event.prevent_default()
                event.stop()
                self.run_worker(self.handle_character(" "))
                return
            else:
                # Handle special characters
                char_map = {
                    "period": ".",
                    "full_stop": ".",
                    "comma": ",",
                    "exclamation_mark": "!",
                    "question_mark": "?",
                    "colon": ":",
                    "semicolon": ";",
                    "apostrophe": "'",
                    "quotation_mark": '"',
                    "hyphen": "-",
                    "minus": "-",
                    "underscore": "_",
                    "slash": "/",
                    "backslash": "\\",
                    "left_parenthesis": "(",
                    "right_parenthesis": ")",
                    "left_square_bracket": "[",
                    "right_square_bracket": "]",
                    "at": "@",
                    "number_sign": "#",
                    "dollar_sign": "$",
                    "percent_sign": "%",
                    "ampersand": "&",
                    "asterisk": "*",
                    "plus": "+",
                    "equals": "=",
                }

                if event.key in char_map:
                    event.prevent_default()
                    event.stop()
                    self.run_worker(self.handle_character(char_map[event.key]))
                    return
                elif len(event.key) == 1:
                    # Regular single character
                    event.prevent_default()
                    event.stop()
                    self.run_worker(self.handle_character(event.key))
                    return
            return

        # ===== COMPLETE State =====
        elif self.game_state == GameState.COMPLETE:
            # N for next phrase
            if event.key == "n":
                event.prevent_default()
                event.stop()
                self.new_paragraph()
                return
            # R to retry
            elif event.key == "r":
                event.prevent_default()
                event.stop()
                self.restart()
                return
            # Theme switching
            elif event.key == "tab":
                event.prevent_default()
                event.stop()
                self.cycle_theme()
                return
            # M or ESC to return to menu
            elif event.key == "m" or event.key == "escape":
                event.prevent_default()
                event.stop()
                self.return_to_menu()
                return
            # User management
            elif event.key == "u":
                event.prevent_default()
                event.stop()
                self.run_worker(self.show_user_menu())
                return
            # Stats view
            elif event.key == "s":
                event.prevent_default()
                event.stop()
                self.run_worker(self.show_stats())
                return
            return

    async def handle_character(self, char: str) -> None:
        """Handle a single character input."""
        # Space grace: ignore space at the beginning of a line (except if target starts with space)
        # This allows users to naturally type space between words across line boundaries
        if char == " " and len(self.typed_text) == 0 and len(self.target_text) > 0:
            if self.target_text[0] != " ":
                # Ignore this space - it's the natural space at a line boundary
                self.update_display()
                return

        # Start timer on first keystroke
        if len(self.typed_text) == 0 and self.start_time == 0.0:
            self.start_time = time.time()
            # Start timer update based on mode
            if self.game_mode == "30sec":
                self.set_interval(0.1, self.update_countdown)
            elif self.game_mode in ["unlimited", "30word"]:
                self.set_interval(0.1, self.update_timer)

        # Ignore spaces typed beyond the target text length (at line boundaries)
        # This prevents false errors when users press space at the end of a line
        if char == " " and len(self.typed_text) >= len(self.target_text):
            # Don't add the space, just trigger line completion check
            await self.check_line_completion()
            self.update_display()
            return

        # Don't allow typing beyond target length (prevents overflow errors)
        if len(self.typed_text) >= len(self.target_text):
            # Already at line end, trigger completion check
            await self.check_line_completion()
            self.update_display()
            return

        self.typed_text += char
        self.total_chars_typed += 1

        # Track mistake if wrong character typed
        current_pos = len(self.typed_text) - 1
        if current_pos < len(self.target_text) and self.typed_text[current_pos] != self.target_text[current_pos]:
            if current_pos not in self.mistake_positions:
                self.mistake_positions.add(current_pos)
                self.mistakes += 1
            # Reset streak on mistake
            self.current_streak = 0
        else:
            # Increment streak on correct character
            self.current_streak += 1
            if self.current_streak > self.best_streak:
                self.best_streak = self.current_streak

        # Update elapsed time (for all modes)
        if self.start_time > 0:
            self.elapsed_time = time.time() - self.start_time

        # Calculate live WPM and accuracy
        if self.start_time > 0:
            elapsed_minutes = self.elapsed_time / 60
            if elapsed_minutes > 0:
                self.live_wpm = (self.total_chars_typed / 5) / elapsed_minutes
            if self.total_chars_typed > 0:
                self.live_accuracy = ((self.total_chars_typed - self.mistakes) / self.total_chars_typed) * 100

        await self.check_line_completion()
        self.update_display()

    def cycle_theme(self) -> None:
        """Cycle to the next theme and show notification."""
        self.theme_index = (self.theme_index + 1) % len(THEMES)
        theme = THEMES[self.theme_index]
        self.theme_notification = f"[bold yellow]Theme: {theme['name']}[/bold yellow]"
        self.update_display()
        self.set_timer(1.5, self.clear_theme_notification)

    def clear_theme_notification(self) -> None:
        """Clear the theme notification message."""
        self.theme_notification = ""
        self.update_display()

    async def show_user_menu(self) -> None:
        """Show the user management menu."""
        result = await self.push_screen_wait(UserMenuScreen(self.current_user, self.user_data))
        if result and result.get("action") in ["switch", "back"]:
            self.current_user = result.get("user")
            self.save_user_data()
        self.update_display()

    async def show_stats(self) -> None:
        """Show the stats and leaderboard screen."""
        await self.push_screen_wait(StatsScreen(self.current_user, self.user_data))
        self.update_display()

    def start_mode(self, mode: str) -> None:
        """Initialize a game mode with a random paragraph and stay in MENU state."""
        self.game_state = GameState.MENU
        self.game_mode = mode
        self.current_paragraph = random.choice(self.paragraphs)
        self.current_lines = self.split_into_lines(self.current_paragraph)
        self.current_line_index = 0
        self.target_text = self.current_lines[0]
        self.typed_text = ""
        self.completed = False
        self.start_time = 0.0
        self.elapsed_time = 0.0
        self.accuracy = 0.0
        self.mistakes = 0
        self.mistake_positions.clear()
        self.lines_completed = 0
        self.total_chars_typed = 0
        self.total_words_typed = 0
        self.countdown_remaining = 30.0
        self.completed_lines_history.clear()
        # Reset streak and live stats
        self.current_streak = 0
        self.best_streak = 0
        self.live_wpm = 0.0
        self.live_accuracy = 0.0
        self.sub_title = f"Mode: {mode.upper()} | U Users | S Stats | TAB Theme | ESC Quit"
        self.update_display()

    async def update_countdown(self) -> None:
        """Update countdown timer for 30-second mode."""
        if self.start_time > 0 and not self.completed:
            elapsed = time.time() - self.start_time
            self.elapsed_time = elapsed
            self.countdown_remaining = max(0, 30.0 - elapsed)

            if self.countdown_remaining <= 0:
                await self.complete_game()

            self.update_display()

    def update_timer(self) -> None:
        """Update elapsed timer for unlimited and 30-word modes."""
        if self.start_time > 0 and not self.completed:
            self.elapsed_time = time.time() - self.start_time
            self.update_display()

    async def check_line_completion(self) -> None:
        """Check if current line is completed and advance to next line."""
        if len(self.typed_text) == len(self.target_text):
            # Line completed! Save it to history
            self.completed_lines_history.append((
                self.target_text,
                self.typed_text,
                self.mistake_positions.copy()
            ))
            self.lines_completed += 1

            # Count words (every 5 characters = 1 word, or actual word count)
            words_in_line = len(self.target_text.split())
            self.total_words_typed += words_in_line

            # Check mode-specific completion
            if self.game_mode == "30word" and self.total_words_typed >= 30:
                await self.complete_game()
                return

            # Check if there are more lines
            if self.current_line_index < len(self.current_lines) - 1:
                # Advance to next line
                self.current_line_index += 1
                self.target_text = self.current_lines[self.current_line_index]
                self.typed_text = ""
                self.mistake_positions.clear()
            else:
                # No more lines - different behavior per mode
                if self.game_mode == "30sec":
                    # In 30-sec mode, cycle to new paragraph
                    self.current_paragraph = random.choice(self.paragraphs)
                    self.current_lines = self.split_into_lines(self.current_paragraph)
                    self.current_line_index = 0
                    self.target_text = self.current_lines[0]
                    self.typed_text = ""
                    self.mistake_positions.clear()
                elif self.game_mode == "unlimited":
                    # In unlimited mode, complete the game
                    await self.complete_game()

    async def complete_game(self) -> None:
        """Mark the game as completed, transition to COMPLETE state, and calculate final stats."""
        self.completed = True
        self.game_state = GameState.COMPLETE

        # Add current line to history if it has any typed text
        # This ensures the last line is visible in COMPLETE state
        if self.typed_text:
            self.completed_lines_history.append((
                self.target_text,
                self.typed_text,
                self.mistake_positions.copy()
            ))

        if self.start_time > 0:
            self.elapsed_time = time.time() - self.start_time

        # Calculate accuracy
        if self.total_chars_typed > 0:
            self.accuracy = ((self.total_chars_typed - self.mistakes) / self.total_chars_typed) * 100
        else:
            self.accuracy = 0.0

        # Calculate WPM
        if self.game_mode == "30sec":
            words = self.total_chars_typed / 5
            minutes = 0.5  # 30 seconds = 0.5 minutes
        elif self.game_mode == "30word":
            words = 30
            minutes = self.elapsed_time / 60
        else:  # unlimited
            words = self.total_chars_typed / 5
            minutes = self.elapsed_time / 60 if self.elapsed_time > 0 else 1

        wpm = int(words / minutes) if minutes > 0 else 0

        # Prompt for username if this is first test
        if self.current_user is None:
            await self.prompt_username()

        # Update stats for current user
        if self.current_user:
            self.update_user_stats(wpm, self.accuracy)

        self.update_display()

    def ready_up(self) -> None:
        """Transition from MENU to READY state."""
        self.game_state = GameState.READY
        self.update_display()

    def cancel_ready(self) -> None:
        """Cancel ready state and return to menu (un-ready)."""
        self.game_state = GameState.MENU
        self.typed_text = ""
        self.start_time = 0.0
        self.elapsed_time = 0.0
        self.update_display()

    def cancel_test(self) -> None:
        """Cancel the current test and return to menu."""
        self.game_state = GameState.MENU
        self.typed_text = ""
        self.start_time = 0.0
        self.elapsed_time = 0.0
        self.update_display()

    def return_to_menu(self) -> None:
        """Return to mode selection screen."""
        self.game_state = GameState.MENU
        self.game_mode = None
        self.typed_text = ""
        self.completed = False
        self.start_time = 0.0
        self.elapsed_time = 0.0
        self.accuracy = 0.0
        self.mistakes = 0
        self.mistake_positions.clear()
        self.current_line_index = 0
        self.lines_completed = 0
        self.total_chars_typed = 0
        self.total_words_typed = 0
        self.countdown_remaining = 30.0
        self.current_lines = []
        self.current_paragraph = ""
        self.completed_lines_history.clear()
        # Reset streak and live stats
        self.current_streak = 0
        self.best_streak = 0
        self.live_wpm = 0.0
        self.live_accuracy = 0.0
        self.sub_title = "U Users | S Stats | TAB Theme | ESC Quit"
        self.update_display()

    def restart(self) -> None:
        """Restart the current mode with the same paragraph and go to READY state."""
        if self.game_mode:
            mode = self.game_mode
            paragraph = self.current_paragraph
            self.game_state = GameState.READY
            self.game_mode = mode
            self.current_paragraph = paragraph
            self.current_lines = self.split_into_lines(self.current_paragraph)
            self.current_line_index = 0
            self.target_text = self.current_lines[0]
            self.typed_text = ""
            self.completed = False
            self.start_time = 0.0
            self.elapsed_time = 0.0
            self.accuracy = 0.0
            self.mistakes = 0
            self.mistake_positions.clear()
            self.lines_completed = 0
            self.total_chars_typed = 0
            self.total_words_typed = 0
            self.countdown_remaining = 30.0
            self.completed_lines_history.clear()
            # Reset streak and live stats
            self.current_streak = 0
            self.best_streak = 0
            self.live_wpm = 0.0
            self.live_accuracy = 0.0
            self.update_display()

    def new_paragraph(self) -> None:
        """Start a new paragraph in the current mode and go to READY state."""
        if self.game_mode:
            self.start_mode(self.game_mode)


def main():
    app = TypingGame()
    app.run()


if __name__ == "__main__":
    main()
