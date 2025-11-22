import math, pygame, sys
from constantes import *
from clases import *
from funciones import *

def segunda_ley(clock, screen, heladera_img):
    #COMPLETAR
    while True:
        pygame.display.set_caption("Segunda ley - Refrigerador")

        keys = pygame.key.get_pressed()
        dt = clock.tick(120) / 1000.0
    
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        if keys[pygame.K_q]:
            return
    
        screen.fill("white")
        screen.blit(heladera_img, (200, 50))

        pygame.display.update()
