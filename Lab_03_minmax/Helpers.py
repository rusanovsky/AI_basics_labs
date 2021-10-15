import pygame

from Constants import *
vec = pygame.math.Vector2

class GameState:
    def __init__(self, grid_map, coins_positions, player_position, enemies_positions, walls):
        self.grid_map = grid_map
        self.coins_positions = coins_positions
        self.player_position = player_position
        self.enemies_positions = enemies_positions
        self.walls = walls

    def is_lose(self):
        for enemy_position in self.enemies_positions:
            if self.player_position[0] == enemy_position[0] and self.player_position[1] == enemy_position[1]:
                return True
        return False

    def is_win(self):
        return len(self.coins_positions) == 0

    def get_score(self):
        # return sum([x[0] - self.player_position[0] + x[1] - self.player_position[1] for x in self.enemies_positions])
        distances_to_enemy = []
        for enemy in self.enemies_positions:
            distances_to_enemy.append(abs(enemy[0] - self.player_position[0]) + abs(enemy[1] - self.player_position[1]))
        distance_to_enemy = min(distances_to_enemy)
        distances_to_all_coins = []
        if self.coins_positions:
            for coin in self.coins_positions:
                distances_to_all_coins.append((abs(coin[0] - self.player_position[0]) + abs(coin[1] - self.player_position[1]), coin))
        else:
            return 1
        distance_to_coin, close_coin = min(distances_to_all_coins, key=lambda x: x[0])
        score = -1 / (distance_to_enemy + 0.001) + 1 / (distance_to_coin + 0.1)
        score = 3 * score if distance_to_coin < distance_to_enemy + 2 else score
        return score


    def get_legal_actions(self, mob_type):
        if mob_type == PLAYER:
            directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (0, 0)]
            allowed_directions = []
            for direction in directions:
                if (self.player_position[0] + direction[0], self.player_position[1] + direction[1]) not in self.walls:
                    allowed_directions.append(vec(direction[::-1]))
            return allowed_directions
        elif mob_type == DEFAULT_GHOST:
            ghost_position = (0, 0)
            for ghost in self.enemies_positions:
                ghost_position = (int(ghost[0]), int(ghost[1]))
            directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]
            allowed_directions = []
            for direction in directions:
                if (ghost_position[0] + direction[0], ghost_position[1] + direction[1]) not in self.walls:
                    allowed_directions.append(vec(direction[::-1]))
            return allowed_directions

    def simulate_state(self, direction, mob_type):

        if mob_type == PLAYER:
            player_position = (self.player_position[0] + direction[1], self.player_position[1] + direction[0])
            return GameState(self.grid_map, self.coins_positions, player_position, self.enemies_positions, self.walls)

        elif mob_type == DEFAULT_GHOST:
            enemies_positions = []
            for ghost in self.enemies_positions:
                enemies_positions.append(ghost)
            for i, ghost in enumerate(enemies_positions):
                ghost_position = (ghost[0] + direction[1], ghost[1] + direction[0])
                enemies_positions[i] = ghost_position
                return GameState(self.grid_map, self.coins_positions, self.player_position, enemies_positions,
                                 self.walls)

    def get_num_agents(self):
        return len(self.enemies_positions) + 1