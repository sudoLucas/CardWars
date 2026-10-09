# escenas/juego.py
import pygame
from config import (
    ANCHO, ALTO, Layout, Botones, Turno, ESCALA_PIXEL,
    DUELO_DURACION, get_dificultad,
)
from escenas.base import Escena
from modelo.juego import Juego


class EscenaJuego(Escena):
    def __init__(self, app, clave_dificultad=None):
        super().__init__(app)

        if clave_dificultad is not None:
            app.clave_dificultad = clave_dificultad
        self.dificultad = get_dificultad(app.clave_dificultad)

        self.juego = Juego(self.dificultad)
        self.tiempo_resolucion = 0

        e = ESCALA_PIXEL

        # Botones en PANTALLA REAL (para los clicks).
        self.boton_reiniciar = pygame.Rect(
            Botones.REINICIAR_X * e,
            Botones.REINICIAR_Y * e,
            Botones.REINICIAR_W * e,
            Botones.REINICIAR_H * e,
        )
        self.boton_siguiente = pygame.Rect(
            Botones.SIGUIENTE_X * e,
            Botones.SIGUIENTE_Y * e,
            Botones.SIGUIENTE_W * e,
            Botones.SIGUIENTE_H * e,
        )

        self.rects_jugador = []
        self.rects_enemigo = []

    def nueva_partida(self):
        self.juego = Juego(self.dificultad)
        self.tiempo_resolucion = 0

    def _ancho_mundo(self):
        return ANCHO // ESCALA_PIXEL

    def calcular_rects(self):
        e = ESCALA_PIXEL
        ancho_m = self._ancho_mundo()

        # --- Cartas del jugador (vivas) ---
        vivas_j = [(i, c) for i, c in enumerate(self.juego.mazo_jugador.cartas) if c.viva]
        cantidad_j = len(vivas_j)
        self.rects_jugador = []

        if cantidad_j > 0:
            x_inicio_m = Layout.x_inicio_cartas(cantidad_j, ancho_m)
            for pos, (idx_real, _) in enumerate(vivas_j):
                x_m = x_inicio_m + pos * (Layout.CARTA_W + Layout.ESPACIO_CARTAS)
                rect = pygame.Rect(
                    x_m * e, Layout.Y_TOP_MANO * e,
                    Layout.CARTA_W * e, Layout.CARTA_H * e,
                )
                self.rects_jugador.append((idx_real, rect))

        # --- Cartas del rival (solo índices) ---
        vivas_e = [(i, c) for i, c in enumerate(self.juego.mazo_enemigo.cartas) if c.viva]
        self.rects_enemigo = [(idx_real, pygame.Rect(0, 0, 0, 0))
                              for idx_real, _ in vivas_e]

    def handle_event(self, evento):
        mouse = pygame.mouse.get_pos()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                from escenas.menu import EscenaMenu
                self.app.cambiar_escena(EscenaMenu(self.app))
                return
            if evento.key == pygame.K_r:
                self.nueva_partida()
            if evento.key == pygame.K_SPACE and self.juego.turno == Turno.RESOLVIENDO:
                self.juego.siguiente_ronda()
                self.tiempo_resolucion = 0

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.boton_reiniciar.collidepoint(mouse):
                self.nueva_partida()
                return

            if self.juego.turno == Turno.JUGADOR:
                for idx, rect in self.rects_jugador:
                    if rect.collidepoint(mouse):
                        self.juego.jugador_tira_carta(idx)
                        self.tiempo_resolucion = pygame.time.get_ticks()
                        break

            elif self.juego.turno == Turno.RESOLVIENDO:
                if self.boton_siguiente.collidepoint(mouse):
                    self.juego.siguiente_ronda()
                    self.tiempo_resolucion = 0

    def update(self, dt):
        self.render.tick(dt)
        self.calcular_rects()

        if self.juego.turno == Turno.RESOLVIENDO:
            if pygame.time.get_ticks() - self.tiempo_resolucion > DUELO_DURACION:
                self.juego.siguiente_ronda()
                self.tiempo_resolucion = 0

        if self.juego.turno == Turno.FIN:
            from escenas.fin import EscenaFin
            self.app.cambiar_escena(EscenaFin(self.app, self.juego))

    def draw(self):
        mouse = pygame.mouse.get_pos()
        self.render.dibujar_escena(
            self.juego, self.rects_jugador, self.rects_enemigo, mouse,
            self.boton_reiniciar, self.boton_siguiente,
        )