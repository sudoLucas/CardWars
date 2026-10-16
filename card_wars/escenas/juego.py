# escenas/juego.py
import os
import random
import pygame
from config import (
    ANCHO, ALTO, Layout, Botones, Turno, ESCALA_PIXEL,
    DUELO_DURACION, get_dificultad, DIRECTORIO_RAIZ,
)
from escenas.base import Escena
from modelo.juego import Juego


# --- Carpeta de emotes ---
CARPETA_EMOTES = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "emotes")

# --- Imagen de la barra de HP ---
RUTA_HP = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "HP.png")

# --- Imagen de la mesa ---
RUTA_MESA = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "mesa.png")

# --- Carpeta de reversos de carta ---
CARPETA_REVERSOS = os.path.join(
    DIRECTORIO_RAIZ, "assets", "imagenes", "Objetos", "cartas"
)

# --- Definicion de personajes ---
# Cada personaje tiene 3 archivos: feliz (1), neutro (2), triste (3)
PERSONAJES = ["Finn", "Arcoiris", "BMO", "Jake"]


def rutas_personaje(nombre):
    """Devuelve (neutro, feliz, triste) para un personaje."""
    return {
        "neutro": os.path.join(CARPETA_EMOTES, f"{nombre}2.png"),
        "feliz":  os.path.join(CARPETA_EMOTES, f"{nombre}1.png"),
        "triste": os.path.join(CARPETA_EMOTES, f"{nombre}3.png"),
    }


# --- Duracion del emote de dano (ms) ---
EMOTE_DURACION = 2500


