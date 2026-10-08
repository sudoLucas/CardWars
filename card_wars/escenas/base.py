# escenas/base.py

class Escena:
    """
    Clase base de todas las escenas.
    """

    def __init__(self, app):
        self.app = app
        self.pantalla = app.pantalla          # surface_mundo (pixelada)
        self.surface_ui = app.surface_ui      # surface_ui (nitida)
        self.fuentes = app.fuentes
        self.render = app.render

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def handle_event(self, evento):
        pass

    def update(self, dt):
        pass

    def draw(self):
        pass