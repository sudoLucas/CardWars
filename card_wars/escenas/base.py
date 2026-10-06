# escenas/base.py

class Escena:
    """
    Clase base de todas las escenas.
    Cada escena recibe una referencia a la App para poder cambiar de escena.
    """

    def __init__(self, app):
        self.app = app
        self.pantalla = app.pantalla
        self.fuentes = app.fuentes
        self.render = app.render

    def on_enter(self):
        """Se llama cuando la escena pasa a ser la activa."""
        pass

    def on_exit(self):
        """Se llama cuando la escena deja de ser la activa."""
        pass

    def handle_event(self, evento):
        """Procesa un evento de pygame."""
        pass

    def update(self, dt):
        """Actualiza la logica (dt en ms)."""
        pass

    def draw(self):
        """Dibuja la escena."""
        pass