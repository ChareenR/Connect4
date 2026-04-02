# Connect4
Your favourite connect4 is HERE!!!

# Connect 4 Game

A fully featured Connect 4 implementation in Python with Pygame, featuring both local multiplayer and AI opponent modes.

## Features

- **Two Game Modes:**
  - **2-Player Mode**: Play against another human on the same computer
  - **Vs AI Mode**: Challenge the computer opponent (play as Red or Yellow)

- **Intelligent AI Opponent:**
  - Uses the **Minimax algorithm** with alpha-beta pruning for optimal decision-making
  - Evaluates board positions based on strategic patterns (center control, sequences, blocking)
  - Configurable difficulty (depth-4 search by default)

- **Smooth Animations:**
  - Animated piece drops with realistic gravity
  - Winning line highlighting with visual feedback

- **Intuitive UI:**
  - Interactive menu with hover effects
  - Real-time turn indicators
  - Restart button and keyboard shortcuts (R to restart, ESC to return to menu)

## Requirements (for source code-see below, if you don't have these, you can play on itchio, otherwise install the .exe for Windows--windows only!)

- Python 3.x
- Pygame

## Installation

1. Install Pygame:
   ```bash
   pip install pygame
   ```

2. Run the game:
   ```bash
   python Connect4.py
   ```

## How to Play

1. **Select Game Mode** from the menu:
   - Click "2-Player" for local multiplayer
   - Click "Vs AI (Red)" to play as Yellow (second player)
   - Click "Vs AI (Yellow)" to play as Red (first player)

2. **Making Moves:**
   - Click on any column to drop your piece
   - Pieces animate downward to the lowest available position
   - A preview circle shows where your piece will land

3. **Winning:**
   - Get 4 of your pieces in a row (horizontal, vertical, or diagonal)
   - A white line highlights your winning sequence
   - Press R to restart or ESC to return to the menu

## Game Design

### Board Layout
- **6 rows × 7 columns** (standard Connect 4 dimensions)
- Red pieces are Player 1 (always goes first)
- Yellow pieces are Player 2

### AI Strategy
The AI uses **Minimax with Alpha-Beta Pruning** to evaluate moves:
- Searches 4 moves ahead (adjustable via `depth` parameter)
- Scores positions based on:
  - Center column control (highest value)
  - Potential winning sequences (3-in-a-row)
  - Blocking opponent threats
  - Board control opportunities

### Drawing Functions
- `draw_board()`: Renders the 6×7 grid with pieces
- `draw_menu()`: Interactive main menu with hover effects
- `draw_text()`: Turn indicators and game status
- `draw_winning_line()`: Highlights winning positions
- `draw_hover()`: Preview circle for valid moves

## Controls

| Key | Action |
|-----|--------|
| **Mouse Click** | Place piece or select menu option |
| **R** | Restart game |
| **ESC** | Return to menu |

## Code Structure

- **Board Logic**: Piece placement, win detection, and draw checking
- **AI Engine**: Minimax algorithm with position evaluation
- **Game State**: Menu system, turn management, and game flow
- **Rendering**: Pygame-based graphics and UI
- **Event Handling**: Mouse and keyboard input processing


## Notes

- The AI opponent can be challenging due to alpha-beta pruning optimization
- Close the window or press ESC from the menu to exit
- Works on Windows, macOS, and Linux

Enjoy the game! 🎮
