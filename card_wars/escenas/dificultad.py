# escenas/dificultad.py
import pygame
from config import ANCHO, ALTO, DIFICULTADES, Botones
from escenas.base import Escena
from vista.colores import (
    NEGRO, BLANCO, AMARILLO, GRIS,
    COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF,
    COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF,
)


class EscenaDificultad(Escena):
    def __init__(self, app):
        super().__init__(app)

        cx = ANCHO // 2
        y = 220
        w = Botones.MENU_W
        h = Botones.MENU_H
        sep = 70

        self.botones = []
        claves = ["facil", "normal", "duro"]
        for i, clave in enumerate(claves):
            cfg = DIFICULTADES[clave]
            texto = cfg.nombre
            rect = pygame.Rect(cx - w // 2, y + i * sep, w, h)
            self.botones.append((clave, texto, rect))

        self.boton_volver = pygame.Rect(cx - w // 2, y + 3 * sep + 20, w, h)

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
        self.pantalla.fill(NEGRO)

        self.render._texto_centrado_ui("DIFICULTAD", self.fuentes["grande"], AMARILLO,
                                        ANCHO // 2, 90)
        self.render._texto_centrado_ui("Elegi el nivel de desafio",
                                        self.fuentes["normal"], BLANCO,
                                        ANCHO // 2, 150)

        for clave, texto, rect in self.botones:
            hover = (self.hover == clave)
            actual = (clave == self.app.clave_dificultad)

            color_on = COLOR_BTN_VERDE if actual else COLOR_BTN_AZUL
            color_off = COLOR_BTN_VERDE_OFF if actual else COLOR_BTN_AZUL_OFF

            self.render.dibujar_boton(rect, texto, hover, color_on, color_off)

            cfg = DIFICULTADES[clave]
            desc_y = rect.y + rect.h + 4
            self.render._texto_centrado_ui(cfg.descripcion,
                                            self.fuentes["chica"], GRIS,
                                            ANCHO // 2, desc_y)

        self.render.dibujar_boton(self.boton_volver, "VOLVER",
                                  self.hover == "volver",
                                  COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF)