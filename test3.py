import math
import random
import sys

import pygame

# 1. Inicialización
pygame.init()
pygame.font.init() # Inicializa el módulo de fuentes
pygame.mixer.init() # <<<--- INICIALIZAR EL MIXER DE SONIDO
ancho, alto = 1280, 720
screen = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Simulación Termodinámica")
clock = pygame.time.Clock()

# Fuente para el HUD
font_hud = pygame.font.Font(None, 30)


# --- CLASE PARTICULA (MODIFICADA) ---
class Particula:
    def __init__(self, x, y, radio, color_inicial, vel_max, temp_ambiente, temp_ebullicion):
        self.x = x
        self.y = y
        self.radio = radio
        self.color = color_inicial
        self.vx = random.uniform(-vel_max, vel_max)
        self.vy = random.uniform(-vel_max, vel_max)
        
        # ¡NUEVO! Temperatura individual de la partícula
        self.temperatura_individual = temp_ambiente 
        self.temp_ambiente_ref = temp_ambiente # Referencia para mapear color
        self.temp_ebullicion_ref = temp_ebullicion # Referencia para mapear color

    def mover(self, num_steps):
        self.x += self.vx / num_steps
        self.y += self.vy / num_steps

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), self.radio)
    
    # --- MÉTODO MODIFICADO ---
    def update_color(self, color_frio, color_caliente):
        """ Actualiza el color basado en la temperatura individual de la partícula. """
        # Mapea la temperatura individual de la partícula a un ratio de color
        ratio = (self.temperatura_individual - self.temp_ambiente_ref) / \
                (self.temp_ebullicion_ref - self.temp_ambiente_ref)
        ratio = max(0, min(1, ratio)) # Asegura que el ratio esté entre 0 y 1
        
        r = int(color_frio[0] + (color_caliente[0] - color_frio[0]) * ratio)
        g = int(color_frio[1] + (color_caliente[1] - color_frio[1]) * ratio)
        b = int(color_frio[2] + (color_caliente[2] - color_frio[2]) * ratio)
        self.color = (r, g, b)

# --- CLASE PARTICULA DE VAPOR ---
class ParticulaVapor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radio = random.randint(4, 7)
        self.color = (210, 210, 210) # Color de vapor
        self.vx = random.uniform(-0.4, 0.4)
        self.vy = random.uniform(-1.2, -0.7) # Siempre hacia arriba
        
        self.tiempo_de_vida_total = VIDA_PARTICULA_VAPOR + random.uniform(-0.5, 0.5)
        self.tiempo_de_vida_restante = self.tiempo_de_vida_total
        self.esta_viva = True
        
        # Usamos una superficie individual para gestionar el alpha (transparencia)
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
        
        # Limpiar la superficie local (a transparente)
        self.surface.fill((0, 0, 0, 0)) 
        
        # Dibujar el círculo en la superficie local con el alpha calculado
        pygame.draw.circle(self.surface, (*self.color, alpha), (self.radio, self.radio), self.radio)
        
        # "Blitear" (copiar) la superficie local a la pantalla principal
        superficie_principal.blit(self.surface, (int(self.x - self.radio), int(self.y - self.radio)))

# --- FUNCIÓN DE COLISIÓN
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


# --- CONFIGURACIÓN DE GRÁFICOS Y FÍSICA ---
ruta_imagen = 'pava.webp'
try:
    pava_img = pygame.image.load(ruta_imagen)
    pava_img_escalada = pygame.transform.scale(pava_img, (500, 500))
except pygame.error as e:
    print(f"Error al cargar la imagen: {e}")
    sys.exit()

# --- Cargar Sonido ---
try:
    # ¡Asegúrate de tener un archivo "boiling.wav" en la misma carpeta!
    sonido_hervir = pygame.mixer.Sound("boiling.wav") 
    sonido_hervir.set_volume(0.5) # Opcional: ajustar volumen (0.0 a 1.0)
except pygame.error as e:
    print(f"Error al cargar el sonido: {e}")
    sonido_hervir = None # Si falla, el sonido no se reproducirá


# CONFIGURACIÓN DE SUB-PASOS
SUB_STEPS = 8

# Constantes Termodinámicas
CALOR_ESPECIFICO_AGUA = 4186
TEMP_AMBIENTE = 20.0
TEMP_EBULLICION = 100.0
K_DISIPACION = 10.0 # Factor de disipación de calor al ambiente

# ¡NUEVO! Constantes para la transferencia de calor entre partículas
K_CALOR_ZONA_CALOR = 1000.0 # Cuánta potencia se transfiere a las partículas en la zona de calor
K_ENFRIAMIENTO_PARTICULA = 0.07 # Cuánta potencia pierde cada partícula al ambiente

