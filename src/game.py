import os
import random
import sys
import time

import pygame
from pygame.locals import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def get_sprite(path, x, y, width, height):
    return pygame.transform.rotozoom(pygame.image.load(path).subsurface((x, y, width, height)), 0, 2)

MINE = -1
UNREVEALED_TILE = -2
FLAG = -3
FALSE_MINE = -4
PASSIVE_MINE = -5

spritesheet = os.path.join(os.path.dirname(__file__), "assets", "sprites.png")

sprites = {
    MINE: get_sprite(spritesheet, 32, 39, 16, 16),
    UNREVEALED_TILE: get_sprite(spritesheet, 0, 39, 16, 16),
    FLAG: get_sprite(spritesheet, 16, 39, 16, 16),
    FALSE_MINE: get_sprite(spritesheet, 48, 39, 16, 16),
    PASSIVE_MINE: get_sprite(spritesheet, 64, 39, 16, 16)
}

revealed_tiles = {
    0: get_sprite(spritesheet, 0, 23, 16, 16),
    1: get_sprite(spritesheet, 16, 23, 16, 16),
    2: get_sprite(spritesheet, 32, 23, 16, 16),
    3: get_sprite(spritesheet, 48, 23, 16, 16),
    4: get_sprite(spritesheet, 64, 23, 16, 16),
    5: get_sprite(spritesheet, 80, 23, 16, 16),
    6: get_sprite(spritesheet, 96, 23, 16, 16),
    7: get_sprite(spritesheet, 112, 23, 16, 16),
    8: get_sprite(spritesheet, 128, 23, 16, 16)
}

LEFT_CLICK = 1
RIGHT_CLICK = 3

