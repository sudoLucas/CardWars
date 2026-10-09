# escenas/dificultad.py
import pygame
from config import ANCHO, ALTO, DIFICULTADES, Botones, ESCALA_PIXEL
from escenas.base import Escena
from vista.colores import (
    NEGRO, BLANCO, AMARILLO, GRIS,
    COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF,
    COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF,
)


class EscenaDificultad(Escena):
    def __init__(self, app):
        super().__init__(app)

        e = ESCALA_PIXEL
        ancho_m = ANCHO // e
        alto_m = ALTO // e
        cx_m = ancho_m // 2

        w = Botones.DIFICULTAD_W
        h = Botones.DIFICULTAD_H
        sep = Botones.DIFICULTAD_ESPACIO_Y
        y0 = 70

        # Los botones se guardan en PANTALLA REAL (x4) para los clicks
        self.botones = []
        claves = ["facil", "normal", "duro"]
        for i, clave in enumerate(claves):
            cfg = DIFICULTADES[clave]
            texto = cfg.nombre
            x = (cx_m - w // 2) * e
            y = (y0 + i * sep) * e
            rect = pygame.Rect(x, y, w * e, h * e)
            self.botones.append((clave, texto, rect))

        # Boton volver
        y_volver = y0 + 3 * sep + 15
        self.boton_volver = pygame.Rect(
            (cx_m - w // 2) * e,
            y_volver * e,
            w * e, h * e,
        )

        self.hover = None

    def handle_event(self, evento):
        mouse = pygame.mouse.get_pos()

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
        # Fondo negro
        self.pantalla.fill(NEGRO)

        # Coordenadas del mundo
        ancho_m = ANCHO // ESCALA_PIXEL
        alto_m = ALTO // ESCALA_PIXEL
        cx_m = ancho_m // 2

        # Titulo
        self.render._texto_centrado_mundo(
            "DIFICULTAD", self.fuentes["grande"], AMARILLO,
            cx_m, 15
        )
        # Subtitulo
        self.render._texto_centrado_mundo(
            "Elegi el nivel de desafio", self.fuentes["normal"], BLANCO,
            cx_m, 45
        )

        # Botones + descripcion debajo de cada uno
        for clave, texto, rect in self.botones:
            hover = (self.hover == clave)
            actual = (clave == self.app.clave_dificultad)

            color_on = COLOR_BTN_VERDE if actual else COLOR_BTN_AZUL
            color_off = COLOR_BTN_VERDE_OFF if actual else COLOR_BTN_AZUL_OFF

            self.render.dibujar_boton(rect, texto, hover, color_on, color_off)

            # Descripcion debajo del boton
            cfg = DIFICULTADES[clave]
            y_desc_m = rect.y // ESCALA_PIXEL + Botones.DIFICULTAD_H + 4
            self.render._texto_centrado_mundo(
                cfg.descripcion, self.fuentes["chica"], GRIS,
                cx_m, y_desc_m
            )

        # Boton VOLVER
        self.render.dibujar_boton(
            self.boton_volver, "VOLVER",
            self.hover == "volver",
            COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF
        )