# vista/colores.py
# Paleta de colores centralizada - ESTILO GAME BOY ADVANCE (GBA)
# Nota: Colores de alta saturación y contraste para emular la pantalla LCD clásica.

# Colores Base GBA (Saturados)
NEGRO       = (16, 16, 24)       # Casi negro, típico de contornos GBA
BLANCO      = (248, 248, 240)    # Blanco LCD ligeramente cálido
AMARILLO    = (248, 216, 0)      # Amarillo interfaz ("Pokemon/Zelda")
VERDE       = (0, 200, 80)       # Verde brillante de menú
ROJO        = (248, 48, 48)      # Rojo GBA muy vivo
AZUL_HP     = (0, 144, 248)      # Azul puro de barra de energía

# Grises (Tonos lavados estilo LCD)
GRIS        = (160, 168, 160)
GRIS_OSCURO = (88, 96, 96)

# Cartas (Paleta estilo RPG de GBA: Golden Sun / Fire Emblem)
COLOR_JUGADOR        = (72, 120, 248)    # Azul héroe
COLOR_JUGADOR_HOVER  = (120, 176, 248)   # Azul héroe seleccionado
COLOR_ENEMIGO        = (216, 40, 40)     # Rojo jefe / rival
COLOR_ENEMIGO_ACTIVA = (248, 120, 48)    # Naranja de alerta
COLOR_MUERTA         = (56, 56, 64)      # Gris de descarte
COLOR_AGUANTE        = (40, 216, 168)    # Verde agua / Stamina
COLOR_DORSO          = (168, 16, 48)     # Bordó clásico de reverso

# Elementos de UI
COLOR_FONDO_BARRA    = (40, 40, 48)      # Fondo oscuro de menú
COLOR_LINEA_DUELO    = (120, 120, 144)   # Separador metálico
COLOR_INFO           = (232, 232, 248)   # Texto de caja de diálogo
COLOR_ETIQ_RIVAL     = (248, 104, 104)   # Fondo indicador enemigo
COLOR_ETIQ_JUGADOR   = (104, 168, 248)   # Fondo indicador jugador

# Botones (Estilo menú de opciones brillante)
COLOR_BTN_VERDE      = (0, 216, 0)
COLOR_BTN_VERDE_OFF  = (0, 120, 0)
COLOR_BTN_AZUL       = (0, 168, 248)
COLOR_BTN_AZUL_OFF   = (0, 88, 168)
