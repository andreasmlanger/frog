"""
To create WASM .apk file, run in console: 'pygbag Frog/main.py'
http://localhost:8000 (or http://localhost:8000?-i for debugging)
Read more on: https://pygame-web.github.io/
"""

import pygame
import asyncio  # needed for WASM
import json
import os
import random
import sys
import time


"""
Global parameters
"""

SIZE = 64  # length/width in pixels of one field
WIDTH = 19  # number of squares, usually odd for symmetry reasons
HEIGHT = 10  # number of squares
GAME_DURATION = 300  # game duration in seconds

# Calculated parameters
SQUARE = (SIZE, SIZE)  # w, h
FONT_SIZE = SIZE // 2
PADDING = SIZE // 6


"""
Utils
"""


def resource_path(relative_path):
    return str(os.path.join(os.path.dirname(__file__), relative_path))


def load_image(f, scale=1.0):
    """
    Loads an image and scales it, so that it fits the size of a SQUARE
    """
    img = pygame.image.load(f)  # load
    original_width, original_height = img.get_size()
    new_height = int(scale * SQUARE[1])
    new_width = int(new_height / original_height * original_width)
    img = pygame.transform.scale(img, (new_width, new_height))
    return img


# Icon
icon = pygame.image.load(resource_path('data/icon.png'))

# Surfaces
img_road = load_image(resource_path('data/surfaces/r.png'))
road_surface = pygame.Surface(img_road.get_size())
road_surface.blit(img_road, (0, 0))

img_big_road_2 = load_image(resource_path('data/surfaces/R2.png'))
big_road_surface_2 = pygame.Surface(img_big_road_2.get_size())
big_road_surface_2.blit(img_big_road_2, (0, 0))

img_big_road_4 = load_image(resource_path('data/surfaces/R4.png'))
big_road_surface_4 = pygame.Surface(img_big_road_4.get_size())
big_road_surface_4.blit(img_big_road_4, (0, 0))

img_big_road_1 = pygame.transform.rotate(img_big_road_2, 180)
big_road_surface_1 = pygame.Surface(img_big_road_1.get_size())
big_road_surface_1.blit(img_big_road_1, (0, 0))

img_big_road_3 = pygame.transform.rotate(img_big_road_4, 180)
big_road_surface_3 = pygame.Surface(img_big_road_3.get_size())
big_road_surface_3.blit(img_big_road_3, (0, 0))

img_grass = load_image(resource_path('data/surfaces/g.png'))
grass_surface = pygame.Surface(img_grass.get_size())
grass_surface.blit(img_grass, (0, 0))

img_train_grass = load_image(resource_path('data/surfaces/gT.png'))
grass_train_surface = pygame.Surface(img_train_grass.get_size())
grass_train_surface.blit(img_train_grass, (0, 0))

img_grass_obstacle_1 = load_image(resource_path('data/surfaces/G1.png'))
grass_obstacle_1_surface = pygame.Surface(img_grass_obstacle_1.get_size())
grass_obstacle_1_surface.blit(img_grass_obstacle_1, (0, 0))

img_grass_obstacle_2 = load_image(resource_path('data/surfaces/G2.png'))
grass_obstacle_2_surface = pygame.Surface(img_grass_obstacle_2.get_size())
grass_obstacle_2_surface.blit(img_grass_obstacle_2, (0, 0))

img_grass_obstacle_3 = load_image(resource_path('data/surfaces/G3.png'))
grass_obstacle_3_surface = pygame.Surface(img_grass_obstacle_3.get_size())
grass_obstacle_3_surface.blit(img_grass_obstacle_3, (0, 0))

img_train_track = load_image(resource_path('data/surfaces/t.png'))
train_surface = pygame.Surface(img_train_track.get_size())
train_surface.blit(img_train_track, (0, 0))

# Frog
frog_image = load_image(resource_path('data/frog/frog.png'), scale=0.8)
dead_frog_image = load_image(resource_path('data/frog/frog_dead.png'), scale=0.8)
sunken_frog_image = load_image(resource_path('data/frog/frog_sunk.png'), scale=0.8)

