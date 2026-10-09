# config.py
"""
Configuracion global del juego.

SISTEMA DE COORDENADAS:
- El "mundo" mide ANCHO/ESCALA_PIXEL x ALTO/ESCALA_PIXEL (por defecto 300x200).
- Todas las constantes de Layout y Botones estan en unidades del MUNDO.
- El render las dibuja tal cual sobre surface_mundo.
- Los textos van al surface_ui en pixeles reales.
"""

from dataclasses import dataclass
import pygame


# ============================================================
# METADATA
# ============================================================
TITULO  = "Card Wars MVP"
VERSION = "0.3.0"
AUTOR   = ""


# ============================================================
# VENTANA / RENDER
# ============================================================
ANCHO_DESEADO, ALTO_DESEADO = 1200, 800
ANCHO, ALTO = ANCHO_DESEADO, ALTO_DESEADO

FPS = 60
RUTA_FUENTE = "assets/fuentes/pixel.ttf"

# Escala pixel art: cada unidad del mundo = ESCALA_PIXEL pixeles reales
ESCALA_PIXEL = 4


def inicializar_ventana():
    global ANCHO, ALTO
    info = pygame.display.Info()
    ancho_pantalla = info.current_w
    alto_pantalla = info.current_h
    ancho_max = int(ancho_pantalla * 0.90)
    alto_max = int(alto_pantalla * 0.90)
    ancho = min(ANCHO_DESEADO, ancho_max)
    alto = min(ALTO_DESEADO, alto_max)
    ancho = (ancho // ESCALA_PIXEL) * ESCALA_PIXEL
    alto = (alto // ESCALA_PIXEL) * ESCALA_PIXEL
    ANCHO, ALTO = ancho, alto
    return ancho, alto


# ============================================================
# ESTADOS
# ============================================================
class Turno:
    JUGADOR     = "jugador"
    RESOLVIENDO = "resolviendo"
    FIN         = "fin"


class Escena:
    MENU       = "menu"
    DIFICULTAD = "dificultad"
    JUEGO      = "juego"
    FIN        = "fin"
    OPCIONES   = "opciones"


# ============================================================
# LAYOUT (en unidades del MUNDO)
# ============================================================
class Layout:
    # Cartas
    CARTA_W, CARTA_H = 55, 68
    ESPACIO_CARTAS   = 14

    # --- Abanico del rival ---
    Y_CENTRO_RIVAL = 28
    ABANICO_SEP_X = 38
    ABANICO_OFFSET_Y = 12
    ABANICO_ANGULO = 8

    # --- Zona de duelo ---
    # Y del centro vertical donde se pelean las cartas.
    # La carta rival se dibuja arriba, la del jugador abajo, con el VS al medio.
    Y_CENTRO_DUELO = 100
    # Separacion del VS respecto al centro (arriba = mas cerca de la rival)
    Y_VS = 78
    # Separacion entre las dos cartas del duelo
    DUELO_SEP_Y = 4

    # --- Mano del jugador ---
    Y_TOP_MANO = 148

    # --- Mensajes de estado ---
    # Y del texto "TU TURNO" / "COMBATE"
    Y_MENSAJE = 138

    @classmethod
    def x_inicio_cartas(cls, cantidad, ancho_mundo):
        total = cantidad * cls.CARTA_W + (cantidad - 1) * cls.ESPACIO_CARTAS
        return (ancho_mundo - total) // 2


# ============================================================
# BOTONES (en unidades del MUNDO)
# ============================================================
class Botones:
    # REINICIAR (abajo a la izquierda, no pisa cartas)
    REINICIAR_W, REINICIAR_H = 60, 12
    REINICIAR_X = 8
    REINICIAR_Y = 185

    # SIGUIENTE RONDA (abajo a la derecha)
    SIGUIENTE_W, SIGUIENTE_H = 70, 12
    SIGUIENTE_X = 300 - 78
    SIGUIENTE_Y = 185

    # MENU
    MENU_W, MENU_H = 140, 22
    MENU_ESPACIO_Y = 30
    MENU_Y_INICIAL = 85

    # DIFICULTAD
    DIFICULTAD_W, DIFICULTAD_H = 90, 14
    DIFICULTAD_ESPACIO_Y       = 35


# ============================================================
# DIFICULTAD
# ============================================================
@dataclass(frozen=True)
class ConfigDificultad:
    nombre:           str
    hp_jugador:       int
    hp_enemigo:       int
    tamano_mazo:      int
    estrategia_ia:    str
    descripcion:      str


DIFICULTAD_FACIL = ConfigDificultad(
    nombre        = "Fácil",
    hp_jugador    = 200,
    hp_enemigo    = 150,
    tamano_mazo   = 3,
    estrategia_ia = "IARandom",
    descripcion   = "La IA juega al azar.",
)

DIFICULTAD_NORMAL = ConfigDificultad(
    nombre        = "Normal",
    hp_jugador    = 250,
    hp_enemigo    = 250,
    tamano_mazo   = 3,
    estrategia_ia = "IAConservadora",
    descripcion   = "La IA guarda sus cartas fuertes.",
)

DIFICULTAD_DURO = ConfigDificultad(
    nombre        = "Duro de cojones",
    hp_jugador    = 250,
    hp_enemigo    = 300,
    tamano_mazo   = 4,
    estrategia_ia = "IAAdaptativa",
    descripcion   = "La IA reacciona a lo que jugas.",
)

DIFICULTADES = {
    "facil":  DIFICULTAD_FACIL,
    "normal": DIFICULTAD_NORMAL,
    "duro":   DIFICULTAD_DURO,
}

DIFICULTAD_DEFAULT = "normal"


# ============================================================
# GAMEPLAY
# ============================================================
DUELO_DURACION = 1500

POOL_CARTAS = [
    ("Gato",    5),
    ("Slime",   5),
    ("Perro",  10),
    ("Lobo",   10),
    ("Dragon", 15),
    ("Tigre",  15),
    ("Fenix",  20),
    ("Titan",  20),
    ("Golem",  25),
    ("Vampiro", 25),
]


# ============================================================
# HELPERS
# ============================================================
def get_dificultad(clave):
    return DIFICULTADES.get(clave, DIFICULTADES[DIFICULTAD_DEFAULT])