# escenas/niveles.py
import os
import sys
import math
import pygame
from config import (
    ANCHO, ALTO, Botones, DIRECTORIO_RAIZ, ESCALA_PIXEL,
)
from escenas.base import Escena
from vista.colores import (
    NEGRO, BLANCO, AMARILLO, GRIS,
)


# --- Colinas (fondo del menu) ---
RUTA_COLINA_FRENTE = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "colina1.png")
RUTA_COLINA_MEDIO  = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "colina2.png")
RUTA_COLINA_FONDO  = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "colina3.png")

# --- Casas (fondo de niveles) ---
RUTA_CASA_1 = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "casa1.png")
RUTA_CASA_2 = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "casa2.png")
RUTA_CASA_3 = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "casa3.png")


# ============================================================
# AJUSTES DE LAS COLINAS (identicos a menu.py)
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
# AJUSTES DE LAS CASAS (capas de fondo)
# ============================================================
# ZOOM: 1.0 = tamano original. 1.5 = 50% mas grande. 0.8 = 20% mas chica.
# VELOCIDAD: 0.0 = quieta. 0.0002 = lenta. 0.0010 = rapida.
# OFFSET_X: positivo = mueve a la DERECHA. negativo = mueve a la IZQUIERDA.
# OFFSET_Y: positivo = mueve hacia ABAJO. negativo = mueve hacia ARRIBA.

# --- Casa3 (la mas lejana, se dibuja primero) ---
CASA3_ZOOM        = 1.1
CASA3_VELOCIDAD   = 0.0001
CASA3_OFFSET_X    = 0
CASA3_OFFSET_Y    = 0

# --- Casa2 (medio) ---
CASA2_ZOOM        = 1.05
CASA2_VELOCIDAD   = 0.001
CASA2_OFFSET_X    = 25
CASA2_OFFSET_Y    = 0

# --- Casa1 (la mas cercana, se dibuja ultima) ---
CASA1_ZOOM        = 1.01
CASA1_VELOCIDAD   = 0.003
CASA1_OFFSET_X    = 0
CASA1_OFFSET_Y    = 0


# ============================================================
# AJUSTES DE LOS BOTONES
# ============================================================
SUBRAYADO_DURACION = 2.0
ESCALA_SELECCIONADO = 1.4


class EscenaNiveles(Escena):
    def __init__(self, app):
        super().__init__(app)

        e = ESCALA_PIXEL

        w = Botones.DIFICULTAD_W * e
        h = Botones.DIFICULTAD_H * e
        sep = Botones.DIFICULTAD_ESPACIO_Y * e
        margen_x = Botones.MENU_X_MARGEN * e
        margen_y = Botones.MENU_Y_MARGEN * e

        n = 3
        y_ultimo = ALTO - margen_y - h

        self.botones = []
        for i in range(n):
            y_px = y_ultimo - (n - 1 - i) * (h + sep)
            x_px = margen_x
            rect = pygame.Rect(x_px, y_px, w, h)
            self.botones.append((f"nivel{i+1}", str(i + 1), rect))

        self.hover = None
        self.indice = 0

        self.timers_subrayado = [0.0] * len(self.botones)
        self.indice_anterior = 0

        # --- Capas de colinas (fondo) ---
        self.capa_fondo = self._cargar(RUTA_COLINA_FONDO, "colina3")
        self.capa_medio = self._cargar(RUTA_COLINA_MEDIO, "colina2")
        self.capa_frente = self._cargar(RUTA_COLINA_FRENTE, "colina1")

        # --- Capas de casas ---
        self.casa_fondo = self._cargar(RUTA_CASA_3, "casa3")
        self.casa_medio = self._cargar(RUTA_CASA_2, "casa2")
        self.casa_frente = self._cargar(RUTA_CASA_1, "casa1")

    def _cargar(self, ruta, nombre):
        if os.path.isfile(ruta):
            try:
                return pygame.image.load(ruta).convert_alpha()
            except Exception as e:
                print(f"[niveles] No se pudo cargar {nombre}: {e}")
        else:
            print(f"[niveles] Imagen NO ENCONTRADA: {ruta}")
        return None

    def _desbloqueados_actuales(self):
        dif = self.app.clave_dificultad
        return self.app.progreso.get(dif, {"nivel1"})

    def _nivel_desbloqueado(self, clave):
        if clave == "volver":
            return True
        return clave in self._desbloqueados_actuales()

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
                from escenas.menu import EscenaMenu
                self.app.cambiar_escena(EscenaMenu(self.app))

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for clave, _, rect in self.botones:
                if rect.collidepoint(mouse):
                    self._accion(clave)
                    break

    def _accion(self, clave):
        if clave == "volver":
            from escenas.menu import EscenaMenu
            self.app.cambiar_escena(EscenaMenu(self.app))
            return

        if not self._nivel_desbloqueado(clave):
            return

        self.app.nivel_actual = clave
        from escenas.juego import EscenaJuego
        self.app.cambiar_escena(EscenaJuego(self.app))

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
        # 1) Colinas (atras de todo)
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

        # 2) Casas encima de las colinas
        # casa3 -> atras
        self._dibujar_capa(
            self.casa_fondo,
            zoom=CASA3_ZOOM,
            velocidad=CASA3_VELOCIDAD,
            fase=3.5,
            offset_x=CASA3_OFFSET_X,
            offset_y=CASA3_OFFSET_Y,
        )
        # casa2 -> medio
        self._dibujar_capa(
            self.casa_medio,
            zoom=CASA2_ZOOM,
            velocidad=CASA2_VELOCIDAD,
            fase=4.1,
            offset_x=CASA2_OFFSET_X,
            offset_y=CASA2_OFFSET_Y,
        )
        # casa1 -> adelante
        self._dibujar_capa(
            self.casa_frente,
            zoom=CASA1_ZOOM,
            velocidad=CASA1_VELOCIDAD,
            fase=4.7,
            offset_x=CASA1_OFFSET_X,
            offset_y=CASA1_OFFSET_Y,
        )

    def draw(self):
        ancho_m = ANCHO // ESCALA_PIXEL
        alto_m = ALTO // ESCALA_PIXEL

        self.pantalla.fill(NEGRO)

        self._dibujar_fondo()

        x_texto = Botones.MENU_X_MARGEN

        self.render._texto_mundo(
            "NIVELES", self.fuentes["grande"], AMARILLO,
            x_texto, 14
        )
        self.render._texto_mundo(
            "Elegi el nivel", self.fuentes["normal"], BLANCO,
            x_texto, 45
        )

        # --- Botones flotantes ---
        for i, (clave, texto, rect) in enumerate(self.botones):
            seleccionado = (i == self.indice)
            desbloqueado = self._nivel_desbloqueado(clave)

            color_texto = BLANCO if desbloqueado else GRIS

            fuente = self.fuentes["mini"]
            surf = fuente.render(texto, False, color_texto)

            if seleccionado and desbloqueado:
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

            if not desbloqueado:
                candado_x = cx + surf.get_width() // 2 + 12
                candado_y = cy - 8
                pygame.draw.rect(
                    self.render.ui, GRIS,
                    (candado_x, candado_y, 10, 12)
                )
                pygame.draw.circle(
                    self.render.ui, GRIS,
                    (candado_x + 5, candado_y),
                    5, 2
                )

            if seleccionado and desbloqueado:
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