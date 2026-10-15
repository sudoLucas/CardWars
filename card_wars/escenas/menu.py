# escenas/menu.py
import os
import sys
import math
import pygame
from config import ANCHO, ALTO, TITULO, VERSION, Botones, DIRECTORIO_RAIZ
from escenas.base import Escena
from escenas.dificultad import EscenaDificultad
from vista.colores import (
    NEGRO, BLANCO, AMARILLO, GRIS,
    COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF,
    COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF,
)


# Rutas de las 3 capas (frente, medio, fondo)
RUTA_COLINA_FRENTE = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "colina1.png")
RUTA_COLINA_MEDIO  = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "colina2.png")
RUTA_COLINA_FONDO  = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "colina3.png")


# ---- Parametros de movimiento por capa ----
# Zoom: cuanto mas grande que la pantalla (mas = mas margen de paneo)
# Velocidad: que tan rapido se mueve (mas alto = mas rapido)
# Amplitud: cuanto se desplaza (fraccion del margen disponible)

# FONDO (mas lejano) -> se mueve lento
FONDO_ZOOM       = 1.10
FONDO_VELOCIDAD  = 0.0004

# MEDIO -> velocidad media (mas sutil)
MEDIO_ZOOM       = 1.25
MEDIO_VELOCIDAD  = 0.0004

# FRENTE (mas cercano) -> mas zoom (mas sutil)
FRENTE_ZOOM      = 1.20
FRENTE_VELOCIDAD = 0.0007
FRENTE_OFFSET_Y = 80


class EscenaMenu(Escena):
    def __init__(self, app):
        super().__init__(app)

        ancho_m = ANCHO // 4
        alto_m = ALTO // 4

        w = Botones.MENU_W
        h = Botones.MENU_H
        sep = Botones.MENU_ESPACIO_Y
        margen_x = Botones.MENU_X_MARGEN
        margen_y = Botones.MENU_Y_MARGEN

        claves = ["jugar", "dificultad", "salir"]
        textos = ["JUGAR", "DIFICULTAD", "SALIR"]
        n = len(claves)

        y_ultimo = alto_m - margen_y - h

        self.botones = []
        for i in range(n):
            y_m = y_ultimo - (n - 1 - i) * (h + sep)
            x_m = margen_x
            rect_pantalla = pygame.Rect(
                x_m * 4, y_m * 4,
                w * 4, h * 4,
            )
            self.botones.append((claves[i], textos[i], rect_pantalla))

        self.hover = None

        # ---------------------------------------------------
        # CARGAR LAS 3 CAPAS
        # ---------------------------------------------------
        self.capa_fondo = self._cargar(RUTA_COLINA_FONDO, "colina3")
        self.capa_medio = self._cargar(RUTA_COLINA_MEDIO, "colina2")
        self.capa_frente = self._cargar(RUTA_COLINA_FRENTE, "colina1")

        # Tiempo de animacion
        self.tiempo_fondo = 0.0

    def _cargar(self, ruta, nombre):
        """Carga una imagen con transparencia (alpha)."""
        if os.path.isfile(ruta):
            try:
                return pygame.image.load(ruta).convert_alpha()
            except Exception as e:
                print(f"[menu] No se pudo cargar {nombre}: {e}")
        else:
            print(f"[menu] Imagen NO ENCONTRADA: {ruta}")
        return None

    def handle_event(self, evento, mouse):
        self.hover = None
        for clave, _, rect in self.botones:
            if rect.collidepoint(mouse):
                self.hover = clave
                break

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for clave, _, rect in self.botones:
                if rect.collidepoint(mouse):
                    self._accion(clave)
                    break

    def _accion(self, clave):
        if clave == "jugar":
            from escenas.juego import EscenaJuego
            self.app.cambiar_escena(EscenaJuego(self.app))
        elif clave == "dificultad":
            self.app.cambiar_escena(EscenaDificultad(self.app))
        elif clave == "salir":
            pygame.quit()
            sys.exit()

    # ---------------------------------------------------
    # DIBUJO DE UNA CAPA (con zoom + paneo)
    # ---------------------------------------------------
    def _dibujar_capa(self, imagen, zoom, velocidad, fase):
        """
        Dibuja una capa con zoom + paneo segun su velocidad.
        El paneo usa solo una FRACCION del margen (movimiento sutil).
        """
        if imagen is None:
            return

        # 1) Escalar al zoom pedido
        ancho_z = int(ANCHO * zoom)
        alto_z = int(ALTO * zoom)
        img_zoom = pygame.transform.smoothscale(imagen, (ancho_z, alto_z))

        # 2) Margen disponible para paneo
        margen_x = ancho_z - ANCHO
        margen_y = alto_z - ALTO

        # 3) Offset animado (usando solo una fraccion del margen)
        AMPLITUD_X = 0.30   # 30% del margen horizontal
        AMPLITUD_Y = 0.20   # 20% del margen vertical

        t = self.tiempo_fondo * velocidad + fase
        # sin/cos -> -1 a 1; * 0.5 + 0.5 -> 0 a 1
        # * AMPLITUD -> 0 a AMPLITUD
        # * margen -> 0 a (AMPLITUD * margen)
        off_x = (math.sin(t) * 0.5 + 0.5) * AMPLITUD_X * margen_x
        off_y = (math.cos(t * 0.7) * 0.5 + 0.5) * AMPLITUD_Y * margen_y

        # 4) Blitear desplazada
        self.render.ui.blit(img_zoom, (-int(off_x), -int(off_y)))

    # ---------------------------------------------------
    # DIBUJO DEL FONDO COMPUESTO
    # ---------------------------------------------------
    def _dibujar_fondo(self):
        """Dibuja las 3 capas: fondo, medio, frente."""
        # Fondo (mas lejano)
        self._dibujar_capa(
            self.capa_fondo,
            zoom=FONDO_ZOOM,
            velocidad=FONDO_VELOCIDAD,
            fase=0.0,
        )
        # Medio
        self._dibujar_capa(
            self.capa_medio,
            zoom=MEDIO_ZOOM,
            velocidad=MEDIO_VELOCIDAD,
            fase=1.3,
        )
        # Frente (mas cercano)
        self._dibujar_capa(
            self.capa_frente,
            zoom=FRENTE_ZOOM,
            velocidad=FRENTE_VELOCIDAD,
            fase=2.7,
        )

    # ---------------------------------------------------
    # DRAW
    # ---------------------------------------------------
    def draw(self):
        ancho_m = ANCHO // 4
        alto_m = ALTO // 4

        self.pantalla.fill(NEGRO)

        # --- Fondo animado con 3 capas ---
        self._dibujar_fondo()

        # --- Textos alineados a la izquierda ---
        x_texto = Botones.MENU_X_MARGEN

        self.render._texto_mundo(
            TITULO, self.fuentes["grande"], AMARILLO,
            x_texto, 14
        )
        self.render._texto_mundo(
            f"v{VERSION}", self.fuentes["chica"], GRIS,
            x_texto, 34
        )
        self.render._texto_mundo(
            "Elegi una opcion", self.fuentes["normal"], BLANCO,
            x_texto, 58
        )

        # --- Botones ---
        for clave, texto, rect in self.botones:
            hover = (self.hover == clave)
            self.render.dibujar_boton(
                rect, texto, hover,
                COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF,
                borde_grosor=Botones.MENU_BORDE_GROSOR,
            )

        # --- Pie ---
        self.render._texto_centrado_mundo(
            "ESC para salir", self.fuentes["chica"], GRIS,
            ancho_m - 40, alto_m - 14
        )

    def update(self, dt):
        self.tiempo_fondo += dt