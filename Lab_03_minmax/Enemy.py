import asyncio
import random
import time
import timeit
import numpy as np
import pygame
from Constants import *
from Search import *
vec = pygame.math.Vector2

import queue

class Enemy:

    def __init__(self, application, start_position, ghost_type):
        self.type = None
        self.application = application
        self.position = start_position
        self.pix_position = self.get_pix_pos()
        self.path = None
        self.grid_position = start_position
        self.direction = vec(0, 0)
        self.personality = ghost_type
        self.speed = 2

    def draw(self):

        pygame.draw.circle(self.application.screen, ICE_COLOR,
                           (self.pix_position.x, self.pix_position.y),
                           self.application.cell_width//2-2)

    def get_pix_pos(self):

        return vec((self.position[0]*self.application.cell_width) + PADDING // 2 + self.application.cell_width // 2,
                   (self.position[1]*self.application.cell_height) +
                   PADDING // 2 + self.application.cell_height // 2)

    def update(self):
        self.target = (int(self.application.player.grid_pos[1]), int(self.application.player.grid_pos[0]))
        if self.target != self.grid_position:
            self.pix_position += self.direction * self.speed
            if self.time_to_move():
                self.move()

        # Setting grid position in reference to pix position
        self.grid_position[0] = (self.pix_position[0]-PADDING +
                            self.application.cell_width//2)//self.application.cell_width+1
        self.grid_position[1] = (self.pix_position[1]-PADDING +
                            self.application.cell_height//2)//self.application.cell_height+1

    def time_to_move(self):
        if int(self.pix_position.x+PADDING//2) % self.application.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_position.y+PADDING//2) % self.application.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True
        return False

    def get_random_direction(self):
        while True:
            rand_int = random.randint(0, 3)
            random_direction = vec(0, 0)
            if rand_int == 0:
                random_direction = vec(-1, 0)
            elif rand_int == 1:
                random_direction = vec(1, 0)
            elif rand_int == 2:
                random_direction = vec(0, 1)
            elif rand_int == 3:
                random_direction = vec(0, -1)
            if vec(self.grid_position + random_direction) not in self.application.walls:
                return random_direction

    def get_a_star_direction(self):
        path = a_star(self.application.grid_map, (int(self.grid_position[1]), int(self.grid_position[0])),
                      (int(self.application.player.grid_pos[1]), int(self.application.player.grid_pos[0])),
                      euclid_heuristic, 0)
        next_step = (path[1][1], path[1][0])
        direction = vec(int(next_step[0] - self.grid_position[0]), int(next_step[1] - self.grid_position[1]))
        print(direction)
        return direction



    def move(self):
        if self.personality == RANDOM:
            self.direction = self.get_random_direction()
        elif self.personality == DEFAULT:
            self.direction = self.get_a_star_direction()


    def BFS(self, start, target):
        grid = self.load_grid()

        if not self.is_valid_target(target):
            print("your goal is wall")
            return [start]
        queue = [start]
        path = []
        visited = []
        directions = [[0, -1], [1, 0], [0, 1], [-1, 0]]

        while queue:
            current = queue[0]
            queue.remove(queue[0])
            visited.append(current)
            if current == target:
                break
            else:
                for direction in directions:
                    step = current + direction
                    if grid[int(step[1]), int(step[0])] != 1:
                        if step not in visited:
                            queue.append(step)
                            path.append({"Current": current, "Next": step})
        shortest = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    shortest.insert(0, step["Current"])

        return shortest

    def DFS(self, start, target):
        grid = self.load_grid()
        if not self.is_valid_target(target):
            print("your goal is wall")
            return [start]

        stack = [start]
        visited = []
        path = []
        directions = [[0, 1], [1, 0], [0, -1], [-1, 0]]
        while stack:
            possible_dirs = []
            for direction in directions:
                step = stack[-1] + direction
                if grid[int(step[1]), int(step[0])] != 1 and step not in visited:
                    possible_dirs.append(direction)

            if len(possible_dirs) == 0:
                stack.pop()
                path = stack

            for direction in possible_dirs:
                step2 = stack[-1] + direction
                stack.append(step2)
                visited.append(stack[-1])
                path.append(stack[-1])
                break

            if stack[-1] == target:
                return path[:-1]


    def UCS(self, start, target):
        grid = self.load_grid()
        if not self.is_valid_target(target):
            print("your goal is wall")
            return [start]
        graph = self.grid_to_graph(grid)
        visited = set()
        start = (int(start.y), int(start.x))
        target = (int(target.y), int(target.x))
        path = []
        q = queue.PriorityQueue()
        q.put((0, start))

        while not q.empty():
            cost, node = q.get()
            if node == target:
                path.append(node)
                return path

            for edge in graph[node]:
                if edge not in visited:
                    visited.add(edge)
                    next_node = edge[:2]
                    step_cost = edge[-1]
                    q.put((step_cost + cost, next_node))
            path.append(q.queue[0][1][::-1])


    def grid_to_graph(self, grid):
        rows, cols = grid.shape
        graph = {}
        for i in range(rows-1):
            cost = random.randint(1, 4)
            for j in range(cols-1):
                if grid[i, j] != 1:
                    adj = []
                    for ele in [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]:
                        if grid[ele[0], ele[1]] == 0:
                            adj.append((ele[0], ele[1], cost))
                    graph[(i, j)] = adj
        return graph

    def draw_path(self):
        for step in self.path[1:-1]:
            pygame.draw.rect(self.application.screen, BLUE, (step[1] * self.application.cell_width + PADDING // 2,
                                                             step[0] * self.application.cell_height + PADDING // 2,
                                                             self.application.cell_width - 5,
                                                             self.application.cell_height - 5))

    def load_grid(self):
        grid = np.zeros((ROWS+1, COLS), dtype=int)
        with open("./Game_data/Map.txt", "r") as file:
            for y, line in enumerate(file):
                for x, char in enumerate(line[:-1]):
                    if char == "W":
                        grid[y, x] = 1
                    else:
                        grid[y, x] = 0
        return grid

    def is_valid_target(self, target):
        grid = self.load_grid()
        if grid[int(target.y), int(target.x)] == 1:
            return False
        else:
            return True

    def exec_timer(self):
        ucs = []
        bfs = []
        dfs = []
        for i in range(10):
            start = np.random.randint(1, 25, (1, 2))[0]
            target = np.random.randint(1, 25, (1, 2))[0]
            start = vec(start[0], start[1])
            target = vec(target[0], target[1])

            if self.is_valid_target(start) and self.is_valid_target(target):
                start_time = time.time()
                for i in range(100):
                    self.UCS(start, target)
                ucs.append(time.time() - start_time)

                start_time = time.time()
                for i in range(100):
                    self.BFS(start, target)
                bfs.append(time.time() - start_time)

                start_time = time.time()
                for i in range(100):
                    self.DFS(start, target)
                dfs.append(time.time() - start_time)

        print(f"Середній час UCS = {np.mean(ucs)}")
        print(f"Середній час BFS = {np.mean(bfs)}")
        print(f"Середній час DFS = {np.mean(dfs)}")

