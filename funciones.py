import math, random
from clases import *
from constantes import SCREEN, TEM_MIN_HELADERA, TEM_MIN_FREEZER

def detectar_y_rebotar_circulo_linea(particula, p1, p2):
    dx_line = p2[0] - p1[0]; dy_line = p2[1] - p1[1]; longitud_cuadrada = dx_line**2 + dy_line**2
    if longitud_cuadrada == 0: return
    t = ((particula.x - p1[0]) * dx_line + (particula.y - p1[1]) * dy_line) / longitud_cuadrada
    t = max(0, min(1, t)) 
    punto_mas_cercano_x = p1[0] + t * dx_line; punto_mas_cercano_y = p1[1] + t * dy_line
    distancia_x = particula.x - punto_mas_cercano_x; distancia_y = particula.y - punto_mas_cercano_y
    distancia = math.sqrt(distancia_x**2 + distancia_y**2)
    if distancia < particula.radio and distancia > 0.001:
        normal_x = distancia_x / distancia; normal_y = distancia_y / distancia
        overlap = particula.radio - distancia
        particula.x += normal_x * overlap; particula.y += normal_y * overlap
        dot_product = particula.vx * normal_x + particula.vy * normal_y
        particula.vx -= 2 * dot_product * normal_x; particula.vy -= 2 * dot_product * normal_y
        particula.vx *= 0.95


def map_value(value, from_low, from_high, to_low, to_high):
    """ Mapea un valor de un rango a otro """
    value = max(from_low, min(from_high, value))
    return to_low + (value - from_low) * (to_high - to_low) / (from_high - from_low)


def crear_particula(masa_actual, min, max):
    # Mapea la masa actual al nivel Y superior del agua
    nivel_superior_y = map_value(masa_actual, MASA_MIN, MASA_MAX, Y_NIVEL_FONDO, Y_NIVEL_TOPE)
    y_start = int(nivel_superior_y)
    y_end = Y_NIVEL_FONDO
    if y_start > y_end:
        y_start = y_end
    # El spawn ocurre entre el nuevo nivel superior y el fondo
    px = random.randint(min, max)
    py = random.randint(y_start, y_end) 
    
    return Particula(px, py, RADIO_PARTICULA, COLOR_FRIO, VELOCIDAD_MAX_INICIAL, TEMP_AMBIENTE, TEMP_EBULLICION)


def crear_particula_vapor(masa_actual, min, max):
    """Crea una partícula de vapor en la superficie del agua."""
    nivel_superior_y = map_value(masa_actual, MASA_MIN, MASA_MAX, Y_NIVEL_FONDO, Y_NIVEL_TOPE)
    px = random.randint(min + 20, max - 20)
    py = nivel_superior_y + random.uniform(-5, 5) # Ligeramente sobre la superficie
    
    return ParticulaVapor(px, py)


def actualizar_calor(dt, particulas, potencia, masa, pava_encendida):
    global P_perdida_total, temperatura_actual
    
    if not particulas:
        temperatura_actual = TEMP_AMBIENTE
        return

    particulas_en_zona_calor = [p for p in particulas if p.y > ZONA_CALOR_Y]
    masa_por_par = masa / len(particulas)

    # Calentamiento solo si está encendida
    if pava_encendida and particulas_en_zona_calor:
        potencia_ind = potencia / len(particulas_en_zona_calor)
    else:
        potencia_ind = 0

    P_perdida_total = 0

    for p in particulas:
        # ENFRIAMIENTO
        if p.temperatura_individual > TEMP_AMBIENTE:
            P_loss = K_ENFRIAMIENTO_PARTICULA * (p.temperatura_individual - TEMP_AMBIENTE)
            energia_loss = P_loss * dt
            dT_loss = energia_loss / (masa_por_par * CALOR_ESPECIFICO_AGUA)
            p.temperatura_individual = max(TEMP_AMBIENTE, p.temperatura_individual - dT_loss)

            P_perdida_total += P_loss

        # CALENTAMIENTO
        if pava_encendida and p in particulas_en_zona_calor:
            energia_gain = potencia_ind * dt
            dT_gain = energia_gain / (masa_por_par * CALOR_ESPECIFICO_AGUA)
            p.temperatura_individual = min(TEMP_EBULLICION, p.temperatura_individual + dT_gain)

    temperatura_actual = sum(p.temperatura_individual for p in particulas) / len(particulas)

    return temperatura_actual


def actualizar_frio(dt, particulas, potencia_heladera, potencia_freezer, masa, heladera_encendida):
    global P_ganancia_total, temperatura_actual

    # Partículas dentro de la zona de enfriamiento general
    particulas_en_heladera = [p for p in particulas if p.y < NIVEL_FONDO_HELADERA]

    # Partículas dentro del freezer (enfriamiento más intenso)
    particulas_en_freezer = [p for p in particulas if p.y < NIVEL_FONDO_FREEZER]

    # Cada partícula representa una fracción de la masa total
    masa_por_par = masa / len(particulas)

    # Potencia de enfriamiento por partícula
    if heladera_encendida:
        # La potencia total se divide entre las partículas afectadas
        pot_ind_heladera = (potencia_heladera / max(1, len(particulas_en_heladera)))
        pot_ind_freezer  = (potencia_freezer  / max(1, len(particulas_en_freezer)))
    else:
        pot_ind_heladera = 0
        pot_ind_freezer  = 0

    # Seguimiento de toda la energía absorbida por el sistema (frío)
    P_ganancia_total = 0

    for p in particulas:

        # ENFRIAMIENTO POR LA HELADERA
        if heladera_encendida and p in particulas_en_heladera:
            energia_loss = pot_ind_heladera * dt
            dT_loss = energia_loss / (masa_por_par * CALOR_ESPECIFICO_AGUA)
            p.temperatura_individual = max(TEM_MIN_HELADERA, p.temperatura_individual - dT_loss)

        # ENFRIAMIENTO MÁS INTENSO POR EL FREEZER
        if heladera_encendida and p in particulas_en_freezer:
            energia_loss = pot_ind_freezer * dt
            dT_loss = energia_loss / (masa_por_par * CALOR_ESPECIFICO_AGUA)
            p.temperatura_individual = max(TEM_MIN_FREEZER, p.temperatura_individual - dT_loss)

    # Temperatura promedio del sistema
    temperatura_actual = sum(p.temperatura_individual for p in particulas) / len(particulas)

    return temperatura_actual


def aproximacion_arco():
    global PAREDES_CONTENEDOR
    puntos_del_arco = []
    num_segmentos = 10 
    centro_x_arco = 390
    centro_y_arco = 450
    radio_x_arco = 165
    radio_y_arco = 50  
    for i in range(num_segmentos + 1):
        angulo = (i / num_segmentos) * math.pi
        x = centro_x_arco + radio_x_arco * math.cos(angulo + math.pi)
        y = centro_y_arco + radio_y_arco * math.sin(angulo)
        puntos_del_arco.append((int(x), int(y)))
    for i in range(num_segmentos):
        PAREDES_CONTENEDOR.append((puntos_del_arco[i], puntos_del_arco[i+1]))
    PAREDES_CONTENEDOR.append(((230, 450), puntos_del_arco[0]))
    PAREDES_CONTENEDOR.append(((550, 450), puntos_del_arco[-1]))


def render_multi_line(text, font, color, x, y, fsize):
    lines = text.splitlines()
    for i, l in enumerate(lines):
        SCREEN.blit(font.render(l, True, color), (x, y + fsize*i))