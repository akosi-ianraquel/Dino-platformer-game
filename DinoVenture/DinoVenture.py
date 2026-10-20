import pygame
import os
import random
from sys import exit
import spritesheet
import highscore

pygame.init()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


screen = pygame.display.set_mode((1200, 500), vsync=1)
pygame.display.set_caption('Dinoventure')
clock = pygame.time.Clock()
title_font = pygame.font.Font(os.path.join(BASE_DIR, 'Pixeltype.ttf'), 80)
score_font = pygame.font.Font(os.path.join(BASE_DIR, 'Pixeltype.ttf'), 35)
button_font = pygame.font.Font(os.path.join(BASE_DIR, 'Pixeltype.ttf'), 30)


MENU = 'menu'
PLAYING = 'playing'
GAME_OVER = 'game_over'
game_state = MENU
score = 0
base_score_constant = 0.2


ground_y = 400        # default y position the dino and cactus 
base_speed = 7        
max_speed = 30        # the game never gets faster than this
points_per_speed = 100   # every 200 points the game speeds up by 1
scroll_speed = base_speed
gravity = 1.2
jump_strength = -20
min_gap = 400          # minimum gap
max_gap = 900          # maxgap on 2 obstacles

powerup_every = 200    # powerup per 200 points
next_powerup_score = powerup_every   
powerup_active = False   # will be true while a powerup is on screen
boost_duration = 8000    # how long the powerup effect lasts (milliseconds)
boost_slow = 0.5         
boost_active = False     
boost_start = 0          
speed_carry = 0         
current_speed = scroll_speed  



bg_image = pygame.image.load(os.path.join(BASE_DIR, 'graphics', 'elements', 'background_default.png')).convert()
bg_image = pygame.transform.scale(bg_image, (1200, 500))
bg_width = bg_image.get_width()
bg_x = 0
bg_ratio = 3 / 5      # to slowdown background, far away illusion
bg_speed = scroll_speed * bg_ratio


tileset = pygame.image.load(os.path.join(BASE_DIR, 'graphics', 'elements', 'tilesetgrass.png')).convert()
grass_tile = tileset.subsurface(pygame.Rect(286, 96, 34, 26))
grass_image = pygame.transform.scale_by(grass_tile, 4.3)
grass_width = grass_image.get_width()
grass_x = 0


cactus_sheet = pygame.image.load(os.path.join(BASE_DIR, 'graphics', 'elements', 'cactus_sprite.png')).convert_alpha()
cactus_part = cactus_sheet.subsurface(pygame.Rect(78, 77, 33, 42))
cactus_image = pygame.transform.scale_by(cactus_part, 2)
cactus_mask = pygame.mask.from_surface(cactus_image)   # only the visible pixels count as a hit
cactus_rects = [cactus_image.get_rect(midbottom=(1300, ground_y)) for _ in range(4)]




powerup_sheet = pygame.image.load(os.path.join(BASE_DIR, 'graphics', 'elements', 'powerup2x.png')).convert_alpha()
powerup_part = powerup_sheet.subsurface(pygame.Rect(145, 113, 755, 822))
powerup_image = pygame.transform.scale(powerup_part, (30, 30))
powerup_mask = pygame.mask.from_surface(powerup_image)
powerup_rect = powerup_image.get_rect(midbottom=(1300, ground_y))  


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
action = IDLE                
frame = 0                    # intial frame on spritesheet pic
frame_delay = 70             # 70 milliseconds before next frame 
last_frame_time = pygame.time.get_ticks()
vertical_velocity = 0
is_jumping = False


start_button = pygame.Rect(0, 0, 200, 60)
start_button.center = (950, 220)

restart_button = pygame.Rect(0, 0, 200, 60)
restart_button.center = (600, 300)

quit_button = pygame.Rect(0, 0, 200, 60)
quit_button.center = (600, 370)


