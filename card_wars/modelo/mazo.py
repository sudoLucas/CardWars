# modelo/mazo.py
import random
from config import POOL_CARTAS, POOL_HECHIZOS, HECHIZOS
from modelo.carta import Carta


class Mazo:
    def __init__(self, tamano, cartas_iniciales=None):
        self.tamano = tamano
        self.cartas = []
        self.rebarajes = 0

        if cartas_iniciales is not None:
            self.cartas = cartas_iniciales
        else:
            self.barajar_inicial()

    def _reparto(self):
        if self.tamano <= 3:
            return 1, 2
        elif self.tamano == 4:
            return 2, 2
        else:
            return 3, 3

    def _crear_criaturas(self, cantidad):
        pool = random.sample(POOL_CARTAS, min(cantidad, len(POOL_CARTAS)))
        return [Carta(n, p, tipo="criatura") for n, p in pool]

    def _crear_hechizos(self, cantidad):
        ids = random.sample(POOL_HECHIZOS, min(cantidad, len(POOL_HECHIZOS)))
        cartas = []
        for hid in ids:
            data = HECHIZOS[hid]
            cartas.append(Carta(
                nombre=data["nombre"],
                poder=0,
                tipo="hechizo",
                hechizo_id=hid,
                costo_mana=data["costo"],
            ))
        return cartas

    def barajar_inicial(self):
        cant_cri, cant_hec = self._reparto()
        self.cartas = []
        self.cartas.extend(self._crear_criaturas(cant_cri))
        self.cartas.extend(self._crear_hechizos(cant_hec))
        random.shuffle(self.cartas)

    def barajar(self):
        cant_cri, cant_hec = self._reparto()
        self.cartas = []
        self.cartas.extend(self._crear_criaturas(cant_cri))
        self.cartas.extend(self._crear_hechizos(cant_hec))
        random.shuffle(self.cartas)
        self.rebarajes += 1

    def vivas(self):
        return [c for c in self.cartas if c.viva]

    def hay_vivas(self):
        return any(c.viva for c in self.cartas)

    def tiene_criaturas_vivas(self):
        """Devuelve True si al menos una carta viva es de tipo criatura."""
        return any(c.viva and getattr(c, "tipo", "criatura") == "criatura"
                   for c in self.cartas)

    def rebarajar_si_hace_falta(self, hp_dueno):
        """Rebaraja si no quedan vivas o si no hay criaturas vivas."""
        if hp_dueno <= 0:
            return False

        # Si no hay vivas, barajar todo
        if not self.hay_vivas():
            self.barajar()
            return True

        # Si hay vivas pero ninguna es criatura, barajar todo
        if not self.tiene_criaturas_vivas():
            self.barajar()
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