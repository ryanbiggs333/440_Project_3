
# from play_connect_four import *
from math import inf as INF

import numpy as np
import pygame
import sys

ROWS = 6
COLS = 7


BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

pygame.init()
SQUARESIZE = 100
CIRCLE_RADIUS = int(SQUARESIZE/2 - 5)
width = COLS * SQUARESIZE
height = (ROWS + 1) * SQUARESIZE
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()


board = np.zeros((ROWS, COLS))


def draw_board(board):
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r *
                             SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            if board[r][c] == 0:
                pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE/2), int(
                    r * SQUARESIZE + SQUARESIZE + SQUARESIZE/2)), CIRCLE_RADIUS)
            elif board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE/2), int(
                    r * SQUARESIZE + SQUARESIZE + SQUARESIZE/2)), CIRCLE_RADIUS)
            else:
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE/2), int(
                    r * SQUARESIZE + SQUARESIZE + SQUARESIZE/2)), CIRCLE_RADIUS)

    pygame.display.update()


def drop_piece(board, col, piece):
    for r in range(ROWS-1, -1, -1):
        if (board[r][col] == 0):
            board[r][col] = piece
            return True
    return False


# TODO: change this so it only checks the last move made
def winning_move(board, player_piece):
    # Check horizontally
    for c in range(COLS-3):
        for r in range(ROWS):
            if board[r][c] == player_piece and board[r][c+1] == player_piece and board[r][c+2] == player_piece and board[r][c+3] == player_piece:
                return True

    # Check vertically
    for c in range(COLS):
        for r in range(ROWS-3):
            if board[r][c] == player_piece and board[r+1][c] == player_piece and board[r+2][c] == player_piece and board[r+3][c] == player_piece:
                return True

    # Check diagonally (positively sloped)
    for c in range(COLS-3):
        for r in range(ROWS-3):
            if board[r][c] == player_piece and board[r+1][c+1] == player_piece and board[r+2][c+2] == player_piece and board[r+3][c+3] == player_piece:
                return True

    # Check diagonally (negatively sloped)
    for c in range(COLS-3):
        for r in range(3, ROWS):
            if board[r][c] == player_piece and board[r-1][c+1] == player_piece and board[r-2][c+2] == player_piece and board[r-3][c+3] == player_piece:
                return True


PLAYER_PIECE = 1
AI_PIECE = 2
EMPTY = 0
WINDOW_LENGTH = 4


def get_valid_locations(board):
    valid_locations = []
    for col in range(COLS):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


def is_valid_location(board, col):
    return board[0][col] == 0


def is_terminal_node(board):
    return (winning_move(board, PLAYER_PIECE)
         or winning_move(board, AI_PIECE)
         or len(get_valid_locations(board)) == 0)


def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if (piece == AI_PIECE) else AI_PIECE
    for p in [piece, opp_piece]:
        multiplier = 1 if p == piece else -1
        #our current minimax function already checks this case
        # if window.count(piece) == 4:
        #     score += INF * multiplier
        if window.count(p) == 3 and window.count(EMPTY) == 1:
            score += 8 * multiplier
        elif window.count(p) == 2 and window.count(EMPTY) == 2:
            score += 2 * multiplier
        elif window.count(p) == 1 and window.count(EMPTY) == 3:
            score += 1 * multiplier
    return score


def heuristic(board, piece):
    score = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, COLS//2])]
    center_count = center_array.count(piece)
    score += center_count * 2
    opp_count = center_array.count(PLAYER_PIECE)
    score -= opp_count * 2

    # Score Horizontal
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLS-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(COLS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROWS-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)
            
    # Score positive sloped diagonal
    for r in range(ROWS-3, ROWS):
        for c in range(COLS-3):
            window = [int(board[r-i][c+i]) for i in range(WINDOW_LENGTH)]
            print("window",window)
            print("w score",evaluate_window(window, piece))
            score += evaluate_window(window, piece)
            
    for r in range(ROWS-3):
        for c in range(COLS-3):
            window = [int(board[r+i][c+i]) for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
    return score

# def heuristic(board, piece):
# 	score = 0

# 	for r in range(ROWS):
# 		for c in range(COLS-3):
# 			window = [board[r][c+i] for i in range(WINDOW_LENGTH)]
# 			score += evaluate_window(window, piece)
# 	return score


def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            # print(board)
            # print("depth: ", depth)
            if winning_move(board, AI_PIECE):
                return (None, INF)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -INF)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, heuristic(board, AI_PIECE))
    if maximizingPlayer:
        score = -INF
        column = valid_locations[0]
        for col in valid_locations:
            b_copy = board.copy()
            drop_piece(b_copy, col, AI_PIECE)
            _, new_score = minimax(b_copy, depth-1, alpha, beta, False)
            if new_score > score:
                score = new_score
                column = col
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        return column, score

    else:  # Minimizing player
        score = INF
        column = valid_locations[0]
        for col in valid_locations:
            b_copy = board.copy()
            drop_piece(b_copy, col, PLAYER_PIECE)
            _, new_score = minimax(b_copy, depth-1, alpha, beta, True)
            if new_score < score:
                score = new_score
                column = col
            beta = min(beta, score)
            if alpha >= beta:
                break
        return column, score


def play_game():
    myfont = pygame.font.SysFont("monospace", 75)
    draw_board(board)
    game_over = False
    turn = 0

    while not game_over:
        for event in pygame.event.get():
            player_piece = turn % 2 + 1
            if event.type == pygame.QUIT:
                sys.exit()
            if player_piece == 1:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    posx = event.pos[0]
                    col = int(posx // SQUARESIZE)
                    drop_piece(board, col, player_piece)
                    turn += 1
                    if winning_move(board, player_piece):
                        label = myfont.render("Player 1 wins!", 1, RED)
                        screen.blit(label, (40, 10))
                        game_over = True

            else:
                col, score = minimax(board, 5, -INF, INF, True)
                print("score: ", score)
                if (col == None):
                  print("No valid moves")
                drop_piece(board, col, player_piece)
                turn += 1
                if winning_move(board, player_piece):
                    label = myfont.render("Player 2 wins!", 1, YELLOW)                 
                    screen.blit(label, (40,10))
                    game_over = True
                            
            # if winning_move(board, player_piece):
            #     if player_piece == 1:
            #         label = myfont.render("Player 1 wins!", 1, RED)
            #     else:
            #         label = myfont.render("Player 2 wins!", 1, YELLOW)
            #         screen.blit(label, (40,10))
            #         game_over = True
            draw_board(board)

    #show the final board state before closing
    pygame.time.wait(3000)

play_game()
