# config.py
"""
Configuracion global del juego.

SISTEMA DE COORDENADAS:
- El "mundo" mide RESOLUCION_INTERNA_W/ESCALA_PIXEL x RESOLUCION_INTERNA_H/ESCALA_PIXEL.
- Todas las constantes de Layout y Botones estan en unidades del MUNDO.
- El render las dibuja tal cual sobre surface_mundo.
- Los textos van al surface_ui en pixeles reales.

SISTEMA DE VENTANA:
- RESOLUCION_INTERNA es la resolucion del juego (nunca cambia).
- VENTANA_W/H es el tamano de la ventana al abrir.
- Pygame escala la resolucion interna a la ventana con SCALED.
"""

import os
from dataclasses import dataclass
import pygame


# ============================================================
# METADATA
# ============================================================
TITULO  = "Card Wars"
VERSION = "0.3.0"
AUTOR   = ""


# ============================================================
# RUTAS (absolutas, relativas a este archivo)
# ============================================================
DIRECTORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# VENTANA / RENDER
# ============================================================
RESOLUCION_INTERNA_W, RESOLUCION_INTERNA_H = 1200, 800

VENTANA_W, VENTANA_H = 900, 600

ANCHO, ALTO = RESOLUCION_INTERNA_W, RESOLUCION_INTERNA_H

FPS = 60

RUTA_FUENTE = os.path.join(DIRECTORIO_RAIZ, "assets", "fuentes", "pixel.ttf")

ESCALA_PIXEL = 4


def inicializar_ventana():
    """
    Devuelve (ancho_ventana, alto_ventana) para crear la ventana.
    La resolucion INTERNA sigue siendo RESOLUCION_INTERNA_W x RESOLUCION_INTERNA_H.
    Si la ventana pedida no entra en el monitor, la achica.
    """
    info = pygame.display.Info()

    ancho_ventana = min(VENTANA_W, int(info.current_w * 0.90))
    alto_ventana = min(VENTANA_H, int(info.current_h * 0.90))

    return ancho_ventana, alto_ventana


# ============================================================
# ESTADOS
# ============================================================
class Turno:
    IA_TIRA          = "ia_tira"
    JUGADOR_TIRA     = "jugador_tira"
    JUGADOR_HECHIZOS = "jugador_hechizos"
    DUELO            = "duelo"
    RESULTADO        = "resultado"
    FIN              = "fin"


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

    # --- Abanico del jugador ---
    ABANICO_SEP_X_JUGADOR = 48
    ABANICO_OFFSET_Y_JUGADOR = 10
    ABANICO_ANGULO_JUGADOR = 8

    # --- Zona de duelo ---
    Y_CENTRO_DUELO = 100
    Y_VS = 78
    DUELO_SEP_Y = 4

    # --- Mano del jugador ---
    Y_TOP_MANO = 148

    # --- Mensajes de estado ---
    Y_MENSAJE = 138

    @classmethod
    def x_inicio_cartas(cls, cantidad, ancho_mundo):
        total = cantidad * cls.CARTA_W + (cantidad - 1) * cls.ESPACIO_CARTAS
        return (ancho_mundo - total) // 2


# ============================================================
# BOTONES (en unidades del MUNDO)
# ============================================================
class Botones:
    REINICIAR_W, REINICIAR_H = 60, 12
    REINICIAR_X = 8
    REINICIAR_Y = 185

    SIGUIENTE_W, SIGUIENTE_H = 70, 12
    SIGUIENTE_X = 300 - 78
    SIGUIENTE_Y = 185

    MENU_W, MENU_H = 80, 8
    MENU_ESPACIO_Y = 3
    MENU_X_MARGEN = 12
    MENU_Y_MARGEN = 12
    MENU_BORDE_GROSOR = 1

    DIFICULTAD_W, DIFICULTAD_H = 90, 14
    DIFICULTAD_ESPACIO_Y       = 35


# ============================================================
# MANA
# ============================================================
MANA_INICIAL  = 7
MANA_MAXIMO   = 14
MANA_SUMA_MIN = 1
MANA_SUMA_MAX = 2


# ============================================================
# HECHIZOS
# ============================================================
HECHIZOS = {
    "vision": {
        "nombre": "Vision",
        "costo": 1,
        "target": "carta_rival",
        "descripcion": "Ver una carta del rival por 1.5s",
    },
    "fuerza": {
        "nombre": "Pocion de fuerza",
        "costo": 2,
        "target": "criatura_propia",
        "bonus_poder": 5,
        "descripcion": "+5 poder a tu criatura este turno",
    },
    "defensa": {
        "nombre": "Pocion de defensa",
        "costo": 2,
        "target": "criatura_propia",
        "bonus_aguante": 5,
        "descripcion": "+5 vida a tu criatura este turno",
    },
    "curacion": {
        "nombre": "Curacion",
        "costo": 3,
        "target": "jugador",
        "bonus_hp": 20,
        "descripcion": "+20 HP al jugador",
    },
    "rayo": {
        "nombre": "Rayo",
        "costo": 3,
        "target": "criatura_rival",
        "daño": 10,
        "descripcion": "10 de dano a una criatura rival",
    },
    "debilidad": {
        "nombre": "Debilidad",
        "costo": 3,
        "target": "criatura_rival",
        "bonus_poder": -5,
        "descripcion": "-5 poder a una criatura rival este turno",
    },
    "robo": {
        "nombre": "Robo",
        "costo": 3,
        "target": "carta_rival",
        "descripcion": "Robar una carta del rival",
    },
        "drenaje": {
        "nombre": "Drenaje",
        "costo": 3,
        "target": "criatura_rival",
        "daño": 8,
        "curacion": 8,
        "descripcion": "8 de dano a una criatura rival y te cura 8 HP",
    },
    "inmovilizar": {
        "nombre": "Inmovilizar",
        "costo": 4,
        "target": "criatura_rival",
        "descripcion": "La criatura rival no ataca este turno",
    },
}

POOL_HECHIZOS = [

    "vision", "fuerza", "defensa", "curacion",
    "rayo", "debilidad", "robo", "inmovilizar",
    "drenaje",
]


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
    descripcion   = "",
)

DIFICULTAD_NORMAL = ConfigDificultad(
    nombre        = "Normal",
    hp_jugador    = 250,
    hp_enemigo    = 250,
    tamano_mazo   = 4,
    estrategia_ia = "IAConservadora",
    descripcion   = "",
)

DIFICULTAD_DURO = ConfigDificultad(
    nombre        = "Duro de cojones",
    hp_jugador    = 250,
    hp_enemigo    = 300,
    tamano_mazo   = 6,
    estrategia_ia = "IAAdaptativa",
    descripcion   = "",
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


# ============================================================
# POOL DE CARTAS
# ============================================================
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