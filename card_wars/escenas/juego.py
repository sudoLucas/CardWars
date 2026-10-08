# escenas/juego.py
import pygame
from config import (
    ANCHO, ALTO, Layout, Botones, Turno,
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

        # Botones
        self.boton_reiniciar = pygame.Rect(
            ANCHO // 2 - Botones.REINICIAR_W // 2, Botones.REINICIAR_Y,
            Botones.REINICIAR_W, Botones.REINICIAR_H,
        )
        self.boton_siguiente = pygame.Rect(
            ANCHO // 2 - Botones.SIGUIENTE_W // 2, Botones.SIGUIENTE_Y,
            Botones.SIGUIENTE_W, Botones.SIGUIENTE_H,
        )

        self.rects_jugador = []
        self.rects_enemigo = []

    # ---------- Helpers ----------
    def nueva_partida(self):
        self.juego = Juego(self.dificultad)
        self.tiempo_resolucion = 0

    def calcular_rects(self):
        # --- Cartas del jugador: solo las VIVAS, reacomodadas ---
        vivas_jugador = [(i, c) for i, c in enumerate(self.juego.mazo_jugador.cartas) if c.viva]
        cantidad_j = len(vivas_jugador)
        self.rects_jugador = []

        if cantidad_j > 0:
            x_inicio = Layout.x_inicio_cartas(cantidad_j, ANCHO)
            for pos, (idx_real, _) in enumerate(vivas_jugador):
                x = x_inicio + pos * (Layout.CARTA_W + Layout.ESPACIO_CARTAS)
                self.rects_jugador.append(
                    (idx_real, pygame.Rect(x, Layout.Y_CARTAS_TU, Layout.CARTA_W, Layout.CARTA_H))
                )

        # --- Cartas del rival: solo las VIVAS ---
        vivas_rival = [(i, c) for i, c in enumerate(self.juego.mazo_enemigo.cartas) if c.viva]
        cantidad_e = len(vivas_rival)
        self.rects_enemigo = []

        if cantidad_e > 0:
            x_inicio = Layout.x_inicio_cartas(cantidad_e, ANCHO)
            for pos, (idx_real, _) in enumerate(vivas_rival):
                x = x_inicio + pos * (Layout.CARTA_W + Layout.ESPACIO_CARTAS)
                self.rects_enemigo.append(
                    (idx_real, pygame.Rect(x, Layout.Y_CARTAS_RIVAL, Layout.CARTA_W, Layout.CARTA_H))
                )

    # ---------- Eventos ----------
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

    # ---------- Update ----------
    def update(self, dt):
        self.render.tick(dt)
        self.calcular_rects()

        # Auto-avance de ronda
        if self.juego.turno == Turno.RESOLVIENDO:
            if pygame.time.get_ticks() - self.tiempo_resolucion > DUELO_DURACION:
                self.juego.siguiente_ronda()
                self.tiempo_resolucion = 0

        # Si terminó, ir a la escena de fin
        if self.juego.turno == Turno.FIN:
            from escenas.fin import EscenaFin
            self.app.cambiar_escena(EscenaFin(self.app, self.juego))

    # ---------- Draw ----------
    def draw(self):
        mouse = pygame.mouse.get_pos()
        self.render.dibujar_escena(
            self.juego, self.rects_jugador, self.rects_enemigo, mouse,
            self.boton_reiniciar, self.boton_siguiente,
        )
