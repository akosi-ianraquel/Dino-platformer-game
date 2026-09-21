import pygame
import os
from sys import exit
import spritesheet

pygame.init()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

screen = pygame.display.set_mode((1200,500))
pygame.display.set_caption('Dinoventure')
clock = pygame.time.Clock() 
text_font = pygame.font.Font(os.path.join(BASE_DIR, 'Pixeltype.ttf'), 50)

tilesetgrass = pygame.image.load(os.path.join(BASE_DIR, 'graphics', 'elements', 'tilesetgrass.png')).convert()
tileset_part = pygame.Rect(0, 96, 96, 27)
tileset_part_subsurface = tilesetgrass.subsurface(tileset_part)
normal_grass_surface = pygame.transform.scale_by(tileset_part_subsurface, 4)
normal_grass_rect = normal_grass_surface.get_rect(midleft = (0, 450))


grass_width = normal_grass_surface.get_width()

sky_image = pygame.image.load(os.path.join(BASE_DIR, 'graphics', 'elements', 'background_default.png')).convert()
sky_surface = pygame.transform.scale(sky_image, (1200,500))

text_surface = text_font.render('Dinoventure', True, 'white')


doux_spritesheet_image = pygame.image.load(os.path.join(BASE_DIR, 'graphics','characters','sheets','character_doux.png')).convert_alpha()
doux_sprite_sheet = spritesheet.SpriteSheet(doux_spritesheet_image)
doux_rect = doux_sprite_sheet.get_image(0, 24, 24, 3, 'BLACK').get_rect(midbottom = (100, 430))


#doux animation frames for idle
animation_list = []
animation_steps = [4, 6, 3, 3]
action = 0 #0 for idle, 1 for run, 2 for jump
last_update = pygame.time.get_ticks()
animation_perframe_cooldown = 80 #milliseconds between frames before load second frame
current_frame = 0
step_counter = 0


#jumping "physics"
ground_y = 430  
vertical_velocity = 0
gravity = 1.2
jump_strength = -22
is_jumping = False




for animation in animation_steps:
    temp_img_list = []
    for _ in range(animation):
        temp_img_list.append(doux_sprite_sheet.get_image(step_counter, 24, 24, 3, 'BLACK'))
        step_counter += 1
    animation_list.append(temp_img_list)






scroll_speed = 7
grass_scroll = 0    




#updater game main loop
while True:
    #event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:   
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not is_jumping:
                vertical_velocity = jump_strength
                is_jumping = True



     
    screen.blit(sky_surface, (0, 0))
    screen.blit(text_surface, (700, 50))
    
   
    grass_scroll -= scroll_speed
    if abs(grass_scroll) > grass_width:
        grass_scroll = 0
        

    
    for i in range(0, 1900, grass_width - 96):
        screen.blit(normal_grass_surface, (i + grass_scroll, 420))  

    prev_action = action
    

    vertical_velocity += gravity
    doux_rect.y += vertical_velocity

    if doux_rect.bottom >= ground_y:
        doux_rect.bottom = ground_y
        vertical_velocity = 0
        is_jumping = False

    action = 2 if is_jumping else 1

    #doux animation
    if action != prev_action:
        current_frame = 0

    current_time = pygame.time.get_ticks()
    if current_time - last_update >= animation_perframe_cooldown:
        current_frame += 1
        last_update = current_time
        if current_frame >= len(animation_list[action]):
            current_frame = 0
        
    
    

    screen.blit(animation_list[action][current_frame], doux_rect)


    pygame.display.update()
    clock.tick(60)

