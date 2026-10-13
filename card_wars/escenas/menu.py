# escenas/menu.py
import os
import sys
import pygame
from config import ANCHO, ALTO, TITULO, VERSION, Botones, DIRECTORIO_RAIZ
from escenas.base import Escena
from escenas.dificultad import EscenaDificultad
from vista.colores import (
    NEGRO, BLANCO, AMARILLO, GRIS,
    COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF,
    COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF,
)


RUTA_FONDO_MENU = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "menuFondo.png")


class EscenaMenu(Escena):
    def __init__(self, app):
        super().__init__(app)

        # Coordenadas del MUNDO
        ancho_m = ANCHO // 4
        alto_m = ALTO // 4

        w = Botones.MENU_W
        h = Botones.MENU_H
        sep = Botones.MENU_ESPACIO_Y
        margen_x = Botones.MENU_X_MARGEN
        margen_y = Botones.MENU_Y_MARGEN

        claves = ["jugar", "dificultad", "salir"]
        textos = ["JUGAR", "DIFICULTAD", "SALIR"]
        n = len(claves)

        y_ultimo = alto_m - margen_y - h

        self.botones = []
        for i in range(n):
            y_m = y_ultimo - (n - 1 - i) * (h + sep)
            x_m = margen_x
            rect_pantalla = pygame.Rect(
                x_m * 4,
                y_m * 4,
                w * 4,
                h * 4,
            )
            self.botones.append((claves[i], textos[i], rect_pantalla))

        self.hover = None

        # Imagen de fondo
        self.fondo = None
        if os.path.isfile(RUTA_FONDO_MENU):
            try:
                img = pygame.image.load(RUTA_FONDO_MENU).convert()
                self.fondo = pygame.transform.smoothscale(img, (ANCHO, ALTO))
            except Exception as e:
                print(f"[menu] No se pudo cargar la imagen de fondo: {e}")
        else:
            print(f"[menu] Imagen NO ENCONTRADA: {RUTA_FONDO_MENU}")

    def handle_event(self, evento, mouse):
        # --- hover (usa el mouse YA traducido) ---
        self.hover = None
        for clave, _, rect in self.botones:
            if rect.collidepoint(mouse):
                self.hover = clave
                break

        # --- teclas ---
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        # --- clicks ---
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
        ancho_m = ANCHO // 4
        alto_m = ALTO // 4

        self.pantalla.fill(NEGRO)

        if self.fondo is not None:
            self.render.ui.blit(self.fondo, (0, 0))

        x_texto = Botones.MENU_X_MARGEN

        self.render._texto_mundo(
            TITULO, self.fuentes["grande"], AMARILLO,
            x_texto, 14
        )
        self.render._texto_mundo(
            f"v{VERSION}", self.fuentes["chica"], GRIS,
            x_texto, 34
        )

        for clave, texto, rect in self.botones:
            hover = (self.hover == clave)
            self.render.dibujar_boton(
                rect, texto, hover,
                COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF,
                borde_grosor=Botones.MENU_BORDE_GROSOR,
            )

        self.render._texto_centrado_mundo(
            "ESC para salir", self.fuentes["chica"], GRIS,
            ancho_m - 40, alto_m - 14
        )