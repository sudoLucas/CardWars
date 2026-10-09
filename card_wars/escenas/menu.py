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

        # Coordenadas del MUNDO (300x200)
        ancho_m = ANCHO // 4
        cx_m = ancho_m // 2

        w = Botones.MENU_W
        h = Botones.MENU_H
        sep = Botones.MENU_ESPACIO_Y
        y0 = Botones.MENU_Y_INICIAL

        # Los botones se guardan en PANTALLA REAL (x4) para los clicks
        self.botones = [
            ("jugar",      "JUGAR",
             pygame.Rect((cx_m - w // 2) * 4, (y0 + 0 * sep) * 4, w * 4, h * 4)),
            ("dificultad", "DIFICULTAD",
             pygame.Rect((cx_m - w // 2) * 4, (y0 + 1 * sep) * 4, w * 4, h * 4)),
            ("salir",      "SALIR",
             pygame.Rect((cx_m - w // 2) * 4, (y0 + 2 * sep) * 4, w * 4, h * 4)),
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
        # Fondo negro en el mundo
        self.pantalla.fill(NEGRO)

        # Coordenadas del mundo
        ancho_m = ANCHO // 4
        alto_m = ALTO // 4
        cx_m = ancho_m // 2

        # --- Titulo (arriba) ---
        self.render._texto_centrado_mundo(
            TITULO, self.fuentes["grande"], AMARILLO,
            cx_m, 14
        )

        # --- Version (debajo del titulo) ---
        self.render._texto_centrado_mundo(
            f"v{VERSION}", self.fuentes["chica"], GRIS,
            cx_m, 34
        )

        # --- Subtitulo ---
        self.render._texto_centrado_mundo(
            "Elegi una opcion", self.fuentes["normal"], BLANCO,
            cx_m, 58
        )

        # --- Botones (dibujados en el mundo) ---
        for clave, texto, rect in self.botones:
            hover = (self.hover == clave)
            self.render.dibujar_boton(rect, texto, hover,
                                      COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF)

        # --- Pie: ESC para salir ---
        self.render._texto_centrado_mundo(
            "ESC para salir", self.fuentes["chica"], GRIS,
            cx_m, alto_m - 14
        )