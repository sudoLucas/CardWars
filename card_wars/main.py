# main.py
import sys
import os
import pygame

import config
from config import (
    TITULO, VERSION, FPS, DIFICULTAD_DEFAULT, ESCALA_PIXEL,
    RESOLUCION_INTERNA_W, RESOLUCION_INTERNA_H,
)
from vista.colores import COLOR_FONDO_BARRA
from vista.fuentes import cargar_fuentes
from vista.render import Render
from escenas.menu import EscenaMenu
from modelo.progreso import Progreso


class App:
    def __init__(self):
        pygame.init()

        # Inicializar el sistema de audio
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"[audio] No se pudo inicializar el audio: {e}")

        self.ancho_ventana, self.alto_ventana = config.inicializar_ventana()
        self.ventana = pygame.display.set_mode(
            (self.ancho_ventana, self.alto_ventana)
        )
        pygame.display.set_caption(f"{TITULO} v{VERSION}")
        self.reloj = pygame.time.Clock()

        self.ancho_interno = RESOLUCION_INTERNA_W
        self.alto_interno = RESOLUCION_INTERNA_H

        self.surface_mundo = pygame.Surface(
            (self.ancho_interno // ESCALA_PIXEL,
             self.alto_interno // ESCALA_PIXEL),
            pygame.SRCALPHA,
        )
        self.surface_ui = pygame.Surface(
            (self.ancho_interno, self.alto_interno),
            pygame.SRCALPHA,
        )
        self.surface_frame = pygame.Surface(
            (self.ancho_interno, self.alto_interno)
        )

        self.fuentes = cargar_fuentes()
        self.render = Render(self.surface_mundo, self.surface_ui, self.fuentes)
        self.pantalla = self.surface_mundo

        self.clave_dificultad = DIFICULTAD_DEFAULT
        self.nivel_actual = None

        self.tiempo_fondo = 0.0

        # --- Progreso persistente ---
        self.progreso = Progreso()

        # --- Estado de la musica ---
        self.musica_actual = None

        self.escena = None
        self.cambiar_escena(EscenaMenu(self))

    def cambiar_escena(self, nueva_escena):
        if self.escena is not None:
            self.escena.on_exit()
        self.escena = nueva_escena
        self.escena.on_enter()

    def _pos_interna(self, pos):
        mx, my = pos
        return (
            int(mx * self.ancho_interno / self.ancho_ventana),
            int(my * self.alto_interno / self.alto_ventana),
        )

    def _mouse_interno(self):
        return self._pos_interna(pygame.mouse.get_pos())

    # ============================================================
    # CONTROL DE MUSICA
    # ============================================================
    def cambiar_musica(self, ruta_musica):
        """Cambia la musica de fondo. Si ya esta sonando esa misma, no hace nada."""
        if not os.path.isfile(ruta_musica):
            print(f"[audio] Musica NO ENCONTRADA: {ruta_musica}")
            return

        # Si ya está sonando la misma canción, no la cortamos
        if self.musica_actual == ruta_musica and pygame.mixer.music.get_busy():
            return

        try:
            pygame.mixer.music.load(ruta_musica)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)  # -1 = loop infinito
            self.musica_actual = ruta_musica
        except Exception as e:
            print(f"[audio] Error al cambiar musica: {e}")

    def parar_musica(self):
        try:
            pygame.mixer.music.stop()
            self.musica_actual = None
        except Exception:
            pass

    def desbloquear_siguiente_nivel(self, dificultad, nivel_actual):
        """Desbloquea el nivel que sigue al actual (si existe)."""
        if nivel_actual is None:
            return

        try:
            num = int(nivel_actual.replace("nivel", ""))
        except ValueError:
            return

        siguiente = f"nivel{num + 1}"
        max_nivel = 3

        if num < max_nivel:
            self.progreso.desbloquear(dificultad, siguiente)

    def run(self):
        while True:
            dt = self.reloj.tick(FPS)

            mouse = self._mouse_interno()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if evento.type in (pygame.MOUSEBUTTONDOWN,
                                   pygame.MOUSEBUTTONUP,
                                   pygame.MOUSEMOTION):
                    mouse = self._pos_interna(evento.pos)

                self.escena.handle_event(evento, mouse)

            self.escena.update(dt)
            self.render.fondo_tablero = None
            self.escena.draw()

            self.surface_frame.fill(COLOR_FONDO_BARRA)
            if self.render.fondo_tablero is not None:
                self.surface_frame.blit(self.render.fondo_tablero, (0, 0))

            mundo_escalado = pygame.transform.scale(
                self.surface_mundo,
                (self.ancho_interno, self.alto_interno),
            )

            self.surface_frame.blit(mundo_escalado, (0, 0))
            self.surface_frame.blit(self.surface_ui, (0, 0))

            frame_escalado = pygame.transform.scale(
                self.surface_frame,
                (self.ancho_ventana, self.alto_ventana),
            )

            self.ventana.blit(frame_escalado, (0, 0))
            pygame.display.flip()

            self.surface_ui.fill((0, 0, 0, 0))


if __name__ == "__main__":
    App().run()