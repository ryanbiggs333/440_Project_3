import numpy as np
import pygame
import sys

ROWS = 6
COLS = 7

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

SQUARESIZE = 100
CIRCLE_RADIUS = int(SQUARESIZE/2 - 5)

width = COLS * SQUARESIZE
height = (ROWS + 1) * SQUARESIZE


pygame.init()

board = np.zeros((ROWS,COLS))
screen = pygame.display.set_mode((width,height))
clock = pygame.time.Clock()


def drop_piece(board,col, piece):
    for r in range(ROWS-1, 0, -1):
        if board[r][col] == 0:
            board[r][col] = piece
            break

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

draw_board(board)
game_over = False
turn = 0

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    
        piece = turn % 2 + 1

        if event.type == pygame.MOUSEBUTTONDOWN:
            posx = event.pos[0]
            col = int(posx // SQUARESIZE)
            drop_piece(board, col, piece)
            turn += 1
            print(turn)
            draw_board(board)