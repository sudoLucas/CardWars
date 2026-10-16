# escenas/dificultad.py
import os
import sys
import math
import pygame
from config import (
    ANCHO, ALTO, DIFICULTADES, Botones, ESCALA_PIXEL, DIRECTORIO_RAIZ,
)
from escenas.base import Escena
from vista.colores import (
    NEGRO, BLANCO, AMARILLO, GRIS,
    COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF,
    COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF,
)


RUTA_COLINA_FRENTE = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "colina1.png")
RUTA_COLINA_MEDIO  = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "colina2.png")
RUTA_COLINA_FONDO  = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "colina3.png")


# ============================================================
# AJUSTES DE LAS COLINAS (IDENTICOS a menu.py)
# ============================================================
FONDO_ZOOM        = 1.25
FONDO_VELOCIDAD   = 0.0001
FONDO_OFFSET_X    = 50
FONDO_OFFSET_Y    = 0

MEDIO_ZOOM        = 1.25
MEDIO_VELOCIDAD   = 0.0002
MEDIO_OFFSET_X    = 25
MEDIO_OFFSET_Y    = -100

FRENTE_ZOOM       = 1.5
FRENTE_VELOCIDAD  = 0.0005
FRENTE_OFFSET_X   = 0
FRENTE_OFFSET_Y   = -320


# ============================================================
# AJUSTES DE LOS BOTONES
# ============================================================
SUBRAYADO_DURACION = 2.0
ESCALA_SELECCIONADO = 1.4


