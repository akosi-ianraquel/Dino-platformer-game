import pygame
import os
from sys import exit
import spritesheet

pygame.init()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

screen = pygame.display.set_mode((1200,500), vsync=1)
pygame.display.set_caption('Dinoventure')
clock = pygame.time.Clock() 
text_font = pygame.font.Font(os.path.join(BASE_DIR, 'Pixeltype.ttf'), 50)
gui_font = pygame.font.Font(os.path.join(BASE_DIR, 'Pixeltype.ttf'), 30)

class button:
    def __init__(self, text, pos, padding_x = 30, padding_y = 16, font = None):
        self.font = font or gui_font
        self.text_surf = self.font.render(text, True, 'black')

        # auto sizer for buttons
        width = self.text_surf.get_width() + padding_x
        height = self.text_surf.get_height() + padding_y

        self.image = pygame.image.load(os.path.join(BASE_DIR, 'graphics', 'elements', 'ui', 'button', '1.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))

        self.top_rect = pygame.Rect(pos, (width, height))
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

    def set_center(self, pos):
        self.top_rect.center = pos
        self.text_rect.center = pos

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.top_rect.collidepoint(event.pos))

    def draw(self):
        screen.blit(self.image, self.top_rect)
        screen.blit(self.text_surf, self.text_rect)



pygame.mixer.music.load(os.path.join(BASE_DIR, 'music', 'menu_bgm.ogg'))
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)




tilesetgrass = pygame.image.load(os.path.join(BASE_DIR, 'graphics', 'elements', 'tilesetgrass.png')).convert()
tileset_part = pygame.Rect(286, 96, 34, 26)
tileset_part_subsurface = tilesetgrass.subsurface(tileset_part)
normal_grass_surface = pygame.transform.scale_by(tileset_part_subsurface, 4.3)
normal_grass_rect = normal_grass_surface.get_rect(midleft = (0, 400))


grass_width = normal_grass_surface.get_width()

main_background = pygame.image.load(os.path.join(BASE_DIR, 'graphics', 'elements', '7','1.png')).convert()
main_background_surface = pygame.transform.scale(main_background, (1200,500))


text_surface = text_font.render('Dinoventure', True, 'white')


doux_spritesheet_image = pygame.image.load(os.path.join(BASE_DIR, 'graphics','characters','sheets','character_doux.png')).convert_alpha()
doux_sprite_sheet = spritesheet.SpriteSheet(doux_spritesheet_image)
doux_rect = doux_sprite_sheet.get_image(0, 24, 24, 3, 'BLACK').get_rect(midbottom = (100, 400))


#doux animation list 
animation_list = []
animation_steps = [4, 6, 3, 3]
action = 0 #0 for idle, initialized value yan pre
last_update = pygame.time.get_ticks()
animation_perframe_cooldown = 70 #miliseconds between frames before load second frame
current_frame = 0
step_counter = 0


#jumping "physics" 
ground_y = 400  
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
bg_scroll = 0

bg_images = []
for i in range(1, 5):
    bg_image = pygame.image.load(os.path.join(BASE_DIR, 'graphics','elements','7', f'{i}.png')).convert_alpha()
    bg_image = pygame.transform.scale(bg_image, (1200, 500))
    bg_images.append(bg_image)
bg_width = bg_images[0].get_width()