class EscenaJuego(Escena):
    def __init__(self, app, clave_dificultad=None):
        super().__init__(app)

        if clave_dificultad is not None:
            app.clave_dificultad = clave_dificultad
        self.dificultad = get_dificultad(app.clave_dificultad)

        self.juego = Juego(self.dificultad)
        self.tiempo_resolucion = 0

        e = ESCALA_PIXEL

        self.boton_reiniciar = pygame.Rect(
            Botones.REINICIAR_X * e,
            Botones.REINICIAR_Y * e,
            Botones.REINICIAR_W * e,
            Botones.REINICIAR_H * e,
        )
        self.boton_siguiente = pygame.Rect(
            Botones.SIGUIENTE_X * e,
            Botones.SIGUIENTE_Y * e,
            Botones.SIGUIENTE_W * e,
            Botones.SIGUIENTE_H * e,
        )

        self.rects_jugador = []
        self.rects_enemigo = []
        self.mouse = (0, 0)

        # --- Cargar barra de HP ---
        self.hp_img = self._cargar(RUTA_HP)

        # --- Cargar mesa ---
        self.mesa_img = self._cargar(RUTA_MESA)

        # --- Elegir personajes al azar ---
        self._elegir_personajes()

        # --- Cargar emotes segun los personajes elegidos ---
        self._cargar_emotes()

        # --- Elegir 3 reversos random (no repetidos) ---
        self._elegir_reversos()

        # Estado actual: "neutro", "feliz" o "triste"
        self.emote_rival_actual = "neutro"
        self.emote_jugador_actual = "neutro"
        self.tiempo_emote = 0

        # Quien recibio dano: "jugador", "rival", "empate" o None
        self.quien_recibio_dano = None

        # Para detectar cambios de HP
        self.hp_jugador_anterior = self.juego.hp_jugador
        self.hp_enemigo_anterior = self.juego.hp_enemigo
        self.mensaje_anterior = self.juego.mensaje

    def _elegir_personajes(self):
        """Elige un personaje random para el jugador y otro distinto para el rival."""
        self.personaje_jugador = random.choice(PERSONAJES)
        opciones_rival = [p for p in PERSONAJES if p != self.personaje_jugador]
        self.personaje_rival = random.choice(opciones_rival)

    def _cargar_emotes(self):
        """Carga los emotes de ambos personajes."""
        rutas_j = rutas_personaje(self.personaje_jugador)
        rutas_r = rutas_personaje(self.personaje_rival)

        self.emote_jug_neutro = self._cargar(rutas_j["neutro"])
        self.emote_jug_feliz  = self._cargar(rutas_j["feliz"])
        self.emote_jug_triste = self._cargar(rutas_j["triste"])

        self.emote_rival_neutro = self._cargar(rutas_r["neutro"])
        self.emote_rival_feliz  = self._cargar(rutas_r["feliz"])
        self.emote_rival_triste = self._cargar(rutas_r["triste"])

    def _elegir_reversos(self):
        """Elige 3 reversos random distintos entre los 6 disponibles."""
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

        # Nuevos personajes random
        self._elegir_personajes()
        self._cargar_emotes()

        # Nuevos reversos random
        self._elegir_reversos()

        self.hp_jugador_anterior = self.juego.hp_jugador
        self.hp_enemigo_anterior = self.juego.hp_enemigo
        self.emote_rival_actual = "neutro"
        self.emote_jugador_actual = "neutro"
        self.tiempo_emote = 0
        self.quien_recibio_dano = None
        self.mensaje_anterior = self.juego.mensaje

    def _ancho_mundo(self):
        return ANCHO // ESCALA_PIXEL

    def calcular_rects(self):
        e = ESCALA_PIXEL
        ancho_m = self._ancho_mundo()

        vivas_j = [(i, c) for i, c in enumerate(self.juego.mazo_jugador.cartas) if c.viva]
        cantidad_j = len(vivas_j)
        self.rects_jugador = []

        if cantidad_j > 0:
            x_inicio_m = Layout.x_inicio_cartas(cantidad_j, ancho_m)
            for pos, (idx_real, _) in enumerate(vivas_j):
                x_m = x_inicio_m + pos * (Layout.CARTA_W + Layout.ESPACIO_CARTAS)
                rect = pygame.Rect(
                    x_m * e, Layout.Y_TOP_MANO * e,
                    Layout.CARTA_W * e, Layout.CARTA_H * e,
                )
                self.rects_jugador.append((idx_real, rect))

        vivas_e = [(i, c) for i, c in enumerate(self.juego.mazo_enemigo.cartas) if c.viva]
        self.rects_enemigo = [(idx_real, pygame.Rect(0, 0, 0, 0))
                              for idx_real, _ in vivas_e]

    def _actualizar_emotes(self):
        """Detecta cambios de HP o empates y actualiza los emotes."""
        self.quien_recibio_dano = None

        mensaje_actual = self.juego.mensaje
        hubo_empate = (
            "Empate" in mensaje_actual
            and mensaje_actual != self.mensaje_anterior
        )

        # Dano al jugador
        if self.juego.hp_jugador < self.hp_jugador_anterior:
            self.emote_jugador_actual = "triste"
            self.emote_rival_actual = "feliz"
            self.tiempo_emote = pygame.time.get_ticks()
            self.quien_recibio_dano = "jugador"

        # Dano al rival
        elif self.juego.hp_enemigo < self.hp_enemigo_anterior:
            self.emote_rival_actual = "triste"
            self.emote_jugador_actual = "feliz"
            self.tiempo_emote = pygame.time.get_ticks()
            self.quien_recibio_dano = "rival"

        # Empate
        elif hubo_empate:
            self.emote_jugador_actual = "triste"
            self.emote_rival_actual = "triste"
            self.tiempo_emote = pygame.time.get_ticks()
            self.quien_recibio_dano = "empate"

        # Volver a neutro
        if self.tiempo_emote > 0:
            if pygame.time.get_ticks() - self.tiempo_emote > EMOTE_DURACION:
                self.emote_rival_actual = "neutro"
                self.emote_jugador_actual = "neutro"
                self.tiempo_emote = 0
                self.quien_recibio_dano = None

        self.hp_jugador_anterior = self.juego.hp_jugador
        self.hp_enemigo_anterior = self.juego.hp_enemigo
        self.mensaje_anterior = mensaje_actual

    def handle_event(self, evento, mouse):
        self.mouse = mouse

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                from escenas.menu import EscenaMenu
                self.app.cambiar_escena(EscenaMenu(self.app))
                return
            if evento.key == pygame.K_r:
                self.nueva_partida()
            if evento.key == pygame.K_SPACE and self.juego.turno == Turno.RESOLVIENDO:
                self.juego.siguiente_ronda()
                self.tiempo_resolucion = 0

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.boton_reiniciar.collidepoint(mouse):
                self.nueva_partida()
                return

            if self.juego.turno == Turno.JUGADOR:
                for idx, rect in self.rects_jugador:
                    if rect.collidepoint(mouse):
                        self.juego.jugador_tira_carta(idx)
                        self.tiempo_resolucion = pygame.time.get_ticks()
                        break

            elif self.juego.turno == Turno.RESOLVIENDO:
                if self.boton_siguiente.collidepoint(mouse):
                    self.juego.siguiente_ronda()
                    self.tiempo_resolucion = 0

    def update(self, dt):
        self.render.tick(dt)
        self.calcular_rects()
        self._actualizar_emotes()

        if self.juego.turno == Turno.RESOLVIENDO:
            if pygame.time.get_ticks() - self.tiempo_resolucion > DUELO_DURACION:
                self.juego.siguiente_ronda()
                self.tiempo_resolucion = 0

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