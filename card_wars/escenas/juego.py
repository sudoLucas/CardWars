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
        self.rects_enemigo = []
        self.mouse = (0, 0)

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
        self.mensaje_hechizo_temporal = ""
        self.tiempo_mensaje_hechizo = 0

        self.rects_cartas_rival_clickeables = []

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
        self.mensaje_hechizo_temporal = ""
        self.tiempo_mensaje_hechizo = 0

    def _ancho_mundo(self):
        return ANCHO // ESCALA_PIXEL

    def _alto_mundo(self):
        return ALTO // ESCALA_PIXEL

    def _calcular_posiciones_abanico(self, cantidad):
        ancho_m = self._ancho_mundo()
        alto_m = self._alto_mundo()

        cx_centro = ancho_m // 2
        
        # Margen inferior en unidades del mundo (ej: 2 = 8px reales)
        MARGEN_INFERIOR = 2
        
        # La Y del centro de la carta para que el borde inferior toque el margen
        cy_centro = alto_m - MARGEN_INFERIOR - (Layout.CARTA_H // 2)

        if cantidad <= 0:
            return []

        if cantidad > 1:
            medio = (cantidad - 1) / 2.0
        else:
            medio = 0

        posiciones = []
        for i in range(cantidad):
            dx = (i - medio) * Layout.ABANICO_SEP_X_JUGADOR
            cx = cx_centro + dx
            cy = cy_centro
            posiciones.append((cx, cy, 0))

        return posiciones

    def _calcular_posiciones_rival(self, cantidad):
        ancho_m = self._ancho_mundo()
        e = ESCALA_PIXEL
        cx_centro = ancho_m // 2
        cy_centro = Layout.Y_CENTRO_RIVAL

        if cantidad <= 0:
            return []

        if cantidad > 1:
            medio = (cantidad - 1) / 2.0
        else:
            medio = 0

        resultado = []
        w = Layout.CARTA_W * e
        h = Layout.CARTA_H * e

        for i in range(cantidad):
            dist_al_centro = abs(i - medio)
            dx = (i - medio) * Layout.ABANICO_SEP_X
            dy = dist_al_centro * Layout.ABANICO_OFFSET_Y

            cx = (cx_centro + int(dx)) * e
            cy = (cy_centro + int(dy)) * e

            rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
            resultado.append((i, rect))
        return resultado

    def calcular_rects(self):
        e = ESCALA_PIXEL

        vivas_j = [(i, c) for i, c in enumerate(self.juego.mazo_jugador.cartas) if c.viva]
        cantidad_j = len(vivas_j)

        self.posiciones_jugador = self._calcular_posiciones_abanico(cantidad_j)
        self.rects_jugador = []

        for pos, (idx_real, _) in enumerate(vivas_j):
            if pos >= len(self.posiciones_jugador):
                break
            cx, cy, _ = self.posiciones_jugador[pos]
            cx_px = cx * e
            cy_px = cy * e
            w = Layout.CARTA_W * e
            h = Layout.CARTA_H * e
            rect = pygame.Rect(cx_px - w // 2, cy_px - h // 2, w, h)
            self.rects_jugador.append((idx_real, rect))

        vivas_e = [(i, c) for i, c in enumerate(self.juego.mazo_enemigo.cartas) if c.viva]
        self.rects_enemigo = [(idx_real, pygame.Rect(0, 0, 0, 0))
                              for idx_real, _ in vivas_e]
        self.rects_cartas_rival_clickeables = self._calcular_posiciones_rival(len(vivas_e))

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
        exito = self.juego.usar_hechizo(idx_hechizo, target_idx=target_idx)
        if self.juego.mensaje_hechizo:
            self._mostrar_mensaje_hechizo(self.juego.mensaje_hechizo)
        self.hechizo_seleccionado = None

    def _aplicar_hechizo_directo(self, idx_hechizo):
        exito = self.juego.usar_hechizo(idx_hechizo, target_idx=None)
        if self.juego.mensaje_hechizo:
            self._mostrar_mensaje_hechizo(self.juego.mensaje_hechizo)
        self.hechizo_seleccionado = None

    def _mensaje_hechizo_visible(self):
        if not self.mensaje_hechizo_temporal:
            return None
        if pygame.time.get_ticks() - self.tiempo_mensaje_hechizo > 2000:
            self.mensaje_hechizo_temporal = ""
            return None
        return self.mensaje_hechizo_temporal

    def handle_event(self, evento, mouse):
        self.mouse = mouse

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                from escenas.menu import EscenaMenu
                self.app.cambiar_escena(EscenaMenu(self.app))
                return
            if evento.key == pygame.K_r:
                self.nueva_partida()

            if evento.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.hechizo_seleccionado = None
                return

            if evento.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_z):
                if self.juego.turno == Turno.RESULTADO:
                    self.juego.siguiente_ronda()
                    self.tiempo_fase = pygame.time.get_ticks()
                    return

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 3:
                self.hechizo_seleccionado = None
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
                for idx, rect in self.rects_jugador:
                    if rect.collidepoint(mouse):
                        carta = self.juego.mazo_jugador[idx]
                        if getattr(carta, "tipo", "criatura") == "criatura":
                            self.juego.jugador_tira_carta(idx)
                            self.tiempo_fase = pygame.time.get_ticks()
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
                        return
                    else:
                        self._aplicar_hechizo_directo(self.hechizo_seleccionado)
                        return

                rect_mesa = self._rect_criatura_jugador_mesa()
                if rect_mesa is not None and rect_mesa.collidepoint(mouse):
                    self.juego.iniciar_duelo()
                    self.tiempo_fase = pygame.time.get_ticks()
                    return

                for idx, rect in self.rects_jugador:
                    if rect.collidepoint(mouse):
                        carta = self.juego.mazo_jugador[idx]
                        if getattr(carta, "tipo", "criatura") == "hechizo":
                            data = HECHIZOS.get(carta.hechizo_id, {})
                            target = data.get("target", "")
                            if target == "carta_rival":
                                self.hechizo_seleccionado = idx
                            else:
                                self._aplicar_hechizo_directo(idx)
                        break

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
            hechizo_seleccionado=self.hechizo_seleccionado,
            rects_cartas_rival_clickeables=self.rects_cartas_rival_clickeables,
            mensaje_hechizo=self._mensaje_hechizo_visible(),
            carta_vision_idx=self.juego.carta_vision_idx,
            vision_activa_hasta=self.juego.vision_activa_hasta,
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