# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A terminal-based typing speed game built with Python using the Textual TUI framework. Features multiple game modes (30-second challenge, 30-word sprint, unlimited practice), user management with persistent stats and leaderboard, customizable themes, and real-time visual feedback with color-coded multi-line text display.

## Package Management

This project uses **uv** for Python package management. Always use `uv` commands instead of pip:

- `uv sync` - Install/sync dependencies from uv.lock
- `uv add <package>` - Add a new dependency
- `uv remove <package>` - Remove a dependency
- `uv run <command>` - Run a command in the project's virtual environment

## Running the Application

- `uv run python main.py` - Run the typing game
- `uv run python -m main` - Alternative way to run the application
- **Never run the program to test** - the user will test it themselves

## Architecture

### Single-File Application
The entire application is contained in `main.py` with a single `TypingGame` class that inherits from `textual.app.App`, plus three modal `Screen` classes for user interactions.

### Game State Machine
The application uses a `GameState` enum to manage flow (main.py:13-20):
- **USER_SETUP**: First-time user creation (forced on first launch)
- **USER_SELECT**: User selection screen (forced if users exist but none selected)
- **MENU**: Main menu - mode selection and settings (ESC quits from here)
- **READY**: Ready to start - waiting for first keystroke (ENTER to cancel)
- **IN_TEST**: Actively typing (ESC to cancel)
- **COMPLETE**: Test finished, showing results (N/R/U/S/ESC options)

### Key Components

**TypingGame Class** (`main.py:376`):
- Uses Textual's reactive attributes for automatic UI updates when state changes
- Key reactive attributes: `game_state`, `game_mode`, `target_text`, `typed_text`, `completed`, `cursor_visible`, timing/stats attributes, user management attributes
- Tracks mistakes per character position in `mistake_positions` set to avoid double-counting during corrections
- Implements visual feedback through color-coded text rendering in `update_display()` (main.py:637):
  - Theme-based styling (correct/incorrect/pending/cursor/complete colors)
  - Green: correctly typed characters (or themed equivalent)
  - White on red background: incorrectly typed characters (or themed equivalent)
  - Dim gray: not yet typed characters
  - Blinking cursor: yellow cursor at current position (or themed equivalent)
  - Completed lines shown dimmed above current line
  - Preview of next 1-2 lines shown dimmed below current line
- Key event handling in `on_key()` (main.py:830) - state machine routes events based on `game_state`
- Cursor blinking implemented via `set_interval(0.5, self.toggle_cursor)`
- Timers managed with intervals: countdown for 30-sec mode, elapsed time for unlimited/30-word modes

**Modal Screens** (main.py:96-373):
- `UsernameScreen`: Text input for username entry (used for first user and new user creation)
- `UserMenuScreen`: User management - switch/create/delete users
- `StatsScreen`: Personal stats and top-5 leaderboard by best WPM

### User Management System
- Persistent storage in `users.json` at project root (main.py:456)
- JSON structure: `{"current_user": "username", "users": {...}}`
- Per-user stats tracked: `tests_completed`, `total_wpm`, `best_wpm`, `total_accuracy`, `best_accuracy`
- Forced user creation flow on first launch (no skip option)
- Forced user selection if users exist but none is current
- Stats updated only after test completion via `update_user_stats()` (main.py:610)
- All user data saved synchronously to JSON after any change

### Game Modes
Three distinct modes implemented (main.py:1093-1114):

1. **30-Second Challenge** (`"30sec"`):
   - Type as many words as possible in 30 seconds
   - Countdown timer with auto-completion at 0
   - Cycles to new random paragraphs when current one is completed
   - WPM calculated using 30 seconds fixed time

2. **30-Word Sprint** (`"30word"`):
   - Complete exactly 30 words as fast as possible
   - Elapsed timer tracking
   - Auto-completes after 30 words typed
   - WPM calculated using actual elapsed time

3. **Unlimited Practice** (`"unlimited"`):
   - Complete full paragraph at own pace
   - Elapsed timer tracking
   - Completes when all lines of paragraph are typed
   - WPM calculated using actual elapsed time

Mode selection and ready-up flow:
1. MENU state shows mode options (1/2/3)
2. Selecting mode initializes paragraph/lines but stays in MENU
3. ENTER transitions to READY state (cursor visible, waiting for first key)
4. Any printable character from READY starts IN_TEST (timer starts)
5. ENTER while READY cancels back to MENU

### Performance Metrics
- **WPM (Words Per Minute)**: Calculated as `(total_characters / 5) / (elapsed_time / 60)` for unlimited, or mode-specific calculations
- **Accuracy**: Calculated as `((total_chars - mistakes) / total_chars) * 100`
- Mistakes tracked per character position to avoid counting same mistake multiple times during corrections (main.py:1062-1066)
- Final stats calculated in `complete_game()` (main.py:1175)

### Multi-Line Text Rendering
- Paragraphs split into lines in `split_into_lines()` (main.py:482) with ~10 words per line
- Current line shown in bordered container with full color coding and cursor
- Completed lines shown above current line (dimmed, color-coded history preserved)
- Preview lines shown below current line (dimmed, 1-2 lines)
- Line completion detected when `len(typed_text) == len(target_text)` (main.py:1134)
- Completed line data saved to `completed_lines_history` with mistake positions
- Auto-advance to next line or paragraph cycling (30-sec mode) or completion (unlimited mode)

### Theme System
Four built-in themes defined in `THEMES` constant (main.py:60-93):
- Dark (default), Light, Ocean, Retro
- Each theme defines colors for: correct, incorrect, pending, cursor, complete
- TAB key cycles through themes (works in MENU and COMPLETE states)
- Theme notification shown briefly after switching (1.5 second timeout)

### Text Content
- `PHRASES`: 18 typing practice phrases including pangrams (main.py:23-42)
- `PARAGRAPHS`: 6 longer practice paragraphs on various topics (main.py:45-57)
- Game modes use paragraphs for multi-line typing practice
- Random selection on mode start and "Next" action

### Special Character Handling
- Comprehensive `char_map` for special keys (main.py:904-931 and 971-998)
- Maps Textual key names to actual characters (e.g., "period" → ".", "comma" → ",")
- Supports punctuation, symbols, brackets, operators
- Same mapping used in both READY and IN_TEST states

### Control Flow and Startup
- `on_mount()` triggers async `startup_flow()` worker (main.py:511)
- Startup flow checks user data and forces user creation/selection if needed
- App cannot reach MENU state without a valid current user
- User data loaded from JSON on mount, saved after any modification

## UI Layout
Composed of Textual widgets (main.py:471-480):
- Header and Footer (built-in Textual widgets)
- Instructions static text (changes based on game state)
- Theme notification (yellow text, auto-clears)
- Completed lines container (shows typed history above)
- Current line bordered container (main typing area with border)
- Preview lines container (shows upcoming text below)
- Completion message area (shows stats, controls, or state-specific messages)

## Game Flow

### Typical Session Flow
1. User launches app → loads/creates user → MENU state
2. Press 1/2/3 to select mode → stays in MENU (mode selected)
3. Press ENTER → transitions to READY state (cursor blinking)
4. Start typing → transitions to IN_TEST (timer starts)
5. Complete test → transitions to COMPLETE (shows stats)
6. Press N for new, R to retry, or ESC for menu → loops back

### Testing Strategy
- User will test the application manually
- Never run the program during development to verify changes
- Focus on code correctness and state machine logic

## Dependencies

- **textual** (>=6.4.0): Terminal UI framework providing the app structure, widgets, reactive attributes, screens, and event handling
- Python 3.14+ required (specified in pyproject.toml)