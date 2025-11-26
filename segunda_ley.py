import math, pygame, sys
from constantes import *
from clases import *
from funciones import *


# funciones para la segunda ley
def crear_particula_heladera(masa_actual, min, max):
    # Mapea la masa actual al nivel Y superior del agua
    nivel_superior_y = map_value(masa_actual, MASA_MIN, MASA_MAX, NIVEL_FONDO_HELADERA, NIVEL_TOPE_HELADERA)
    y_start = int(nivel_superior_y)
    y_end = NIVEL_FONDO_HELADERA
    if y_start > y_end:
        y_start = y_end
    # El spawn ocurre entre el nuevo nivel superior y el fondo
    px = random.randint(min, max)
    py = random.randint(y_start, y_end)
    return Particula(px, py, RADIO_PARTICULA, COLOR_FRIO, VELOCIDAD_MAX_INICIAL, TEMP_AMBIENTE, TEMP_EBULLICION)

def crear_particula_freezer(masa_actual, min, max):
    # Mapea la masa actual al nivel Y superior del agua
    nivel_superior_y = map_value(masa_actual, MASA_MIN, MASA_MAX, NIVEL_FONDO_FREEZER, NIVEL_TOPE_FREEZER)
    y_start = int(nivel_superior_y)
    y_end = NIVEL_FONDO_FREEZER
    if y_start > y_end:
        y_start = y_end
    # El spawn ocurre entre el nuevo nivel superior y el fondo
    px = random.randint(min, max)
    py = random.randint(y_start, y_end)
    return Particula(px, py, RADIO_PARTICULA, COLOR_FRIO, VELOCIDAD_MAX_INICIAL, TEMP_AMBIENTE, TEMP_EBULLICION)

# Aca si arranca la cuestion
def segunda_ley(clock):
    #COMPLETAR
    masa_actual = 1.5

    potencia_heladera = 500
    heladera_encendida = True
    paredes_heladera = [((268, 254), (573, 254)), ((573, 254), (573, 589)), ((573, 589), (268, 589)), ((268, 589), (268, 254))]
    particulas_heladera = []

    potencia_freezer = 1000
    paredes_freezer = [((268 , 80), (573, 80)), ((573, 80), (573, 220)), ((573, 220), (268, 220)), ((268, 220), (268, 80))]
    particulas_freezer = []

    # creo las particulas de la heladera
    cantidad_inicial = int(10)
    for _ in range(cantidad_inicial):
        particulas_heladera.append(crear_particula_heladera(masa_actual, MIN_SPAWN, MAX_SPAWN))

    # Creo tambien las del freezer
    cantidad_inicial = int(10)
    for _ in range(cantidad_inicial):
        particulas_freezer.append(crear_particula_freezer(masa_actual, MIN_SPAWN, MAX_SPAWN))

    particulas_combinadas = particulas_heladera + particulas_freezer

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

        temperatura_actual = actualizar_frio(dt, particulas_combinadas, potencia_heladera, potencia_freezer, masa_actual, heladera_encendida)

        # Manejo de las fisicas de las particulas de la heladera
        # a ver que hace esto
        for p in particulas_heladera:

            # Mapear la temperatura individual de la partícula a empuje y velocidad máxima
            temp_ratio_individual = (p.temperatura_individual - TEMP_AMBIENTE) / (TEMP_EBULLICION - TEMP_AMBIENTE)
            temp_ratio_individual = max(0, min(1, temp_ratio_individual))

            empuje_individual = temp_ratio_individual * MAX_EMPUJE_CALOR_PARTICULA
            max_vel_individual = MAX_VELOCIDAD_BASE + (temp_ratio_individual * (MAX_VELOCIDAD_TOPE - MAX_VELOCIDAD_BASE))

            for _ in range(SUB_STEPS):
                p.mover(SUB_STEPS) 

                for pared_p1, pared_p2 in paredes_heladera:
                    detectar_y_rebotar_circulo_linea(p, pared_p1, pared_p2)

                p.vy += GRAVEDAD / SUB_STEPS

                # Aplicar empuje basado en la temperatura individual de la partícula
                # El empuje se aplica en toda la columna de agua
                p.vy -= empuje_individual / SUB_STEPS 

                velocidad_actual = math.sqrt(p.vx**2 + p.vy**2)
                if velocidad_actual > max_vel_individual:
                    factor = max_vel_individual / velocidad_actual
                    p.vx *= factor
                    p.vy *= factor

            p.update_color(COLOR_CONGELADO, COLOR_FRIO, TEM_MIN_HELADERA, TEMP_AMBIENTE)


        # Manejo de fisicas de las particulas del freezer
        for p in particulas_freezer:

            # Mapear la temperatura individual de la partícula a empuje y velocidad máxima
            temp_ratio_individual = (p.temperatura_individual - TEMP_AMBIENTE) / (TEMP_EBULLICION - TEMP_AMBIENTE)
            temp_ratio_individual = max(0, min(1, temp_ratio_individual))

            empuje_individual = temp_ratio_individual * MAX_EMPUJE_CALOR_PARTICULA
            max_vel_individual = MAX_VELOCIDAD_BASE + (temp_ratio_individual * (MAX_VELOCIDAD_TOPE - MAX_VELOCIDAD_BASE))

            for _ in range(SUB_STEPS):
                p.mover(SUB_STEPS) 

                for pared_p1, pared_p2 in paredes_freezer:
                    detectar_y_rebotar_circulo_linea(p, pared_p1, pared_p2)

                p.vy += GRAVEDAD / SUB_STEPS

                # Aplicar empuje basado en la temperatura individual de la partícula
                # El empuje se aplica en toda la columna de agua
                p.vy -= empuje_individual / SUB_STEPS 

                velocidad_actual = math.sqrt(p.vx**2 + p.vy**2)
                if velocidad_actual > max_vel_individual:
                    factor = max_vel_individual / velocidad_actual
                    p.vx *= factor
                    p.vy *= factor

            p.update_color(COLOR_CONGELADO, COLOR_FRIO, TEM_MIN_FREEZER, TEMP_AMBIENTE)


        # Dibujo las cuestiones
        SCREEN.blit(FONDO_IMG, (0, 0))
        SCREEN.blit(pygame.transform.scale(MESA_IMG, (1500, 1200)), (-600, 400))

        texto_temp = FONT_HUD.render(f"Temp Prom: {temperatura_actual:.1f}°C", True, COLOR_TEXTO_1)

        SCREEN.blit(texto_temp, (X_MENU_ANCLA, 40))

        SCREEN.blit(HELADERA_IMG_ESCALADA, (200, 0))
        for i, j in paredes_heladera:
            pygame.draw.line(SCREEN, (255, 0, 0), i, j, 3)

        for i, j in paredes_freezer:
            pygame.draw.line(SCREEN, (255, 0, 0), i, j, 3)

        for p in particulas_heladera:
            p.dibujar(SCREEN)

        for p in particulas_freezer:
            p.dibujar(SCREEN)

        pygame.display.update()