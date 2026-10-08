# config.py
"""
Configuracion global del juego.
Separado por secciones para que agregar cosas nuevas no mezcle responsabilidades.
"""

from dataclasses import dataclass


# ============================================================
# METADATA
# ============================================================
TITULO  = "Card Wars MVP"
VERSION = "0.2.0"
AUTOR   = ""


# ============================================================
# VENTANA / RENDER
# ============================================================
ANCHO, ALTO = 820, 620
FPS = 60

# Ruta de la fuente pixel art (si no existe, hace fallback a Arial)
RUTA_FUENTE = "assets/fuentes/2player.ttf"


# ============================================================
# ESTADOS DEL JUEGO
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
# LAYOUT
# ============================================================
class Layout:
    CARTA_W, CARTA_H = 120, 170
    ESPACIO_CARTAS   = 20

    Y_CARTAS_RIVAL = 55
    Y_CARTAS_TU    = 435

    Y_ZONA_DUELO = 245
    Y_MENSAJE    = 355

    MARGEN_LATERAL = 20
    MARGEN_SUP     = 10

    HP_BAR_W, HP_BAR_H = 200, 30
    HP_BAR_Y           = 10
    HP_BAR_X_IZQ       = 20
    HP_BAR_X_DER       = ANCHO - 220

    MINI_W, MINI_H = 130, 80
    MINI_JUGADOR_X_OFFSET = -160
    MINI_ENEMIGO_X_OFFSET = 30
    MINI_Y_OFFSET         = 10

    @classmethod
    def x_inicio_cartas(cls, cantidad, ancho_pantalla=ANCHO):
        total = cantidad * cls.CARTA_W + (cantidad - 1) * cls.ESPACIO_CARTAS
        return (ancho_pantalla - total) // 2


class Botones:
    REINICIAR_W, REINICIAR_H = 160, 30
    REINICIAR_Y              = 580

    SIGUIENTE_W, SIGUIENTE_H = 180, 28
    SIGUIENTE_Y              = 545

    MENU_W, MENU_H = 240, 50
    MENU_ESPACIO_Y = 70
    MENU_Y_INICIAL = 250


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
    nombre        = "Facil",
    hp_jugador    = 200,
    hp_enemigo    = 150,
    tamano_mazo   = 3,
    estrategia_ia = "IARandom",
    descripcion   = "La IA juega al azar. Ideal para aprender.",
)

DIFICULTAD_NORMAL = ConfigDificultad(
    nombre        = "Normal",
    hp_jugador    = 250,
    hp_enemigo    = 250,
    tamano_mazo   = 3,
    estrategia_ia = "IAConservadora",
    descripcion   = "La IA guarda sus cartas fuertes. Desafio parejo.",
)

DIFICULTAD_DURO = ConfigDificultad(
    nombre        = "Duro",
    hp_jugador    = 250,
    hp_enemigo    = 300,
    tamano_mazo   = 4,
    estrategia_ia = "IAAdaptativa",
    descripcion   = "La IA reacciona a lo que jugas. Sin piedad.",
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