# Constantes Físicas Base
GRAVEDAD = 0.02
MAX_EMPUJE_CALOR_PARTICULA = 0.0005 # Empuje que genera una partícula caliente
MAX_VELOCIDAD_BASE = 2.0
MAX_VELOCIDAD_TOPE = 5.0

# CONSTANTES DE NIVEL (CORREGIDAS)
MASA_MIN = 0.5 # kg
MASA_MAX = 2.0 # kg
Y_NIVEL_FONDO = 450 # Y-pixel del fondo real de la pava (coincide con centro_y_arco)
Y_NIVEL_TOPE = 160 # Y-pixel para la masa máxima


# CONSTANTES DE VAPORIZACIÓN
CALOR_LATENTE_VAPORIZACION = 2260000 # J/kg (Energía para convertir agua en vapor)
PARTICULAS_VAPOR_POR_LIQUIDA = 3      # Cuántas partículas de vapor crea 1 de líquido
VIDA_PARTICULA_VAPOR = 2.5           # Segundos que vive una partícula de vapor

def map_value(value, from_low, from_high, to_low, to_high):
    """ Mapea un valor de un rango a otro """
    # Asegurar que el valor esté dentro del rango original
    value = max(from_low, min(from_high, value))
    return to_low + (value - from_low) * (to_high - to_low) / (from_high - from_low)

# Variables de Control (Mutables)
POTENCIA_PAVA = 2000.0
MASA_AGUA = 1.0 # Empezamos con 1.0 kg

# Variables de Estado
# Ahora, 'temperatura_actual' representará el promedio del agua, útil para el HUD.
temperatura_actual = TEMP_AMBIENTE
tiempo_simulado = 0.0
esta_hirviendo = False
pava_encendida = True 
sonido_hervir_reproduciendose = False 

# Constantes de Color
COLOR_FRIO = (0,100,255); COLOR_CALIENTE =  (255,0,0)

# Coordenadas de las paredes
PAREDES_CONTENEDOR = [
    ((260, 150), (505, 150)), ((505, 150), (520, 200)), ((520, 200), (535, 300)),
    ((535, 300), (550, 450)), ((230, 450), (245, 300)), ((245, 300), (260, 150)),
]

# --- APROXIMACIÓN DEL ARCO INFERIOR ---
puntos_del_arco = []
num_segmentos = 10 
centro_x_arco = 390; centro_y_arco = 450; radio_x_arco = 165; radio_y_arco = 50  
for i in range(num_segmentos + 1):
    angulo = (i / num_segmentos) * math.pi
    x = centro_x_arco + radio_x_arco * math.cos(angulo + math.pi)
    y = centro_y_arco + radio_y_arco * math.sin(angulo)
    puntos_del_arco.append((int(x), int(y)))
for i in range(num_segmentos):
    PAREDES_CONTENEDOR.append((puntos_del_arco[i], puntos_del_arco[i+1]))
PAREDES_CONTENEDOR.append(((230, 450), puntos_del_arco[0]))
PAREDES_CONTENEDOR.append(((550, 450), puntos_del_arco[-1])) 


# --- DEFINICIÓN DE BOTONES DEL MENÚ 
X_MENU_ANCLA = 750
COLOR_BOTON = (220, 220, 220)
COLOR_TEXTO_BOTON = (0, 0, 0)
pot_down_rect = pygame.Rect(X_MENU_ANCLA, 80, 25, 25); pot_up_rect = pygame.Rect(X_MENU_ANCLA + 30, 80, 25, 25)
masa_down_rect = pygame.Rect(X_MENU_ANCLA, 110, 25, 25); masa_up_rect = pygame.Rect(X_MENU_ANCLA + 30, 110, 25, 25)
texto_plus = font_hud.render("+", True, COLOR_TEXTO_BOTON); texto_minus = font_hud.render("-", True, COLOR_TEXTO_BOTON)


#VARIABLES DE SIMULACIÓN Y FUNCIÓN DE CREACIÓN ---
PARTICULAS = []
PARTICULAS_VAPOR = [] # Lista para el vapor
masa_vaporizada_acumulada = 0.0 # Acumulador para la vaporización

RADIO_PARTICULA = 5
VELOCIDAD_MAX_INICIAL = 2.0 
PARTICULAS_POR_KG = 150 

min_x_spawn = 265; max_x_spawn = 500 

