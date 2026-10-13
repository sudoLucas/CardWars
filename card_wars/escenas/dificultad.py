# escenas/dificultad.py
import os
import pygame
from config import ANCHO, ALTO, DIFICULTADES, Botones, ESCALA_PIXEL, DIRECTORIO_RAIZ
from escenas.base import Escena
from vista.colores import (
    NEGRO, BLANCO, AMARILLO, GRIS,
    COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF,
    COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF,
)


RUTA_FONDO_MENU = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "menuFondo.png")


class EscenaDificultad(Escena):
    def __init__(self, app):
        super().__init__(app)

        e = ESCALA_PIXEL
        ancho_m = ANCHO // e
        alto_m = ALTO // e

        w = Botones.DIFICULTAD_W
        h = Botones.DIFICULTAD_H
        sep = Botones.DIFICULTAD_ESPACIO_Y
        margen_x = Botones.MENU_X_MARGEN
        margen_y = Botones.MENU_Y_MARGEN

        claves = ["facil", "normal", "duro"]

        # --- 3 botones pegados al borde inferior izquierdo ---
        # Misma logica que el menu: el ULTIMO boton arriba del margen inferior.
        n = len(claves)
        y_ultimo = alto_m - margen_y - h

        self.botones = []
        for i in range(n):
            y_m = y_ultimo - (n - 1 - i) * (h + sep)
            x_m = margen_x
            rect = pygame.Rect(x_m * e, y_m * e, w * e, h * e)
            cfg = DIFICULTADES[claves[i]]
            self.botones.append((claves[i], cfg.nombre, rect))

        # --- Boton VOLVER, arriba de todo ---
        # Va por encima del primer boton (facil)
        y_volver = y_ultimo - n * (h + sep)
        self.boton_volver = pygame.Rect(
            margen_x * e,
            y_volver * e,
            w * e, h * e,
        )

        self.hover = None

        # Imagen de fondo (igual que menu)
        self.fondo = None
        if os.path.isfile(RUTA_FONDO_MENU):
            try:
                img = pygame.image.load(RUTA_FONDO_MENU).convert()
                self.fondo = pygame.transform.smoothscale(img, (ANCHO, ALTO))
            except Exception as e:
                print(f"[dificultad] No se pudo cargar la imagen de fondo: {e}")
        else:
            print(f"[dificultad] Imagen NO ENCONTRADA: {RUTA_FONDO_MENU}")

    def handle_event(self, evento, mouse):
        self.hover = None
        for clave, _, rect in self.botones:
            if rect.collidepoint(mouse):
                self.hover = clave
                break
        if self.boton_volver.collidepoint(mouse):
            self.hover = "volver"

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            from escenas.menu import EscenaMenu
            self.app.cambiar_escena(EscenaMenu(self.app))

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for clave, _, rect in self.botones:
                if rect.collidepoint(mouse):
                    self.app.clave_dificultad = clave
                    from escenas.menu import EscenaMenu
                    self.app.cambiar_escena(EscenaMenu(self.app))
                    return
            if self.boton_volver.collidepoint(mouse):
                from escenas.menu import EscenaMenu
                self.app.cambiar_escena(EscenaMenu(self.app))

    def draw(self):
        ancho_m = ANCHO // ESCALA_PIXEL
        alto_m = ALTO // ESCALA_PIXEL

        self.pantalla.fill(NEGRO)

        if self.fondo is not None:
            self.render.ui.blit(self.fondo, (0, 0))

        # Textos alineados a la izquierda (mismo margen que los botones)
        x_texto = Botones.MENU_X_MARGEN

        self.render._texto_mundo(
            "DIFICULTAD", self.fuentes["grande"], AMARILLO,
            x_texto, 14
        )
        self.render._texto_mundo(
            "Elegi el nivel", self.fuentes["normal"], BLANCO,
            x_texto, 45
        )

        # Botones
        for clave, texto, rect in self.botones:
            hover = (self.hover == clave)
            actual = (clave == self.app.clave_dificultad)

            color_on = COLOR_BTN_VERDE if actual else COLOR_BTN_AZUL
            color_off = COLOR_BTN_VERDE_OFF if actual else COLOR_BTN_AZUL_OFF

            self.render.dibujar_boton(rect, texto, hover, color_on, color_off,
                                      borde_grosor=Botones.MENU_BORDE_GROSOR)

        # Pie
        self.render._texto_centrado_mundo(
            "ESC para volver", self.fuentes["chica"], GRIS,
            ancho_m - 40, alto_m - 14
        )