# escenas/menu.py
import os
import sys
import math
import pygame
from config import (
    ANCHO, ALTO, TITULO, VERSION, Botones, DIRECTORIO_RAIZ,
    ESCALA_PIXEL,
)
from escenas.base import Escena
from escenas.dificultad import EscenaDificultad
from vista.colores import (
    NEGRO, BLANCO, AMARILLO, GRIS,
    COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF,
    COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF,
)


RUTA_COLINA_FRENTE = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "colina1.png")
RUTA_COLINA_MEDIO  = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "colina2.png")
RUTA_COLINA_FONDO  = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "colina3.png")


FONDO_ZOOM       = 1.10
FONDO_VELOCIDAD  = 0.0004

MEDIO_ZOOM       = 1.25
MEDIO_VELOCIDAD  = 0.0004

FRENTE_ZOOM      = 1.60
FRENTE_VELOCIDAD = 0.0007

# Duracion del subrayado animado (en segundos)
SUBRAYADO_DURACION = 2.0

# Escala del texto cuando el boton esta seleccionado
ESCALA_SELECCIONADO = 1.4


class EscenaMenu(Escena):
    def __init__(self, app):
        super().__init__(app)

        # --- Botones en PIXELES REALES (espacio UI) ---
        w = Botones.MENU_W * ESCALA_PIXEL
        h = Botones.MENU_H * ESCALA_PIXEL
        sep = Botones.MENU_ESPACIO_Y * ESCALA_PIXEL
        margen_x = Botones.MENU_X_MARGEN * ESCALA_PIXEL
        margen_y = Botones.MENU_Y_MARGEN * ESCALA_PIXEL

        claves = ["jugar", "dificultad", "salir"]
        textos = ["JUGAR", "DIFICULTAD", "SALIR"]
        n = len(claves)

        y_ultimo = ALTO - margen_y - h

        self.botones = []
        for i in range(n):
            y_px = y_ultimo - (n - 1 - i) * (h + sep)
            x_px = margen_x
            rect = pygame.Rect(x_px, y_px, w, h)
            self.botones.append((claves[i], textos[i], rect))

        self.hover = None
        self.indice = 0

        # Timers del subrayado animado (0.0 a 1.0)
        self.timers_subrayado = [0.0] * len(self.botones)
        self.indice_anterior = 0

        self.capa_fondo = self._cargar(RUTA_COLINA_FONDO, "colina3")
        self.capa_medio = self._cargar(RUTA_COLINA_MEDIO, "colina2")
        self.capa_frente = self._cargar(RUTA_COLINA_FRENTE, "colina1")

        self.tiempo_fondo = 0.0

    def _cargar(self, ruta, nombre):
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
        for i, (clave, _, rect) in enumerate(self.botones):
            if rect.collidepoint(mouse):
                self.hover = clave
                self.indice = i
                break

        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_w, pygame.K_UP):
                self.indice = (self.indice - 1) % len(self.botones)
            elif evento.key in (pygame.K_s, pygame.K_DOWN):
                self.indice = (self.indice + 1) % len(self.botones)
            elif evento.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_z):
                clave = self.botones[self.indice][0]
                self._accion(clave)
            elif evento.key == pygame.K_ESCAPE:
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

    def _dibujar_capa(self, imagen, zoom, velocidad, fase):
        if imagen is None:
            return

        ancho_z = int(ANCHO * zoom)
        alto_z = int(ALTO * zoom)
        img_zoom = pygame.transform.smoothscale(imagen, (ancho_z, alto_z))

        margen_x = ancho_z - ANCHO
        margen_y = alto_z - ALTO

        AMPLITUD_X = 0.30
        AMPLITUD_Y = 0.20

        t = self.tiempo_fondo * velocidad + fase
        off_x = (math.sin(t) * 0.5 + 0.5) * AMPLITUD_X * margen_x
        off_y = (math.cos(t * 0.7) * 0.5 + 0.5) * AMPLITUD_Y * margen_y

        self.render.ui.blit(img_zoom, (-int(off_x), -int(off_y)))

    def _dibujar_fondo(self):
        self._dibujar_capa(self.capa_fondo, zoom=FONDO_ZOOM,
                           velocidad=FONDO_VELOCIDAD, fase=0.0)
        self._dibujar_capa(self.capa_medio, zoom=MEDIO_ZOOM,
                           velocidad=MEDIO_VELOCIDAD, fase=1.3)
        self._dibujar_capa(self.capa_frente, zoom=FRENTE_ZOOM,
                           velocidad=FRENTE_VELOCIDAD, fase=2.7)

    def draw(self):
        ancho_m = ANCHO // 4
        alto_m = ALTO // 4

        self.pantalla.fill(NEGRO)

        self._dibujar_fondo()

        # --- Textos del titulo (en unidades del mundo, van a UI) ---
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

        # --- Botones flotantes (sin fondo, sin borde) ---
        for i, (clave, texto, rect) in enumerate(self.botones):
            seleccionado = (i == self.indice)

            # Renderizamos el texto con la fuente mini
            fuente = self.fuentes["mini"]
            surf = fuente.render(texto, False, BLANCO)

            # Si esta seleccionado, escalamos el surface (esto SIEMPRE crece)
            if seleccionado:
                nuevo_w = int(surf.get_width() * ESCALA_SELECCIONADO)
                nuevo_h = int(surf.get_height() * ESCALA_SELECCIONADO)
                surf = pygame.transform.scale(surf, (nuevo_w, nuevo_h))

            # Posicionamos centrado en el rect
            cx = rect.x + rect.width // 2
            cy = rect.y + rect.height // 2
            x = cx - surf.get_width() // 2
            y = cy - surf.get_height() // 2

            # Sombra
            sombra = pygame.transform.scale(surf, surf.get_size())
            sombra.fill((0, 0, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.render.ui.blit(sombra, (x + 2, y + 2))

            # Texto
            self.render.ui.blit(surf, (x, y))

            # Subrayado animado debajo del texto
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

        # --- Pie ---
        self.render._texto_centrado_mundo(
            "ESC para salir", self.fuentes["chica"], GRIS,
            ancho_m - 40, alto_m - 14
        )

    def update(self, dt):
        self.tiempo_fondo += dt

        # Si el indice cambio, reseteamos el timer del boton anterior
        if self.indice != self.indice_anterior:
            self.timers_subrayado[self.indice_anterior] = 0.0
            self.indice_anterior = self.indice

        # El timer del boton seleccionado crece hasta 1.0 en SUBRAYADO_DURACION seg
        for i in range(len(self.botones)):
            if i == self.indice:
                self.timers_subrayado[i] = min(
                    self.timers_subrayado[i] + dt / (SUBRAYADO_DURACION * 150.0),
                    1.0
                )
            else:
                self.timers_subrayado[i] = 0.0