class EscenaDificultad(Escena):
    def __init__(self, app):
        super().__init__(app)

        e = ESCALA_PIXEL

        w = Botones.DIFICULTAD_W * e
        h = Botones.DIFICULTAD_H * e
        sep = Botones.DIFICULTAD_ESPACIO_Y * e
        margen_x = Botones.MENU_X_MARGEN * e
        margen_y = Botones.MENU_Y_MARGEN * e

        claves = ["facil", "normal", "duro"]
        textos = ["FACIL", "NORMAL", "DURO DE COJONES"]
        n = len(claves)

        y_ultimo = ALTO - margen_y - h

        self.botones = []
        for i in range(n):
            y_px = y_ultimo - (n - 1 - i) * (h + sep)
            x_px = margen_x
            rect = pygame.Rect(x_px, y_px, w, h)
            cfg = DIFICULTADES[claves[i]]
            self.botones.append((claves[i], cfg.nombre, rect))

        # --- Boton VOLVER, arriba de todo ---
        y_volver = y_ultimo - n * (h + sep)
        rect_volver = pygame.Rect(margen_x, y_volver, w, h)
        self.botones.insert(0, ("volver", "VOLVER", rect_volver))

        self.hover = None
        self.indice = 0

        self.timers_subrayado = [0.0] * len(self.botones)
        self.indice_anterior = 0

        self.capa_fondo = self._cargar(RUTA_COLINA_FONDO, "colina3")
        self.capa_medio = self._cargar(RUTA_COLINA_MEDIO, "colina2")
        self.capa_frente = self._cargar(RUTA_COLINA_FRENTE, "colina1")

    def _cargar(self, ruta, nombre):
        if os.path.isfile(ruta):
            try:
                return pygame.image.load(ruta).convert_alpha()
            except Exception as e:
                print(f"[dificultad] No se pudo cargar {nombre}: {e}")
        else:
            print(f"[dificultad] Imagen NO ENCONTRADA: {ruta}")
        return None

    def handle_event(self, evento, mouse):
        # --- Hover con mouse ---
        self.hover = None
        for i, (clave, _, rect) in enumerate(self.botones):
            if rect.collidepoint(mouse):
                self.hover = clave
                self.indice = i
                break

        # --- Navegacion con teclado ---
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_w, pygame.K_UP):
                self.indice = (self.indice - 1) % len(self.botones)
            elif evento.key in (pygame.K_s, pygame.K_DOWN):
                self.indice = (self.indice + 1) % len(self.botones)
            elif evento.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_z):
                clave = self.botones[self.indice][0]
                self._accion(clave)
            elif evento.key == pygame.K_ESCAPE:
                from escenas.menu import EscenaMenu
                self.app.cambiar_escena(EscenaMenu(self.app))

        # --- Click con mouse ---
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for clave, _, rect in self.botones:
                if rect.collidepoint(mouse):
                    self._accion(clave)
                    break

    def _accion(self, clave):
        if clave == "volver":
            from escenas.menu import EscenaMenu
            self.app.cambiar_escena(EscenaMenu(self.app))
        else:
            self.app.clave_dificultad = clave
            from escenas.menu import EscenaMenu
            self.app.cambiar_escena(EscenaMenu(self.app))

    def _dibujar_capa(self, imagen, zoom, velocidad, fase,
                      offset_x=0, offset_y=0):
        if imagen is None:
            return

        ancho_z = int(ANCHO * zoom)
        alto_z = int(ALTO * zoom)
        img_zoom = pygame.transform.smoothscale(imagen, (ancho_z, alto_z))

        margen_x = ancho_z - ANCHO
        margen_y = alto_z - ALTO

        AMPLITUD_X = 0.30
        AMPLITUD_Y = 0.20

        t = self.app.tiempo_fondo * velocidad + fase
        off_x = (math.sin(t) * 0.5 + 0.5) * AMPLITUD_X * margen_x
        off_y = (math.cos(t * 0.7) * 0.5 + 0.5) * AMPLITUD_Y * margen_y

        x_final = -int(off_x) + offset_x
        y_final = -int(off_y) + offset_y

        self.render.ui.blit(img_zoom, (x_final, y_final))

    def _dibujar_fondo(self):
        # Mismo orden que menu.py: colina3 -> colina2 -> colina1
        self._dibujar_capa(
            self.capa_fondo,
            zoom=FONDO_ZOOM,
            velocidad=FONDO_VELOCIDAD,
            fase=0.0,
            offset_x=FONDO_OFFSET_X,
            offset_y=FONDO_OFFSET_Y,
        )
        self._dibujar_capa(
            self.capa_medio,
            zoom=MEDIO_ZOOM,
            velocidad=MEDIO_VELOCIDAD,
            fase=1.3,
            offset_x=MEDIO_OFFSET_X,
            offset_y=MEDIO_OFFSET_Y,
        )
        self._dibujar_capa(
            self.capa_frente,
            zoom=FRENTE_ZOOM,
            velocidad=FRENTE_VELOCIDAD,
            fase=2.7,
            offset_x=FRENTE_OFFSET_X,
            offset_y=FRENTE_OFFSET_Y,
        )

    def draw(self):
        ancho_m = ANCHO // ESCALA_PIXEL
        alto_m = ALTO // ESCALA_PIXEL

        self.pantalla.fill(NEGRO)

        self._dibujar_fondo()

        x_texto = Botones.MENU_X_MARGEN

        self.render._texto_mundo(
            "DIFICULTAD", self.fuentes["grande"], AMARILLO,
            x_texto, 14
        )
        self.render._texto_mundo(
            "Elegi el nivel", self.fuentes["normal"], BLANCO,
            x_texto, 45
        )

        # --- Botones flotantes (mismo estilo que menu) ---
        for i, (clave, texto, rect) in enumerate(self.botones):
            seleccionado = (i == self.indice)
            actual = (clave == self.app.clave_dificultad)

            fuente = self.fuentes["mini"]
            surf = fuente.render(texto, False, BLANCO)

            if seleccionado:
                nuevo_w = int(surf.get_width() * ESCALA_SELECCIONADO)
                nuevo_h = int(surf.get_height() * ESCALA_SELECCIONADO)
                surf = pygame.transform.scale(surf, (nuevo_w, nuevo_h))

            cx = rect.x + rect.width // 2
            cy = rect.y + rect.height // 2
            x = cx - surf.get_width() // 2
            y = cy - surf.get_height() // 2

            sombra = pygame.transform.scale(surf, surf.get_size())
            sombra.fill((0, 0, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.render.ui.blit(sombra, (x + 2, y + 2))

            self.render.ui.blit(surf, (x, y))

            # Asterisco en la dificultad actual
            if actual and clave != "volver":
                self.render._texto_centrado_ui(
                    "*", self.fuentes["mini"], AMARILLO,
                    rect.x + 6, cy - 6
                )

            if seleccionado:
                progreso = self.timers_subrayado[i]
                ancho_total = surf.get_width()
                ancho_actual = int(ancho_total * progreso)
                if ancho_actual > 0:
                    x_sub = cx - ancho_total // 2
                    y_sub = y + surf.get_height() + 4
                    pygame.draw.rect(
                        self.render.ui, BLANCO,
                        (x_sub, y_sub, ancho_actual, 3)
                    )

        self.render._texto_centrado_mundo(
            "ESC para volver", self.fuentes["chica"], GRIS,
            ancho_m - 40, alto_m - 14
        )

    def update(self, dt):
        # ESTA es la linea que faltaba: incrementa el tiempo compartido
        self.app.tiempo_fondo += dt

        if self.indice != self.indice_anterior:
            self.timers_subrayado[self.indice_anterior] = 0.0
            self.indice_anterior = self.indice

        for i in range(len(self.botones)):
            if i == self.indice:
                self.timers_subrayado[i] = min(
                    self.timers_subrayado[i] + dt / (SUBRAYADO_DURACION * 150.0),
                    1.0
                )
            else:
                self.timers_subrayado[i] = 0.0