title_text = title_font.render('Dinoventure', True, 'white')
game_over_text = title_font.render('Game Over', True, 'white')
dark_overlay = pygame.Surface((1200, 500))  
dark_overlay.set_alpha(140)
dark_overlay.fill('black')


power_overlay = pygame.Surface((1200, 500))  
power_overlay.set_alpha(140)
power_overlay.fill('aquamarine2')



def draw_button(text, rect):
    pygame.draw.rect(screen, 'white', rect, border_radius=10)
    label = button_font.render(text, True, 'black')
    screen.blit(label, label.get_rect(center=rect.center))


def draw_boost_timer():
    # NEW: powerup icon, seconds left and a shrinking bar in the top left corner
    remaining = max(0, boost_duration - (pygame.time.get_ticks() - boost_start))
    screen.blit(powerup_image, (20, 20))
    timer_text = score_font.render(f'x2 {remaining / 1000:.1f}s', True, 'white')
    screen.blit(timer_text, (60, 24))


def random_gap():
    # the faster the game, the bigger the gap, so the player always has the same time to react
    return (random.randint(min_gap, max_gap) * scroll_speed // base_speed) * 0.8


def reset_cacti():
    # line the cacti up off the right edge, one after another, with random gaps
    x = 1200
    for cactus in cactus_rects:
        cactus.left = x + random_gap()
        cactus.bottom = ground_y
        x = cactus.right


def reset_powerup():
    # CHANGED: replaces reset_powerups(); a new run has no powerup on screen and the first one comes at 200 points
    global powerup_active, next_powerup_score
    powerup_active = False
    next_powerup_score = powerup_every


def spawn_powerup():
    global powerup_active, next_powerup_score
    powerup_rect.midbottom = (1250, ground_y)
    for cactus in sorted(cactus_rects, key=lambda c: c.x):      # CHANGED: it only checked one cactus before
        if powerup_rect.inflate(160, 0).colliderect(cactus):
            powerup_rect.left = cactus.right + 80
    powerup_active = True
    next_powerup_score = (score // powerup_every + 1) * powerup_every   # the next multiple of 200

def place_cactus(cactus):
    #random cactus placement 
    farthest = max(c.right for c in cactus_rects)
    cactus.left = max(1200, farthest) + random_gap()


def reset_game():
    global vertical_velocity, is_jumping, score, scroll_speed, boost_active, speed_carry
    dino_rect.midbottom = (100, ground_y)
    vertical_velocity = 0
    is_jumping = False
    score = 0
    scroll_speed = base_speed
    boost_active = False   # NEW: a new run starts without the effect
    speed_carry = 0        # NEW
    reset_cacti()
    reset_powerup()   


def update_animation():
    global frame, last_frame_time
    current_tick = pygame.time.get_ticks()
    if current_tick - last_frame_time >= frame_delay:
        last_frame_time = current_tick
        frame += 1
        if frame >= len(dino_frames[action]):
            frame = 0


def draw_scene():
    screen.blit(bg_image, (bg_x, 0))
    screen.blit(bg_image, (bg_x + bg_width, 0))
    for x in range(0, 1200 + grass_width, grass_width):
        screen.blit(grass_image, (x + grass_x, 390))
    screen.blit(dino_frames[action][frame], dino_rect)
    for cactus in cactus_rects:
        screen.blit(cactus_image, cactus)
    if powerup_active:   
        screen.blit(powerup_image, powerup_rect)

def music_player(filename, volume, times):
    pygame.mixer.music.load(os.path.join(BASE_DIR, 'music', filename))
    pygame.mixer.music.play(times)
    pygame.mixer.music.set_volume(volume)


def sound_effect(filename, volume):
    sound = pygame.mixer.Sound(os.path.join(BASE_DIR, 'music', filename))
    sound.play()
    sound.set_volume(volume)

reset_cacti()
high_score = highscore.load()

#menu sound
music_player('menu_bgm.ogg', 0.7, -1)
    

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN and game_state == PLAYING:
            if event.key == pygame.K_SPACE and not is_jumping:
                vertical_velocity = jump_strength
                sound_effect('jump.ogg', 1)
                is_jumping = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == MENU and start_button.collidepoint(event.pos):
                game_state = PLAYING
                music_player('bgm.ogg', 0.7, -1)
            elif game_state == GAME_OVER and restart_button.collidepoint(event.pos): 
                reset_game()
                music_player('bgm.ogg', 0.7, -1)
                game_state = PLAYING
            elif game_state == GAME_OVER and quit_button.collidepoint(event.pos):
                pygame.quit()
                exit()


    if game_state == MENU:
        action = IDLE
        update_animation()

    elif game_state == PLAYING:
        # NEW: while the powerup effect runs, the game is slower and the score counts double
        score_multiplier = 1
        slow_factor = 1
        if boost_active:
            boost_progress = (pygame.time.get_ticks() - boost_start) / boost_duration   # 0 at pickup -> 1 at the end
            if boost_progress >= 1:
                boost_active = False              # time is up, the normal pacing is back
            else:
                score_multiplier = 2
                slow_factor = boost_slow + (1 - boost_slow) * boost_progress   

        score += base_score_constant * score_multiplier    
        scroll_speed = min(base_speed + (score // points_per_speed), max_speed)  
        current_speed = scroll_speed * slow_factor        
        speed_carry += current_speed                       
        move = int(speed_carry)
        speed_carry -= move

        bg_speed = current_speed * bg_ratio                
        bg_x -= bg_speed
        if bg_x <= -bg_width:
            bg_x += bg_width
        grass_x -= move                                   
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
        
        for cactus in cactus_rects:
            cactus.x -= move                       
            if cactus.right < 0:
                place_cactus(cactus)
        
        
        if score >= next_powerup_score and not powerup_active:
            spawn_powerup()

        
        elif powerup_active:
            powerup_rect.x -= move                 
            if powerup_rect.right < 0:
                powerup_active = False

        dino_mask = pygame.mask.from_surface(dino_frames[action][frame])
        for cactus in cactus_rects:
            offset = (cactus.x - dino_rect.x, cactus.y - dino_rect.y)
            if dino_mask.overlap(cactus_mask, offset):
                game_state = GAME_OVER
                boost_active = False   
                music_player('game_over.ogg', 0.7, 1)
                if int(score) > high_score:
                    high_score = int(score)
                    highscore.save(high_score)
                break
        
        
        if powerup_active and game_state == PLAYING:
            offset = (powerup_rect.x - dino_rect.x, powerup_rect.y - dino_rect.y)
            if dino_mask.overlap(powerup_mask, offset):
                sound_effect('powerup2x.ogg', 1)
                screen.blit(power_overlay, (0, 0))
                powerup_active = False
                boost_active = True                    
                boost_start = pygame.time.get_ticks()  
                next_powerup_score = (score // powerup_every + 1) * powerup_every   
                
                
                
    draw_scene()

    if game_state == MENU:
        screen.blit(title_text, (800, 50))
        draw_button('Start', start_button)

    elif game_state == GAME_OVER:
        screen.blit(dark_overlay, (0, 0))
        screen.blit(game_over_text, game_over_text.get_rect(center=(600, 175)))
        draw_button('Restart', restart_button)
        draw_button('Quit', quit_button)

    if game_state != MENU:
        score_text = score_font.render(f'Score: {int(score)}', True, 'white')
        screen.blit(score_text, (950, 30))

    if boost_active:   #timer in the top left corner while the effect lasts
        draw_boost_timer()

    high_text = score_font.render(f'High Score: {high_score}', True, 'white')
    if game_state == MENU:
        screen.blit(high_text, high_text.get_rect(center=(950, 290)))
    else:
        screen.blit(high_text, (950, 60))
    
    



    pygame.display.update()
    clock.tick(60)
