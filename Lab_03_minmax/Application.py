import sys
import time

from Player import *
from Enemy import *
from Map_generator import *
from Helpers import *
pygame.init()
vec = pygame.math.Vector2





class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.background = None
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = MENU
        self.cell_width = MAZE_WIDTH//COLS
        self.cell_height = MAZE_HEIGHT//ROWS
        self.walls = []
        self.coins = []
        self.teleports = []
        self.enemies = []
        self.e_pos = []
        self.p_pos = (1, 1)
        self.map_generator = Generator()
        self.grid_map = None
        self.load_map()
        self.player = Player(self, vec(self.p_pos))
        self.high_score = self.load_score()
        self.start_time = time.time()

    def start_game(self):
        """
        This is the main loop of game that controls game state and calls function to draw the contents
        and/or functions that process the input events in game.
        :return:
        """
        while self.running:
            if self.state == MENU:
                self.start_events()
                self.start_draw()
            elif self.state == GAMING:
                self.playing_events()
                self.playing_update()
                self.playing_draw()
            elif self.state == GAME_OVER:
                self.game_over_events()
                self.game_over_draw()
            elif self.state == WINNER:
                self.winner_events()
                self.winner_draw()
            else:
                self.running = False
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def load_score(self):
        """
        This function reads the file and loads the highest score.
        :return: int: score
        """
        with open("./Game_data/Score.txt", "r") as file:
            score = int(file.read())
            print(score)
        return score

    def write_score(self, score):
        """
        This function write the score on file.
        :param score: int score
        """
        with open("./Game_data/Score.txt", "w") as file:
            file.write(str(score))

    def draw_text(self, words, screen, pos, size, colour, font_name, centered=False):
        """
        Drawing the text with color, font, size and etc.
        :param words: str - Text to draw
        :param screen: Surface - The surface on which text will be painted)
        :param pos: tuple(x,y) X and Y - screen positions of left top corner of test
        :param size: int - Size of text
        :param colour: tuple(R,G,B)
        :param font_name: str - font name
        :param centered: bool - need to draw the text in center or not. Default=FALSE
        """
        font = pygame.font.SysFont(font_name, size)
        text = font.render(words, False, colour)
        text_size = text.get_size()
        if centered:
            pos[0] = pos[0]-text_size[0]//2
            pos[1] = pos[1]-text_size[1]//2
        screen.blit(text, pos)

    def load_map(self):
        """
        This method loads the map background and reads the map file,
        that consists of WALLS, COINS, TELEPORTS,
        ENEMIES' spawn and PLAYER`s spawn.

        Also we create the list of VECTORS(int,int) that helps us to make main process of game
        :return:
        """
        self.background = pygame.image.load('./Game_data/back.png')
        self.background = pygame.transform.scale(self.background, (MAZE_WIDTH, MAZE_HEIGHT))
        self.grid_map = self.map_generator.create_labyrinth(ROWS, COLS)
        for y_index in range(ROWS):
            for x_index in range(COLS):
                if self.grid_map[y_index, x_index] == WALL:
                    self.walls.append(vec(x_index, y_index))
                elif self.grid_map[y_index, x_index] == COIN:
                    self.coins.append(vec(x_index, y_index))
                elif self.grid_map[y_index, x_index] == DEFAULT_GHOST:
                    self.enemies.append(Enemy(self, vec(x_index, y_index), DEFAULT))
                elif self.grid_map[y_index, x_index] == RANDOM_GHOST:
                    self.enemies.append(Enemy(self, vec(x_index, y_index), RANDOM))


    def draw_grid(self):
        """
        Simple method to draw grid. Uses only for debug.
        :return:
        """
        for x in range(WIDTH//self.cell_width):
            pygame.draw.line(self.background, GREY, (x*self.cell_width, 0),
                             (x*self.cell_width, HEIGHT))
        for x in range(HEIGHT//self.cell_height):
            pygame.draw.line(self.background, GREY, (0, x*self.cell_height),
                             (WIDTH, x*self.cell_height))

    def reset(self):
        """
        This method allow to reset the game after lose or win
        :return:
        """
        self.walls = []
        self.player.lives = PLAYER_LIVES
        self.player.current_score = 0
        self.player.grid_pos = vec((1, 1))
        self.player.pix_pos = self.player.get_pix_pos()
        self.player.direction *= 0
        for enemy in self.enemies:
            enemy.grid_pos = vec(enemy.position)
            enemy.pix_pos = enemy.get_pix_pos()
        self.load_map()
        self.state = GAMING

# This block of code describes an intro functions of game. Start screen and start screen's key inputs

    def start_events(self):
        """
        Method control the inputs. Press SCAPE to start play. ESC for exit
        :return:
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = GAMING

    def start_draw(self):
        """
        Drawing the main menu.
        :return:
        """
        self.screen.fill(BLACK)
        self.draw_text('Pacman', self.screen, [
                       WIDTH//2, HEIGHT//2-50], START_TEXT_SIZE, RED, START_FONT, centered=True)
        self.draw_text('Press space to play', self.screen, [
                       WIDTH//2, HEIGHT//2], START_TEXT_SIZE, RED, START_FONT, centered=True)
        self.draw_text(f'HIGH SCORE {self.high_score}', self.screen, [4, 0],
                       START_TEXT_SIZE, WHITE, START_FONT)
        pygame.display.update()

# This is the main block of code controls game process and gameplay

    def playing_events(self):
        """
        This method allows you to control in game player.
        :return:
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.change_direction(vec(-1, 0))
                if event.key == pygame.K_RIGHT:
                    self.player.change_direction(vec(1, 0))
                if event.key == pygame.K_UP:
                    self.player.change_direction(vec(0, -1))
                if event.key == pygame.K_DOWN:
                    self.player.change_direction(vec(0, 1))

    def playing_update(self):
        """
        Updating the player and check is he winner. If he is game turn to winner state.
        :return:
        """
        if len(self.coins) == 0:
            play_time = time.time() - self.start_time
            with open("results.csv", "a") as file:
                file.write(f"{self.player.algo},{self.player.current_score},{play_time},win\n")

            self.state = WINNER
        self.player.update()

    def playing_draw(self):
        """
        This method draw main game scenes and update it.
        :return:
        """
        self.screen.fill(BLACK)
        self.screen.blit(self.background, (PADDING // 2, PADDING // 2))
        self.draw_coins()
        self.draw_walls()
        self.draw_text(f'CURRENT SCORE: {self.player.current_score}',
                       self.screen, [60, 0], 36, WHITE, START_FONT)
        self.draw_text(f'HIGH SCORE: {self.high_score}', self.screen, [WIDTH//2+60, 0], 36, WHITE, START_FONT)
        self.player.draw()
        # self.player.draw_path()
        for enemy in self.enemies:
            enemy.update()
            enemy.draw()

            # enemy.path = enemy.BFS(vec(enemy.position), self.player.grid_pos)
            # enemy.path = enemy.DFS(vec(enemy.position), self.player.grid_pos)
            # enemy.path = enemy.UCS(vec(enemy.position), self.player.grid_pos)
            # enemy.draw_path()
        pygame.display.update()

    def remove_life(self):
        """
        This method control Player's lives and control moment of lose.
        :return:
        """
        self.player.lives -= 1

        if self.player.lives == 0:
            with open("results.csv", "a") as file:
                play_time = time.time() - self.start_time
                file.write(f"{self.player.algo},{self.player.current_score},{play_time},lose\n")
            if self.player.current_score > self.high_score:
                self.high_score = self.player.current_score
            self.write_score(self.player.current_score)
            self.state = GAME_OVER
        else:
            self.player.grid_pos = vec(self.player.starting_pos)
            self.player.pix_pos = self.player.get_pix_pos()
            self.player.direction *= 0
            for enemy in self.enemies:
                enemy.grid_pos = vec(enemy.position)
                enemy.pix_pos = enemy.get_pix_pos()

    def draw_coins(self):
        """
        Simple draw coins method.
        :return:
        """
        for coin in self.coins:
            if self.player.target_coin is not None and coin[1] == self.player.target_coin[0] and coin[0] == self.player.target_coin[1]:
                pygame.draw.circle(self.screen, RED,
                                   (int(coin.x*self.cell_width) + self.cell_width // 2 + PADDING // 2,
                                    int(coin.y*self.cell_height) + self.cell_height // 2 + PADDING // 2), 5)
            else:

                pygame.draw.circle(self.screen, YELLOW,
                                   (int(coin.x * self.cell_width) + self.cell_width // 2 + PADDING // 2,
                                    int(coin.y * self.cell_height) + self.cell_height // 2 + PADDING // 2), 5)

    def draw_walls(self):
        maze = self.grid_map
        h = maze.shape[0]
        w = maze.shape[1]
        for x in range(h):
            for y in range(w):
                if maze[x, y] == WALL:
                    pygame.draw.rect(self.screen, GREY, (y * self.cell_width + PADDING // 2,
                                                         x * self.cell_height + PADDING // 2,
                                                         self.cell_width - 1, self.cell_height - 1))
                elif maze[x, y] == WATER:
                    pygame.draw.rect(self.screen, WATER_COLOR, (y * self.cell_width + PADDING // 2,
                                                                x * self.cell_height + PADDING // 2,
                                                                self.cell_width - 1, self.cell_height - 1))
                elif maze[x, y] in [ICE, SWAMP]:
                    fill_color = ICE_COLOR
                    texture_color = WHITE
                    if maze[x, y] == SWAMP:
                        texture_color = EARTH
                        fill_color = SWAMP_COLOR
                    pygame.draw.rect(self.screen, fill_color, (y * self.cell_width + PADDING // 2,
                                                               x * self.cell_height + PADDING // 2,
                                                               self.cell_width - 1, self.cell_height - 1))
                    pygame.draw.rect(self.screen, texture_color, (y * self.cell_width + PADDING // 2 + 7,
                                                                  x * self.cell_height + PADDING // 2 + 7,
                                                                  6, 6))
                    pygame.draw.rect(self.screen, texture_color, (y * self.cell_width + PADDING // 2 + 1,
                                                                  x * self.cell_height + PADDING // 2 + 1,
                                                                  6, 6))

        pygame.display.update()

    def draw_teleports(self):
        """
        Drawing teleports on map
        :return:
        """
        for teleport in self.teleports:
            pygame.draw.circle(self.screen, BLACK,
                               (int(teleport.x*self.cell_width) + self.cell_width // 2 + PADDING // 2,
                                int(teleport.y*self.cell_height) + self.cell_height // 2 + PADDING // 2), 16)
            pygame.draw.circle(self.screen, BLUE,
                               (int(teleport.x*self.cell_width) + self.cell_width // 2 + PADDING // 2,
                                int(teleport.y*self.cell_height) + self.cell_height // 2 + PADDING // 2), 12)

# This block of code manages game over state of game
    def game_over_events(self):
        """
        Control inputs in 'Game over' state of game.
        You can play again if you press Space or left game with pressing the ESC button
        :return:
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def game_over_draw(self):
        """
        Draws game over screen.
        :return:
        """
        self.screen.fill(BLACK)
        quit_text = "Press the escape button to QUIT"
        again_text = "Press space to PLAY AGAIN"
        self.draw_text("GAME OVER", self.screen, [WIDTH//2, 100],  52, RED, "Sans Serif MS", centered=True)
        self.draw_text(again_text, self.screen, [
                       WIDTH//2, HEIGHT//2],  36, GREY, "Sans Serif MS", centered=True)
        self.draw_text(quit_text, self.screen, [
                       WIDTH//2, HEIGHT//1.5],  36, GREY, "Sans Serif MS", centered=True)
        pygame.display.update()

# This block of code manages an win state of game
    def winner_events(self):
        """
        Control inputs in 'WON' state of game.
        You can play again if you press Space or left game with pressing the ESC button
        :return:
        """
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                temp_score = self.player.current_score
                self.reset()
                self.player.current_score = temp_score
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            if event.type == pygame.QUIT:
                self.running = False

    def winner_draw(self):
        """
        Draws winner screen.
        :return:
        """
        self.screen.fill(BLACK)
        self.draw_text("You are WINNER!", self.screen, [
            WIDTH // 2, HEIGHT // 2 - 50], 36, GREEN, "Sans Serif MS", centered=True)
        win_text = "Press space to PLAY AGAIN"
        self.draw_text(win_text, self.screen, [
            WIDTH // 2, HEIGHT // 2], 36, GREEN, "Sans Serif MS", centered=True)
        pygame.display.update()

    def get_state(self) -> GameState:
        grid = self.grid_map
        enemy_positions = []
        coins_positions = []
        walls_positions = []
        player_position = (int(self.player.grid_pos[1]), int(self.player.grid_pos[0]))
        for enemy in self.enemies:
            enemy_positions.append((int(enemy.position[1]), int(enemy.position[0])))
        for coin in self.coins:
            coins_positions.append((int(coin[1]), int(coin[0])))
        for wall in self.walls:
            walls_positions.append((int(wall[1]), int(wall[0])))
        return GameState(grid, coins_positions, player_position, enemy_positions, walls_positions)


