from operator import truediv

import numpy as np
import pygame
import sys
import Connect_4_AB as ab
import importlib
importlib.reload(ab)


ROWS = 6
COLS = 7


BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

MAX_DEPTH = 4
MAX_TIME = 2
MAXIMIZE = 1

pygame.init()   
SQUARESIZE = 100
CIRCLE_RADIUS = int(SQUARESIZE/2 - 5)
width = COLS * SQUARESIZE
height = (ROWS + 1) * SQUARESIZE
screen = pygame.display.set_mode((width,height))
clock = pygame.time.Clock()



board = np.zeros((ROWS,COLS))



        
def draw_board(board):
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE ))
            if board[r][c] == 0:
                pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE/2), int(r* SQUARESIZE + SQUARESIZE + SQUARESIZE/2)), CIRCLE_RADIUS)
            elif board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE/2), int(r* SQUARESIZE + SQUARESIZE + SQUARESIZE/2)), CIRCLE_RADIUS)
            else :
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE/2), int(r* SQUARESIZE + SQUARESIZE + SQUARESIZE/2)), CIRCLE_RADIUS)

    pygame.display.update()

def drop_piece(board,col, piece):
    for r in range(ROWS-1, -1, -1):
        if board[r][col] == 0:
            board[r][col] = piece
            return True
    return False

def winning_move(board, player_piece): #TODO: change this so it only checks the last move made
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

def get_valid_moves(board):
    return [col for col in range(COLS) if board[0][col] == 0]

def next_row(board, col):
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == 0:
            return r
    return -1

def play_game():
    myfont = pygame.font.SysFont("monospace", 75)
    draw_board(board)
    game_over = False
    turn = 0

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            player_piece = turn % 2 + 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                posx = event.pos[0]
                col = int(posx // SQUARESIZE)
                if col in get_valid_moves(board):
                    drop_piece(board, col, player_piece)
                    turn += 1
                    if winning_move(board, player_piece):
                        if player_piece == 1:
                            label = myfont.render("Player 1 wins!", 1, RED)
                        else:
                            label = myfont.render("Player 2 wins!", 1, YELLOW)
                            screen.blit(label, (40,10))
                            game_over = True
                    draw_board(board)

            #AI
            if not game_over and turn % 2 == 1:
                col = ab.iterative_deepening(board, MAX_DEPTH, MAX_TIME, MAXIMIZE)
                #print(dir(ab))
                turn += 1
                if col in get_valid_moves(board):
                    drop_piece(board, col, 2)
                    if winning_move(board, 2):
                        print("Player 2 wins!")
                        game_over = True
                        turn += 1
                    draw_board(board)



    #show the final board state before closing
    pygame.time.wait(3000)

play_game()