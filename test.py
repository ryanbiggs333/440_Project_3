import numpy as np
import pygame
import sys
import time


ROWS = 6
COLS = 7
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

SQUARESIZE = 100
CIRCLE_RADIUS = int(SQUARESIZE / 2 - 5)

width = COLS * SQUARESIZE
height = (ROWS + 1) * SQUARESIZE

pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
board = np.zeros((ROWS, COLS))



def drop_piece(board, row, col, piece):
    board[row][col] = piece


def get_valid_moves(board):
    return [col for col in range(COLS) if board[0][col] == 0]


def next_row(board, col):
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == 0:
            return r
    return -1


def winning_move(board, piece):
    # horizontal
    for c in range(COLS - 3):
        for r in range(ROWS):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][
                c + 3] == piece:
                return True
    # vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][
                c] == piece:
                return True
    # diagonals
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][
                c + 3] == piece:
                return True
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][
                c + 3] == piece:
                return True
    return False


def score_position(board, piece):
    score = 0
    center_array = [int(i) for i in list(board[:, COLS // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3 #center

    #Scoring
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLS - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    for c in range(COLS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROWS - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)

    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + 3 - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)
    return score


def evaluate_window(window, piece):
    score = 0
    opp_piece = 1 if piece == 2 else 2
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4  # block if possible
    return score


def aplphaBeta(board, depth, alpha, beta, maximize):
    valid_moves = get_valid_moves(board)
    is_terminal = winning_move(board, 1) or winning_move(board, 2) or len(valid_moves) == 0
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, 2):
                return (None, float('inf'))
            elif winning_move(board, 1):
                return (None, float('-inf'))
            else:
                return (None, 0)  # No moves left
        else:
            return (None, score_position(board, 2))

    if maximize:
        value = -np.inf
        best_col = np.random.choice(valid_moves)
        for col in valid_moves:
            row = next_row(board, col)
            if row == -1: continue
            boardCopy = board.copy()
            drop_piece(boardCopy, row, col, 2)
            _, newScore = aplphaBeta(boardCopy, depth - 1, alpha, beta, False)
            if newScore > value:
                value = newScore
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
    else:
        value = np.inf
        best_col = np.random.choice(valid_moves)
        for col in valid_moves:
            row = next_row(board, col)
            if row == -1: continue
            boardCopy = board.copy()
            drop_piece(boardCopy, row, col, 1)
            _, newScore = aplphaBeta(boardCopy, depth - 1, alpha, beta, True)
            if newScore < value:
                value = newScore
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value


def iterative_deepening(board, max_depth, time_limit, maximize):
    start_time = time.time()
    best_move = None
    alpha, beta = -np.inf, np.inf
    for depth in range(1, max_depth + 1):
        if time.time() - start_time > time_limit:
            break
        best_move, _ = aplphaBeta(board, depth, alpha, beta, maximize)
    return best_move


def draw_board(board):
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            color = BLACK if board[r][c] == 0 else (RED if board[r][c] == 1 else YELLOW)
            pygame.draw.circle(screen, color, (int(c * SQUARESIZE + SQUARESIZE / 2),
                                               int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), CIRCLE_RADIUS)
    pygame.display.update()


# Game loop
draw_board(board)
game_over = False
turn = 0

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            posx = event.pos[0]
            col = int(posx // SQUARESIZE)
            if col in get_valid_moves(board):
                row = next_row(board, col)
                drop_piece(board, row, col, (turn % 2) + 1)
                if winning_move(board, (turn % 2) + 1):
                    print(f"Player {turn % 2 + 1} wins!")
                    game_over = True
                turn += 1
                draw_board(board)

        # alpha beta turn
        if not game_over and turn % 2 == 1:
            col = iterative_deepening(board, max_depth=4, time_limit=2, maximize=True)
            if col in get_valid_moves(board):
                row = next_row(board, col)
                drop_piece(board, row, col, 2)
                if winning_move(board, 2):
                    print("AI wins!")
                    game_over = True
                turn += 1
                draw_board(board)

