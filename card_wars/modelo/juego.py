# modelo/juego.py
from config import Turno
from modelo.mazo import Mazo
from modelo.ia import crear_estrategia


class Juego:
    def __init__(self, dificultad):
        self.dificultad = dificultad
        self.estrategia = crear_estrategia(dificultad.estrategia_ia)
        self.reiniciar()

    def reiniciar(self):
        tamano = self.dificultad.tamano_mazo
        self.mazo_jugador = Mazo(tamano)
        self.mazo_enemigo = Mazo(tamano)
        self.hp_jugador = self.dificultad.hp_jugador
        self.hp_enemigo = self.dificultad.hp_enemigo
        self.hp_jugador_max = self.dificultad.hp_jugador
        self.hp_enemigo_max = self.dificultad.hp_enemigo
        self.turno = Turno.JUGADOR
        self.ronda = 1
        self.mensaje = "zz Round one: elegi una carta pa' bajar"
        self.carta_jugada_jugador = None
        self.carta_jugada_enemigo = None

    # ---------- Turno del jugador ----------
    def jugador_tira_carta(self, idx):
        if self.turno != Turno.JUGADOR:
            return
        if idx >= len(self.mazo_jugador):
            return

        carta_j = self.mazo_jugador[idx]
        if not carta_j.viva:
            self.mensaje = "zz Carta descartada, pa"
            return

        # Asegurar que el rival tenga carta
        if not self.mazo_enemigo.hay_vivas():
            self.mazo_enemigo.rebarajar_si_hace_falta(self.hp_enemigo)

        # La IA decide
        carta_e, idx_e = self.estrategia.elegir(
            self.mazo_enemigo, self.mazo_jugador,
            self.hp_enemigo, self.hp_jugador,
        )

        if carta_e is None:
            self.chequear_fin()
            return

        self.carta_jugada_jugador = idx
        self.carta_jugada_enemigo = idx_e

        self.resolver_batalla(carta_j, carta_e)
        self.turno = Turno.RESOLVIENDO
        self.chequear_fin()

    # ---------- Resolucion 1 vs 1 ----------
    def resolver_batalla(self, carta_j, carta_e):
        if carta_j.poder > carta_e.poder:
            dano = carta_j.poder - carta_e.poder
            carta_e.recibir_golpe(carta_j.poder)
            self.hp_enemigo -= dano
            self.mensaje = (f"zz {carta_j.nombre} ({carta_j.poder}) vence a "
                            f"{carta_e.nombre} ({carta_e.poder}) - {dano} HP al rival")
        elif carta_e.poder > carta_j.poder:
            dano = carta_e.poder - carta_j.poder
            carta_j.recibir_golpe(carta_e.poder)
            self.hp_jugador -= dano
            self.mensaje = (f"zz {carta_e.nombre} ({carta_e.poder}) vence a "
                            f"{carta_j.nombre} ({carta_j.poder}) - {dano} HP a ti")
        else:
            carta_j.morir()
            carta_e.morir()
            self.mensaje = "zz Empate: las cartas se mataron"

    # ---------- Avanzar ronda ----------
    def siguiente_ronda(self):
        if self.turno == Turno.FIN:
            return
        self.ronda += 1
        self.carta_jugada_jugador = None
        self.carta_jugada_enemigo = None

        self.mazo_jugador.rebarajar_si_hace_falta(self.hp_jugador)
        self.mazo_enemigo.rebarajar_si_hace_falta(self.hp_enemigo)

        self.turno = Turno.JUGADOR
        self.mensaje = f"zz Round {self.ronda}: elegi una carta para bajar"
        self.chequear_fin()

    # ---------- Fin de partida ----------
    def chequear_fin(self):
        if self.hp_jugador <= 0:
            self.turno = Turno.FIN
            self.mensaje = "zz PERDISTE. Toca R para reiniciar"
            return True
        elif self.hp_enemigo <= 0:
            self.turno = Turno.FIN
            self.mensaje = "zz GANASTE. Toca R para reiniciar"
            return True
        return False