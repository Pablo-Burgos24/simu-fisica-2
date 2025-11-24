import pygame, sys
from constantes import H0, H2, H3, H4
from clases import Button
from funciones import aproximacion_arco
from primera_ley import primera_ley
from segunda_ley import segunda_ley

pygame.init()
pygame.font.init()
pygame.mixer.init()
clock = pygame.time.Clock()

#Dimensiones de ventana
ancho, alto = 1280, 720
screen = pygame.display.set_mode((ancho, alto))


# Sonidos
try:
    sonido_hervir = pygame.mixer.Sound("Sonidos/boiling.wav") 
    sonido_hervir.set_volume(0.5)
except pygame.error as e:
    print(f"Error al cargar el sonido: {e}")
    sonido_hervir = None

# Imagenes
try:
    pava_img = pygame.image.load('Imagenes/pava.png')
    heladera_img = pygame.image.load('Imagenes/heladera.png')
    mesa_img = pygame.image.load('Imagenes/mesa.png')
    fondo_img = pygame.image.load('Imagenes/pizarra_fondo.jpg')
    pava_img_escalada = pygame.transform.scale(pava_img, (500, 500))
    heladera_img_escalada = pygame.transform.scale(heladera_img, (450, 650))
    mesa_img_escalada = pygame.transform.scale(mesa_img, (750, 600))
except pygame.error as e:
    print(f"Error al cargar la imagen: {e}")
    sys.exit()

#Botones
pava_btn = Button(350, 400, pava_img, pava_img, 0.4)
heladera_btn = Button(725, 300, heladera_img, heladera_img, 0.2)
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

    title_h0 = H0.render("TERMODINAMICA", True, "white")
    primera_h2 = H2.render("Primera ley", True, "white")
    segunda_h2 = H2.render("Segunda Ley", True, "white")
    selecciona_h3 = H3.render("Seleccione su simulacion:", True, "white")
    integrantes_h4 = H4.render("Burgos Pablo - Genaro de Boni - Sajnovsky Jose - Maxi", True, "white")

    screen.blit(fondo_img, (0, 0))
    screen.blit(mesa_img_escalada, (275, 500))

    screen.blit(title_h0, (250, 25))
    screen.blit(primera_h2, (350, 250))
    screen.blit(segunda_h2, (725, 250))
    screen.blit(selecciona_h3, (300, 150))
    screen.blit(integrantes_h4, (400, 700))

    # Dibujar botones
    for b in lista_botones:
        action, hover = b.draw(screen, False)
        acciones.append(action)
        hover_any |= hover
        
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if hover_any else pygame.SYSTEM_CURSOR_ARROW)

    # Acciones de los botones
    if acciones[0]:   # pava_btn
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        primera_ley(clock, screen, pava_img_escalada, sonido_hervir)

    if acciones[1]:   # heladera_btn
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        segunda_ley(clock, screen, heladera_img_escalada)

    pygame.display.update()
