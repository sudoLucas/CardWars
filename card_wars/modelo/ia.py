# modelo/ia.py
import random
from config import HECHIZOS


# ============================================================
# BASE
# ============================================================
class Estrategia:
    """Interfaz base. No se instancia directamente."""
    nombre = "Estrategia"

    def elegir(self, mazo_propio, mazo_rival, hp_propio, hp_rival):
        raise NotImplementedError

    def usar_hechizo(self, juego):
        """Por defecto, la IA no usa hechizos."""
        pass


# ============================================================
# FACIL - Juega al azar
# ============================================================
class IARandom(Estrategia):
    nombre = "Aleatoria"

    def elegir(self, mazo_propio, mazo_rival, hp_propio, hp_rival):
        criaturas = [c for c in mazo_propio.vivas() if c.tipo == "criatura"]
        if not criaturas:
            return None, None
        carta = random.choice(criaturas)
        return carta, mazo_propio.indice(carta)


# ============================================================
# NORMAL - Guarda las cartas fuertes
# ============================================================
class IAConservadora(Estrategia):
    nombre = "Conservadora"

    def elegir(self, mazo_propio, mazo_rival, hp_propio, hp_rival):
        criaturas_propias = [c for c in mazo_propio.vivas() if c.tipo == "criatura"]
        criaturas_rivales = [c for c in mazo_rival.vivas() if c.tipo == "criatura"]

        if not criaturas_propias:
            return None, None

        if not criaturas_rivales:
            elegida = min(criaturas_propias, key=lambda c: c.poder)
            return elegida, mazo_propio.indice(elegida)

        peor_rival = max(c.poder for c in criaturas_rivales)
        ganadoras = [c for c in criaturas_propias if c.poder > peor_rival]

        if ganadoras:
            elegida = min(ganadoras, key=lambda c: c.poder)
        else:
            elegida = min(criaturas_propias, key=lambda c: c.poder)

        return elegida, mazo_propio.indice(elegida)

    def usar_hechizo(self, juego):
        if juego.hp_enemigo >= juego.hp_enemigo_max * 0.4:
            return

        for carta in juego.mazo_enemigo.cartas:
            if carta.tipo != "hechizo" or not carta.viva:
                continue
            data = HECHIZOS[carta.hechizo_id]
            if carta.hechizo_id == "curacion" and \
               juego.puede_pagar("enemigo", data["costo"]):
                juego.hp_enemigo = min(
                    juego.hp_enemigo_max,
                    juego.hp_enemigo + data["bonus_hp"]
                )
                carta.morir()
                juego.gastar_mana("enemigo", data["costo"])
                return


# ============================================================
# DURO - Se adapta al estado de la partida
# ============================================================
class IAAdaptativa(Estrategia):
    nombre = "Adaptativa"

    def elegir(self, mazo_propio, mazo_rival, hp_propio, hp_rival):
        criaturas_propias = [c for c in mazo_propio.vivas() if c.tipo == "criatura"]
        criaturas_rivales = [c for c in mazo_rival.vivas() if c.tipo == "criatura"]

        if not criaturas_propias:
            return None, None

        if not criaturas_rivales:
            elegida = max(criaturas_propias, key=lambda c: c.poder)
            return elegida, mazo_propio.indice(elegida)

        peor_rival = max(c.poder for c in criaturas_rivales)
        mejor_propia = max(criaturas_propias, key=lambda c: c.poder)
        mas_debil_propia = min(criaturas_propias, key=lambda c: c.poder)

        if hp_rival <= mejor_propia.poder and hp_propio > peor_rival:
            return mejor_propia, mazo_propio.indice(mejor_propia)

        if hp_propio < hp_rival:
            ganadoras = [c for c in criaturas_propias if c.poder >= peor_rival]
            if ganadoras:
                elegida = max(ganadoras, key=lambda c: c.poder)
                return elegida, mazo_propio.indice(elegida)
            return mas_debil_propia, mazo_propio.indice(mas_debil_propia)

        ganadoras = [c for c in criaturas_propias if c.poder > peor_rival]
        if ganadoras:
            elegida = min(ganadoras, key=lambda c: c.poder)
        else:
            elegida = mas_debil_propia

        return elegida, mazo_propio.indice(elegida)

    def usar_hechizo(self, juego):
        for carta in juego.mazo_enemigo.cartas:
            if carta.tipo != "hechizo" or not carta.viva:
                continue
            data = HECHIZOS[carta.hechizo_id]
            if not juego.puede_pagar("enemigo", data["costo"]):
                continue

            hid = carta.hechizo_id

            if hid == "rayo":
                if juego.carta_jugada_jugador is not None:
                    criatura_j = juego.mazo_jugador[juego.carta_jugada_jugador]
                    if criatura_j.tipo == "criatura" and criatura_j.viva:
                        criatura_j.recibir_golpe(data["daño"])
                        carta.morir()
                        juego.gastar_mana("enemigo", data["costo"])
                        return

            elif hid == "debilidad":
                if juego.carta_jugada_jugador is not None:
                    criatura_j = juego.mazo_jugador[juego.carta_jugada_jugador]
                    if criatura_j.tipo == "criatura" and criatura_j.viva:
                        criatura_j.poder += data["bonus_poder"]
                        if criatura_j.poder < 0:
                            criatura_j.poder = 0
                        carta.morir()
                        juego.gastar_mana("enemigo", data["costo"])
                        return

            elif hid == "curacion":
                if juego.hp_enemigo < juego.hp_enemigo_max * 0.5:
                    juego.hp_enemigo = min(
                        juego.hp_enemigo_max,
                        juego.hp_enemigo + data["bonus_hp"]
                    )
                    carta.morir()
                    juego.gastar_mana("enemigo", data["costo"])
                    return

            elif hid == "fuerza":
                if juego.carta_jugada_enemigo is not None:
                    criatura_e = juego.mazo_enemigo[juego.carta_jugada_enemigo]
                    if criatura_e.tipo == "criatura" and criatura_e.viva:
                        criatura_e.poder += data["bonus_poder"]
                        carta.morir()
                        juego.gastar_mana("enemigo", data["costo"])
                        return

            elif hid == "inmovilizar":
                if juego.carta_jugada_jugador is not None:
                    criatura_j = juego.mazo_jugador[juego.carta_jugada_jugador]
                    if criatura_j.tipo == "criatura" and criatura_j.viva:
                        criatura_j.recibir_golpe(data["daño_aguante"])
                        carta.morir()
                        juego.gastar_mana("enemigo", data["costo"])
                        return


# ============================================================
# TUTORIAL - Siempre tira la mas debil
# ============================================================
class IATutorial(Estrategia):
    nombre = "Tutorial"

    def elegir(self, mazo_propio, mazo_rival, hp_propio, hp_rival):
        criaturas = [c for c in mazo_propio.vivas() if c.tipo == "criatura"]
        if not criaturas:
            return None, None
        elegida = min(criaturas, key=lambda c: c.poder)
        return elegida, mazo_propio.indice(elegida)


# ============================================================
# REGISTRO
# ============================================================
ESTRATEGIAS = {
    "IARandom":       IARandom,
    "IAConservadora": IAConservadora,
    "IAAdaptativa":   IAAdaptativa,
    "IATutorial":     IATutorial,
}


def crear_estrategia(nombre):
    """Devuelve una instancia de estrategia. Fallback a IARandom."""
    clase = ESTRATEGIAS.get(nombre, IARandom)
    return clase()