import pygame
import sys
import math

# Constants
ROWS = 6
COLS = 7
SQUARE_SIZE = 100
RADIUS = SQUARE_SIZE//2 - 5
BOARD_WIDTH = COLS * SQUARE_SIZE
BOARD_HEIGHT = ROWS * SQUARE_SIZE
TOP_OFFSET = 100
SCREEN_WIDTH = BOARD_WIDTH
SCREEN_HEIGHT = BOARD_HEIGHT + TOP_OFFSET

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

PLAYER_1 = 1
PLAYER_2 = 2
EMPTY = 0
HUMAN = 0
AI = 1

DROP_SPEED = 15
MENU, TWOPLAYER, VSAI = 0, 1, 2

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Connect 4")
font = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()

# Globals
board = None
turn = PLAYER_1
game_over = False
winner = None
moving_piece = None
winning_positions = None
restart_button_rect = None
game_state = MENU
game_mode = TWOPLAYER
human_side = None
ai_side = None
ai_should_move = False

# -------------------------------------------------------------------
# Board logic
# -------------------------------------------------------------------
def create_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def drop_piece(board, row, col, player):
    board[row][col] = player

def is_valid_location(board, col):
    return board[0][col] == EMPTY

def get_next_open_row(board, col):
    for r in range(ROWS-1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return None

def winning_move(board, row, col, player):
    # Horizontal
    for c in range(COLS - 3):
        if all(board[row][c+i] == player for i in range(4)):
            return [(row, c+i) for i in range(4)]
    # Vertical
    for r in range(ROWS - 3):
        if all(board[r+i][col] == player for i in range(4)):
            return [(r+i, col) for i in range(4)]
    # Diagonal (top-left to bottom-right)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r+i][c+i] == player for i in range(4)):
                return [(r+i, c+i) for i in range(4)]
    # Diagonal (top-right to bottom-left)
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            if all(board[r+i][c-i] == player for i in range(4)):
                return [(r+i, c-i) for i in range(4)]
    return None

def is_draw(board):
    return all(board[0][c] != EMPTY for c in range(COLS))

def any_winning_move(board):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != EMPTY:
                if winning_move(board, r, c, board[r][c]):
                    return True
    return False

# -------------------------------------------------------------------
# AI evaluation and minimax
# -------------------------------------------------------------------
def evaluate_window(window, player):
    score = 0
    opponent = PLAYER_2 if player == PLAYER_1 else PLAYER_1
    if window.count(player) == 4:
        score += 100
    elif window.count(player) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(player) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opponent) == 3 and window.count(EMPTY) == 1:
        score -= 4
    return score

def score_position(board, player):
    score = 0
    # Center column
    center_col = COLS // 2
    center_array = [board[r][center_col] for r in range(ROWS)]
    score += center_array.count(player) * 3

    # Horizontal
    for r in range(ROWS):
        row_array = [board[r][c] for c in range(COLS)]
        for c in range(COLS - 3):
            window = row_array[c:c+4]
            score += evaluate_window(window, player)

    # Vertical
    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS - 3):
            window = col_array[r:r+4]
            score += evaluate_window(window, player)

    # Diagonal positive slope
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, player)

    # Diagonal negative slope
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            window = [board[r+i][c-i] for i in range(4)]
            score += evaluate_window(window, player)

    return score

def is_terminal_node(board):
    return any_winning_move(board) or is_draw(board)

def minimax(board, depth, alpha, beta, maximizingPlayer, player):
    valid_locations = [c for c in range(COLS) if is_valid_location(board, c)]
    if depth == 0 or is_terminal_node(board):
        if is_terminal_node(board):
            # Win/loss: return large positive for player win, negative for opponent win
            if any_winning_move(board):
                # Find who won
                for r in range(ROWS):
                    for c in range(COLS):
                        if board[r][c] != EMPTY and winning_move(board, r, c, board[r][c]):
                            if board[r][c] == player:
                                return (None, 10000)
                            else:
                                return (None, -10000)
                return (None, 0)  # draw
            else:
                return (None, 0)  # draw
        else:
            return (None, score_position(board, player))

    if maximizingPlayer:
        value = -math.inf
        best_col = valid_locations[0] if valid_locations else None
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = [row[:] for row in board]
            drop_piece(temp_board, row, col, player)
            new_score = minimax(temp_board, depth-1, alpha, beta, False, player)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
    else:
        value = math.inf
        best_col = valid_locations[0] if valid_locations else None
        opponent = PLAYER_2 if player == PLAYER_1 else PLAYER_1
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = [row[:] for row in board]
            drop_piece(temp_board, row, col, opponent)
            new_score = minimax(temp_board, depth-1, alpha, beta, True, player)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

