import pygame
from Constants import *
vec = pygame.math.Vector2



class Player:
    def __init__(self, application, pos):
        self.application = application
        self.starting_pos = [pos.x, pos.y]
        self.grid_pos = pos
        self.pix_pos = self.get_pix_pos()
        self.direction = vec(0, 0)
        self.stored_direction = None
        self.able_to_move = True
        self.current_score = 0
        self.speed = 2
        self.lives = PLAYER_LIVES

    def update(self):

        if self.able_to_move:
            self.pix_pos += self.direction*self.speed
        if self.is_in_bounds():
            if self.stored_direction is not None:
                self.direction = self.stored_direction
            self.able_to_move = self.is_able_to_move()

        self.grid_pos[0] = (self.pix_pos[0] - PADDING +
                            self.application.cell_width // 2) // self.application.cell_width + 1
        self.grid_pos[1] = (self.pix_pos[1] - PADDING +
                            self.application.cell_height // 2) // self.application.cell_height + 1
        # print(self.grid_pos)
        if self.on_coin():
            self.eat_coin()
        if self.on_enemy():
            self.application.remove_life()
        self.on_teleport()

    def draw(self):

        pygame.draw.circle(self.application.screen, PLAYER_COLOUR, (int(self.pix_pos.x),
                                                                    int(self.pix_pos.y)), self.application.cell_width // 2 - 2)

        for x in range(self.lives):
            pygame.draw.circle(self.application.screen, GREEN, (30 + 20 * x, HEIGHT - 15), 7)

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
        """
        Using grid position to calculate a pixel position on game screen
        :return: vec(x_pixel_position, y_pixel_position)
        """
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
