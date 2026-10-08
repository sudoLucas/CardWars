# main.py
import sys
import pygame

from config import TITULO, VERSION, ANCHO, ALTO, FPS, DIFICULTAD_DEFAULT
from vista.fuentes import cargar_fuentes
from vista.render import Render
from escenas.menu import EscenaMenu


ESCALA_PIXEL = 4


class App:
    def __init__(self):
        pygame.init()

        # Ventana real (NO la pisamos nunca)
        self.ventana = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(f"{TITULO} v{VERSION}")
        self.reloj = pygame.time.Clock()

        # Surface del mundo (baja resolucion)
        self.surface_mundo = pygame.Surface((ANCHO // ESCALA_PIXEL, ALTO // ESCALA_PIXEL))

        # Surface de UI (resolucion completa, con alpha)
        self.surface_ui = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)

        # Fuentes
        self.fuentes = cargar_fuentes()

        # Render
        self.render = Render(self.surface_mundo, self.surface_ui, self.fuentes)

        # Alias para compatibilidad con las escenas (que usan self.pantalla)
        # Apunta al MUNDO, donde las escenas dibujan las formas.
        self.pantalla = self.surface_mundo

        # Estado global
        self.clave_dificultad = DIFICULTAD_DEFAULT
        self.escena = None

        self.cambiar_escena(EscenaMenu(self))

    def cambiar_escena(self, nueva_escena):
        if self.escena is not None:
            self.escena.on_exit()
        self.escena = nueva_escena
        self.escena.on_enter()

    def run(self):
        while True:
            dt = self.reloj.tick(FPS)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.escena.handle_event(evento)

            self.escena.update(dt)
            self.escena.draw()

            # Escalar el MUNDO
            mundo_escalado = pygame.transform.scale(self.surface_mundo, (ANCHO, ALTO))

            # Componer en la VENTANA real
            self.ventana.blit(mundo_escalado, (0, 0))
            self.ventana.blit(self.surface_ui, (0, 0))

            pygame.display.flip()

            # Limpiar la UI para el proximo frame
            self.surface_ui.fill((0, 0, 0, 0))


if __name__ == "__main__":
    App().run()