def ai_move(board, player):
    valid_moves = [c for c in range(COLS) if is_valid_location(board, c)]
    if not valid_moves:
        return None
    depth = 4  # you can adjust for difficulty
    col, _ = minimax(board, depth, -math.inf, math.inf, True, player)
    return col

# -------------------------------------------------------------------
# Drawing functions
# -------------------------------------------------------------------
def draw_hover(board, turn, moving_piece):
    if moving_piece is not None:
        return
    x, y = pygame.mouse.get_pos()
    if y > TOP_OFFSET:
        col = x // SQUARE_SIZE
        if 0 <= col < COLS and is_valid_location(board, col):
            row = get_next_open_row(board, col)
            if row is not None:
                center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = TOP_OFFSET + row * SQUARE_SIZE + SQUARE_SIZE // 2
                color = RED if turn == PLAYER_1 else YELLOW
                pygame.draw.circle(screen, color, (center_x, center_y), RADIUS, 4)

def draw_board(board, moving_piece=None):
    screen.fill(BLACK)
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * SQUARE_SIZE, TOP_OFFSET + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, BLUE, rect, 3)
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = TOP_OFFSET + row * SQUARE_SIZE + SQUARE_SIZE // 2
            if board[row][col] == PLAYER_1:
                color = RED
            elif board[row][col] == PLAYER_2:
                color = YELLOW
            else:
                color = GRAY
            pygame.draw.circle(screen, color, (center_x, center_y), RADIUS)
            pygame.draw.circle(screen, BLACK, (center_x, center_y), RADIUS, 2)
    if moving_piece:
        col = moving_piece['col']
        player = moving_piece['player']
        y = moving_piece['y']
        center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
        color = RED if player == PLAYER_1 else YELLOW
        pygame.draw.circle(screen, color, (center_x, y), RADIUS)
        pygame.draw.circle(screen, BLACK, (center_x, y), RADIUS, 2)

def draw_text(turn, game_over, winner):
    if game_over:
        if winner == PLAYER_1:
            msg = "Red wins! Press R to restart"
        elif winner == PLAYER_2:
            msg = "Yellow wins! Press R to restart"
        else:
            msg = "It's a draw! Press R to restart"
        text = font.render(msg, True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, TOP_OFFSET // 2))
        screen.blit(text, text_rect)
    else:
        turn_text = "Red's turn" if turn == PLAYER_1 else "Yellow's turn"
        text = font.render(turn_text, True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, TOP_OFFSET // 2))
        screen.blit(text, text_rect)
    restart_text = small_font.render("Press R to restart", True, WHITE)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, TOP_OFFSET - 20))
    screen.blit(restart_text, restart_rect)

def draw_restart_button():
    button_rect = pygame.Rect(SCREEN_WIDTH - 120, 10, 100, 40)
    pygame.draw.rect(screen, GRAY, button_rect)
    pygame.draw.rect(screen, BLACK, button_rect, 2)
    text = small_font.render("Restart", True, WHITE)
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)
    return button_rect

def draw_winning_line(winning_positions):
    if not winning_positions:
        return
    first = winning_positions[0]
    last = winning_positions[-1]
    center1 = (first[1] * SQUARE_SIZE + SQUARE_SIZE // 2,
               TOP_OFFSET + first[0] * SQUARE_SIZE + SQUARE_SIZE // 2)
    center2 = (last[1] * SQUARE_SIZE + SQUARE_SIZE // 2,
               TOP_OFFSET + last[0] * SQUARE_SIZE + SQUARE_SIZE // 2)
    pygame.draw.line(screen, WHITE, center1, center2, 8)

def draw_menu():
    screen.fill((20, 20, 40))  # dark background

    # Title
    title = font.render("CONNECT 4", True, WHITE)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
    screen.blit(title, title_rect)

    # Button definitions (rectangles and text)
    buttons = []
    y_start = 280
    button_height = 60
    button_width = 280
    spacing = 20

    # 2-Player button
    btn_2p = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, y_start, button_width, button_height)
    buttons.append((btn_2p, "2-Player", TWOPLAYER))

    # Vs AI (Red) button
    btn_ai_red = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, y_start + button_height + spacing, button_width, button_height)
    buttons.append((btn_ai_red, "Vs AI (Red)", VSAI, PLAYER_1))  # human plays Red (first)

    # Vs AI (Yellow) button
    btn_ai_yellow = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, y_start + 2*(button_height + spacing), button_width, button_height)
    buttons.append((btn_ai_yellow, "Vs AI (Yellow)", VSAI, PLAYER_2))  # human plays Yellow (second)

    mouse_x, mouse_y = pygame.mouse.get_pos()

    for btn in buttons:
        # Determine hover color
        if btn[0].collidepoint(mouse_x, mouse_y):
            color = (120, 120, 180)
        else:
            color = (70, 70, 110)

        pygame.draw.rect(screen, color, btn[0], border_radius=10)
        pygame.draw.rect(screen, WHITE, btn[0], 2, border_radius=10)

        # Render text
        text = small_font.render(btn[1], True, WHITE)
        text_rect = text.get_rect(center=btn[0].center)
        screen.blit(text, text_rect)

    return buttons   # return list of (rect, game_mode, side) for handling clicks