def draw_background(target = None):
    target = target if target is not None else screen
    speed = 0.3
    for layer in bg_images:
        offset = (bg_scroll * speed) % bg_width
        tiles_needed = (1200 // bg_width) + 2
        for x in range(-1, tiles_needed):
            target.blit(layer, (x * bg_width - offset, 0))
        speed += 0.3




#menu states erp
MAIN_MENU = 'MAIN_MENU'
PLAYING = 'PLAYING'
PAUSED = 'PAUSED'
game_state = MAIN_MENU



pause_btn = button('||', (50, 50))

pause_box = pygame.Rect(0, 0, 320, 230)
pause_box.center = (600, 250)

btn_main_menu = button('Main Menu', (0, 0))
btn_main_menu.set_center((600, 195))

btn_resume = button('Resume', (0, 0))
btn_resume.set_center((600, 250))

btn_quit = button('Quit', (0, 0))
btn_quit.set_center((600, 305))

menu_button_font = pygame.font.Font(os.path.join(BASE_DIR, 'Pixeltype.ttf'), 55)

btn_start_game = button('Start', (0, 0), padding_x = 60, padding_y = 30, font = menu_button_font)
btn_start_game.set_center((1000, 220))

btn_quit_menu = button('Quit', (0, 0), padding_x = 60, padding_y = 30, font = menu_button_font)
btn_quit_menu.set_center((1000, 300))

menu_render_surface = pygame.Surface((1200, 500))
MENU_ZOOM = 1.6

DINO_START_POS = (100, 400)  #reference for original posistions

def reset_dino():
    global action, current_frame, vertical_velocity, is_jumping
    doux_rect.midbottom = DINO_START_POS
    action = 0
    current_frame = 0
    vertical_velocity = 0
    is_jumping = False


def draw_game_frame():
    draw_background()
    screen.blit(text_surface, (700, 50))
    for i in range(0, 1900, grass_width):
        screen.blit(normal_grass_surface, (i + grass_scroll, 390))
    screen.blit(animation_list[action][current_frame], doux_rect)

#updater game main loop
while True:
    #event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:   
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if game_state == PLAYING and event.key == pygame.K_SPACE and not is_jumping:
                vertical_velocity = jump_strength
                is_jumping = True
            elif game_state == PAUSED:
                if event.key == pygame.K_ESCAPE:
                    game_state = PLAYING
                    pygame.mixer.music.unpause()
            
            elif event.key == pygame.K_ESCAPE:
                    game_state = PAUSED
                    pygame.mixer.music.pause()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == MAIN_MENU:
                if btn_start_game.is_clicked(event):
                    game_state = PLAYING
                    pygame.mixer.music.load(os.path.join(BASE_DIR, 'music', 'bgm.ogg'))
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(0.3)

                elif btn_quit_menu.is_clicked(event):
                    pygame.quit()
                    exit()

            elif game_state == PLAYING:
                if pause_btn.is_clicked(event):
                    game_state = PAUSED
                    pygame.mixer.music.pause()

            elif game_state == PAUSED:
                if btn_resume.is_clicked(event):
                    game_state = PLAYING
                    pygame.mixer.music.unpause()

                elif btn_main_menu.is_clicked(event):
                    reset_dino()
                    game_state = MAIN_MENU
                    pygame.mixer.music.load(os.path.join(BASE_DIR, 'music', 'menu_bgm.ogg'))
                    pygame.mixer.music.play(-1) 
                    pygame.mixer.music.set_volume(0.4)

                elif btn_quit.is_clicked(event):
                    pygame.quit()
                    exit()

    if game_state == MAIN_MENU:
        action = 0  #idle animation in main menu
        
        current_time = pygame.time.get_ticks()
        if current_time - last_update >= animation_perframe_cooldown:
            current_frame += 1
            last_update = current_time
            if current_frame >= len(animation_list[action]):
                current_frame = 0

        #freeze
        draw_background(menu_render_surface)
        for i in range(0, 1900, grass_width):
            menu_render_surface.blit(normal_grass_surface, (i + grass_scroll, 390))
        menu_render_surface.blit(animation_list[action][current_frame], doux_rect)

        #zoom in effect function for main menu 
        crop_w, crop_h = int(1200 / MENU_ZOOM), int(500 / MENU_ZOOM)
        crop_x = max(0, min(doux_rect.centerx - crop_w // 2, 1200 - crop_w))
        crop_y = max(0, min(doux_rect.centery - crop_h // 2, 500 - crop_h))
        zoomed = pygame.transform.scale(
            menu_render_surface.subsurface((crop_x, crop_y, crop_w, crop_h)),
            (1200, 500)
        )
        screen.blit(zoomed, (0, 0))

        # title and buttons draw 
        screen.blit(text_surface, (700, 50))
        btn_start_game.draw()
        btn_quit_menu.draw()

        pygame.display.update()
        clock.tick(60)
        continue

    if game_state == PAUSED:
        draw_game_frame()  # frozen elemnets bg_scroll/grass_scroll/doux_rect 

        overlay = pygame.Surface((1200, 500), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, (120, 120, 120), pause_box, border_radius=12)
        btn_main_menu.draw()
        btn_resume.draw()
        btn_quit.draw()

        pygame.display.update()
        clock.tick(60)
        continue

    # game_state == PLAYING
    bg_scroll += scroll_speed * 0.7

    grass_scroll -= scroll_speed
    if abs(grass_scroll) > grass_width:
        grass_scroll = 0

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

    draw_game_frame()
    pause_btn.draw()

    pygame.display.update()
    clock.tick(60)