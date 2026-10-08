# escenas/fin.py
import pygame
from config import ANCHO, ALTO, Botones
from escenas.base import Escena
from vista.colores import (
    NEGRO, BLANCO, AMARILLO, VERDE, ROJO, GRIS,
    COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF,
    COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF,
)


class EscenaFin(Escena):
    def __init__(self, app, juego):
        super().__init__(app)
        self.juego = juego
        self.gano = juego.hp_enemigo <= 0

        cx = ANCHO // 2
        y = 380
        w = Botones.MENU_W
        h = Botones.MENU_H
        sep = 70

        self.botones = [
            ("revancha", "REVANCHA", pygame.Rect(cx - w // 2, y + 0 * sep, w, h)),
            ("menu",     "MENU",     pygame.Rect(cx - w // 2, y + 1 * sep, w, h)),
        ]
        self.hover = None

    def handle_event(self, evento):
        mouse = pygame.mouse.get_pos()

        self.hover = None
        for clave, _, rect in self.botones:
            if rect.collidepoint(mouse):
                self.hover = clave
                break

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            from escenas.menu import EscenaMenu
            self.app.cambiar_escena(EscenaMenu(self.app))

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for clave, _, rect in self.botones:
                if rect.collidepoint(mouse):
                    if clave == "revancha":
                        from escenas.juego import EscenaJuego
                        self.app.cambiar_escena(EscenaJuego(self.app))
                    else:
                        from escenas.menu import EscenaMenu
                        self.app.cambiar_escena(EscenaMenu(self.app))
                    break

    def draw(self):
        self.pantalla.fill(NEGRO)

        color = VERDE if self.gano else ROJO
        texto = "GANASTE" if self.gano else "PERDISTE"
        self.render._texto_centrado_ui(texto, self.fuentes["grande"], color,
                                        ANCHO // 2, 120)

        self.render._texto_centrado_ui(
            f"Rondas jugadas: {self.juego.ronda}",
            self.fuentes["normal"], BLANCO, ANCHO // 2, 200)
        self.render._texto_centrado_ui(
            f"HP final - Tu: {max(0, self.juego.hp_jugador)} | "
            f"Maquina: {max(0, self.juego.hp_enemigo)}",
            self.fuentes["normal"], BLANCO, ANCHO // 2, 240)

        for clave, texto_btn, rect in self.botones:
            hover = (self.hover == clave)
            self.render.dibujar_boton(rect, texto_btn, hover,
                                      COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF)

        self.render._texto_centrado_ui("ESC para volver al menu",
                                        self.fuentes["chica"], GRIS,
                                        ANCHO // 2, ALTO - 30)