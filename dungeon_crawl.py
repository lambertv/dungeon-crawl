import pygame
import random
from enum import Enum

CAPTION = "Game game"
SCREEN_SIZE = [800,600]
BOARD_WIDTH =  8
BOARD_HEIGHT = 10
BLOCK_SIZE = 50
BOARD_X = (SCREEN_SIZE[0]-BOARD_WIDTH*BLOCK_SIZE)/2 
BOARD_Y = (SCREEN_SIZE[1]-BOARD_HEIGHT*BLOCK_SIZE)/2 

BACKGROUND_COLOR = (0,0,0)
CORRIDOR_COLOR = (100,100,100)
PLAYER_COLOR = (50, 50, 200)
ENEMY_COLOR = (200, 50, 50)

class Movement(Enum):
    up = (0,-1)
    down = (0,1)
    left = (-1,0)
    right = (1,0)
    stay = (0,0)

class Gamestate(Enum):
    dungeon = 0
    battle = 1
    game_over = 2

class Dungeon():

    def __init__(self, width, height):
        self.board = [[True for i in range(height)] for j in range(width)]
        self.width = width
        self.height = height
        self.player = Player(0,0)
        self.enemies = []
        self.battle_enemy = None
        self.gamestate = Gamestate.dungeon

        self.board = [ [1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
                       [0, 1, 0, 0, 1, 1, 1, 0, 0, 1],
                       [0, 1, 1, 1, 1, 0, 1, 1, 0, 1],
                       [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                       [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                       [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                       [1, 0, 1, 0, 0, 0, 1, 1, 0, 0],
                       [1, 1, 1, 0, 1, 1, 1, 1, 1, 0] ]

        self.enemies = [Enemy(5,5), Enemy(7,0), Enemy(0,7)]

    def update_movement(self):
        if self.player.move(self):
            for enemy in self.enemies:
                enemy.move(self)

    def update_battle(self):
        if self.player.health <= 0:
            self.gamestate = Gamestate.game_over
        elif self.battle_enemy.health <= 0:
            self.gamestate = Gamestate.dungeon
            self.enemies.remove(self.battle_enemy)

class Player():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.movement = Movement.stay
        self.health = 100
        self.attack = 5

    def attacked(self, enemy):
        if random.randint(0,10) < 8:
            self.health -= enemy.attack
            print "ENEMY HIT!"
        else:
            print "ENEMY MISS!"
    
    def move(self, dungeon):
        
        new_x = self.x + self.movement[0]
        new_y = self.y + self.movement[1]

        for enemy in dungeon.enemies:
            if enemy.x == new_x and enemy.y == new_y:
                dungeon.gamestate = Gamestate.battle
                dungeon.battle_enemy = enemy
                print "BATTLE"
                return 0

        if 0 <= new_x < len(dungeon.board) and 0 <= new_y < len(dungeon.board[0]) and dungeon.board[new_x][new_y]:
            self.x = new_x
            self.y = new_y
            return 1
        else:
            return 0

class Enemy():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.movement = Movement.stay
        self.health = 30
        self.attack = 3

    def attacked(self, player):
        if random.randint(0,10) < 9:
            self.health -= player.attack
            print "PLAYER HIT!"
        else:
            print "PLAYER MISS!"

    def move(self, dungeon):

        movement_list = [Movement.right, Movement.left, Movement.down, Movement.up, Movement.stay]
        self.movement = random.choice(movement_list)
        new_x = self.x + self.movement[0]
        new_y = self.y + self.movement[1]

        if dungeon.player.x == new_x and dungeon.player.y == new_y:
            dungeon.gamestate = Gamestate.battle
            dungeon.battle_enemy = self
            print "BATTLE"
            return 0

        if 0 <= new_x < len(dungeon.board) and 0 <= new_y < len(dungeon.board[0]) and dungeon.board[new_x][new_y]:
            for enemy in dungeon.enemies:
                if enemy.x == new_x and enemy.y == new_y:
                    new_x = self.x
                    new_y = self.y
            self.x = new_x
            self.y = new_y

        return 1

class Graphics():

    def __init__(self):
       self.board_x = BOARD_X
       self.board_y = BOARD_Y

    def coordinate_to_pixel(self, x, y):
        return (x*BLOCK_SIZE+self.board_x, y*BLOCK_SIZE+self.board_y)

    def draw_block(self, screen, x, y, color):
        pixel_x, pixel_y = self.coordinate_to_pixel(x, y)
        draw_rect = pygame.Rect(pixel_x, pixel_y, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(screen, color, draw_rect)

    def draw_dungeon(self, screen, dungeon):
        for x in range(dungeon.width):
            for y in range(dungeon.height):
                if dungeon.board[x][y]:
                    self.draw_block(screen, x, y, CORRIDOR_COLOR)

    def draw_player(self, screen, player):
        self.draw_block(screen, player.x, player.y, PLAYER_COLOR)

    def draw_enemies(self, screen, enemies):
        for enemy in enemies:
            self.draw_block(screen, enemy.x, enemy.y, ENEMY_COLOR)

    def draw(self, screen, dungeon):
        screen.fill(BACKGROUND_COLOR)
        self.draw_dungeon(screen, dungeon)
        self.draw_player(screen, dungeon.player)
        self.draw_enemies(screen, dungeon.enemies)

class Game():

    def __init__(self):
        self.dungeon = Dungeon(BOARD_WIDTH, BOARD_HEIGHT)
        self.graphics = Graphics()
        self.screen = pygame.display.get_surface()
        self.done = False

        self.graphics.draw(self.screen, self.dungeon)
        pygame.display.update()

    def game_loop(self):
        if self.key_presses():
            self.update()
            self.graphics.draw(self.screen, self.dungeon)
            pygame.display.update()

    def key_presses(self):

        take_turn = False
        if self.dungeon.gamestate == Gamestate.dungeon:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                elif event.type == pygame.KEYDOWN:
                    take_turn = True
                    self.dungeon.player.movement = Movement.stay
                    if event.key == pygame.K_RIGHT:
                        self.dungeon.player.movement = Movement.right
                    elif event.key == pygame.K_LEFT:
                        self.dungeon.player.movement = Movement.left
                    elif event.key == pygame.K_UP:
                        self.dungeon.player.movement = Movement.up
                    elif event.key == pygame.K_DOWN:
                        self.dungeon.player.movement = Movement.down

        elif self.dungeon.gamestate == Gamestate.battle:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        take_turn = True
                        self.dungeon.player.attacked(self.dungeon.battle_enemy)
                        self.dungeon.battle_enemy.attacked(self.dungeon.player)
                        print "PLAYER:", self.dungeon.player.health
                        print "ENEMY:", self.dungeon.battle_enemy.health

        return take_turn
 
    def update(self):
        if self.dungeon.gamestate == Gamestate.dungeon:
            self.dungeon.update_movement()
        elif self.dungeon.gamestate == Gamestate.battle:
            self.dungeon.update_battle()
        else:
            print "GAME OVER"
            self.done = True

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption(CAPTION)
    pygame.display.set_mode(SCREEN_SIZE)
    game_instance = Game()
    while not game_instance.done:
        game_instance.game_loop()
    pygame.quit()



