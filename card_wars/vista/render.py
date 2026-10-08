# vista/render.py
import math
import pygame
from config import ANCHO, ALTO, Layout, Turno
from vista.colores import (
    NEGRO, BLANCO, AMARILLO, VERDE, ROJO, GRIS_OSCURO,
    COLOR_JUGADOR, COLOR_JUGADOR_HOVER, COLOR_ENEMIGO,
    COLOR_ENEMIGO_ACTIVA, COLOR_DORSO, COLOR_MUERTA, COLOR_AGUANTE,
    COLOR_FONDO_BARRA, COLOR_LINEA_DUELO, COLOR_INFO,
    COLOR_ETIQ_RIVAL, COLOR_ETIQ_JUGADOR,
    COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF,
    COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF,
)


# Escala de pixelado (debe coincidir con main.py)
ESCALA_PIXEL = 4


OLA_AMPLITUD   = 4.0
OLA_FRECUENCIA = 0.015
OLA_VELOCIDAD  = 0.005

ABANICO_ANGULO    = 5
ABANICO_SEP_X     = 100
ABANICO_OFFSET_Y  = 18


class Render:
    def __init__(self, surface_mundo, surface_ui, fuentes):
        self.mundo = surface_mundo
        self.ui = surface_ui
        self.f = fuentes
        self.tiempo = 0.0
        self.escala = ESCALA_PIXEL

    def tick(self, dt):
        self.tiempo += dt

    # ---------- Helpers ----------
    def _texto_centrado_ui(self, txt, fuente, color, cx, y):
        """Dibuja texto centrado en la surface UI (coordenadas de pantalla completa)."""
        surf = fuente.render(txt, True, color)
        self.ui.blit(surf, (cx - surf.get_width() // 2, y))
        return surf.get_rect(topleft=(cx - surf.get_width() // 2, y))

    def _texto_ui(self, txt, fuente, color, x, y):
        """Dibuja texto en la surface UI (coordenadas de pantalla completa)."""
        surf = fuente.render(txt, True, color)
        self.ui.blit(surf, (x, y))
        return surf.get_rect(topleft=(x, y))

    def _offset_ola(self, x):
        return math.sin(x * OLA_FRECUENCIA + self.tiempo * OLA_VELOCIDAD) * OLA_AMPLITUD

    def _dibujar_rect_mundo(self, color, rect, radio=0):
        """Dibuja un rect en la surface del MUNDO con coordenadas divididas por escala."""
        e = self.escala
        r = pygame.Rect(rect[0] // e, rect[1] // e, rect[2] // e, rect[3] // e)
        pygame.draw.rect(self.mundo, color, r, border_radius=radio // e if radio else 0)

    # ---------- Superficie de una carta ----------
    def _superficie_carta(self, carta, color_fondo):
        """Devuelve una surface de carta del tamano del MUNDO (dividido por escala)."""
        e = self.escala
        w, h = Layout.CARTA_W // e, Layout.CARTA_H // e
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        if not carta.viva:
            color = COLOR_MUERTA
        else:
            color = color_fondo

        pygame.draw.rect(surf, color, (0, 0, w, h), border_radius=5)
        pygame.draw.rect(surf, BLANCO, (0, 0, w, h), 1, border_radius=5)

        return surf

    def _superficie_dorso(self):
        e = self.escala
        w, h = Layout.CARTA_W // e, Layout.CARTA_H // e
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        pygame.draw.rect(surf, COLOR_DORSO, (0, 0, w, h), border_radius=5)
        pygame.draw.rect(surf, BLANCO, (0, 0, w, h), 1, border_radius=5)

        cx = w // 2
        cy = h // 2
        pulso = 1.0 + 0.08 * math.sin(self.tiempo * 0.004)
        tam = int(15 * pulso)

        pygame.draw.polygon(surf, (60, 15, 25), [
            (cx, cy - tam), (cx + tam, cy), (cx, cy + tam), (cx - tam, cy),
        ])
        pygame.draw.polygon(surf, BLANCO, [
            (cx, cy - tam), (cx + tam, cy), (cx, cy + tam), (cx - tam, cy),
        ], 1)

        return surf

    # ---------- Carta grande ----------
    def dibujar_carta(self, x, y, carta, color_fondo, hover=False, resaltada=False, ola=False):
        """
        Dibuja una carta. Los ELEMENTOS van al mundo.
        El texto (nombre, poder, aguante) va a la UI con coordenadas * escala.
        """
        e = self.escala
        w_m, h_m = Layout.CARTA_W // e, Layout.CARTA_H // e

        if ola:
            y = y + self._offset_ola(x)

        # Posicion en el mundo
        xm, ym = x // e, y // e

        if not carta.viva:
            color = COLOR_MUERTA
        elif resaltada:
            color = COLOR_ENEMIGO_ACTIVA
        elif hover:
            color = COLOR_JUGADOR_HOVER
        else:
            color = color_fondo

        # Rect de fondo (mundo)
        rect_m = pygame.Rect(xm, ym, w_m, h_m)
        pygame.draw.rect(self.mundo, color, rect_m, border_radius=5)
        borde = AMARILLO if resaltada else BLANCO
        pygame.draw.rect(self.mundo, borde, rect_m, 1, border_radius=5)

        # Barra de aguante (mundo)
        if carta.viva:
            max_ag = carta.poder
            ancho_max_m = w_m - 12
            ancho_actual_m = int(ancho_max_m * carta.aguante / max_ag) if max_ag > 0 else 0
            barra_y = ym + h_m - 18
            pygame.draw.rect(self.mundo, COLOR_FONDO_BARRA,
                             (xm + 6, barra_y, ancho_max_m, 5), border_radius=2)
            pygame.draw.rect(self.mundo, COLOR_AGUANTE,
                             (xm + 6, barra_y, ancho_actual_m, 5), border_radius=2)
        else:
            # Cruz dibujada en el mundo
            cx_m = xm + w_m // 2
            cy_m = ym + h_m // 2 + 5
            pygame.draw.line(self.mundo, (200, 60, 60),
                             (cx_m - 8, cy_m - 8), (cx_m + 8, cy_m + 8), 3)
            pygame.draw.line(self.mundo, (200, 60, 60),
                             (cx_m + 8, cy_m - 8), (cx_m - 8, cy_m + 8), 3)

        # --- Textos a la UI con coordenadas * escala ---
        # Nombre (esquina sup izq)
        self._texto_ui(carta.nombre, self.f["chica"], BLANCO, x + 8, y + 6)

        # Poder (centro arriba)
        poder_txt = str(carta.poder) if carta.viva else "0"
        poder_color = AMARILLO if carta.viva else (120, 40, 40)
        self._texto_centrado_ui(poder_txt, self.f["grande"], poder_color,
                                 x + Layout.CARTA_W // 2, y + 40)

        # Etiqueta PODER
        self._texto_centrado_ui("PODER", self.f["chica"], BLANCO,
                                 x + Layout.CARTA_W // 2, y + 80)

        if carta.viva:
            self._texto_centrado_ui("AGUANTE", self.f["chica"], COLOR_AGUANTE,
                                     x + Layout.CARTA_W // 2, y + 105)
            max_ag = carta.poder
            self._texto_centrado_ui(f"{carta.aguante}/{max_ag}",
                                     self.f["chica"], BLANCO,
                                     x + Layout.CARTA_W // 2, y + 140)

        return pygame.Rect(x, y, Layout.CARTA_W, Layout.CARTA_H)

    # ---------- Carta rotada ----------
    def dibujar_carta_rotada(self, cx, cy, surf, angulo, ola=False):
        if ola:
            cy += self._offset_ola(cx) * self.escala

        rotada = pygame.transform.rotate(surf, angulo)
        e = self.escala
        rect = rotada.get_rect(center=(cx // e, cy // e))
        self.mundo.blit(rotada, rect)

    # ---------- Barra de HP ----------
    def dibujar_hp(self, x, y, hp, hp_max, etiqueta, color):
        e = self.escala
        w, h = Layout.HP_BAR_W, Layout.HP_BAR_H

        # Barra en el mundo
        xm, ym = x // e, y // e
        wm, hm = w // e, h // e
        pygame.draw.rect(self.mundo, COLOR_FONDO_BARRA, (xm, ym, wm, hm), border_radius=3)
        ancho = max(0, int(wm * hp / hp_max))
        pygame.draw.rect(self.mundo, color, (xm, ym, ancho, hm), border_radius=3)

        # Texto en la UI
        txt = f"{etiqueta}: {max(0, hp)} HP"
        self._texto_centrado_ui(txt, self.f["normal"], BLANCO,
                                 x + w // 2, y + 6)

    # ---------- Mini carta ----------
    def dibujar_mini(self, x, y, carta, color_fondo, activa=False):
        e = self.escala
        w, h = Layout.MINI_W, Layout.MINI_H

        # Fondo en el mundo
        xm, ym = x // e, y // e
        wm, hm = w // e, h // e

        if not carta.viva:
            color = COLOR_MUERTA
        elif activa:
            color = COLOR_ENEMIGO_ACTIVA
        else:
            color = color_fondo

        pygame.draw.rect(self.mundo, color, (xm, ym, wm, hm), border_radius=4)
        pygame.draw.rect(self.mundo, BLANCO, (xm, ym, wm, hm), 1, border_radius=4)

        # Textos en la UI
        self._texto_ui(carta.nombre, self.f["mini"], BLANCO, x + 8, y + 5)

        if carta.viva:
            self._texto_ui(f"P {carta.poder}", self.f["mini"], AMARILLO, x + 8, y + 27)
            self._texto_ui(f"AGU {carta.aguante}", self.f["chica"], COLOR_AGUANTE, x + 8, y + 52)
        else:
            self._texto_ui("MUERTA", self.f["normal"], (200, 60, 60), x + 15, y + 28)

    # ---------- Boton ----------
    def dibujar_boton(self, rect, texto, hover, color_on, color_off):
        e = self.escala
        color = color_on if hover else color_off

        # Fondo del boton en el mundo
        rm = pygame.Rect(rect.x // e, rect.y // e, rect.w // e, rect.h // e)
        pygame.draw.rect(self.mundo, color, rm, border_radius=3)
        pygame.draw.rect(self.mundo, BLANCO, rm, 1, border_radius=3)

        # Texto en la UI
        surf = self.f["chica"].render(texto, True, BLANCO)
        self.ui.blit(surf, (rect.x + rect.w // 2 - surf.get_width() // 2,
                             rect.y + rect.h // 2 - surf.get_height() // 2))

    # ---------- Escena completa ----------
    def dibujar_escena(self, juego, rects_jugador, rects_enemigo, mouse,
                       boton_reiniciar, boton_siguiente):
        self.mundo.fill(NEGRO)

        # HP
        self.dibujar_hp(Layout.HP_BAR_X_IZQ, Layout.HP_BAR_Y,
                        juego.hp_jugador, juego.hp_jugador_max, "TU", VERDE)
        self.dibujar_hp(Layout.HP_BAR_X_DER, Layout.HP_BAR_Y,
                        juego.hp_enemigo, juego.hp_enemigo_max, "MAQUINA", ROJO)

        # Ronda
        self._texto_centrado_ui(f"RONDA {juego.ronda}",
                                 self.f["ronda"], AMARILLO, ANCHO // 2, 12)

        # Rebarajes
        reb_j = juego.mazo_jugador.rebarajes
        if reb_j:
            self._texto_centrado_ui(f"Rebarajes - Tu: {reb_j}",
                                     self.f["chica"], COLOR_INFO, ANCHO // 2, 38)

        # Etiqueta rival
        self._texto_centrado_ui("CARTAS DEL RIVAL",
                                 self.f["chica"], COLOR_ETIQ_RIVAL,
                                 ANCHO // 2, Layout.Y_CARTAS_RIVAL - 15)

        # Cartas rival en abanico
        cantidad = len(rects_enemigo)
        cx_centro = ANCHO // 2
        cy_centro = Layout.Y_CARTAS_RIVAL + Layout.CARTA_H // 2

        superficies = [self._superficie_dorso() for _ in range(cantidad)]

        if cantidad > 1:
            medio = (cantidad - 1) / 2.0
            angulos = [-ABANICO_ANGULO * (i - medio) / medio for i in range(cantidad)]
        else:
            angulos = [0]

        orden = sorted(range(cantidad),
                       key=lambda i: abs(i - (cantidad - 1) / 2.0),
                       reverse=True)

        for i in orden:
            dist_al_centro = abs(i - (cantidad - 1) / 2.0)
            dx = (i - (cantidad - 1) / 2.0) * ABANICO_SEP_X
            dy = dist_al_centro * ABANICO_OFFSET_Y
            cx = cx_centro + int(dx)
            cy = cy_centro + int(dy)
            self.dibujar_carta_rotada(cx, cy, superficies[i], angulos[i], ola=True)

        # Linea zona duelo (mundo)
        e = self.escala
        pygame.draw.line(self.mundo, COLOR_LINEA_DUELO,
                         (40 // e, (Layout.Y_ZONA_DUELO - 5) // e),
                         ((ANCHO - 40) // e, (Layout.Y_ZONA_DUELO - 5) // e), 1)

        # Mini cartas
        if juego.carta_jugada_jugador is not None:
            cj = juego.mazo_jugador[juego.carta_jugada_jugador]
            self.dibujar_mini(
                ANCHO // 2 + Layout.MINI_JUGADOR_X_OFFSET,
                Layout.Y_ZONA_DUELO + Layout.MINI_Y_OFFSET,
                cj, COLOR_JUGADOR)

        self._texto_centrado_ui("VS", self.f["grande"], AMARILLO,
                                 ANCHO // 2, Layout.Y_ZONA_DUELO + 30)

        if juego.carta_jugada_enemigo is not None:
            ce = juego.mazo_enemigo[juego.carta_jugada_enemigo]
            self.dibujar_mini(
                ANCHO // 2 + Layout.MINI_ENEMIGO_X_OFFSET,
                Layout.Y_ZONA_DUELO + Layout.MINI_Y_OFFSET,
                ce, COLOR_ENEMIGO, activa=True)

        # Mensaje
        self._texto_centrado_ui(juego.mensaje, self.f["mensaje"], AMARILLO,
                                 ANCHO // 2, Layout.Y_MENSAJE)

        # Etiqueta tus cartas
        self._texto_centrado_ui("TUS CARTAS (click para tirar a la mesa)",
                                 self.f["chica"], COLOR_ETIQ_JUGADOR,
                                 ANCHO // 2, Layout.Y_CARTAS_TU - 15)

        # Cartas jugador
        for idx, rect in rects_jugador:
            carta = juego.mazo_jugador[idx]
            seleccionable = (juego.turno == Turno.JUGADOR and carta.viva)
            hover = seleccionable and rect.collidepoint(mouse)
            self.dibujar_carta(rect.x, rect.y, carta, COLOR_JUGADOR, hover=hover, ola=True)

        # Botones
        if juego.turno == Turno.RESOLVIENDO:
            self.dibujar_boton(boton_siguiente, "SIGUIENTE RONDA (ESPACIO)",
                               boton_siguiente.collidepoint(mouse),
                               COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF)

        self.dibujar_boton(boton_reiniciar, "REINICIAR (R)",
                           boton_reiniciar.collidepoint(mouse),
                           COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF)