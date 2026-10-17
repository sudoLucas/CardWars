# modelo/progreso.py
import os
import json
from config import DIRECTORIO_RAIZ


RUTA_PROGRESO = "progreso.json"


class Progreso:
    def __init__(self, ruta=RUTA_PROGRESO):
        self.ruta = ruta
        self.datos = self._cargar()

    def _cargar(self):
        if not os.path.isfile(self.ruta):
            return {
                "facil": ["nivel1"],
                "normal": ["nivel1"],
                "duro": ["nivel1"],
            }
        try:
            with open(self.ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
            for dif in ("facil", "normal", "duro"):
                if dif not in datos:
                    datos[dif] = ["nivel1"]
            return datos
        except Exception as e:
            print(f"[progreso] Error al cargar {self.ruta}: {e}")
            return {
                "facil": ["nivel1"],
                "normal": ["nivel1"],
                "duro": ["nivel1"],
            }

    def guardar(self):
        try:
            with open(self.ruta, "w", encoding="utf-8") as f:
                json.dump(self.datos, f, indent=2)
        except Exception as e:
            print(f"[progreso] Error al guardar {self.ruta}: {e}")

    def desbloqueados(self, dificultad):
        return set(self.datos.get(dificultad, ["nivel1"]))

    def desbloquear(self, dificultad, nivel):
        if dificultad not in self.datos:
            self.datos[dificultad] = ["nivel1"]
        if nivel not in self.datos[dificultad]:
            self.datos[dificultad].append(nivel)
            self.guardar()