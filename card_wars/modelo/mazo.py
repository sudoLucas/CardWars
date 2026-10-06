# modelo/mazo.py
import random
from config import POOL_CARTAS
from modelo.carta import Carta


class Mazo:
    def __init__(self, tamano, pool=None):
        self.tamano = tamano
        self.pool = pool or POOL_CARTAS
        self.cartas = []
        self.rebarajes = 0
        self.barajar()

    def barajar(self):
        elegidas = random.sample(self.pool, self.tamano)
        self.cartas = [Carta(n, p) for n, p in elegidas]

    def vivas(self):
        return [c for c in self.cartas if c.viva]

    def hay_vivas(self):
        return any(c.viva for c in self.cartas)

    def rebarajar_si_hace_falta(self, hp_dueno):
        """Si no quedan vivas y el dueno sigue con HP, baraja nuevas cartas."""
        if not self.hay_vivas() and hp_dueno > 0:
            self.barajar()
            self.rebarajes += 1
            return True
        return False

    def elegir_al_azar_viva(self):
        vivas = self.vivas()
        if not vivas:
            return None, None
        carta = random.choice(vivas)
        return carta, self.cartas.index(carta)

    def indice(self, carta):
        return self.cartas.index(carta)

    def __len__(self):
        return len(self.cartas)

    def __getitem__(self, idx):
        return self.cartas[idx]