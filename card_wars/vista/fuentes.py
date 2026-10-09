# card_wars/vista/fuentes.py
import os
import pygame
from config import RUTA_FUENTE


def _cargar(ruta, tamano, fallback="Arial", bold=False):
    if os.path.isfile(ruta):
        try:
            return pygame.font.Font(ruta, tamano)
        except Exception:
            pass
    return pygame.font.SysFont(fallback, tamano, bold=bold)


def cargar_fuentes():
    # Tamano en PIXELES REALES (no se multiplican por escala).
    return {
        "mini":    _cargar(RUTA_FUENTE, 16, bold=False),
        "chica":   _cargar(RUTA_FUENTE, 18, bold=False),
        "normal":  _cargar(RUTA_FUENTE, 22, bold=True),
        "mensaje": _cargar(RUTA_FUENTE, 24, bold=True),
        "ronda":   _cargar(RUTA_FUENTE, 28, bold=True),
        "grande":  _cargar(RUTA_FUENTE, 40, bold=True),
        "icono":   _cargar(RUTA_FUENTE, 44, bold=True),
    }