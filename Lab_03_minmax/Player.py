import random

import numpy as np
import pygame
from Constants import *
from Search import *
vec = pygame.math.Vector2



class Player:
    def __init__(self, application, pos):
        self.application = application
        self.starting_pos = [pos.x, pos.y]
        self.grid_pos = pos
        self.old_grid_pos = None
        self.pix_pos = self.get_pix_pos()
        self.direction = vec(0, 0)
        self.stored_direction = None
        self.able_to_move = True
        self.current_score = 0
        self.speed = 2
        self.lives = PLAYER_LIVES
        self.destination = DESTINATION
        self.points = self.generate_4_points()
        self.target_coin = None
        self.algo = EXPECT

    def update(self):


        if self.able_to_move:
            self.pix_pos += self.direction*self.speed
        if self.is_in_bounds():
            if self.stored_direction is not None:
                self.direction = self.stored_direction
            self.able_to_move = self.is_able_to_move()

        new_pos = [(self.pix_pos[0] - PADDING + self.application.cell_width // 2) // self.application.cell_width + 1,
                        (self.pix_pos[1] - PADDING + self.application.cell_height // 2) // self.application.cell_height + 1]

        if new_pos != self.grid_pos:
            self.old_grid_pos = self.grid_pos
            self.grid_pos = new_pos

            # self.path = a_star(self.application.grid_map, start, end, take_all_coins_heuristic, self.application.coins)
            # self.path, self.c = self.way_through_all_points()

        if self.on_coin():
            self.eat_coin()
        if self.on_enemy():
            self.application.remove_life()
        self.on_teleport()
        if self.algo == MINMAX:
            self.change_direction(self.min_max())
        elif self.algo == EXPECT:
            self.change_direction(self.expect_max())

    def get_allowed_directions(self, mob):
        if mob == 1:
            directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (0, 0)]
            allowed_directions = []
            for direction in directions:
                if vec(self.grid_pos[0] + direction[0], self.grid_pos[1] + direction[1]) not in self.application.walls:
                    allowed_directions.append(direction)
            return allowed_directions
        else:
            return vec(0, 0)

    def min_max(self):
        DEPTH = 3
        def maximize(game_state, depth, alpha, beta):
            if game_state.is_lose() or game_state.is_win():
                return game_state.get_score()
            allowed_actions = game_state.get_legal_actions(PLAYER)
            best_score = -999999
            temp_score = best_score
            best_action = vec(0, 0)
            for action in allowed_actions:
                new_state = game_state.simulate_state(action, PLAYER)
                temp_score = minimize(new_state, depth, DEFAULT_GHOST, alpha, beta)
                if temp_score > best_score:
                    best_score = temp_score
                    best_action = action
                alpha = max(alpha, best_score)
                if best_score > beta:
                    return best_score

            if depth == 0:
                return vec(best_action)
            else:
                return best_score

        def minimize(state, depth, ghost, alpha,beta):

            if state.is_lose() or state.is_win():
                return state.get_score()
            next_ghost = ghost + 1
            if ghost == state.get_num_agents() - 1:
                next_ghost = PLAYER
            allowed_actions = state.get_legal_actions(ghost)
            best_score = 999999
            score = best_score
            for action in allowed_actions:
                if next_ghost == PLAYER:
                    if depth == DEPTH - 1:
                        score = state.simulate_state(action, ghost).get_score()
                    else:
                        score = maximize(state.simulate_state(action, ghost), depth + 2, alpha, beta)
                else:
                    score = minimize(state.simulate_state(action, ghost), depth - 1, next_ghost, alpha, beta)
                if score < best_score:
                    best_score = score
                beta = min(beta, best_score)
                if best_score < alpha:
                    return best_score
            return best_score

        return maximize(self.application.get_state(), 0, -999999, 999999)

    def expect_max(self):
        DEPTH = 3

        def maximize(state, depth):
            if state.is_lose() or state.is_win():
                return state.get_score()
            actions = state.get_legal_actions(PLAYER)
            best_score = -99999
            score = best_score
            best_action = vec(0, 0)
            for action in actions:
                new_state = state.simulate_state(action, PLAYER)
                score = minimize(new_state, depth, DEFAULT_GHOST)
                if score > best_score:
                    best_score = score
                    best_action = action
            if depth == 0:
                return best_action
            else:
                return best_score

        def minimize(state, depth, ghost):
            if state.is_lose():
                return state.get_score()
            next_ghost = ghost + 1
            if ghost == state.get_num_agents() - 1:
                next_ghost = PLAYER
            actions = state.get_legal_actions(ghost)
            best_score = 99999
            score = best_score
            for action in actions:
                prob = 1.0/len(actions)
                if next_ghost == PLAYER:
                    if depth == DEPTH - 1:
                        score = state.simulate_state(action, ghost).get_score()
                        score += prob * score
                    else:
                        score = maximize(state.simulate_state(action, ghost), depth + 1)
                        score += prob * score
                else:
                    score = minimize(state.simulate_state(action, ghost), depth, next_ghost)
                    score += prob * score
            return score
        return maximize(self.application.get_state(),0)


    def minmax(self):
        curr_score = -1000
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (0, 0)]
        allowed_directions = []
        for direction in directions:
            if vec(self.grid_pos[0] + direction[0], self.grid_pos[1] + direction[1]) not in self.application.walls:
                allowed_directions.append(direction)
        scores = []
        for direction in allowed_directions:
            scores.append(self.get_score(direction))
        step_index = 0
        for i in range(len(scores)):
            if scores[i] >= curr_score:
                curr_score = scores[i]
                step_index = i
        return vec(allowed_directions[step_index])

    def grab_coin(self):
        coins = []
        if self.application.coins:
            for c in self.application.coins:
                coins.append((int(c[1]), int(c[0])))
            if self.target_coin in coins:
                path = a_star(self.application.grid_map, (int(self.grid_pos[1]), int(self.grid_pos[0])),
                              (int(self.target_coin[0]), int(self.target_coin[1])), manhattan_heuristic, 0)
                next_step = (path[1][1], path[1][0])
                direction = vec(int(next_step[0] - self.grid_pos[0]), int(next_step[1] - self.grid_pos[1]))
                return direction
            else:
                print("position", self.grid_pos)
                distances = [(manhattan_heuristic(self.grid_pos, coin, 0), coin) for coin in coins]
                print(distances)
                print("position", self.grid_pos)
                closest_coin = distances[np.argmin(distances, axis=0)[0]][1]
                self.target_coin = (int(closest_coin[0]), int(closest_coin[1]))
                print(self.target_coin)
                return vec(0, 0)
        return vec(0, 0)

    def get_score(self, direction):
        new_step = (int(self.grid_pos[0] + direction[0]), int(self.grid_pos[1] + direction[1]))
        enemy = (int(self.application.enemies[0].grid_position[0]), int(self.application.enemies[0].grid_position[1]))
        distance_to_enemy = manhattan_heuristic(new_step, enemy, 0)

        distances = []
        for coin in self.application.coins:
            distances.append((manhattan_heuristic(coin, self.grid_pos, 0), coin))

        distance_and_coin = min(distances, key=lambda x: x[0])
        self.target_coin = distance_and_coin[1][::-1]
        new_step = (int(self.grid_pos[0] + direction[0]), int(self.grid_pos[1] + direction[1]))
        if manhattan_heuristic(new_step, distance_and_coin[1], 0) < distance_and_coin[0]:
            if distance_and_coin[0] < 4 and distance_to_enemy > 7:
                return distance_and_coin[0] * 10
            elif distance_to_enemy < 5:
                return distance_to_enemy * 50
            elif distance_to_enemy < 10 and distance_and_coin[0] < 2:
                return distance_and_coin[0] * 2 + distance_to_enemy * 2
            else:
                return -1
        return -1

    def draw(self):

        pygame.draw.circle(self.application.screen, PLAYER_COLOUR, (int(self.pix_pos.x),
                                                                    int(self.pix_pos.y)), self.application.cell_width // 2 - 2)

        for x in range(self.lives):
            pygame.draw.circle(self.application.screen, GREEN, (30 + 20 * x, HEIGHT - 15), 7)

    def draw_path(self):

        if self.c is not None:
            for c in self.c[1:-1]:
                pygame.draw.circle(self.application.screen, YELLOW,
                                   (c[1] * self.application.cell_width + 10 + PADDING // 2,
                                    c[0] * self.application.cell_height + 10 + PADDING // 2), 6)

        for p in self.path:
            pygame.draw.circle(self.application.screen, (0, 255, 0),
                               (p[1] * self.application.cell_width + 10 + PADDING // 2,
                                p[0] * self.application.cell_height + 10 + PADDING // 2), 4)


    def way_through_4_points(self):
        hero = (self.grid_pos[1], self.grid_pos[0])
        points = [hero] + self.points
        points.append(self.destination)
        if hero in self.points:
            self.points.remove(hero)
        routs = []
        for j in range(len(points) - 1):
            temp_routs = []
            for i in range(j + 1, len(points)):
                point1 = (int(points[j][0]), int(points[j][1]))
                point2 = (int(points[i][0]), int(points[i][1]))
                temp_routs.append(a_star(self.application.grid_map, point1, point2, euclid_heuristic, 0))
            routs += min(temp_routs, key=len)

        return routs, points

    def way_through_all_points(self):
        coins = []
        for c in self.application.coins:
            coins.append((c[1], c[0]))
        hero = (self.grid_pos[1], self.grid_pos[0])
        points = [hero] + coins
        points.append(self.destination)

        if hero in self.points:
            self.points.remove(hero)
        routs = []
        for j in range(len(points) - 1):
            temp_routs = []
            for i in range(j + 1, len(points)):
                point1 = (int(points[j][0]), int(points[j][1]))
                point2 = (int(points[i][0]), int(points[i][1]))
                temp_routs.append(a_star(self.application.grid_map, point1, point2, euclid_heuristic, 0))
            routs += min(temp_routs, key=len)

        return routs, points

    def generate_4_points(self):
        points = []
        for _ in range(4):
            point = random.choice(self.application.coins)
            points.append((point[1], point[0]))
        return points
    def on_coin(self):

        if self.grid_pos in self.application.coins:
            return True
        return False

    def eat_coin(self):


        self.application.coins.remove(self.grid_pos)
        self.current_score += 1

    def on_teleport(self):


        if self.grid_pos in self.application.teleports:
            if self.grid_pos == self.application.teleports[0]:
                self.grid_pos = self.application.teleports[1] + vec((-1, 0))
                self.pix_pos = self.get_pix_pos()
            elif self.grid_pos == self.application.teleports[1]:
                self.grid_pos = self.application.teleports[0] + vec((1, 0))
                self.pix_pos = self.get_pix_pos()
            elif self.grid_pos == self.application.teleports[2]:
                self.grid_pos = self.application.teleports[3] + vec((-1, 0))
                self.pix_pos = self.get_pix_pos()
            elif self.grid_pos == self.application.teleports[3]:
                self.grid_pos = self.application.teleports[2] + vec((1, 0))
                self.pix_pos = self.get_pix_pos()

    def on_enemy(self):

        for enemy in self.application.enemies:
            if enemy.position == self.grid_pos:
                return True

    def change_direction(self, direction):

        self.stored_direction = direction

    def get_pix_pos(self):

        return vec((self.grid_pos[0] * self.application.cell_width) + PADDING // 2 + self.application.cell_width // 2,
                   (self.grid_pos[1] * self.application.cell_height) +
                   PADDING // 2 + self.application.cell_height // 2)

    def is_in_bounds(self):

        if int(self.pix_pos.x + PADDING // 2) % self.application.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_pos.y + PADDING // 2) % self.application.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True

    def is_able_to_move(self):

        for wall in self.application.walls:
            if vec(self.grid_pos+self.direction) == wall:
                return False
        return True