# --- FUNCIÓN CREAR_PARTICULA (CORREGIDA) ---
def crear_particula(masa_actual):
    """Crea y devuelve una nueva partícula DENTRO del volumen de agua actual."""
    
    # Mapea la masa actual al nivel Y superior del agua
    # MASA_MIN (0.5kg) -> Y_NIVEL_FONDO (450)
    # MASA_MAX (2.0kg) -> Y_NIVEL_TOPE (160)
    nivel_superior_y = map_value(masa_actual, MASA_MIN, MASA_MAX, Y_NIVEL_FONDO, Y_NIVEL_TOPE)
    
    # El spawn ocurre entre el nuevo nivel superior y el fondo
    px = random.randint(min_x_spawn, max_x_spawn)
    
    # --- LA CORRECCIÓN ESTÁ AQUÍ ---
    # Asegura que 'inicio' (nivel_superior_y) sea siempre <= 'fin' (Y_NIVEL_FONDO)
    y_start = int(nivel_superior_y)
    y_end = Y_NIVEL_FONDO
    
    # Si por alguna razón y_start > y_end (rango inválido), fíjalos
    if y_start > y_end:
        y_start = y_end
        
    py = random.randint(y_start, y_end) 
    # --- FIN DE LA CORRECCIÓN ---
    
    # ¡MODIFICADO! Se pasa TEMP_AMBIENTE y TEMP_EBULLICION a la partícula
    return Particula(px, py, RADIO_PARTICULA, COLOR_FRIO, VELOCIDAD_MAX_INICIAL, TEMP_AMBIENTE, TEMP_EBULLICION)

def crear_particula_vapor(masa_actual):
    """Crea una partícula de vapor en la superficie del agua."""
    # Mapea la masa al nivel Y de la superficie
    nivel_superior_y = map_value(masa_actual, MASA_MIN, MASA_MAX, Y_NIVEL_FONDO, Y_NIVEL_TOPE)
    
    # Rango de spawn en la superficie
    px = random.randint(min_x_spawn + 20, max_x_spawn - 20)
    py = nivel_superior_y + random.uniform(-5, 5) # Ligeramente sobre la superficie
    
    return ParticulaVapor(px, py)

# Creación inicial de partículas
cantidad_inicial = int(MASA_AGUA * PARTICULAS_POR_KG)
for _ in range(cantidad_inicial):
    PARTICULAS.append(crear_particula(MASA_AGUA))
    
run = True

