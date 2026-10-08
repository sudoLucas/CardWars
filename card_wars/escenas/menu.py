# escenas/menu.py
import sys
import pygame
from config import ANCHO, ALTO, TITULO, VERSION, Botones
from escenas.base import Escena
from escenas.dificultad import EscenaDificultad
from vista.colores import (
    NEGRO, BLANCO, AMARILLO, GRIS,
    COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF,
    COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF,
)


class EscenaMenu(Escena):
    def __init__(self, app):
        super().__init__(app)

        cx = ANCHO // 2
        y = Botones.MENU_Y_INICIAL
        w = Botones.MENU_W
        h = Botones.MENU_H
        sep = Botones.MENU_ESPACIO_Y

        self.botones = [
            ("jugar",      "JUGAR",       pygame.Rect(cx - w // 2, y + 0 * sep, w, h)),
            ("dificultad", "DIFICULTAD",  pygame.Rect(cx - w // 2, y + 1 * sep, w, h)),
            ("salir",      "SALIR",       pygame.Rect(cx - w // 2, y + 2 * sep, w, h)),
        ]

        self.hover = None

    def handle_event(self, evento):
        mouse = pygame.mouse.get_pos()

        self.hover = None
        for clave, _, rect in self.botones:
            if rect.collidepoint(mouse):
                self.hover = clave
                break

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for clave, _, rect in self.botones:
                if rect.collidepoint(mouse):
                    self._accion(clave)
                    break

    def _accion(self, clave):
        if clave == "jugar":
            from escenas.juego import EscenaJuego
            self.app.cambiar_escena(EscenaJuego(self.app))
        elif clave == "dificultad":
            self.app.cambiar_escena(EscenaDificultad(self.app))
        elif clave == "salir":
            pygame.quit()
            sys.exit()

    def draw(self):
        # Fondo en el mundo
        self.pantalla.fill(NEGRO)

        # Textos en la UI
        self.render._texto_centrado_ui(TITULO, self.fuentes["grande"], AMARILLO,
                                        ANCHO // 2, 90)
        self.render._texto_centrado_ui(f"v{VERSION}", self.fuentes["chica"], GRIS,
                                        ANCHO // 2, 130)
        self.render._texto_centrado_ui("Elegi una opcion",
                                        self.fuentes["normal"], BLANCO,
                                        ANCHO // 2, 180)

        # Botones (dibujan fondo en mundo + texto en UI)
        for clave, texto, rect in self.botones:
            hover = (self.hover == clave)
            self.render.dibujar_boton(rect, texto, hover,
                                      COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF)

        self.render._texto_centrado_ui("ESC para salir",
                                        self.fuentes["chica"], GRIS,
                                        ANCHO // 2, ALTO - 30)