import pygame, sys
from constantes import H0, H2, H4
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
    pava_img = pygame.image.load('Imagenes/pava.webp')
    heladera_img = pygame.image.load('Imagenes/heladera.png')
    pava_img_escalada = pygame.transform.scale(pava_img, (500, 500))
    heladera_img_escalada = pygame.transform.scale(heladera_img, (450, 600))
except pygame.error as e:
    print(f"Error al cargar la imagen: {e}")
    sys.exit()

#Botones
pava_btn = Button(350, 400, pava_img, pava_img, 0.25)
heladera_btn = Button(700, 300, heladera_img, heladera_img, 0.2)

aproximacion_arco()

run = True

while run:
    pygame.display.set_caption("Menu")
    keys = pygame.key.get_pressed()

    for evento in pygame.event.get():
        if (evento.type == pygame.QUIT) or (keys[pygame.K_ESCAPE]):
            run = False
            pygame.quit()
            sys.exit()

    title_h0 = H0.render("TERMODINAMICA", True, "black")
    primera_h2 = H2.render("Primera ley", True, "black")
    segunda_h2 = H2.render("Segunda Ley", True, "black")
    integrantes_h4 = H4.render("Burgos Pablo - Genaro de Boni - Sajnovsky Jose - Maxi", True, "black")

    screen.fill("white")
    screen.blit(title_h0, (250,60))
    screen.blit(primera_h2, (350,600))
    screen.blit(segunda_h2, (700,600))
    screen.blit(integrantes_h4, (100, 700))


    if pava_btn.draw(screen, False):
        primera_ley(clock, screen, pava_img_escalada, sonido_hervir)

    elif heladera_btn.draw(screen, False):
        segunda_ley(clock, screen, heladera_img_escalada)

    pygame.display.update()
