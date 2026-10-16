# main.py
import sys
import pygame

import config
from config import (
    TITULO, VERSION, FPS, DIFICULTAD_DEFAULT, ESCALA_PIXEL,
    RESOLUCION_INTERNA_W, RESOLUCION_INTERNA_H,
)
from vista.fuentes import cargar_fuentes
from vista.render import Render
from escenas.menu import EscenaMenu


class App:
    def __init__(self):
        pygame.init()

        # Tamano REAL de la ventana (900x600 por defecto)
        self.ancho_ventana, self.alto_ventana = config.inicializar_ventana()
        self.ventana = pygame.display.set_mode(
            (self.ancho_ventana, self.alto_ventana)
        )
        pygame.display.set_caption(f"{TITULO} v{VERSION}")
        self.reloj = pygame.time.Clock()

        # Resolucion INTERNA (siempre 1200x800)
        self.ancho_interno = RESOLUCION_INTERNA_W
        self.alto_interno = RESOLUCION_INTERNA_H

        # Superficies internas
        self.surface_mundo = pygame.Surface(
            (self.ancho_interno // ESCALA_PIXEL,
             self.alto_interno // ESCALA_PIXEL)
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

        # Tiempo compartido entre escenas (para que el fondo no se resetee)
        self.tiempo_fondo = 0.0

        self.escena = None
        self.cambiar_escena(EscenaMenu(self))

    def cambiar_escena(self, nueva_escena):
        if self.escena is not None:
            self.escena.on_exit()
        self.escena = nueva_escena
        self.escena.on_enter()

    def _pos_interna(self, pos):
        """Convierte una posicion de la ventana real a coords internas."""
        mx, my = pos
        return (
            int(mx * self.ancho_interno / self.ancho_ventana),
            int(my * self.alto_interno / self.alto_ventana),
        )

    def _mouse_interno(self):
        """Posicion actual del mouse en coords internas."""
        return self._pos_interna(pygame.mouse.get_pos())

    def run(self):
        while True:
            dt = self.reloj.tick(FPS)

            # Mouse traducido al espacio interno
            mouse = self._mouse_interno()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Si el evento trae posicion, actualizamos el mouse
                if evento.type in (pygame.MOUSEBUTTONDOWN,
                                   pygame.MOUSEBUTTONUP,
                                   pygame.MOUSEMOTION):
                    mouse = self._pos_interna(evento.pos)

                self.escena.handle_event(evento, mouse)

            self.escena.update(dt)
            self.escena.draw()

            # 1) Escalar el MUNDO a la resolucion interna
            mundo_escalado = pygame.transform.scale(
                self.surface_mundo,
                (self.ancho_interno, self.alto_interno),
            )

            # 2) Componer mundo + UI en el frame interno
            self.surface_frame.blit(mundo_escalado, (0, 0))
            self.surface_frame.blit(self.surface_ui, (0, 0))

            # 3) Escalar el frame al tamano de la ventana
            frame_escalado = pygame.transform.scale(
                self.surface_frame,
                (self.ancho_ventana, self.alto_ventana),
            )

            # 4) Blitear a la ventana
            self.ventana.blit(frame_escalado, (0, 0))
            pygame.display.flip()

            self.surface_ui.fill((0, 0, 0, 0))


if __name__ == "__main__":
    App().run()