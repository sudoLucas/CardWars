# main.py
import sys
import pygame

from config import TITULO, VERSION, ANCHO, ALTO, FPS, DIFICULTAD_DEFAULT
from vista.fuentes import cargar_fuentes
from vista.render import Render
from escenas.menu import EscenaMenu


class App:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(f"{TITULO} v{VERSION}")
        self.reloj = pygame.time.Clock()
        self.fuentes = cargar_fuentes()
        self.render = Render(self.pantalla, self.fuentes)

        # Estado global
        self.clave_dificultad = DIFICULTAD_DEFAULT
        self.escena = None

        # Arrancar en el menu
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

            pygame.display.flip()


if __name__ == "__main__":
    App().run()