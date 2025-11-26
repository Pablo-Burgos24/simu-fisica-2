import pygame, sys
from constantes import *
from clases import Button
from funciones import aproximacion_arco, render_multi_line
from primera_ley import primera_ley
from segunda_ley import segunda_ley

pygame.init()
pygame.font.init()
pygame.mixer.init()
clock = pygame.time.Clock()

#Botones
pava_btn = Button(350, 400, PAVA_IMG, PAVA_IMG, 0.4)
heladera_btn = Button(725, 300, HELADERA_IMG, HELADERA_IMG, 0.2)
lista_botones = [pava_btn, heladera_btn]

aproximacion_arco()

run = True

while run:
    pygame.display.set_caption("Menu")

    #Variables
    keys = pygame.key.get_pressed()
    hover_any = False
    acciones = []

    for evento in pygame.event.get():
        if (evento.type == pygame.QUIT) or (keys[pygame.K_ESCAPE]):
            run = False
            pygame.quit()
            sys.exit()

    autores_text = "Autores:\n- Burgos Pablo\n- Genaro de Boni\n- Sajnovsky Jose\n- Maxi"

    title_h0 = H0.render("TERMODINAMICA", True, COLOR_TEXTO_1)
    primera_h2 = H2.render("Primera ley", True, COLOR_TEXTO_1)
    segunda_h2 = H2.render("Segunda Ley", True, COLOR_TEXTO_1)
    selecciona_h3 = H3.render("Seleccione su simulacion:", True, COLOR_TEXTO_1)

    SCREEN.blit(FONDO_IMG, (0, 0))
    SCREEN.blit(MESA_IMG_ESCALADA, (275, 500))

    SCREEN.blit(title_h0, (250, 25))
    SCREEN.blit(primera_h2, (350, 250))
    SCREEN.blit(segunda_h2, (725, 250))
    SCREEN.blit(selecciona_h3, (300, 150))
    render_multi_line(autores_text, H4, COLOR_TEXTO_1, 50, 550, 25)

    # Dibujar botones
    for b in lista_botones:
        action, hover = b.draw(SCREEN, False)
        acciones.append(action)
        hover_any |= hover
        
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if hover_any else pygame.SYSTEM_CURSOR_ARROW)

    # Acciones de los botones
    if acciones[0]:   # pava_btn
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        primera_ley(clock)

    if acciones[1]:   # heladera_btn
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        segunda_ley(clock)

    pygame.display.update()