# Cars
green_car_small_image = load_image(resource_path('data/objects/green_car_small.png'), scale=0.8)
green_car_image = load_image(resource_path('data/objects/green_car.png'), scale=0.8)
green_bus_image = load_image(resource_path('data/objects/green_bus.png'), scale=0.8)
red_car_image = load_image(resource_path('data/objects/red_car.png'), scale=0.8)
red_truck_image = load_image(resource_path('data/objects/red_truck.png'), scale=0.8)
red_bus_image = load_image(resource_path('data/objects/red_bus.png'), scale=0.8)

# Trunks
green_trunk_image = load_image(resource_path('data/objects/green_trunk.png'), scale=0.8)
red_trunk_image = load_image(resource_path('data/objects/red_trunk.png'), scale=0.8)

# Train
train_image = load_image(resource_path('data/objects/train.png'), scale=0.8)


def get_surface(x):
    if x == 'r' or x == 'w':
        return road_surface
    elif x == 'R1':
        return big_road_surface_1
    elif x == 'R2':
        return big_road_surface_2
    elif x == 'R3':
        return big_road_surface_3
    elif x == 'R4':
        return big_road_surface_4
    elif x == 't':
        return train_surface
    elif x == 'G1':
        return grass_obstacle_1_surface
    elif x == 'G2':
        return grass_obstacle_2_surface
    elif x == 'G3':
        return grass_obstacle_3_surface
    elif x == 'gT':
        return grass_train_surface
    return grass_surface


def load_image_for_object(kind):
    if kind == 'train':
        return train_image
    elif kind == 'trunk':
        return random.choice([red_trunk_image, green_trunk_image])
    cars = [green_car_small_image, green_car_image, green_bus_image, red_car_image, red_truck_image, red_bus_image]
    return random.choice(cars)


# Sounds
pygame.mixer.init()  # only 'ogg' works in WASM, not 'mp3' or 'wav'!
train_sound = pygame.mixer.Sound(resource_path('data/sounds/train.ogg'))
water_sound = pygame.mixer.Sound(resource_path('data/sounds/water.ogg'))
horn_sound = pygame.mixer.Sound(resource_path('data/sounds/horn.ogg'))


# Font
def get_font(font_size=FONT_SIZE):
    font_path = resource_path('data/font/montserrat.ttf')
    return pygame.font.Font(font_path, font_size)


