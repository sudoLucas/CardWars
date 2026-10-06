# vista/fuentes.py
import pygame

# Se inicializan despues de pygame.init()
def cargar_fuentes():
    return {
        "normal":  pygame.font.SysFont("Arial", 16, bold=True),
        "grande":  pygame.font.SysFont("Arial", 30, bold=True),
        "chica":   pygame.font.SysFont("Arial", 13),
        "mensaje": pygame.font.SysFont("Arial", 17, bold=True),
        "ronda":   pygame.font.SysFont("Arial", 20, bold=True),
        "mini":    pygame.font.SysFont("Arial", 14, bold=True),
        "icono":   pygame.font.SysFont("Arial", 38, bold=True),
    }