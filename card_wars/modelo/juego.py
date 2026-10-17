# modelo/juego.py
import random
import pygame
from config import (
    Turno, HECHIZOS,
    MANA_INICIAL, MANA_MAXIMO, MANA_SUMA_MIN, MANA_SUMA_MAX,
    TUTORIAL_ROUNDS,
)
from modelo.mazo import Mazo
from modelo.carta import Carta
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
        self.mana_jugador = MANA_INICIAL
        self.mana_enemigo = MANA_INICIAL
        self.ronda = 1
        self.turno = Turno.IA_TIRA
        self.mensaje = "zz La IA elige su carta..."
        self.carta_jugada_jugador = None
        self.carta_jugada_enemigo = None
        self.mensaje_hechizo = ""
        self.carta_vision_idx = None
        self.vision_activa_hasta = 0

        if getattr(self.dificultad, "es_tutorial", False):
            self._forzar_mazo_tutorial()

    def _forzar_mazo_tutorial(self):
        """Reemplaza los mazos por los del tutorial segun la ronda."""
        if self.ronda == 1:
            self.mazo_jugador.cartas = [
                Carta("Perro", 10, tipo="criatura"),
                Carta("Slime", 5, tipo="criatura"),
                Carta("Gato", 5, tipo="criatura"),
            ]
            self.mazo_enemigo.cartas = [
                Carta("Gato", 5, tipo="criatura"),
            ]
        elif self.ronda == 2:
            self.mazo_jugador.cartas = [
                Carta("Dragon", 15, tipo="criatura"),
                Carta("Vision", 0, tipo="hechizo", hechizo_id="vision", costo_mana=1),
                Carta("Robo", 0, tipo="hechizo", hechizo_id="robo", costo_mana=3),
            ]
            self.mazo_enemigo.cartas = [
                Carta("Perro", 10, tipo="criatura"),
            ]
        elif self.ronda == 3:
            self.mazo_jugador.cartas = [
                Carta("Fenix", 20, tipo="criatura"),
                Carta("Golem", 25, tipo="criatura"),
                Carta("Titan", 20, tipo="criatura"),
            ]
            self.mazo_enemigo.cartas = [
                Carta("Dragon", 15, tipo="criatura"),
            ]

    # ---------- Mana ----------
    def sumar_mana(self):
        suma_j = random.randint(MANA_SUMA_MIN, MANA_SUMA_MAX)
        suma_e = random.randint(MANA_SUMA_MIN, MANA_SUMA_MAX)
        self.mana_jugador = min(MANA_MAXIMO, self.mana_jugador + suma_j)
        self.mana_enemigo = min(MANA_MAXIMO, self.mana_enemigo + suma_e)

    def puede_pagar(self, jugador, costo):
        if jugador == "jugador":
            return self.mana_jugador >= costo
        return self.mana_enemigo >= costo

    def gastar_mana(self, jugador, costo):
        if jugador == "jugador":
            self.mana_jugador = max(0, self.mana_jugador - costo)
        else:
            self.mana_enemigo = max(0, self.mana_enemigo - costo)

    # ---------- Fase: IA tira primero ----------
    def ia_tira_carta(self):
        if self.turno != Turno.IA_TIRA:
            return

        carta_e, idx_e = self.estrategia.elegir(
            self.mazo_enemigo, self.mazo_jugador,
            self.hp_enemigo, self.hp_jugador,
        )

        if carta_e is None:
            if not self.mazo_enemigo.hay_vivas() or not self.mazo_enemigo.tiene_criaturas_vivas():
                self.mazo_enemigo.barajar()

                carta_e, idx_e = self.estrategia.elegir(
                    self.mazo_enemigo, self.mazo_jugador,
                    self.hp_enemigo, self.hp_jugador,
                )

        if carta_e is None:
            self.chequear_fin()
            return

        self.carta_jugada_enemigo = idx_e
        self.turno = Turno.JUGADOR_TIRA
        self.mensaje = "zz Tu turno: elegi una criatura para bajar"

    # ---------- Fase: jugador tira ----------
    def jugador_tira_carta(self, idx):
        if self.turno != Turno.JUGADOR_TIRA:
            return
        if idx >= len(self.mazo_jugador):
            return

        carta_j = self.mazo_jugador[idx]
        if not carta_j.viva:
            self.mensaje = "zz Carta descartada"
            return
        if getattr(carta_j, "tipo", "criatura") != "criatura":
            self.mensaje_hechizo = "zz Solo podes tirar criaturas aca"
            return

        self.carta_jugada_jugador = idx
        self.turno = Turno.JUGADOR_HECHIZOS
        self.mensaje = "zz Podes usar hechizos o clickear tu criatura para pelear"

    # ---------- Fase: jugador hechizos ----------
    def usar_hechizo(self, idx_carta, target_idx=None):
        if self.turno != Turno.JUGADOR_HECHIZOS:
            return False
        if idx_carta >= len(self.mazo_jugador):
            return False

        carta = self.mazo_jugador[idx_carta]
        if getattr(carta, "tipo", "criatura") != "hechizo" or not carta.viva:
            return False

        data = HECHIZOS[carta.hechizo_id]
        costo = data["costo"]

        if not self.puede_pagar("jugador", costo):
            self.mensaje_hechizo = "zz Sin mana suficiente"
            return False

        hid = carta.hechizo_id
        resultado = False

        if hid == "vision":
            if target_idx is None:
                return False
            self.carta_vision_idx = target_idx
            self.vision_activa_hasta = pygame.time.get_ticks() + 1500
            self.mensaje_hechizo = "zz Mirando una carta del rival"
            resultado = True

        elif hid == "robo":
            if target_idx is None:
                return False
            self._robar_carta_rival(target_idx)
            self.mensaje_hechizo = "zz Robaste una carta"
            resultado = True

        elif hid == "curacion":
            self.hp_jugador = min(self.hp_jugador_max,
                                  self.hp_jugador + data["bonus_hp"])
            self.mensaje_hechizo = f"zz +{data['bonus_hp']} HP"
            resultado = True

        elif hid == "rayo":
            criatura_e = self._criatura_jugada_enemiga()
            if criatura_e is not None:
                criatura_e.recibir_golpe(data["daño"])
                self.mensaje_hechizo = f"zz -{data['daño']} a la criatura rival"
                resultado = True

        elif hid == "drenaje":
            criatura_e = self._criatura_jugada_enemiga()
            if criatura_e is not None:
                criatura_e.recibir_golpe(data["daño"])
                self.hp_jugador = min(self.hp_jugador_max,
                                      self.hp_jugador + data["curacion"])
                self.mensaje_hechizo = f"zz -{data['daño']} rival, +{data['curacion']} HP"
                resultado = True

        elif hid == "fuerza":
            criatura_j = self._criatura_jugada_jugador()
            if criatura_j is not None:
                criatura_j.buff_poder += data["bonus_poder"]
                criatura_j.poder += data["bonus_poder"]
                self.mensaje_hechizo = f"zz +{data['bonus_poder']} poder"
                resultado = True

        elif hid == "defensa":
            criatura_j = self._criatura_jugada_jugador()
            if criatura_j is not None:
                criatura_j.buff_aguante += data["bonus_aguante"]
                criatura_j.aguante += data["bonus_aguante"]
                criatura_j.aguante_original += data["bonus_aguante"]
                self.mensaje_hechizo = f"zz +{data['bonus_aguante']} vida"
                resultado = True

        elif hid == "debilidad":
            criatura_e = self._criatura_jugada_enemiga()
            if criatura_e is not None:
                criatura_e.buff_poder += data["bonus_poder"]
                criatura_e.poder += data["bonus_poder"]
                if criatura_e.poder < 0:
                    criatura_e.poder = 0
                self.mensaje_hechizo = f"zz -{-data['bonus_poder']} poder al rival"
                resultado = True

        elif hid == "inmovilizar":
            criatura_e = self._criatura_jugada_enemiga()
            if criatura_e is not None:
                criatura_e.inmovilizada = True
                self.mensaje_hechizo = "zz Criatura rival inmovilizada"
                resultado = True

        if resultado:
            carta.morir()
            self.gastar_mana("jugador", costo)

        return resultado

    def hechizo_es_usable(self, idx_carta):
        if idx_carta >= len(self.mazo_jugador):
            return False
        carta = self.mazo_jugador[idx_carta]
        if getattr(carta, "tipo", "criatura") != "hechizo" or not carta.viva:
            return False
        data = HECHIZOS[carta.hechizo_id]
        if not self.puede_pagar("jugador", data["costo"]):
            return False
        target = data["target"]
        if target == "criatura_rival":
            if self._criatura_jugada_enemiga() is None:
                return False
        elif target == "criatura_propia":
            if self._criatura_jugada_jugador() is None:
                return False
        return True

    # ---------- Fase: duelo ----------
    def iniciar_duelo(self):
        if self.turno != Turno.JUGADOR_HECHIZOS:
            return False
        if self.carta_jugada_jugador is None or self.carta_jugada_enemigo is None:
            return False

        if (self.carta_jugada_jugador >= len(self.mazo_jugador.cartas)
                or self.carta_jugada_enemigo >= len(self.mazo_enemigo.cartas)):
            self.chequear_fin()
            return False

        carta_j = self.mazo_jugador[self.carta_jugada_jugador]
        carta_e = self.mazo_enemigo[self.carta_jugada_enemigo]

        if not carta_e.viva:
            self.mensaje = "zz La criatura rival ya fue derrotada"
            self.turno = Turno.RESULTADO
            self.chequear_fin()
            return True

        if not carta_j.viva:
            self.mensaje = "zz Tu criatura ya no esta en la mesa"
            self.turno = Turno.RESULTADO
            self.chequear_fin()
            return True

        self._ia_usar_hechizos()

        self.turno = Turno.DUELO
        self.resolver_batalla(carta_j, carta_e)
        self.turno = Turno.RESULTADO
        self.chequear_fin()
        return True

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

    # ---------- IA usa hechizos ----------
    def _ia_usar_hechizos(self):
        if hasattr(self.estrategia, "usar_hechizo"):
            self.estrategia.usar_hechizo(self)
        if self.mensaje_hechizo:
            self.mensaje_hechizo = ""

    # ---------- Helpers ----------
    def _criatura_jugada_jugador(self):
        if self.carta_jugada_jugador is None:
            return None
        if self.carta_jugada_jugador >= len(self.mazo_jugador.cartas):
            return None
        c = self.mazo_jugador[self.carta_jugada_jugador]
        if getattr(c, "tipo", "criatura") != "criatura":
            return None
        if not c.viva:
            return None
        return c

    def _criatura_jugada_enemiga(self):
        if self.carta_jugada_enemigo is None:
            return None
        if self.carta_jugada_enemigo >= len(self.mazo_enemigo.cartas):
            return None
        c = self.mazo_enemigo[self.carta_jugada_enemigo]
        if getattr(c, "tipo", "criatura") != "criatura":
            return None
        if not c.viva:
            return None
        return c

    def _robar_carta_rival(self, target_idx):
        vivas_e = [(i, c) for i, c in enumerate(self.mazo_enemigo.cartas) if c.viva]
        if not vivas_e:
            return
        if target_idx is None:
            target_idx = 0
        target_idx = max(0, min(target_idx, len(vivas_e) - 1))
        idx_real, carta = vivas_e[target_idx]
        self.mazo_enemigo.cartas.pop(idx_real)
        self.mazo_jugador.cartas.append(carta)

    # ---------- Avanzar ronda ----------
    def siguiente_ronda(self):
        if self.turno == Turno.FIN:
            return

        es_tutorial = getattr(self.dificultad, "es_tutorial", False)

        if es_tutorial and self.ronda >= TUTORIAL_ROUNDS:
            self.turno = Turno.FIN
            return

        self.ronda += 1
        self.carta_jugada_jugador = None
        self.carta_jugada_enemigo = None
        self.mensaje_hechizo = ""

        if es_tutorial:
            self._forzar_mazo_tutorial()
        else:
            self.mazo_jugador.rebarajar_si_hace_falta(self.hp_jugador)
            self.mazo_enemigo.rebarajar_si_hace_falta(self.hp_enemigo)

        self.sumar_mana()

        self.turno = Turno.IA_TIRA
        self.mensaje = "zz La IA elige su carta..."
        self.chequear_fin()

    # ---------- Fin de partida ----------
    def chequear_fin(self):
        if self.hp_jugador <= 0:
            self.turno = Turno.FIN
            self.mensaje = "zz PERDISTE"
            return True
        elif self.hp_enemigo <= 0:
            self.turno = Turno.FIN
            self.mensaje = "zz GANASTE"
            return True
        return False