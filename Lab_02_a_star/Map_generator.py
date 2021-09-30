import sys

import numpy as np
import pygame
from contracts import *
from Constants import *
import random


class Generator:
    def __init__(self):
        self.cols = 0
        self.rows = 0
        self.grid = np.NAN
        self.empty_position_count = 0

    def generate_maze(self, rows, cols):
        zero_counter = 0
        v = 0
        grid = np.full_like(np.zeros((rows, cols)), fill_value=BLOCKED, dtype=int)
        for i in range(rows):
            for j in range(cols):
                if i % 2 == 1 and j % 2 == 1:
                    grid[i, j] = PASSAGE
                    zero_counter += 1
        self.cols = cols
        self.rows = rows
        self.grid = grid
        self.empty_position_count = zero_counter
        current_cell = (1, 1)
        stack = []
        visited = [current_cell]
        while v < zero_counter - 1:
            all_neighbors = self.get_neighbors_of_cell(current_cell, PASSAGE)
            neighbors = []
            for n in all_neighbors:
                if n not in visited:
                    neighbors.append(n)
            next_cell = []
            if neighbors:
                next_cell = random.choice(neighbors)
            if next_cell:
                visited.append(next_cell)
                stack.append(current_cell)
                self.connect_cell(current_cell, next_cell)
                current_cell = next_cell
                self.grid[current_cell] = PASSAGE
                v += 1
            elif stack:
                current_cell = stack.pop()

    def fill_grid_with_game_objects(self):
        empty_positions_amount = self.empty_position_count
        ice_block_amount = empty_positions_amount // 10
        swamp_block_amount = empty_positions_amount // 8
        water_block_amount = empty_positions_amount // 8
        coins_amount = empty_positions_amount // 30
        empty_positions = self.get_empty_blocks_positions()
        for _ in range(ice_block_amount):
            position = random.choice(empty_positions)
            self.grid[position] = ICE
        for _ in range(swamp_block_amount):
            position = random.choice(empty_positions)
            self.grid[position] = SWAMP
        for _ in range(water_block_amount):
            position = random.choice(empty_positions)
            self.grid[position] = WATER
        for _ in range(coins_amount):
            position = random.choice(empty_positions)
            self.grid[position] = COIN

    def make_more_ways(self):
        height = self.grid.shape[0]
        width = self.grid.shape[1]
        additional_ways = (height + width) // 2
        good_walls = []
        for i in range(1, height-1):
            for j in range(1, width-1):
                if (self.grid[i, j] == WALL and self.grid[i - 1, j] != WALL and self.grid[i + 1, j] != WALL) \
                        or (self.grid[i, j] == WALL and self.grid[i, j - 1] != WALL and self.grid[i, j + 1] != WALL):
                    good_walls.append((i, j))
        for _ in range(additional_ways):
            position = random.choice(good_walls)
            self.grid[position] = PASSAGE

    def create_labyrinth(self, rows, cols):
        self.generate_maze(rows, cols)
        self.make_more_ways()
        self.fill_grid_with_game_objects()
        return self.grid

    def get_empty_blocks_positions(self):
        height = self.grid.shape[0]
        width = self.grid.shape[1]
        empty_blocks_positions = []
        for i in range(height):
            for j in range(width):
                if self.grid[i, j] == PASSAGE:
                    empty_blocks_positions.append((i, j))
        return empty_blocks_positions

    def connect_cell(self, first_cell, second_cell):
        if first_cell[0] == second_cell[0]:
            new_passage_cell = (first_cell[0], (first_cell[1] + second_cell[1]) // 2)
            self.grid[new_passage_cell] = PASSAGE
        elif first_cell[1] == second_cell[1]:
            new_passage_cell = ((first_cell[0] + second_cell[0]) // 2, first_cell[1])
            self.grid[new_passage_cell] = PASSAGE

    def is_border_wall(self, cell):
        if cell[0] == 0 \
                or cell[0] == self.rows - 1 \
                or cell[1] == 0 \
                or cell[1] == self.cols - 1:
            return True
        return False

    def get_neighbors_of_cell(self, cell, status):
        neighbors = []
        cells = [(cell[0] - 2, cell[1]),
                 (cell[0] + 2, cell[1]),
                 (cell[0], cell[1] - 2),
                 (cell[0], cell[1] + 2)]
        for cell in cells:
            if self.is_valid_cell(cell) and self.grid[cell] == status:
                neighbors.append(cell)
        return neighbors

    def is_valid_cell(self, cell):
        if cell[0] < 0 \
                or cell[0] >= self.rows \
                or cell[1] < 0 \
                or cell[1] >= self.cols:
            return False
        return True