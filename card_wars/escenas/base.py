# escenas/base.py

class Escena:
    """
    Clase base de todas las escenas.
    """

    def __init__(self, app):
        self.app = app
        self.pantalla = app.pantalla
        self.surface_ui = app.surface_ui
        self.fuentes = app.fuentes
        self.render = app.render

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def handle_event(self, evento, mouse):
        """
        mouse ya viene traducido al espacio interno (1200x800).
        """
        pass

    def update(self, dt):
        pass

    def draw(self):
        pass