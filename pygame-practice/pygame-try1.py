import pygame
import os
from sys import exit

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

sky_image = pygame.image.load(os.path.join(BASE_DIR, 'graphics', 'elements', 'Background.png')).convert()
sky_surface = pygame.transform.scale(sky_image, (1200,500))

text_surface = text_font.render('Dinoventure', True, 'white')



screen.blit(sky_surface)
screen.blit(text_surface, (700, 50))
screen.blit(normal_grass_surface, (normal_grass_rect))


while True: 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:   
            pygame.quit()
            exit()

    
    

  





    
    pygame.display.update()
    clock.tick(60)