class Game:
    def __init__(self, num_rows, num_columns, num_mines):
        assert num_rows > 1 and num_columns > 1
        assert num_mines > 0 and num_mines < num_rows * num_columns - 1
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.num_mines = num_mines
        self.width = num_rows * 32
        self.height = num_columns * 32
        self.running = False
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Minesweeper')

    def cleanup(self):
        for i in range(self.num_rows):
            for j in range(self.num_columns):
                if self.displayed_board[i][j] == MINE:
                    pass
                elif self.board[i][j] == MINE:
                    if self.displayed_board[i][j] == UNREVEALED_TILE:
                        self.displayed_board[i][j] = PASSIVE_MINE
                elif self.displayed_board[i][j] == FLAG:
                    self.displayed_board[i][j] = FALSE_MINE

    def run(self):
        self.reset()
        self.running = True
        clock = pygame.time.Clock()
        first_time = True
        while True:
            self.screen.fill(BLACK)
            for i in range(self.num_rows):
                for j in range(self.num_columns):
                    if self.displayed_board[i][j] < 0:
                        self.screen.blit(sprites[self.displayed_board[i][j]], (i * 32, j * 32))
                    else:
                        self.screen.blit(revealed_tiles[self.board[i][j]], (i * 32, j * 32))
            if self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONUP:
                        x, y = pygame.mouse.get_pos()
                        index_x = x // 32
                        index_y = y // 32
                        if event.button == LEFT_CLICK:
                            if self.displayed_board[index_x][index_y] != UNREVEALED_TILE:
                                continue
                            if self.board[index_x][index_y] == 0:
                                first_time = False
                                self._explore_zero(index_x, index_y)
                                continue
                            if self.board[index_x][index_y] == MINE and first_time:
                                first_time = False
                                while self.board[index_x][index_y] == MINE:
                                    self.reset()
                                if self.board[index_x][index_y] == 0:
                                    self._explore_zero(index_x, index_y)
                                    continue
                            elif self.board[index_x][index_y] == MINE:
                                self.displayed_board[index_x][index_y] = MINE
                                self.cleanup()
                                self.running = False
                                break
                            first_time = False
                            self.displayed_board[index_x][index_y] = self.board[index_x][index_y]
                            self.tiles_left -= 1
                        elif event.button == RIGHT_CLICK:
                            if self.displayed_board[index_x][index_y] == FLAG:
                                self.displayed_board[index_x][index_y] = UNREVEALED_TILE
                            elif self.displayed_board[index_x][index_y] == UNREVEALED_TILE:
                                self.displayed_board[index_x][index_y] = FLAG
                if self.tiles_left == self.num_mines and self.running:
                    self.cleanup()
                    self.running = False
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
            pygame.display.update()
            clock.tick(60)

    def _explore_zero(self, x, y):
        if self.board[x][y] == MINE or self.board[x][y] == FLAG:
            return
        self.tiles_left -= 1
        if self.board[x][y] != 0:
            self.displayed_board[x][y] = self.board[x][y]
            return
        self.displayed_board[x][y] = 0
        if x != 0 and self.displayed_board[x - 1][y] == UNREVEALED_TILE:
            self._explore_zero(x - 1, y)
        if x != self.num_rows - 1 and self.displayed_board[x + 1][y] == UNREVEALED_TILE:
            self._explore_zero(x + 1, y)
        if y != 0 and self.displayed_board[x][y - 1] == UNREVEALED_TILE:
            self._explore_zero(x, y - 1)
        if y != self.num_columns - 1 and self.displayed_board[x][y + 1] == UNREVEALED_TILE:
            self._explore_zero(x, y + 1)
        if x != 0 and y != 0 and self.displayed_board[x - 1][y - 1] == UNREVEALED_TILE:
            self._explore_zero(x - 1, y - 1)
        if x != 0 and y != self.num_columns - 1 and self.displayed_board[x - 1][y + 1] == UNREVEALED_TILE:
            self._explore_zero(x - 1, y + 1)
        if x != self.num_rows - 1 and y != 0 and self.displayed_board[x + 1][y - 1] == UNREVEALED_TILE:
            self._explore_zero(x + 1, y - 1)
        if x != self.num_rows - 1 and y != self.num_columns - 1 and self.displayed_board[x + 1][y + 1] == UNREVEALED_TILE:
            self._explore_zero(x + 1, y + 1)

    def _display_board(self):
        for i in range(self.num_columns):
            print(' '.join(map(str, [self.board[j][i] for j in range(self.num_rows)])))

    def reset(self):
        indices = [(i, j) for j in range(self.num_columns) for i in range(self.num_rows)]
        mine_indices = set()
        board = [[0] * self.num_columns for i in range(self.num_rows)]
        for i in range(self.num_mines):
            random_index = random.randint(0, len(indices) - 1)
            x, y = indices[random_index]
            indices.remove(indices[random_index])
            mine_indices.add((x, y))
            board[x][y] = MINE
        for x, y in mine_indices:
            if x > 0 and board[x - 1][y] != -1:
                board[x - 1][y] += 1
            if x > 0 and y > 0 and board[x - 1][y - 1] != -1:
                board[x - 1][y - 1] += 1
            if x > 0 and y < self.num_columns - 1 and board[x - 1][y + 1] != -1:
                board[x - 1][y + 1] += 1
            if y < self.num_columns - 1 and board[x][y + 1] != -1:
                board[x][y + 1] += 1
            if y > 0 and board[x][y - 1] != -1:
                board[x][y - 1] += 1
            if x < self.num_rows - 1 and board[x + 1][y] != -1:
                board[x + 1][y] += 1
            if x < self.num_rows - 1 and y < self.num_columns - 1 and board[x + 1][y + 1] != -1:
                board[x + 1][y + 1] += 1
            if x < self.num_rows - 1 and y > 0 and board[x + 1][y - 1] != -1:
                board[x + 1][y - 1] += 1
        self.board = board
        self.displayed_board = [[UNREVEALED_TILE] * self.num_columns for i in range(self.num_rows)]
        self.mine_indices = mine_indices
        self.tiles_left = self.num_rows * self.num_columns

if __name__ == '__main__':
    Game(30, 16, 80).run()
