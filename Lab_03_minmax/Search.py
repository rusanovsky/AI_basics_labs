import numpy as np
from Map_generator import Generator
import pygame
from Constants import *
import sys


class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.cost_to_step = 0
        self.heuristic = 0
        self.total = 0

    def __eq__(self, other):
        return self.position == other.position


def a_star(maze, start, end, func, coins):
    start_node = Node(None, start)
    start_node.cost_to_step = maze[start]

    end_node = Node(None, end)
    end_node.cost_to_step = maze[end]

    open_list = []
    closed_list = []

    open_list.append(start_node)

    while open_list:
        current_node = open_list[0]
        temp_index = 0
        for index, node in enumerate(open_list):
            if node.total < current_node.total:
                current_node = node
                temp_index = index

        open_list.pop(temp_index)
        closed_list.append(current_node)

        if current_node == end_node:
            path = []
            temp = current_node
            while temp is not None:
                path.append(temp.position)
                temp = temp.parent
            return list(reversed(path))

        children = []
        for direction in [[1, 0], [-1, 0], [0, 1], [0, -1]]:
            next_position = (current_node.position[0] + direction[0],
                             current_node.position[1] + direction[1])

            if next_position[0] > maze.shape[0] - 1\
                    or next_position[0] < 0 \
                    or next_position[1] > maze.shape[1] - 1 \
                    or next_position[1] < 0:
                continue

            if maze[next_position] == 1:
                continue

            new_node = Node(current_node, next_position)
            children.append(new_node)

        for child in children:
            if child in closed_list:
                continue

            child.cost_to_step = maze[child.position]
            child.heuristic = func(child.position, end_node.position, coins)
            child.total = child.cost_to_step + child.heuristic

            for open_node in open_list:
                if child == open_node and child.cost_to_step > open_node.cost_to_step:
                    continue
            open_list.append(child)


def manhattan_heuristic(start, end, coins):
    return abs(start[0] - end[0]) + abs(start[1] - end[1])


def euclid_heuristic(start, end, coins):
    return ((start[0] - end[0]) - (start[1] - end[1])) ** 2

def greedy_heuristic(start, end, coins):
    return ((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2) ** 0.5

def take_all_coins_heuristic(start, end, coins):
    coef = 10 ** 1
    ways_to_coins = []
    for coin in coins:
        coin_position = (coin[1], coin[0])
        ways_to_coins.append(euclid_heuristic(start, coin_position, coins))
    print(min(ways_to_coins))
    return min(ways_to_coins)