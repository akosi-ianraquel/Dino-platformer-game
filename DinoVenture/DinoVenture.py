import pygame
import os
import random
from sys import exit
import spritesheet

pygame.init()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


screen = pygame.display.set_mode((1200, 500), vsync=1)
pygame.display.set_caption('Dinoventure')
clock = pygame.time.Clock()
title_font = pygame.font.Font(os.path.join(BASE_DIR, 'Pixeltype.ttf'), 50)
button_font = pygame.font.Font(os.path.join(BASE_DIR, 'Pixeltype.ttf'), 30)


MENU = 'menu'
PLAYING = 'playing'
GAME_OVER = 'game_over'
game_state = MENU


ground_y = 400        # the y position the dino and cactus stand on
scroll_speed = 7      # how fast the grass and cactus move left
gravity = 1.2
jump_strength = -16


# One picture drawn twice side by side, so it can scroll forever
bg_image = pygame.image.load(os.path.join(BASE_DIR, 'graphics', 'elements', 'background_default.png')).convert()
bg_image = pygame.transform.scale(bg_image, (1200, 500))
bg_width = bg_image.get_width()
bg_x = 0
bg_speed = 3          # slower than the grass, so it looks far away


tileset = pygame.image.load(os.path.join(BASE_DIR, 'graphics', 'elements', 'tilesetgrass.png')).convert()
grass_tile = tileset.subsurface(pygame.Rect(286, 96, 34, 26))
grass_image = pygame.transform.scale_by(grass_tile, 4.3)
grass_width = grass_image.get_width()
grass_x = 0


cactus_sheet = pygame.image.load(os.path.join(BASE_DIR, 'graphics', 'elements', 'cactus_sprite.png')).convert_alpha()
cactus_part = cactus_sheet.subsurface(pygame.Rect(78, 77, 33, 42))
cactus_image = pygame.transform.scale_by(cactus_part, 2)
cactus_rect = cactus_image.get_rect(midbottom=(1300, ground_y))
cactus_mask = pygame.mask.from_surface(cactus_image)   # only the visible pixels count as a hit


dino_sheet = spritesheet.SpriteSheet(
    pygame.image.load(os.path.join(BASE_DIR, 'graphics', 'characters', 'sheets', 'character_doux.png')).convert_alpha())

# Cut the sheet into frames: 4 idle, 6 run, 3 jump
IDLE, RUN, JUMP = 0, 1, 2
dino_frames = []
sheet_index = 0
for how_many in [4, 6, 3]:
    row = []
    for _ in range(how_many):
        row.append(dino_sheet.get_image(sheet_index, 24, 24, 3, 'BLACK'))
        sheet_index += 1
    dino_frames.append(row)

dino_rect = dino_frames[IDLE][0].get_rect(midbottom=(100, ground_y))
action = IDLE                # which animation is playing
frame = 0                    # which picture of that animation we are on
frame_delay = 70             # milliseconds between pictures
last_frame_time = pygame.time.get_ticks()
vertical_velocity = 0
is_jumping = False


start_button = pygame.Rect(0, 0, 200, 60)
start_button.center = (950, 220)
restart_button = pygame.Rect(0, 0, 200, 60)
restart_button.center = (600, 250)


title_text = title_font.render('Dinoventure', True, 'white')
game_over_text = title_font.render('Game Over', True, 'white')
dark_overlay = pygame.Surface((1200, 500))   # darkens the screen on the game over screen
dark_overlay.set_alpha(140)
dark_overlay.fill('black')


def draw_button(text, rect):
    pygame.draw.rect(screen, 'white', rect, border_radius=10)
    label = button_font.render(text, True, 'black')
    screen.blit(label, label.get_rect(center=rect.center))


def place_cactus():
    # put the cactus off the right edge, with a random extra distance
    cactus_rect.midbottom = (1300 + random.randint(0, 600), ground_y)


def reset_game():
    global vertical_velocity, is_jumping
    dino_rect.midbottom = (100, ground_y)
    vertical_velocity = 0
    is_jumping = False
    place_cactus()


def update_animation():
    global frame, last_frame_time
    now = pygame.time.get_ticks()
    if now - last_frame_time >= frame_delay:
        last_frame_time = now
        frame += 1
        if frame >= len(dino_frames[action]):
            frame = 0


def draw_scene():
    screen.blit(bg_image, (bg_x, 0))
    screen.blit(bg_image, (bg_x + bg_width, 0))
    for x in range(0, 1200 + grass_width, grass_width):
        screen.blit(grass_image, (x + grass_x, 390))
    screen.blit(dino_frames[action][frame], dino_rect)
    screen.blit(cactus_image, cactus_rect)

def music_player(filename, volume):
    pygame.mixer.music.load(os.path.join(BASE_DIR, 'music', filename))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(volume)
    

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN and game_state == PLAYING:
            if event.key == pygame.K_SPACE and not is_jumping:
                vertical_velocity = jump_strength
                is_jumping = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == MENU and start_button.collidepoint(event.pos):
                game_state = PLAYING
            elif game_state == GAME_OVER and restart_button.collidepoint(event.pos):
                reset_game()
                game_state = PLAYING


    if game_state == MENU:
        action = IDLE
        update_animation()

    elif game_state == PLAYING:
        bg_x -= bg_speed
        if bg_x <= -bg_width:
            bg_x += bg_width
        grass_x -= scroll_speed
        if grass_x <= -grass_width:
            grass_x += grass_width

        vertical_velocity += gravity
        dino_rect.y += vertical_velocity
        if dino_rect.bottom >= ground_y:
            dino_rect.bottom = ground_y
            vertical_velocity = 0
            is_jumping = False

        new_action = JUMP if is_jumping else RUN
        if new_action != action:
            action = new_action
            frame = 0
        update_animation()
        


        cactus_rect.x -= scroll_speed
        if cactus_rect.right < 0:
            place_cactus()


        dino_mask = pygame.mask.from_surface(dino_frames[action][frame])
        offset = (cactus_rect.x - dino_rect.x, cactus_rect.y - dino_rect.y)
        if dino_mask.overlap(cactus_mask, offset):
            game_state = GAME_OVER


    draw_scene()

    if game_state == MENU:
        screen.blit(title_text, (700, 50))
        draw_button('Start', start_button)

    elif game_state == GAME_OVER:
        screen.blit(dark_overlay, (0, 0))
        screen.blit(game_over_text, game_over_text.get_rect(center=(600, 175)))
        draw_button('Restart', restart_button)

    pygame.display.update()
    clock.tick(60)