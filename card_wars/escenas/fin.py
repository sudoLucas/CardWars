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
            ("revancha", "zz REVANCHA", pygame.Rect(cx - w // 2, y + 0 * sep, w, h)),
            ("menu",     "zz MENU",     pygame.Rect(cx - w // 2, y + 1 * sep, w, h)),
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

        # Titulo grande
        color = VERDE if self.gano else ROJO
        texto = "zz GANASTE" if self.gano else "zz PERDISTE"
        self.render._texto_centrado(texto, self.fuentes["grande"], color,
                                    ANCHO // 2, 120)

        # Stats
        self.render._texto_centrado(
            f"zz Rondas jugadas: {self.juego.ronda}",
            self.fuentes["normal"], BLANCO, ANCHO // 2, 200)
        self.render._texto_centrado(
            f"zz HP final - Tu: {max(0, self.juego.hp_jugador)} | "
            f"Maquina: {max(0, self.juego.hp_enemigo)}",
            self.fuentes["normal"], BLANCO, ANCHO // 2, 240)

        # Botones
        for clave, texto_btn, rect in self.botones:
            hover = (self.hover == clave)
            self.render.dibujar_boton(rect, texto_btn, hover,
                                      COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF)

        # Pie
        self.render._texto_centrado("zz ESC para volver al menu",
                                    self.fuentes["chica"], GRIS,
                                    ANCHO // 2, ALTO - 30)