# 2. Bucle Principal del Juego
while run:
    
    dt = clock.get_time() / 1000.0
    
    # A. Gestión de Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            run = False
        
        #LÓGICA DE CLICS (ACTUALIZADA PARA MASA)
        if evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if pot_up_rect.collidepoint(mouse_pos):
                POTENCIA_PAVA += 100
            elif pot_down_rect.collidepoint(mouse_pos):
                POTENCIA_PAVA -= 100; 
                if POTENCIA_PAVA < 0: POTENCIA_PAVA = 0
                
            elif masa_up_rect.collidepoint(mouse_pos):
                if MASA_AGUA < MASA_MAX:
                    MASA_AGUA += 0.1
                    # Añadir partículas (7 en este caso)
                    for _ in range(int(PARTICULAS_POR_KG / 10)):
                        PARTICULAS.append(crear_particula(MASA_AGUA))
                        
            elif masa_down_rect.collidepoint(mouse_pos):
                # Usar una comprobación más segura para floats
                if MASA_AGUA > MASA_MIN + 0.05: 
                    MASA_AGUA -= 0.1
                    # Quitar partículas
                    for _ in range(int(PARTICULAS_POR_KG / 10)):
                        if PARTICULAS: PARTICULAS.pop()

        #Lógica de teclado (ACTUALIZADA PARA RESET Y ON/OFF)
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
                PARTICULAS.clear()
                PARTICULAS_VAPOR.clear() 
                
                cantidad_actual = int(MASA_AGUA * PARTICULAS_POR_KG)
                for _ in range(cantidad_inicial):
                    PARTICULAS.append(crear_particula(MASA_AGUA)) 
            
            elif evento.key == pygame.K_SPACE:
                pava_encendida = not pava_encendida 
                if not pava_encendida: # <<<--- DETENER SONIDO AL APAGAR
                    if sonido_hervir:
                        sonido_hervir.stop()
                    sonido_hervir_reproduciendose = False
            
    # B. ACTUALIZACIÓN DE LA LÓGICA
    
    # Hacemos global el acumulador para modificarlo
    globals()['masa_vaporizada_acumulada'] = masa_vaporizada_acumulada
    
    # --- 0. DETERMINAR POTENCIA APLICADA (MODIFICADO) ---
    potencia_aplicada_total = 0
    if pava_encendida:
        potencia_aplicada_total = POTENCIA_PAVA
    
    
    # --- REORDENADO: 1. APLICAR PÉRDIDAS Y GANANCIAS DE CALOR ---
    ZONA_CALOR_Y = 430 # Definir la zona de calor aquí
    P_perdida_total = 0.0

    if PARTICULAS:
        masa_por_particula = MASA_AGUA / len(PARTICULAS)
        particulas_en_zona_calor = [p for p in PARTICULAS if p.y > ZONA_CALOR_Y]
        
        potencia_por_particula_calor = 0
        if pava_encendida and particulas_en_zona_calor:
            potencia_por_particula_calor = potencia_aplicada_total / len(particulas_en_zona_calor)

        for p in PARTICULAS:
            # --- ENFRIAMIENTO (SIEMPRE OCURRE) ---
            if p.temperatura_individual > TEMP_AMBIENTE:
                P_perdida_individual = K_ENFRIAMIENTO_PARTICULA * (p.temperatura_individual - TEMP_AMBIENTE)
                P_perdida_total += P_perdida_individual # Acumular pérdida total
                
                energia_perdida = P_perdida_individual * dt
                dT_individual_perdida = energia_perdida / (masa_por_particula * CALOR_ESPECIFICO_AGUA)
                p.temperatura_individual -= dT_individual_perdida
                p.temperatura_individual = max(TEMP_AMBIENTE, p.temperatura_individual)
                
            # --- CALENTAMIENTO (SI ESTÁ EN LA ZONA DE CALOR) ---
            if pava_encendida and p in particulas_en_zona_calor:
                energia_ganada = potencia_por_particula_calor * dt
                dT_individual_ganada = energia_ganada / (masa_por_particula * CALOR_ESPECIFICO_AGUA)
                
                # Las partículas se calientan, pero no por encima de la ebullición
                p.temperatura_individual += dT_individual_ganada
                p.temperatura_individual = min(TEMP_EBULLICION, p.temperatura_individual)


    # --- REORDENADO: 2. CALCULAR ESTADO PROMEDIO (DESPUÉS DE CAMBIOS) ---
    if PARTICULAS:
        temperatura_actual = sum(p.temperatura_individual for p in PARTICULAS) / len(PARTICULAS)
    else:
        temperatura_actual = TEMP_AMBIENTE

    # --- REORDENADO: 3. DECIDIR SI HIERVE ---
    if temperatura_actual >= TEMP_EBULLICION - 0.1: # 99.9°C
        esta_hirviendo = True
    else:
        esta_hirviendo = False 

            
    # --- REORDENADO: 4. LÓGICA DE VAPORIZACIÓN Y SONIDO ---
    if esta_hirviendo:
        # --- Lógica de Sonido ---
        if pava_encendida and sonido_hervir and not sonido_hervir_reproduciendose:
            sonido_hervir.play(loops=-1) # loops=-1 para que se repita
            sonido_hervir_reproduciendose = True
            
        # --- Lógica de Vaporización ---
        # La energía neta es la potencia de la pava menos la que se está perdiendo al ambiente
        P_neta_para_vaporizar = potencia_aplicada_total - P_perdida_total
        
        # Solo vaporiza si hay energía "extra" después de compensar las pérdidas
        if P_neta_para_vaporizar > 0 and MASA_AGUA > 0:
            energia_para_vaporizar = P_neta_para_vaporizar * dt
            masa_a_vaporizar = energia_para_vaporizar / CALOR_LATENTE_VAPORIZACION
            
            MASA_AGUA = max(0, MASA_AGUA - masa_a_vaporizar)
            masa_vaporizada_acumulada += masa_a_vaporizar
            
            particulas_a_gestionar = int(masa_vaporizada_acumulada * PARTICULAS_POR_KG)
            
            if particulas_a_gestionar > 0:
                masa_vaporizada_acumulada -= particulas_a_gestionar / PARTICULAS_POR_KG
                
                for _ in range(particulas_a_gestionar):
                    if PARTICULAS:
                        # Quitamos la partícula de líquido con la temperatura más alta para simular vaporización
                        particula_a_quitar = max(PARTICULAS, key=lambda p: p.temperatura_individual)
                        PARTICULAS.remove(particula_a_quitar) 
                    
                    for _ in range(PARTICULAS_VAPOR_POR_LIQUIDA):
                        PARTICULAS_VAPOR.append(crear_particula_vapor(MASA_AGUA))

        if MASA_AGUA <= 0: # Si se acaba el agua
            esta_hirviendo = False
            if sonido_hervir: 
                sonido_hervir.stop()
            sonido_hervir_reproduciendose = False
            
    else: # Si no está hirviendo
        if sonido_hervir and sonido_hervir_reproduciendose: 
            sonido_hervir.stop()
            sonido_hervir_reproduciendose = False
    
    # El tiempo solo avanza si la pava está encendida
    if pava_encendida:
        tiempo_simulado += dt

    # --- 2. MAPEAR TEMPERATURA INDIVIDUAL A FÍSICA (MODIFICADO) ---
    # (Esta sección no cambia)
    
    # --- 3. BUCLE DE SUB-PASOS (Física de colisión y convección) ---
    for p in PARTICULAS:
        
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
        
        # --- LLAMADA A UPDATE_COLOR MODIFICADA ---
        # El color ahora se basa en la temperatura individual de la partícula
        p.update_color(COLOR_FRIO, COLOR_CALIENTE)

    # --- 4. ACTUALIZACIÓN DEL VAPOR ---
    for pv in PARTICULAS_VAPOR[:]:
        pv.update(dt)
        if not pv.esta_viva:
            PARTICULAS_VAPOR.remove(pv)

    # C. DIBUJO / RENDERIZADO
    screen.fill("white")

    for p1, p2 in PAREDES_CONTENEDOR:
        pygame.draw.line(screen, "black", p1, p2, 8) 
    
    screen.blit(pava_img_escalada, (200, 100))

    # Dibujar líquido
    for p in PARTICULAS:
        p.dibujar(screen)
        
    # Dibujar vapor (ENCIMA del líquido y la pava)
    for pv in PARTICULAS_VAPOR:
        pv.dibujar(screen)
        
    # 4. DIBUJAR EL HUD (Posición Corregida y con Estado)
    
    pygame.draw.rect(screen, COLOR_BOTON, pot_up_rect)
    pygame.draw.rect(screen, COLOR_BOTON, pot_down_rect)
    pygame.draw.rect(screen, COLOR_BOTON, masa_up_rect)
    pygame.draw.rect(screen, COLOR_BOTON, masa_down_rect)
    
    screen.blit(texto_plus, (pot_up_rect.x + 7, pot_up_rect.y + 2))
    screen.blit(texto_minus, (pot_down_rect.x + 8, pot_down_rect.y + 2))
    screen.blit(texto_plus, (masa_up_rect.x + 7, masa_up_rect.y + 2))
    screen.blit(texto_minus, (masa_down_rect.x + 8, masa_down_rect.y + 2))
    
    texto_temp = font_hud.render(f"Temp Prom: {temperatura_actual:.1f}°C", True, (0,0,0)) # Ahora es temp promedio
    texto_tiempo = font_hud.render(f"Tiempo: {tiempo_simulado:.1f} s", True, (0,0,0))
    texto_potencia = font_hud.render(f"Potencia: {POTENCIA_PAVA:.0f} W", True, (0,0,0))
    texto_masa = font_hud.render(f"Masa: {MASA_AGUA:.1f} kg", True, (0,0,0))
    
    color_estado = (0, 150, 0) if pava_encendida else (200, 0, 0) # Verde si ON, Rojo si OFF
    texto_estado = font_hud.render(f"Estado: {'ENCENDIDA' if pava_encendida else 'APAGADA'}", True, color_estado)
    
    texto_particulas = font_hud.render(f"Partículas: {len(PARTICULAS)}", True, (100,100,100))
    
    texto_reset = font_hud.render("Presiona 'R' para reiniciar", True, (50,50,50))
    texto_toggle = font_hud.render("[ESPACIO] para On/Off", True, (50,50,50))
    
    texto_ambiente = font_hud.render(f"T. Ambiente: {TEMP_AMBIENTE:.1f}°C", True, (100, 100, 100))
    
    screen.blit(texto_temp, (X_MENU_ANCLA, 20))
    screen.blit(texto_tiempo, (X_MENU_ANCLA, 50))
    screen.blit(texto_potencia, (X_MENU_ANCLA + 65, 85)) 
    screen.blit(texto_masa, (X_MENU_ANCLA + 65, 115))   
    
    screen.blit(texto_estado, (X_MENU_ANCLA, 145))
    screen.blit(texto_particulas, (X_MENU_ANCLA, 175))
    screen.blit(texto_reset, (X_MENU_ANCLA, 205))
    screen.blit(texto_toggle, (X_MENU_ANCLA, 225))
    screen.blit(texto_ambiente, (X_MENU_ANCLA, 255))


    # D. Actualizar pantalla y controlar FPS
    pygame.display.flip()
    clock.tick(120)

# 3. Finalización:
pygame.quit()
sys.exit()