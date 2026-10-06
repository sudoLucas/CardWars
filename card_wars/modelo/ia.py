# modelo/ia.py
"""
Estrategias de IA para el rival.

Todas heredan de Estrategia e implementan:
    elegir(mazo_propio, mazo_rival, hp_propio, hp_rival) -> (carta, idx)

El Juego solo llama a .elegir(). No sabe ni le importa como decide cada una.
"""

import random


# ============================================================
# BASE
# ============================================================
class Estrategia:
    """Interfaz base. No se instancia directamente."""
    nombre = "Estrategia"

    def elegir(self, mazo_propio, mazo_rival, hp_propio, hp_rival):
        raise NotImplementedError


# ============================================================
# FACIL - Juega al azar
# ============================================================
class IARandom(Estrategia):
    nombre = "Aleatoria"

    def elegir(self, mazo_propio, mazo_rival, hp_propio, hp_rival):
        return mazo_propio.elegir_al_azar_viva()


# ============================================================
# NORMAL - Guarda las cartas fuertes
# Regla: juega la mas debil que pueda ganar.
#        Si no puede ganar, sacrifica la mas debil.
# ============================================================
class IAConservadora(Estrategia):
    nombre = "Conservadora"

    def elegir(self, mazo_propio, mazo_rival, hp_propio, hp_rival):
        vivas_propias = mazo_propio.vivas()
        vivas_rivales = mazo_rival.vivas()

        if not vivas_propias:
            return None, None

        # Si no sabemos que tiene el rival, jugamos la mas debil
        if not vivas_rivales:
            return self._mas_debil(mazo_propio, vivas_propias)

        # Poder maximo del rival (lo peor que nos pueden tirar)
        peor_rival = max(c.poder for c in vivas_rivales)

        # Buscamos la carta mas debil que AUN pueda ganarle al peor del rival
        ganadoras = [c for c in vivas_propias if c.poder > peor_rival]

        if ganadoras:
            # La mas debil de las ganadoras (no gastamos la bomba)
            elegida = min(ganadoras, key=lambda c: c.poder)
        else:
            # No podemos ganar contra el peor: sacrificamos la mas debil
            elegida = min(vivas_propias, key=lambda c: c.poder)

        return elegida, mazo_propio.indice(elegida)

    @staticmethod
    def _mas_debil(mazo, vivas):
        elegida = min(vivas, key=lambda c: c.poder)
        return elegida, mazo.indice(elegida)


# ============================================================
# DURO - Se adapta al estado de la partida
# Mira HP relativo y cartas vivas del jugador.
# ============================================================
class IAAdaptativa(Estrategia):
    nombre = "Adaptativa"

    def elegir(self, mazo_propio, mazo_rival, hp_propio, hp_rival):
        vivas_propias = mazo_propio.vivas()
        vivas_rivales = mazo_rival.vivas()

        if not vivas_propias:
            return None, None

        if not vivas_rivales:
            elegida = max(vivas_propias, key=lambda c: c.poder)
            return elegida, mazo_propio.indice(elegida)

        peor_rival = max(c.poder for c in vivas_rivales)
        mejor_propia = max(vivas_propias, key=lambda c: c.poder)
        mas_debil_propia = min(vivas_propias, key=lambda c: c.poder)

        # --- Cerrar la partida si puede ---
        # Si estamos por debajo y el jugador puede morir con un golpe,
        # jugamos la bomba para intentar terminar YA.
        if hp_rival <= mejor_propia.poder:
            # Pero solo si no nos matan antes
            if hp_propio > peor_rival:
                return mejor_propia, mazo_propio.indice(mejor_propia)

        # --- Estamos perdiendo por HP: ser agresivos ---
        if hp_propio < hp_rival:
            # Jugar la mas fuerte que no pierda contra el peor del rival
            ganadoras = [c for c in vivas_propias if c.poder >= peor_rival]
            if ganadoras:
                elegida = max(ganadoras, key=lambda c: c.poder)
                return elegida, mazo_propio.indice(elegida)
            # No podemos ganar: sacrificamos la mas debil
            return mas_debil_propia, mazo_propio.indice(mas_debil_propia)

        # --- Estamos ganando por HP: conservar ---
        # Igual que la conservadora: la mas debil que gane.
        ganadoras = [c for c in vivas_propias if c.poder > peor_rival]
        if ganadoras:
            elegida = min(ganadoras, key=lambda c: c.poder)
        else:
            elegida = mas_debil_propia

        return elegida, mazo_propio.indice(elegida)


# ============================================================
# REGISTRO
# El Juego busca aca la clase por nombre. Config usa el string.
# ============================================================
ESTRATEGIAS = {
    "IARandom":        IARandom,
    "IAConservadora":  IAConservadora,
    "IAAdaptativa":    IAAdaptativa,
}


def crear_estrategia(nombre):
    """Devuelve una instancia de estrategia. Fallback a IARandom."""
    clase = ESTRATEGIAS.get(nombre, IARandom)
    return clase()