# vista/fuentes.py
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
    # Fallback
    return pygame.font.SysFont(fallback, tamano, bold=bold)


def cargar_fuentes():
    """
    Carga todas las fuentes del juego.
    Si existe assets/fuentes/2player.ttf, la usa para todo.
    """
    return {
        "normal":  _cargar(RUTA_FUENTE, 16, bold=True),
        "grande":  _cargar(RUTA_FUENTE, 30, bold=True),
        "chica":   _cargar(RUTA_FUENTE, 13),
        "mensaje": _cargar(RUTA_FUENTE, 17, bold=True),
        "ronda":   _cargar(RUTA_FUENTE, 20, bold=True),
        "mini":    _cargar(RUTA_FUENTE, 14, bold=True),
        "icono":   _cargar(RUTA_FUENTE, 38, bold=True),
    }