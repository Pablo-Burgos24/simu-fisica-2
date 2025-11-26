import pygame, random
from constantes import *

class Particula():
    def __init__(self, x, y, radio, color_inicial, vel_max, temp_ambiente, temp_ebullicion):
        self.x = x
        self.y = y
        self.radio = radio
        self.color = color_inicial
        self.vx = random.uniform(-vel_max, vel_max)
        self.vy = random.uniform(-vel_max, vel_max)
        self.temperatura_individual = temp_ambiente 
        self.temp_ambiente_ref = temp_ambiente # Referencia para mapear color
        self.temp_ebullicion_ref = temp_ebullicion # Referencia para mapear color

    def mover(self, num_steps):
        self.x += self.vx / num_steps
        self.y += self.vy / num_steps

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), self.radio)
    
    def update_color(self, color_frio, color_caliente, temp_min = None, temp_max = None):
        """ Actualiza el color basado en la temperatura individual de la partícula. """
        # Mapea la temperatura individual de la partícula a un ratio de color

        # Si no se pasan min/max, usar los valores de referencia (modo calentamiento)
        if temp_min is None:
            temp_min = self.temp_ambiente_ref
        if temp_max is None:
            temp_max = self.temp_ebullicion_ref

        ratio = (self.temperatura_individual - temp_min) / (temp_max - temp_min)
        ratio = max(0, min(1, ratio)) # Asegura que el ratio esté entre 0 y 1
        
        r = int(color_frio[0] + (color_caliente[0] - color_frio[0]) * ratio)
        g = int(color_frio[1] + (color_caliente[1] - color_frio[1]) * ratio)
        b = int(color_frio[2] + (color_caliente[2] - color_frio[2]) * ratio)
        self.color = (r, g, b)


class ParticulaVapor():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radio = random.randint(4, 7)
        self.color = (210, 210, 210)
        self.vx = random.uniform(-0.4, 0.4)
        self.vy = random.uniform(-1.2, -0.7)
        self.tiempo_de_vida_total = VIDA_PARTICULA_VAPOR + random.uniform(-0.5, 0.5)
        self.tiempo_de_vida_restante = self.tiempo_de_vida_total
        self.esta_viva = True
        
        # Usamos una superficie individual para gestionar la transparencia
        self.surface = pygame.Surface((self.radio * 2, self.radio * 2), pygame.SRCALPHA)

    def update(self, dt):
        """Actualiza el tiempo de vida y la posición."""
        self.tiempo_de_vida_restante -= dt
        if self.tiempo_de_vida_restante <= 0:
            self.esta_viva = False
            return
        
        self.x += self.vx
        self.y += self.vy

    def dibujar(self, superficie_principal):
        """Dibuja la partícula con un efecto de 'fade out'."""
        if not self.esta_viva:
            return
        
        # Calcular alpha (transparencia) basado en la vida restante
        ratio_vida = self.tiempo_de_vida_restante / self.tiempo_de_vida_total
        alpha = int(150 * ratio_vida) # 150 es el alpha máximo (semi-transparente)
        alpha = max(0, min(alpha, 255))
        
        self.surface.fill((0, 0, 0, 0)) 
        pygame.draw.circle(self.surface, (*self.color, alpha), (self.radio, self.radio), self.radio)
        superficie_principal.blit(self.surface, (int(self.x - self.radio), int(self.y - self.radio)))


class Button():
    def __init__(self, x, y, image, selected_image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.selected_image = pygame.transform.scale(selected_image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface, is_selected):
        action = False
        pos = pygame.mouse.get_pos()

        # Mostrar imagen según si está seleccionada o no
        image = self.selected_image if is_selected else self.image
        surface.blit(image, (self.rect.x, self.rect.y))

        hover = self.rect.collidepoint(pos)

        # Detectar click
        if hover and pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
            #select_sound.play()
            self.clicked = True
            action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action, hover