# modelo/progreso.py

class Progreso:
    def __init__(self, ruta=None):

        self.datos = {
            "facil": ["nivel1"],
            "normal": ["nivel1"],
            "duro": ["nivel1"],
        }

    def desbloqueados(self, dificultad):
        return set(self.datos.get(dificultad, ["nivel1"]))

    def desbloquear(self, dificultad, nivel):
        if dificultad not in self.datos:
            self.datos[dificultad] = ["nivel1"]
        if nivel not in self.datos[dificultad]:
            self.datos[dificultad].append(nivel)
            
    def guardar(self):
        pass