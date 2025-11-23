import pygame
pygame.font.init()

SUB_STEPS = 8

# termodinamicas
CALOR_ESPECIFICO_AGUA = 4186
TEMP_AMBIENTE = 20.0
TEMP_EBULLICION = 100.0
K_DISIPACION = 10.0 # Factor de disipación de calor al ambiente
K_CALOR_ZONA_CALOR = 1000.0 # Cuánta potencia se transfiere a las partículas en la zona de calor
K_ENFRIAMIENTO_PARTICULA = 0.07 # Cuánta potencia pierde cada partícula al ambiente

# fisicas base
GRAVEDAD = 0.02
MAX_EMPUJE_CALOR_PARTICULA = 0.0005 # Empuje que genera una partícula caliente
MAX_VELOCIDAD_BASE = 2.0
MAX_VELOCIDAD_TOPE = 5.0

# nivel
MASA_MIN = 0.5 # kg
MASA_MAX = 2.0 # kg
Y_NIVEL_FONDO = 450 # Y-pixel del fondo real de la pava (coincide con centro_y_arco)
Y_NIVEL_TOPE = 160 # Y-pixel para la masa máxima

# vaporizacion
CALOR_LATENTE_VAPORIZACION = 2260000 # J/kg (Energía para convertir agua en vapor)
PARTICULAS_VAPOR_POR_LIQUIDA = 3      # Cuántas partículas de vapor crea 1 de líquido
VIDA_PARTICULA_VAPOR = 2.5           # Segundos

# color
COLOR_FRIO = (0,100,255)
COLOR_CALIENTE =  (255,0,0)

# Coordenadas de las paredes
PAREDES_CONTENEDOR = [
    ((260, 150), (505, 150)), ((505, 150), (520, 200)), ((520, 200), (535, 300)),
    ((535, 300), (550, 450)), ((230, 450), (245, 300)), ((245, 300), (260, 150)),
]

# botones
X_MENU_ANCLA = 750
COLOR_BOTON = (220, 220, 220)
COLOR_TEXTO_BOTON = (0, 0, 0)

# particulas
RADIO_PARTICULA = 5
VELOCIDAD_MAX_INICIAL = 2.0 
PARTICULAS_POR_KG = 150

# zona de calor
ZONA_CALOR_Y = 430

# Fuentes
H0 = pygame.font.Font("Fuentes/HandyGeorge.ttf", 84)
H1 = pygame.font.Font("Fuentes/HandyGeorge.ttf", 48)
H2 = pygame.font.Font("Fuentes/HandyGeorge.ttf", 32)
H3 = pygame.font.Font("Fuentes/HandyGeorge.ttf", 24)
H4 = pygame.font.Font("Fuentes/HandyGeorge.ttf", 16)
