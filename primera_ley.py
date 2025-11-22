import math, pygame, sys
from constantes import *
from clases import *
from funciones import *

def primera_ley(clock, screen, pava_img, sonido_hervir):
    # Variables de Estado
    temperatura_actual = TEMP_AMBIENTE
    tiempo_simulado = 0.0
    esta_hirviendo = False
    pava_encendida = True 
    sonido_hervir_reproduciendose = False
    min_x_spawn = 265
    max_x_spawn = 500 

    # Variables de control
    potencia_pava = 2000
    masa_agua = 1.0

    # Variables de simulacion
    particulas = []
    particulas_vapor = []
    masa_vaporizada_acumulada = 0.0

    #Fuentes
    font_hud = pygame.font.Font(None, 30)

    # botones
    pot_down_rect = pygame.Rect(X_MENU_ANCLA, 80, 25, 25)
    pot_up_rect = pygame.Rect(X_MENU_ANCLA + 30, 80, 25, 25)
    masa_down_rect = pygame.Rect(X_MENU_ANCLA, 110, 25, 25)
    masa_up_rect = pygame.Rect(X_MENU_ANCLA + 30, 110, 25, 25)
    texto_plus = font_hud.render("+", True, COLOR_TEXTO_BOTON)
    texto_minus = font_hud.render("-", True, COLOR_TEXTO_BOTON)


    # Creación inicial de partículas
    cantidad_inicial = int(masa_agua * PARTICULAS_POR_KG)
    for _ in range(cantidad_inicial):
        particulas.append(crear_particula(masa_agua, min_x_spawn, max_x_spawn))


    while True:
        pygame.display.set_caption("Primera ley - Pava")

        keys = pygame.key.get_pressed()
        dt = clock.tick(120) / 1000.0
    
        for evento in pygame.event.get():
            if (evento.type == pygame.QUIT):
                pygame.quit()
                sys.exit()

            # LÓGICA DE CLICS
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if pot_up_rect.collidepoint(mouse_pos):
                    potencia_pava += 100
                elif pot_down_rect.collidepoint(mouse_pos):
                    potencia_pava -= 100; 
                    if potencia_pava < 0: potencia_pava = 0

                elif masa_up_rect.collidepoint(mouse_pos):
                    if masa_agua < MASA_MAX:
                        masa_agua += 0.1
                        for _ in range(int(PARTICULAS_POR_KG / 10)):
                            particulas.append(crear_particula(masa_agua, min_x_spawn, max_x_spawn))

                elif masa_down_rect.collidepoint(mouse_pos):
                    # Usar una comprobación más segura para floats
                    if masa_agua > MASA_MIN + 0.05: 
                        masa_agua -= 0.1
                        # Quitar partículas
                        for _ in range(int(PARTICULAS_POR_KG / 10)):
                            if particulas: particulas.pop()


            #Lógica de teclado
            if keys[pygame.K_q]:
                return
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    temperatura_actual = TEMP_AMBIENTE # Reinicia el promedio
                    tiempo_simulado = 0.0
                    esta_hirviendo = False
                    pava_encendida = True 

                    if sonido_hervir: # <<<--- DETENER SONIDO AL REINICIAR
                        sonido_hervir.stop()
                        sonido_hervir_reproduciendose = False

                    # Resetear partículas (y sus temperaturas individuales)
                    particulas.clear()
                    particulas_vapor.clear() 

                    cantidad_actual = int(masa_agua * PARTICULAS_POR_KG)
                    for _ in range(cantidad_inicial):
                        particulas.append(crear_particula(masa_agua, min_x_spawn, max_x_spawn)) 

                elif evento.key == pygame.K_SPACE:
                    pava_encendida = not pava_encendida 
                    if not pava_encendida: # <<<--- DETENER SONIDO AL APAGAR
                        if sonido_hervir:
                            sonido_hervir.stop()
                        sonido_hervir_reproduciendose = False

        # Hacemos global el acumulador para modificarlo
        globals()['masa_vaporizada_acumulada'] = masa_vaporizada_acumulada

        # DETERMINAR POTENCIA APLICADA
        potencia_aplicada_total = 0
        if pava_encendida:
            potencia_aplicada_total = potencia_pava

        temperatura_actual = actualizar_calor(dt, particulas, potencia_pava, masa_agua, pava_encendida)

        # DECIDIR SI HIERVE
        if temperatura_actual >= TEMP_EBULLICION - 0.1: # 99.9°C
            esta_hirviendo = True
        else:
            esta_hirviendo = False 


        # LÓGICA DE VAPORIZACIÓN Y SONIDO
        if esta_hirviendo:
            # Lógica de Sonido
            if pava_encendida and sonido_hervir and not sonido_hervir_reproduciendose:
                sonido_hervir.play(loops=-1) # loops=-1 para que se repita
                sonido_hervir_reproduciendose = True

            # Lógica de Vaporización
            P_neta_para_vaporizar = potencia_aplicada_total - P_perdida_total

            # Solo vaporiza si hay energía "extra" después de compensar las pérdidas
            if P_neta_para_vaporizar > 0 and masa_agua > 0:
                energia_para_vaporizar = P_neta_para_vaporizar * dt
                masa_a_vaporizar = energia_para_vaporizar / CALOR_LATENTE_VAPORIZACION

                masa_agua = max(0, masa_agua - masa_a_vaporizar)
                masa_vaporizada_acumulada += masa_a_vaporizar

                particulas_a_gestionar = int(masa_vaporizada_acumulada * PARTICULAS_POR_KG)

                if particulas_a_gestionar > 0:
                    masa_vaporizada_acumulada -= particulas_a_gestionar / PARTICULAS_POR_KG

                    for _ in range(particulas_a_gestionar):
                        if particulas:
                            # Quitamos la partícula de líquido con la temperatura más alta para simular vaporización
                            particula_a_quitar = max(particulas, key=lambda p: p.temperatura_individual)
                            particulas.remove(particula_a_quitar) 

                        for _ in range(PARTICULAS_VAPOR_POR_LIQUIDA):
                            particulas_vapor.append(crear_particula_vapor(masa_agua))

            # Si se acaba el agua
            if masa_agua <= 0:
                esta_hirviendo = False
                if sonido_hervir: 
                    sonido_hervir.stop()
                sonido_hervir_reproduciendose = False

            if sonido_hervir and sonido_hervir_reproduciendose: 
                sonido_hervir.stop()
                sonido_hervir_reproduciendose = False

        # El tiempo solo avanza si la pava está encendida
        if pava_encendida:
            tiempo_simulado += dt

        # BUCLE DE SUB-PASOS (Física de colisión y convección)
        for p in particulas:

            # Mapear la temperatura individual de la partícula a empuje y velocidad máxima
            temp_ratio_individual = (p.temperatura_individual - TEMP_AMBIENTE) / (TEMP_EBULLICION - TEMP_AMBIENTE)
            temp_ratio_individual = max(0, min(1, temp_ratio_individual))

            empuje_individual = temp_ratio_individual * MAX_EMPUJE_CALOR_PARTICULA
            max_vel_individual = MAX_VELOCIDAD_BASE + (temp_ratio_individual * (MAX_VELOCIDAD_TOPE - MAX_VELOCIDAD_BASE))

            for _ in range(SUB_STEPS):
                p.mover(SUB_STEPS) 

                for pared_p1, pared_p2 in PAREDES_CONTENEDOR:
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

            p.update_color(COLOR_FRIO, COLOR_CALIENTE)

        # ACTUALIZACIÓN DEL VAPOR
        for pv in particulas_vapor[:]:
            pv.update(dt)
            if not pv.esta_viva:
                particulas_vapor.remove(pv)

        #DIBUJAR EL HUD
        screen.fill("white")

        screen.blit(pava_img, (200, 100))

        for p in particulas:
            p.dibujar(screen)

        for pv in particulas_vapor:
            pv.dibujar(screen)

        pygame.draw.rect(screen, COLOR_BOTON, pot_up_rect)
        pygame.draw.rect(screen, COLOR_BOTON, pot_down_rect)
        pygame.draw.rect(screen, COLOR_BOTON, masa_up_rect)
        pygame.draw.rect(screen, COLOR_BOTON, masa_down_rect)

        screen.blit(texto_plus, (pot_up_rect.x + 7, pot_up_rect.y + 2))
        screen.blit(texto_minus, (pot_down_rect.x + 8, pot_down_rect.y + 2))
        screen.blit(texto_plus, (masa_up_rect.x + 7, masa_up_rect.y + 2))
        screen.blit(texto_minus, (masa_down_rect.x + 8, masa_down_rect.y + 2))

        color_estado = (0, 150, 0) if pava_encendida else (200, 0, 0) # Verde si ON, Rojo si OFF

        texto_temp = font_hud.render(f"Temp Prom: {temperatura_actual:.1f}°C", True, (0,0,0)) # Ahora es temp promedio
        texto_tiempo = font_hud.render(f"Tiempo: {tiempo_simulado:.1f} s", True, (0,0,0))
        texto_potencia = font_hud.render(f"Potencia: {potencia_pava:.0f} W", True, (0,0,0))
        texto_masa = font_hud.render(f"Masa: {masa_agua:.1f} kg", True, (0,0,0))
        texto_estado = font_hud.render(f"Estado: {'ENCENDIDA' if pava_encendida else 'APAGADA'}", True, color_estado)
        texto_particulas = font_hud.render(f"Partículas: {len(particulas)}", True, (100,100,100))
        texto_reset = font_hud.render("Presiona 'R' para reiniciar", True, (50,50,50))
        texto_toggle = font_hud.render("[ESPACIO] para On/Off", True, (50,50,50))
        texto_salir = font_hud.render("'Q' para salir", True, (50,50,50))
        texto_ambiente = font_hud.render(f"T. Ambiente: {TEMP_AMBIENTE:.1f}°C", True, (100, 100, 100))

        screen.blit(texto_temp, (X_MENU_ANCLA, 20))
        screen.blit(texto_tiempo, (X_MENU_ANCLA, 50))
        screen.blit(texto_potencia, (X_MENU_ANCLA + 65, 85)) 
        screen.blit(texto_masa, (X_MENU_ANCLA + 65, 115))   
        screen.blit(texto_estado, (X_MENU_ANCLA, 145))
        screen.blit(texto_particulas, (X_MENU_ANCLA, 175))
        screen.blit(texto_reset, (X_MENU_ANCLA, 205))
        screen.blit(texto_toggle, (X_MENU_ANCLA, 225))
        screen.blit(texto_salir, (X_MENU_ANCLA, 245))
        screen.blit(texto_ambiente, (X_MENU_ANCLA, 275))

        pygame.display.flip()