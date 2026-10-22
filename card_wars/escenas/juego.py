# escenas/juego.py
import os
import random
import math
import pygame
from config import (
    ANCHO, ALTO, Layout, Botones, Turno, ESCALA_PIXEL,
    DUELO_DURACION, get_dificultad, DIRECTORIO_RAIZ, HECHIZOS,
)
from escenas.base import Escena
from modelo.juego import Juego


CARPETA_EMOTES = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "emotes")
RUTA_HP = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "HP.png")
RUTA_MESA = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "mesa.png")
CARPETA_REVERSOS = os.path.join(
    DIRECTORIO_RAIZ, "assets", "imagenes", "Objetos", "cartas"
)

PERSONAJES = ["Finn", "Arcoiris", "BMO", "Jake"]


def rutas_personaje(nombre):
    return {
        "neutro": os.path.join(CARPETA_EMOTES, f"{nombre}2.png"),
        "feliz":  os.path.join(CARPETA_EMOTES, f"{nombre}1.png"),
        "triste": os.path.join(CARPETA_EMOTES, f"{nombre}3.png"),
    }


EMOTE_DURACION = 2500
DELAY_IA_TIRA = 800
DELAY_RESULTADO = 2000


class EscenaJuego(Escena):
    def __init__(self, app, clave_dificultad=None):
        super().__init__(app)

        if clave_dificultad is not None:
            app.clave_dificultad = clave_dificultad
        self.dificultad = get_dificultad(app.clave_dificultad)

        self.juego = Juego(self.dificultad)
        self.tiempo_resolucion = 0
        self.tiempo_fase = pygame.time.get_ticks()

        e = ESCALA_PIXEL

        self.boton_reiniciar = pygame.Rect(
            Botones.REINICIAR_X * e, Botones.REINICIAR_Y * e,
            Botones.REINICIAR_W * e, Botones.REINICIAR_H * e,
        )
        self.boton_siguiente = pygame.Rect(
            Botones.SIGUIENTE_X * e, Botones.SIGUIENTE_Y * e,
            Botones.SIGUIENTE_W * e, Botones.SIGUIENTE_H * e,
        )

        self.rects_jugador = []
        self.posiciones_jugador = []
        self.escalas_jugador = []
        self.rects_enemigo = []
        self.mouse = (0, 0)
        self.foco_teclado = 0
        self.foco_zona = "mano"
        self.foco_objetivo = 0

        self.hp_img = self._cargar(RUTA_HP)
        self.mesa_img = self._cargar(RUTA_MESA)

        self._elegir_personajes()
        self._cargar_emotes()
        self._elegir_reversos()

        self.emote_rival_actual = "neutro"
        self.emote_jugador_actual = "neutro"
        self.tiempo_emote = 0
        self.quien_recibio_dano = None

        self.hp_jugador_anterior = self.juego.hp_jugador
        self.hp_enemigo_anterior = self.juego.hp_enemigo
        self.mensaje_anterior = self.juego.mensaje

        self.hechizo_seleccionado = None
        self.animacion_target_inicio = None
        self.mensaje_hechizo_temporal = ""
        self.tiempo_mensaje_hechizo = 0

        self.rects_cartas_rival_clickeables = []
        self.slots_rival_objetivo = []

    def _elegir_personajes(self):
        self.personaje_jugador = random.choice(PERSONAJES)
        opciones_rival = [p for p in PERSONAJES if p != self.personaje_jugador]
        self.personaje_rival = random.choice(opciones_rival)

    def _cargar_emotes(self):
        rutas_j = rutas_personaje(self.personaje_jugador)
        rutas_r = rutas_personaje(self.personaje_rival)

        self.emote_jug_neutro = self._cargar(rutas_j["neutro"])
        self.emote_jug_feliz  = self._cargar(rutas_j["feliz"])
        self.emote_jug_triste = self._cargar(rutas_j["triste"])

        self.emote_rival_neutro = self._cargar(rutas_r["neutro"])
        self.emote_rival_feliz  = self._cargar(rutas_r["feliz"])
        self.emote_rival_triste = self._cargar(rutas_r["triste"])

    def _elegir_reversos(self):
        numeros = random.sample(range(1, 7), 3)
        self.reversos_img = []
        for n in numeros:
            ruta = os.path.join(CARPETA_REVERSOS, f"reversoCarta{n}.png")
            img = self._cargar(ruta)
            if img is not None:
                self.reversos_img.append(img)

    def _cargar(self, ruta):
        if os.path.isfile(ruta):
            try:
                return pygame.image.load(ruta).convert_alpha()
            except Exception as e:
                print(f"[juego] No se pudo cargar {ruta}: {e}")
        else:
            print(f"[juego] Imagen NO ENCONTRADA: {ruta}")
        return None

    def nueva_partida(self):
        self.juego = Juego(self.dificultad)
        self.tiempo_resolucion = 0
        self.tiempo_fase = pygame.time.get_ticks()

        self._elegir_personajes()
        self._cargar_emotes()
        self._elegir_reversos()

        self.hp_jugador_anterior = self.juego.hp_jugador
        self.hp_enemigo_anterior = self.juego.hp_enemigo
        self.emote_rival_actual = "neutro"
        self.emote_jugador_actual = "neutro"
        self.tiempo_emote = 0
        self.quien_recibio_dano = None
        self.mensaje_anterior = self.juego.mensaje

        self.hechizo_seleccionado = None
        self.animacion_target_inicio = None
        self.mensaje_hechizo_temporal = ""
        self.tiempo_mensaje_hechizo = 0
        self.foco_teclado = 0
        self.foco_zona = "mano"
        self.foco_objetivo = 0

    def _ancho_mundo(self):
        return ANCHO // ESCALA_PIXEL

    def _alto_mundo(self):
        return ALTO // ESCALA_PIXEL

    def _calcular_posiciones_abanico(self, cartas, reservar_hueco=False):
        ancho_m = self._ancho_mundo()
        alto_m = self._alto_mundo()
        return Layout.distribucion_mano(
            cartas, ancho_m, alto_m, reservar_hueco,
        )

    def _factor_espaciado_rival(self):
        if self.hechizo_seleccionado is None or self.animacion_target_inicio is None:
            return 1
        carta = self.juego.mazo_jugador[self.hechizo_seleccionado]
        if HECHIZOS.get(carta.hechizo_id, {}).get("target") != "carta_rival":
            return 1
        elapsed = pygame.time.get_ticks() - self.animacion_target_inicio
        return Layout.factor_animacion_objetivo(elapsed)

    def _calcular_posiciones_rival(self, cantidad):
        ancho_m = self._ancho_mundo()
        e = ESCALA_PIXEL
        resultado = []
        posiciones = Layout.posiciones_rival(
            cantidad, ancho_m, self._factor_espaciado_rival(),
        )
        for i, (cx_m, cy_m) in enumerate(posiciones):
            cx = cx_m * e
            cy = cy_m * e
            rect = pygame.Rect(cx - 60, cy - 60, 120, 120)
            resultado.append((i, rect))
        return resultado

    def calcular_rects(self):
        e = ESCALA_PIXEL

        vivas_j = [
            (i, carta)
            for i, carta in enumerate(self.juego.mazo_jugador.cartas)
            if carta.viva and i != self.juego.carta_jugada_jugador
        ]
        self.posiciones_jugador, self.escalas_jugador = (
            self._calcular_posiciones_abanico(
                [carta for _, carta in vivas_j],
                reservar_hueco=self.juego.carta_jugada_jugador is not None,
            )
        )
        self.rects_jugador = []

        for pos, (idx_real, carta) in enumerate(vivas_j):
            if pos >= len(self.posiciones_jugador):
                break
            cx, cy, _ = self.posiciones_jugador[pos]
            cx_px = cx * e
            cy_px = cy * e
            escala = self.escalas_jugador[pos]
            w = int(Layout.CARTA_W * escala * e)
            h = int(Layout.CARTA_H * escala * e)
            rect = pygame.Rect(
                cx_px - w // 2,
                cy_px - h // 2,
                w,
                h,
            )
            self.rects_jugador.append((idx_real, rect))

        vivas_e = [
            (i, carta)
            for i, carta in enumerate(self.juego.mazo_enemigo.cartas)
            if carta.viva
        ]
        self.rects_enemigo = [(idx_real, pygame.Rect(0, 0, 0, 0))
                              for idx_real, _ in vivas_e]
        posiciones_rival = self._calcular_posiciones_rival(len(vivas_e))
        indices_objetivo = {
            indice: objetivo
            for objetivo, (indice, _) in enumerate(
                self.juego._cartas_rivales_objetivo()
            )
        }
        self.rects_cartas_rival_clickeables = [
            (indices_objetivo[indice_real], rect)
            for (indice_real, _), (_, rect) in zip(vivas_e, posiciones_rival)
            if indice_real in indices_objetivo
        ]
        self.slots_rival_objetivo = [
            visual
            for visual, (indice_real, _) in enumerate(vivas_e)
            if indice_real in indices_objetivo
        ]

        if len(self.rects_jugador) > 0:
            if self.foco_teclado >= len(self.rects_jugador):
                self.foco_teclado = len(self.rects_jugador) - 1
        else:
            self.foco_teclado = 0
            if self.foco_zona == "mano":
                self.foco_zona = "mesa" if self.juego.carta_jugada_jugador is not None else "mano"

        if self.rects_cartas_rival_clickeables:
            indices = [idx for idx, _ in self.rects_cartas_rival_clickeables]
            if self.foco_objetivo not in indices:
                self.foco_objetivo = indices[0]
        else:
            self.foco_objetivo = 0
            if self.foco_zona == "objetivo":
                self.foco_zona = "mano"

    def _actualizar_emotes(self):
        self.quien_recibio_dano = None

        mensaje_actual = self.juego.mensaje
        hubo_empate = (
            "Empate" in mensaje_actual
            and mensaje_actual != self.mensaje_anterior
        )

        if self.juego.hp_jugador < self.hp_jugador_anterior:
            self.emote_jugador_actual = "triste"
            self.emote_rival_actual = "feliz"
            self.tiempo_emote = pygame.time.get_ticks()
            self.quien_recibio_dano = "jugador"

        elif self.juego.hp_enemigo < self.hp_enemigo_anterior:
            self.emote_rival_actual = "triste"
            self.emote_jugador_actual = "feliz"
            self.tiempo_emote = pygame.time.get_ticks()
            self.quien_recibio_dano = "rival"

        elif hubo_empate:
            self.emote_jugador_actual = "triste"
            self.emote_rival_actual = "triste"
            self.tiempo_emote = pygame.time.get_ticks()
            self.quien_recibio_dano = "empate"

        if self.tiempo_emote > 0:
            if pygame.time.get_ticks() - self.tiempo_emote > EMOTE_DURACION:
                self.emote_rival_actual = "neutro"
                self.emote_jugador_actual = "neutro"
                self.tiempo_emote = 0
                self.quien_recibio_dano = None

        self.hp_jugador_anterior = self.juego.hp_jugador
        self.hp_enemigo_anterior = self.juego.hp_enemigo
        self.mensaje_anterior = mensaje_actual

    def _rect_criatura_jugador_mesa(self):
        if self.juego.carta_jugada_jugador is None:
            return None
        ancho_m = self._ancho_mundo()
        e = ESCALA_PIXEL
        cx_duelo = ancho_m // 2
        cy_duelo = Layout.Y_CENTRO_DUELO

        x_m = cx_duelo - Layout.CARTA_W // 2
        y_m = cy_duelo + Layout.DUELO_SEP_Y
        return pygame.Rect(
            x_m * e, y_m * e,
            Layout.CARTA_W * e, Layout.CARTA_H * e,
        )

    def _mostrar_mensaje_hechizo(self, texto):
        self.mensaje_hechizo_temporal = texto
        self.tiempo_mensaje_hechizo = pygame.time.get_ticks()

    def _aplicar_hechizo_con_target(self, idx_hechizo, target_idx):
        self.juego.usar_hechizo(idx_hechizo, target_idx=target_idx)
        if self.juego.mensaje_hechizo:
            self._mostrar_mensaje_hechizo(self.juego.mensaje_hechizo)
        self.hechizo_seleccionado = None
        self.animacion_target_inicio = None
        self.foco_zona = "mano"
        self.calcular_rects()

    def _seleccionar_hechizo_target(self, idx_hechizo):
        self.hechizo_seleccionado = idx_hechizo
        self.animacion_target_inicio = pygame.time.get_ticks()
        self.foco_zona = "objetivo"
        if self.rects_cartas_rival_clickeables:
            self.foco_objetivo = self.rects_cartas_rival_clickeables[0][0]

    def _aplicar_hechizo_directo(self, idx_hechizo):
        self.juego.usar_hechizo(idx_hechizo, target_idx=None)
        if self.juego.mensaje_hechizo:
            self._mostrar_mensaje_hechizo(self.juego.mensaje_hechizo)
        self.hechizo_seleccionado = None
        self.animacion_target_inicio = None
        self.foco_zona = "mano"
        self.calcular_rects()

    def _mensaje_hechizo_visible(self):
        if not self.mensaje_hechizo_temporal:
            return None
        if pygame.time.get_ticks() - self.tiempo_mensaje_hechizo > 2000:
            self.mensaje_hechizo_temporal = ""
            return None
        return self.mensaje_hechizo_temporal

    def _mover_foco_objetivo(self, dx, dy):
        if not self.rects_cartas_rival_clickeables:
            return
        actuales = dict(self.rects_cartas_rival_clickeables)
        actual = actuales.get(self.foco_objetivo)
        if actual is None:
            self.foco_objetivo = self.rects_cartas_rival_clickeables[0][0]
            return

        cx, cy = actual.center
        candidatos = []
        for indice, rect in self.rects_cartas_rival_clickeables:
            if indice == self.foco_objetivo:
                continue
            vx, vy = rect.centerx - cx, rect.centery - cy
            avance = vx * dx + vy * dy
            if avance > 0:
                lateral = abs(vx * dy - vy * dx)
                candidatos.append((lateral + avance * 0.2, indice))

        if candidatos:
            self.foco_objetivo = min(candidatos)[1]
        else:
            extremos = [
                ((rect.centerx - cx) * dx + (rect.centery - cy) * dy, indice)
                for indice, rect in self.rects_cartas_rival_clickeables
            ]
            self.foco_objetivo = min(extremos)[1]

    def _mover_foco_teclado(self, direccion):
        dx, dy = direccion
        if self.foco_zona == "objetivo":
            self._mover_foco_objetivo(dx, dy)
            return

        if self.foco_zona == "mesa":
            if dy > 0 and self.rects_jugador:
                self.foco_zona = "mano"
            return

        if dx:
            if self.rects_jugador:
                self.foco_teclado = (
                    self.foco_teclado + (1 if dx > 0 else -1)
                ) % len(self.rects_jugador)
        elif dy and self.juego.turno == Turno.JUGADOR_HECHIZOS:
            if dy < 0 and self.juego.carta_jugada_jugador is not None:
                self.foco_zona = "mesa"

    def _confirmar_foco_teclado(self):
        if self.juego.turno == Turno.RESULTADO:
            self.juego.siguiente_ronda()
            self.tiempo_fase = pygame.time.get_ticks()
            self.foco_zona = "mano"
            self.calcular_rects()
            return

        if self.foco_zona == "objetivo":
            if self.hechizo_seleccionado is not None:
                self._aplicar_hechizo_con_target(
                    self.hechizo_seleccionado, self.foco_objetivo,
                )
            return

        if self.foco_zona == "mesa":
            if self.juego.turno == Turno.JUGADOR_HECHIZOS:
                self.juego.iniciar_duelo()
                self.tiempo_fase = pygame.time.get_ticks()
                self.foco_zona = "mano"
            return

        if not self.rects_jugador:
            return
        idx, _ = self.rects_jugador[self.foco_teclado]
        carta = self.juego.mazo_jugador[idx]

        if self.juego.turno == Turno.JUGADOR_TIRA:
            if getattr(carta, "tipo", "criatura") == "criatura":
                self.juego.jugador_tira_carta(idx)
                self.tiempo_fase = pygame.time.get_ticks()
                self.foco_zona = "mesa"
                self.calcular_rects()
            return

        if self.juego.turno != Turno.JUGADOR_HECHIZOS:
            return
        if getattr(carta, "tipo", "criatura") != "hechizo":
            return
        if not self.juego.hechizo_es_usable(idx):
            self.juego.usar_hechizo(idx, target_idx=None)
            return

        data = HECHIZOS.get(carta.hechizo_id, {})
        if data.get("target") == "carta_rival":
            self._seleccionar_hechizo_target(idx)
        else:
            self._aplicar_hechizo_directo(idx)

    def _cancelar_foco_teclado(self):
        if self.hechizo_seleccionado is not None:
            self.hechizo_seleccionado = None
            self.animacion_target_inicio = None
            self.foco_zona = "mano"
            return True
        if self.foco_zona == "mesa":
            self.foco_zona = "mano"
            return True
        return False

    def handle_event(self, evento, mouse):
        self.mouse = mouse

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if self._cancelar_foco_teclado():
                    return
                from escenas.menu import EscenaMenu
                self.app.cambiar_escena(EscenaMenu(self.app))
                return
            if evento.key == pygame.K_r:
                self.nueva_partida()
                return

            if evento.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                self._cancelar_foco_teclado()
                return

            if evento.key in (pygame.K_a, pygame.K_LEFT):
                self._mover_foco_teclado((-1, 0))
                return
            if evento.key in (pygame.K_d, pygame.K_RIGHT):
                self._mover_foco_teclado((1, 0))
                return
            if evento.key in (pygame.K_w, pygame.K_UP):
                self._mover_foco_teclado((0, -1))
                return
            if evento.key in (pygame.K_s, pygame.K_DOWN):
                self._mover_foco_teclado((0, 1))
                return

            if evento.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_z):
                self._confirmar_foco_teclado()
                return

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 3:
                self._cancelar_foco_teclado()
                return

            if evento.button != 1:
                return

            if self.boton_reiniciar.collidepoint(mouse):
                self.nueva_partida()
                return

            if self.juego.turno == Turno.RESULTADO:
                if self.boton_siguiente.collidepoint(mouse):
                    self.juego.siguiente_ronda()
                    self.tiempo_fase = pygame.time.get_ticks()
                    return

            if self.juego.turno == Turno.JUGADOR_TIRA:
                for idx, rect in self._cartas_mano_en_orden_de_clic():
                    if rect.collidepoint(mouse):
                        carta = self.juego.mazo_jugador[idx]
                        self.foco_teclado = next(
                            (pos for pos, (real, _) in enumerate(self.rects_jugador)
                             if real == idx),
                            self.foco_teclado,
                        )
                        self.foco_zona = "mano"
                        if getattr(carta, "tipo", "criatura") == "criatura":
                            self.juego.jugador_tira_carta(idx)
                            self.tiempo_fase = pygame.time.get_ticks()
                            self.foco_zona = "mesa"
                            self.calcular_rects()
                        break

            elif self.juego.turno == Turno.JUGADOR_HECHIZOS:
                if self.hechizo_seleccionado is not None:
                    carta = self.juego.mazo_jugador[self.hechizo_seleccionado]
                    data = HECHIZOS.get(carta.hechizo_id, {})
                    target = data.get("target", "")

                    if target == "carta_rival":
                        for idx_slot, rect_rival in self.rects_cartas_rival_clickeables:
                            if rect_rival.collidepoint(mouse):
                                self._aplicar_hechizo_con_target(
                                    self.hechizo_seleccionado, idx_slot
                                )
                                return
                        self.hechizo_seleccionado = None
                        self.animacion_target_inicio = None
                        self.foco_zona = "mano"
                        return
                    else:
                        self._aplicar_hechizo_directo(self.hechizo_seleccionado)
                        return

                rect_mesa = self._rect_criatura_jugador_mesa()
                if rect_mesa is not None and rect_mesa.collidepoint(mouse):
                    self.juego.iniciar_duelo()
                    self.tiempo_fase = pygame.time.get_ticks()
                    self.foco_zona = "mano"
                    return

                for idx, rect in self._cartas_mano_en_orden_de_clic():
                    if rect.collidepoint(mouse):
                        carta = self.juego.mazo_jugador[idx]
                        self.foco_teclado = next(
                            (pos for pos, (real, _) in enumerate(self.rects_jugador)
                             if real == idx),
                            self.foco_teclado,
                        )
                        self.foco_zona = "mano"
                        if getattr(carta, "tipo", "criatura") == "hechizo":
                            data = HECHIZOS.get(carta.hechizo_id, {})
                            target = data.get("target", "")
                            if target == "carta_rival":
                                self._seleccionar_hechizo_target(idx)
                            else:
                                self._aplicar_hechizo_directo(idx)
                        break

    def _cartas_mano_en_orden_de_clic(self):
        return list(reversed(self.rects_jugador))

    def update(self, dt):
        self.render.tick(dt)
        self.calcular_rects()
        self._actualizar_emotes()

        ahora = pygame.time.get_ticks()

        if self.juego.turno == Turno.IA_TIRA:
            if ahora - self.tiempo_fase > DELAY_IA_TIRA:
                self.juego.ia_tira_carta()
                self.tiempo_fase = ahora

        if self.juego.turno == Turno.FIN:
            from escenas.fin import EscenaFin
            self.app.cambiar_escena(EscenaFin(self.app, self.juego))

    def draw(self):
        self.render.dibujar_escena(
            self.juego, self.rects_jugador, self.rects_enemigo, self.mouse,
            self.boton_reiniciar, self.boton_siguiente,
            emote_rival=self._emote_rival(),
            emote_jugador=self._emote_jugador(),
            emote_activo=self.tiempo_emote > 0,
            quien_recibio_dano=self.quien_recibio_dano,
            hp_img=self.hp_img,
            mesa_img=self.mesa_img,
            reversos_img=self.reversos_img,
            posiciones_jugador=self.posiciones_jugador,
            escalas_jugador=self.escalas_jugador,
            foco_mano=self.foco_teclado if self.foco_zona == "mano" else None,
            foco_objetivo=self.foco_objetivo if self.foco_zona == "objetivo" else None,
            slots_rival_objetivo=self.slots_rival_objetivo,
            hechizo_seleccionado=self.hechizo_seleccionado,
            rects_cartas_rival_clickeables=self.rects_cartas_rival_clickeables,
            mensaje_hechizo=self._mensaje_hechizo_visible(),
            carta_vision_idx=self.juego.carta_vision_idx,
            vision_activa_hasta=self.juego.vision_activa_hasta,
            foco_teclado=self.foco_teclado,
            factor_espaciado_rival=self._factor_espaciado_rival(),
        )

    def _emote_rival(self):
        if self.emote_rival_actual == "feliz":
            return self.emote_rival_feliz
        elif self.emote_rival_actual == "triste":
            return self.emote_rival_triste
        return self.emote_rival_neutro

    def _emote_jugador(self):
        if self.emote_jugador_actual == "feliz":
            return self.emote_jug_feliz
        elif self.emote_jugador_actual == "triste":
            return self.emote_jug_triste
        return self.emote_jug_neutro