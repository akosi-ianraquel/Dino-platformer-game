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







#updater game main loop
while True:
    #event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:   
            pygame.quit()
            exit()






       
    pygame.display.update()
    clock.tick(60)