import numpy as np
import time
import play_connect_four as Cfour

ROWS = 6
COLS = 7

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
    valid_moves = Cfour.get_valid_moves(board)
    is_terminal = Cfour.winning_move(board, 1) or Cfour.winning_move(board, 2) or len(valid_moves) == 0
    if depth == 0 or is_terminal:
        if is_terminal:
            if Cfour.winning_move(board, 2):
                return (None, float('inf'))
            elif Cfour.winning_move(board, 1):
                return (None, float('-inf'))
            else:
                return (None, 0)  # No moves left
        else:
            return (None, score_position(board, 2))

    if maximize:
        value = -np.inf
        best_col = np.random.choice(valid_moves)
        for col in valid_moves:
            row = Cfour.next_row(board, col)
            if row == -1: continue
            boardCopy = board.copy()
            Cfour.drop_piece(boardCopy, col, 2)
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
            row = Cfour.next_row(board, col)
            if row == -1: continue
            boardCopy = board.copy()
            Cfour.drop_piece(boardCopy, col, 1)
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