# -------------------------------------------------------------------
# Game reset
# -------------------------------------------------------------------
def reset_game():
    global board, turn, game_over, winner, moving_piece, winning_positions, ai_should_move
    board = create_board()
    turn = PLAYER_1
    game_over = False
    winner = None
    moving_piece = None
    winning_positions = None
    ai_should_move = False

    # If in AI mode and AI is red (starts), trigger AI move
    if game_mode == VSAI and ai_side == PLAYER_1:
        ai_should_move = True

def start_ai_move():
    global moving_piece, ai_should_move, turn
    if moving_piece is not None or game_over:
        ai_should_move = False
        return
    # Determine which player is AI
    ai_player = PLAYER_1 if ai_side == PLAYER_1 else PLAYER_2
    # Only if it's AI's turn
    if turn != ai_player:
        ai_should_move = False
        return
    # Get AI move
    col = ai_move(board, ai_player)
    if col is not None:
        row = get_next_open_row(board, col)
        if row is not None:
            target_y = TOP_OFFSET + row * SQUARE_SIZE + SQUARE_SIZE // 2
            moving_piece = {
                'col': col,
                'row': row,
                'y': TOP_OFFSET - RADIUS,
                'target_y': target_y,
                'player': ai_player
            }
    ai_should_move = False

# -------------------------------------------------------------------
# Main loop
# -------------------------------------------------------------------
def main():
    global board, turn, game_over, winner, moving_piece, winning_positions, restart_button_rect, game_state, game_mode, human_side, ai_side, ai_should_move

    reset_game()
    game_state = MENU

    while True:
        if game_state == MENU:
            buttons = draw_menu()
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in buttons:
                        if btn[0].collidepoint(event.pos):
                            game_mode = btn[2]
                            if game_mode == VSAI:
                                human_side = btn[3]          # PLAYER_1 or PLAYER_2
                                ai_side = PLAYER_2 if human_side == PLAYER_1 else PLAYER_1
                            else:
                                human_side = None
                            game_state = TWOPLAYER
                            reset_game()
                            # If AI starts (AI is red), the flag is already set in reset_game
                            break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            clock.tick(30)
            continue

        # ---- Game loop (TWOPLAYER or VSAI) ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    reset_game()
                    continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button_rect and restart_button_rect.collidepoint(event.pos):
                    reset_game()
                elif not game_over and moving_piece is None:
                    # Only allow human to move if it's human's turn
                    if game_mode == VSAI:
                        # In AI mode, human can only move if turn == human_side
                        if turn != human_side:
                            continue
                    x, y = pygame.mouse.get_pos()
                    if y > TOP_OFFSET:
                        col = x // SQUARE_SIZE
                        if 0 <= col < COLS and is_valid_location(board, col):
                            row = get_next_open_row(board, col)
                            if row is not None:
                                target_y = TOP_OFFSET + row * SQUARE_SIZE + SQUARE_SIZE // 2
                                moving_piece = {
                                    'col': col,
                                    'row': row,
                                    'y': TOP_OFFSET - RADIUS,
                                    'target_y': target_y,
                                    'player': turn
                                }

        # Update moving piece animation
        if moving_piece is not None:
            moving_piece['y'] += DROP_SPEED
            if moving_piece['y'] >= moving_piece['target_y']:
                moving_piece['y'] = moving_piece['target_y']
                col = moving_piece['col']
                row = moving_piece['row']
                player = moving_piece['player']
                drop_piece(board, row, col, player)
                winning_line = winning_move(board, row, col, player)
                if winning_line:
                    game_over = True
                    winner = player
                    winning_positions = winning_line
                elif is_draw(board):
                    game_over = True
                    winner = None
                else:
                    turn = PLAYER_2 if turn == PLAYER_1 else PLAYER_1
                moving_piece = None

                # After move, if vs AI and it's AI's turn and game not over, trigger AI move
                if not game_over and game_mode == VSAI and turn == ai_side:
                    ai_should_move = True

        # AI move trigger
        if ai_should_move and moving_piece is None and not game_over:
            start_ai_move()

        # Draw everything
        draw_board(board, moving_piece)
        draw_text(turn, game_over, winner)
        draw_hover(board, turn, moving_piece)
        restart_button_rect = draw_restart_button()
        draw_winning_line(winning_positions)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()