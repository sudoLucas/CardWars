# card_wars/vista/fuentes.py
import os
import pygame
from config import RUTA_FUENTE


def _cargar(ruta, tamano, fallback="Arial", bold=False):
    """Carga una fuente TTF. Si no existe, hace fallback a SysFont."""
    if os.path.isfile(ruta):
        try:
            return pygame.font.Font(ruta, tamano)
        except Exception:
            pass
    # Fallback: SysFont si el .ttf no está disponible
    return pygame.font.SysFont(fallback, tamano, bold=bold)


def cargar_fuentes():
    e = 4  # debe coincidir con ESCALA_PIXEL de render.py
    return {
        "mini":    _cargar(RUTA_FUENTE, 6  * e, bold=False),  # = 24
        "chica":   _cargar(RUTA_FUENTE, 8  * e, bold=False),  # = 32
        "normal":  _cargar(RUTA_FUENTE, 9  * e, bold=True),   # = 36
        "mensaje": _cargar(RUTA_FUENTE, 10 * e, bold=True),   # = 40
        "ronda":   _cargar(RUTA_FUENTE, 12 * e, bold=True),   # = 48
        "grande":  _cargar(RUTA_FUENTE, 16 * e, bold=True),   # = 64
        "icono":   _cargar(RUTA_FUENTE, 18 * e, bold=True),   # = 72
    }