"""
Main game code
"""


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Frog')
        pygame.display.set_icon(icon)
        self.width = WIDTH * SQUARE[0]
        self.height = HEIGHT * SQUARE[1]
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.FPS = 30
        self.score = 0
        self.high_score = 0  # high score of session
        self.global_high_score = self.load_high_score_from_json()
        self.font = get_font()
        self.frog = Frog()
        self.objects = []  # list to store cars, trains and trunks
        self.surface = []  # list to store background (2d)
        self.finish_time = self.set_finish_time()
        self.background_scroll = 0
        self.key_pressed = False
        self.game_over = False  # game within session
        self.session_over = False  # complete session of GAME_DURATION
        self.is_running = True
        self.input = 'keyboard'  # track if keyboard or touch is used to play

    @staticmethod
    def set_finish_time():
        return time.time() + GAME_DURATION

    @staticmethod
    def load_high_score_from_json():
        try:
            with open('high_score.json') as file:
                return json.load(file)['HighScore']
        except FileNotFoundError:
            return 0

    def update_high_score_in_json(self):
        new_high_score = max(self.score, self.high_score)
        if new_high_score > self.global_high_score:
            try:
                with open('high_score.json', 'w') as file:
                    json.dump({'HighScore': new_high_score}, file)
            except FileNotFoundError:
                pass

    def restart_game(self):
        self.game_over = False
        self.update_high_score()
        self.score = 0  # reset score
        self.frog = Frog()
        self.objects = []
        self.create_new_surface()
        self.background_scroll = 0
        self.key_pressed = False

    def update_high_score(self):
        self.high_score = max(self.score, self.high_score)

    def create_new_surface(self):
        self.surface = [['g'] * WIDTH] * HEIGHT + [['r'] * WIDTH, ['g'] * WIDTH]
        while len(self.surface) < 2 * HEIGHT:
            self.add_row()

    # main game loop
    async def main(self):
        self.create_new_surface()
        while self.is_running:
            self.clock.tick(60)
            self.handle_events()
            if time.time() < self.finish_time:
                self.update()
            else:
                if not self.session_over:
                    self.session_over = True
                    self.game_over = True
                    self.update_high_score_in_json()
                self.display_stats('You have played enough!')
            self.render()
            await asyncio.sleep(0)

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if self.game_over:
                self.update_high_score_in_json()
                if event.type == pygame.KEYDOWN or self.left_mouse_click(event):
                    self.restart_game()
            else:
                self.update_input_type(event)
                touch = self.get_touch_direction(event)  # handle touch or mouse-click events if present
                self.key_pressed = self.move(touch)  # check if frog is moved by event (key or touch)

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.is_running = False

    def update_input_type(self, event):
        if self.left_mouse_click(event):
            self.input = 'touch'
        elif event.type == pygame.KEYDOWN:
            self.input = 'keyboard'
    
    @staticmethod
    def left_mouse_click(event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

    def get_touch_direction(self, event):
        if self.left_mouse_click(event):
            x_touch, y_touch = event.pos[0] // SIZE, event.pos[1] // SIZE
            x_frog = int(round(self.frog.x, 0))
            if y_touch < 7 or x_touch == x_frog:  # top of screen
                return 'U'  # up
            elif x_touch < x_frog:  # bottom half of screen, left side
                return 'L'  # left
            elif x_touch > x_frog:  # bottom half of screen, right side
                return 'R'  # right

    def update_objects(self, kind='car'):
        for o in self.objects:
            if o.kind == kind:
                if o.rect[1] > 2 * self.height:
                    self.objects.remove(o)
                o.update()
                o.draw(self.screen, self.background_scroll)

    def update(self):
        if self.background_scroll > 0:
            self.background_scroll -= (self.background_scroll // SQUARE[1]) * 2 + 2  # gradually scroll back

        self.draw_background(self.surface[:self.height * 2], self.background_scroll)

        self.update_objects(kind='trunk')  # trunk below frog
        self.frog.draw(self.screen, self.background_scroll)
        self.update_objects(kind='car')  # car and train above frog
        self.update_objects(kind='train')

        if not self.game_over:
            self.check_for_collision()
        self.render_score()

    @staticmethod
    def render():
        pygame.display.flip()

    def move(self, touch=None):
        key = pygame.key.get_pressed()
        move_up = key[pygame.K_UP] or touch == 'U'
        move_left = key[pygame.K_LEFT] or touch == 'L'
        move_right = key[pygame.K_RIGHT] or touch == 'R'
        if not self.key_pressed:
            frog_x = int(round(self.frog.x, 0))
            if move_up:
                next_row = self.surface[HEIGHT + 2]
                if 'G' not in next_row[frog_x]:
                    if next_row[0] != 'w':
                        self.frog.x = frog_x  # snap to grid
                    self.move_background_by_one()
                    return True
            elif move_left or move_right:
                this_row = self.surface[HEIGHT + 1]
                if move_left and self.frog.x > 0 and 'G' not in this_row[frog_x - 1]:
                    self.frog.move_left()
                    return True
                elif move_right and self.frog.x < WIDTH - 1 and 'G' not in this_row[frog_x + 1]:
                    self.frog.move_right()
                    return True

    def move_background_by_one(self):
        self.background_scroll += SQUARE[1]
        for o in self.objects:
            o.shift_down()
        self.surface = self.surface[1:]
        if len(self.surface) < 2 * HEIGHT:
            self.add_row()
        self.score += 1

    def render_score(self):
        # Timer
        time_to_go = max(0.0, self.finish_time - time.time())
        minutes = int(time_to_go // 60)
        seconds = int(time_to_go % 60)
        timer_text = self.font.render(f'{minutes:02d}:{seconds:02d}', True, (0, 0, 0))
        self.screen.blit(timer_text, (PADDING, PADDING))

        # Game Over
        if self.game_over:
            what_to_do = 'Press any key' if self.input == 'keyboard' else 'Touch anywhere'
            game_over_text = self.font.render(f'{what_to_do} to restart!', True, (0, 0, 0))
            game_over_rect = game_over_text.get_rect()
            game_over_rect.midtop = (self.width // 2, PADDING)
            self.screen.blit(game_over_text, game_over_rect)

        # Score
        high_score = f' [{self.high_score}]' if self.high_score > 0 else ''
        score_text = self.font.render(f'Score: {self.score}{high_score}', True, (0, 0, 0))
        score_rect = score_text.get_rect()
        score_rect.topright = (self.width - PADDING, PADDING)
        self.screen.blit(score_text, score_rect)

    def get_speed(self, kind):
        if kind == 'train':
            return 20
        elif kind == 'trunk':
            return random.choice([1, 2])
        else:  # car
            if self.score < 50:
                return random.choice([1, 2])
            elif self.score < 100:
                return random.choice([1, 2, 3])
            elif self.score < 150:
                return random.choice([2, 3, 4])
            return random.choice([2, 3, 4, 5])

    def get_number_of_objects(self, kind):
        if kind == 'train':
            return 1
        elif kind == 'trunk':
            if self.score < 100:
                return random.choice([3, 4])
            return random.choice([2, 3])
        else:  # car
            if self.score < 50:
                return random.choice([1, 2])
            elif self.score < 100:
                return random.choice([2, 3])
            elif self.score < 150:
                return random.choice([2, 3, 4])
            return random.choice([3, 4])

    @staticmethod
    def get_ranges(nr):
        if nr == 1:
            return [(0, 1)]
        elif nr == 2:
            return [(0.1, 0.4), (0.6, 0.9)]
        elif nr == 3:
            return [(0.1, 0.25), (0.4, 0.6), (0.75, 0.9)]
        return [(0.1, 0.15), (0.3, 0.4), (0.6, 0.65), (0.8, 0.9)]

    def add_objects(self, kind='car', direction=None):
        if not direction:
            direction = random.choice([-1, 1])
        y = int((2 * HEIGHT - len(self.surface) - 0.5) * SQUARE[1])
        speed = self.get_speed(kind) * direction
        nr = self.get_number_of_objects(kind)
        for r in self.get_ranges(nr):
            x = random.randrange(int(r[0] * self.width), int(r[1] * self.width))
            o = Object(x, y, speed, kind=kind)
            self.objects.append(o)

    def add_row(self):
        if self.surface[-1][-1].lower().startswith('g'):
            if self.score > 50 and random.random() < 0.3:
                self.add_water()
            elif random.random() < 0.4:
                self.add_road(double=True)
            else:
                self.add_road()
        else:
            if self.score > 25 and random.random() < 0.1:
                self.add_train()
            else:
                self.surface.append(self.grass_row())
    
    def add_train(self):
        self.surface.append(self.grass_row(train=True))
        self.add_objects(kind='train')
        self.surface.append(['t'] * WIDTH)
        while random.random() < 0.3:
            self.surface.append(self.grass_row(train=True))
            self.add_objects(kind='train')
            self.surface.append(['t'] * WIDTH)
    
    def add_water(self):
        direction = random.choice([-1, 1])
        self.add_objects(kind='trunk', direction=direction)
        self.surface.append(['w'] * WIDTH)
        while random.random() < 0.3:
            direction = -direction
            self.add_objects(kind='trunk', direction=direction)
            self.surface.append(['w'] * WIDTH)

    def add_road(self, double=False):
        self.add_objects()
        if double:
            self.surface.append(['R1', 'R3'] * (WIDTH // 2) + ['R1'])
            self.add_objects()
            self.surface.append(['R2', 'R4'] * (WIDTH // 2) + ['R2'])
        else:
            self.surface.append(['r'] * WIDTH)

    def grass_row(self, train=False):
        if train:
            return ['g'] * 2 + ['gT'] + ['g'] * (WIDTH - 6) + ['gT'] + ['g'] * 2
        row = []
        for k in range(WIDTH):
            if random.random() < 0.1:
                row.append('G1')
            elif self.score > 50 and random.random() < 0.1:
                row.append('G2')
            elif self.score > 100 and random.random() < 0.1:
                row.append('G3')
            else:
                row.append('g')
        return row

    def draw_background(self, arr, s):
        for row, y in zip(arr, range(-self.height, self.height, SQUARE[1])):
            for square, x in zip(row, range(0, self.width, SQUARE[0])):
                self.screen.blit(get_surface(square), (x, self.height - y - SQUARE[1] - s))

    def check_for_collision(self):
        if self.frog.rect.right < 0 or self.frog.rect.left > self.width:
            self.game_over = True  # out of screen
        in_water = self.surface[HEIGHT + 1][0] == 'w'
        for o in self.objects:
            o_rect = (o.rect[0], o.rect[1] - self.background_scroll, o.rect[2], o.rect[3])
            if self.frog.rect.colliderect(o_rect):
                if o.kind == 'trunk':
                    self.frog.x += o.speed / SQUARE[0]  # move frog with trunk
                    in_water = False
                else:  # car or train
                    self.frog.image = dead_frog_image
                    if o.kind == 'car':
                        horn_sound.play()
                    self.game_over = True
        if in_water:
            self.frog.image = sunken_frog_image
            water_sound.play()
            self.game_over = True

    def write_text(self, text, x, y, scale=1.0):
        """
        Write text at relative coordinates (x, y) based on screen
        """
        text_color = (0, 0, 0)
        font = get_font(font_size=(int(scale * FONT_SIZE)))
        text_surface = font.render(str(text), True, text_color)
        text_x = int(x * self.width)
        text_y = int(y * self.height)
        self.screen.blit(text_surface, (text_x, text_y))

    def display_stats(self, header):
        """
        Show the stats screen
        """
        self.update_high_score()
        self.screen.fill((255, 255, 255))
        self.write_text(header, 0.2, 0.05)
        self.write_text("Today's HighScore:", 0.2, 0.3, scale=0.9)
        self.write_text(self.high_score, 0.5, 0.27, scale=1.8)
        if self.global_high_score:
            self.write_text("All-Time Record:", 0.2, 0.5, scale=0.9)
            self.write_text(self.global_high_score, 0.5, 0.47, scale=1.8)


class Frog:
    def __init__(self):
        self.image = frog_image
        self.rect = self.image.get_rect()
        self.x = WIDTH // 2  # frog position only determined by x

    def move_right(self):
        self.x += 1

    def move_left(self):
        self.x -= 1

    def draw(self, surface, scroll=0):
        x = int((self.x + 0.5) * SQUARE[0])
        y = int((HEIGHT - 1.5) * SQUARE[1]) - scroll
        self.rect.center = (x, y)
        surface.blit(self.image, self.rect)


class Object:
    def __init__(self, x, y, speed, kind='car'):
        self.kind = kind
        self.image = load_image_for_object(self.kind)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed
        self.pause = False
        self.alarm_pre_time = 0.5
        self.wait_timer = None
        self.play_sound = False
        if speed < 0:
            self.image = pygame.transform.rotate(self.image, 180)

    def shift_down(self):
        self.rect[1] += SQUARE[1]

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.right > (WIDTH + 2) * SQUARE[0]:
            if self.kind == 'train':  # trains have a pause between disappearing and reappearing and also make sound
                self.pause = True
                if not self.wait_timer:
                    self.wait_timer = time.time() + random.choice([2, 3, 4])
                    self.play_sound = True
                elif time.time() >= self.wait_timer - self.alarm_pre_time and self.play_sound:
                    if 0 < self.rect.y < HEIGHT * SQUARE[1]:
                        train_sound.play()
                    self.play_sound = False
                elif time.time() >= self.wait_timer:
                    self.wait_timer = None
                    self.pause = False
            if not self.pause:
                if self.rect.right < 0:
                    self.rect.right = (WIDTH + 2) * SQUARE[0]
                else:
                    self.rect.right = 0

    def draw(self, surface, scr=0):
        x = self.rect[0]
        y = self.rect[1] - scr
        surface.blit(self.image, (x, y))


if __name__ == '__main__':
    game = Game()
    asyncio.run(game.main())
