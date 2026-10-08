# card_wars/vista/render.py
import math
import pygame

from config import ANCHO, ALTO, Layout, Turno
from vista.colores import (
    NEGRO, BLANCO, AMARILLO, ROJO, GRIS_OSCURO,
    COLOR_JUGADOR, COLOR_JUGADOR_HOVER, COLOR_ENEMIGO,
    COLOR_ENEMIGO_ACTIVA, COLOR_DORSO, COLOR_MUERTA, COLOR_AGUANTE,
    COLOR_FONDO_BARRA, COLOR_INFO,
    COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF,
    COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF,
)

ESCALA_PIXEL = 4

# ---------- Parametros de la ola ----------
OLA_AMPLITUD   = 6.0
OLA_FRECUENCIA = 0.04
OLA_VELOCIDAD  = 0.004

# ---------- Parametros del abanico ----------
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

    # ---------- Helpers de Texto GBA Nativos (Dibujan en el Mundo) ----------
    def _texto_mundo(self, txt, fuente, color, xm, ym):
        """
        Mantenemos el nombre por compatibilidad, pero ahora dibuja en la UI.
        Recibe coordenadas de MUNDO y las convierte a pantalla completa.
        """
        e = self.escala
        x = xm * e
        y = ym * e

        sombra = fuente.render(str(txt), False, NEGRO)
        self.ui.blit(sombra, (x + 1, y + 1))

        surf = fuente.render(str(txt), False, color)
        self.ui.blit(surf, (x, y))
        return surf.get_rect(topleft=(x, y))

    def _texto_centrado_mundo(self, txt, fuente, color, cx_m, ym):
        """
        Mantenemos el nombre por compatibilidad, pero ahora dibuja en la UI.
        Recibe coordenadas de MUNDO y las convierte a pantalla completa.
        """
        e = self.escala
        cx = cx_m * e
        y = ym * e

        surf = fuente.render(str(txt), False, color)
        x = cx - surf.get_width() // 2

        sombra = fuente.render(str(txt), False, NEGRO)
        self.ui.blit(sombra, (x + 1, y + 1))

        self.ui.blit(surf, (x, y))
        return surf.get_rect(topleft=(x, y))

    # ---------- Adaptadores de Compatibilidad con Escenas ----------
    def _texto_ui(self, txt, fuente, color, x, y):
        return self._texto_mundo(txt, fuente, color, x // self.escala, y // self.escala)

    def _texto_centrado_ui(self, txt, fuente, color, cx, y):
        return self._texto_centrado_mundo(txt, fuente, color, cx // self.escala, y // self.escala)

    def _offset_ola(self, x):
        return math.sin(x * OLA_FRECUENCIA + self.tiempo * OLA_VELOCIDAD) * OLA_AMPLITUD

    def _dibujar_rect_mundo(self, color, rect, radio=0):
        e = self.escala
        r = pygame.Rect(rect[0] // e, rect[1] // e, rect[2] // e, rect[3] // e)
        pygame.draw.rect(self.mundo, color, r, border_radius=radio // e if radio else 0)

    # ---------- Componentes Visuales del Juego ----------
    def _superficie_carta(self, carta, color_fondo):
        e = self.escala
        w, h = Layout.CARTA_W // e, Layout.CARTA_H // e
        surf = pygame.Surface((w, h))
        color = COLOR_MUERTA if not carta.viva else color_fondo
        surf.fill(color)
        pygame.draw.rect(surf, BLANCO, (0, 0, w, h), 1)
        pygame.draw.line(surf, NEGRO, (0, h - 1), (w - 1, h - 1))
        pygame.draw.line(surf, NEGRO, (w - 1, 0), (w - 1, h - 1))
        return surf

    def _superficie_dorso(self):
        e = self.escala
        w, h = Layout.CARTA_W // e, Layout.CARTA_H // e
        surf = pygame.Surface((w, h))
        surf.fill(COLOR_DORSO)
        pygame.draw.rect(surf, BLANCO, (0, 0, w, h), 1)
        pygame.draw.line(surf, NEGRO, (0, h - 1), (w - 1, h - 1))
        pygame.draw.line(surf, NEGRO, (w - 1, 0), (w - 1, h - 1))
        cx, cy = w // 2, h // 2
        pulso = 1.0 + 0.08 * math.sin(self.tiempo * 0.004)
        tam = int(6 * pulso)
        pygame.draw.polygon(surf, (40, 10, 15), [(cx, cy - tam), (cx + tam, cy), (cx, cy + tam), (cx - tam, cy)])
        pygame.draw.polygon(surf, AMARILLO, [(cx, cy - tam), (cx + tam, cy), (cx, cy + tam), (cx - tam, cy)], 1)
        return surf

    def dibujar_carta(self, x, y, carta, color_fondo, hover=False, resaltada=False, ola=False):
        e = self.escala
        w_m, h_m = Layout.CARTA_W // e, Layout.CARTA_H // e
        xm = x // e
        ym = (y + self._offset_ola(x)) // e if ola else y // e

        if not carta.viva: color = COLOR_MUERTA
        elif resaltada: color = COLOR_ENEMIGO_ACTIVA
        elif hover: color = COLOR_JUGADOR_HOVER
        else: color = color_fondo

        rect_m = pygame.Rect(xm, ym, w_m, h_m)
        pygame.draw.rect(self.mundo, color, rect_m)
        borde_color = AMARILLO if resaltada else BLANCO
        pygame.draw.rect(self.mundo, borde_color, rect_m, 1)

        if carta.viva:
            max_ag = carta.poder
            ancho_max_m = w_m - 8
            ancho_actual_m = int(ancho_max_m * carta.aguante / max_ag) if max_ag > 0 else 0
            barra_y = ym + h_m - 6
            pygame.draw.rect(self.mundo, COLOR_FONDO_BARRA, (xm + 4, barra_y, ancho_max_m, 2))
            pygame.draw.rect(self.mundo, COLOR_AGUANTE, (xm + 4, barra_y, ancho_actual_m, 2))
        else:
            cx_m, cy_m = xm + w_m // 2, ym + h_m // 2 + 2
            pygame.draw.line(self.mundo, ROJO, (cx_m - 4, cy_m - 4), (cx_m + 4, cy_m + 4), 1)
            pygame.draw.line(self.mundo, ROJO, (cx_m + 4, cy_m - 4), (cx_m - 4, cy_m + 4), 1)

        self._texto_mundo(carta.nombre[:8], self.f["chica"], BLANCO, xm + 3, ym + 2)
        poder_txt = str(carta.poder) if carta.viva else "0"
        poder_color = AMARILLO if carta.viva else GRIS_OSCURO
        self._texto_centrado_mundo(poder_txt, self.f["grande"], poder_color, xm + w_m // 2, ym + 10)
        self._texto_centrado_mundo("PODER", self.f["mini"], BLANCO, xm + w_m // 2, ym + 22)

        if carta.viva:
            self._texto_centrado_mundo("AGUANTE", self.f["mini"], COLOR_AGUANTE, xm + w_m // 2, ym + 29)
            self._texto_centrado_mundo(f"{carta.aguante}/{carta.poder}", self.f["mini"], BLANCO, xm + w_m // 2, ym + 35)

        return pygame.Rect(x, y, Layout.CARTA_W, Layout.CARTA_H)

    def dibujar_carta_rotada(self, cx, cy, surf, angulo, ola=False):
        e = self.escala
        if ola: cy += self._offset_ola(cx) * e
        rotada = pygame.transform.rotate(surf, angulo)
        rect = rotada.get_rect(center=(cx // e, cy // e))
        self.mundo.blit(rotada, rect)

    def dibujar_hp(self, x, y, hp, hp_max, etiqueta, color):
        e = self.escala
        w, h = Layout.HP_BAR_W, Layout.HP_BAR_H
        xm, ym = x // e, y // e
        wm, hm = w // e, h // e

        pygame.draw.rect(self.mundo, COLOR_FONDO_BARRA, (xm, ym, wm, hm))
        ancho = max(0, int(wm * hp / hp_max))
        pygame.draw.rect(self.mundo, color, (xm, ym, ancho, hm))
        pygame.draw.rect(self.mundo, BLANCO, (xm, ym, wm, hm), 1)

        txt = f"{etiqueta}: {max(0, hp)}"
        self._texto_centrado_mundo(txt, self.f["chica"], BLANCO, xm + wm // 2, ym + 1)

    def dibujar_mini(self, x, y, carta, color_fondo, activa=False):
        e = self.escala
        w, h = Layout.MINI_W, Layout.MINI_H
        xm, ym = x // e, y // e
        wm, hm = w // e, h // e

        color = COLOR_MUERTA if not carta.viva else (COLOR_ENEMIGO_ACTIVA if activa else color_fondo)
        pygame.draw.rect(self.mundo, color, (xm, ym, wm, hm))
        pygame.draw.rect(self.mundo, BLANCO, (xm, ym, wm, hm), 1)

        self._texto_mundo(carta.nombre[:6], self.f["mini"], BLANCO, xm + 2, ym + 1)
        if carta.viva:
            self._texto_mundo(f"P:{carta.poder}", self.f["mini"], AMARILLO, xm + 2, ym + 6)
        return pygame.Rect(x, y, Layout.MINI_W, Layout.MINI_H)

    def dibujar_boton(self, rect, texto, hover, color_on, color_off):
        e = self.escala
        xm, ym = rect[0] // e, rect[1] // e
        wm, hm = rect[2] // e, rect[3] // e

        color_base = color_on if hover else color_off
        rect_m = pygame.Rect(xm, ym, wm, hm)
        pygame.draw.rect(self.mundo, color_base, rect_m)
        pygame.draw.rect(self.mundo, BLANCO, rect_m, 1)
        pygame.draw.line(self.mundo, NEGRO, (xm, ym + hm - 1), (xm + wm - 1, ym + hm - 1))
        pygame.draw.line(self.mundo, NEGRO, (xm + wm - 1, ym), (xm + wm - 1, ym + hm - 1))

        offset_y = 1 if hover else 0
        self._texto_centrado_mundo(texto, self.f["chica"], BLANCO, xm + wm // 2, ym + hm // 2 - 4 + offset_y)
        return rect

    # ---------- Escena completa ----------
    def dibujar_escena(self, juego, rects_jugador, rects_enemigo, mouse, btn_reiniciar, btn_siguiente):
        e = self.escala
        self.mundo.fill(COLOR_FONDO_BARRA)

        alto_m = self.mundo.get_height()
        ancho_m = self.mundo.get_width()
        pygame.draw.line(self.mundo, (120, 120, 144), (0, alto_m // 2), (ancho_m, alto_m // 2), 1)

        # HP
        self.dibujar_hp(10 * e, 10 * e,
                        juego.hp_enemigo, juego.hp_enemigo_max, "RIVAL", (216, 40, 40))
        self.dibujar_hp(10 * e, (alto_m * e) - 25,
                        juego.hp_jugador, juego.hp_jugador_max, "TU", (0, 144, 248))

        # ---------- Cartas del RIVAL en abanico ----------
        cantidad_e = len(rects_enemigo)
        cx_centro = ANCHO // 2
        cy_centro = Layout.Y_CARTAS_RIVAL + Layout.CARTA_H // 2

        if cantidad_e > 0:
            if cantidad_e > 1:
                medio = (cantidad_e - 1) / 2.0
                angulos = [-ABANICO_ANGULO * (i - medio) / medio for i in range(cantidad_e)]
            else:
                angulos = [0]

            orden = sorted(range(cantidad_e),
                           key=lambda i: abs(i - (cantidad_e - 1) / 2.0),
                           reverse=True)

            for i in orden:
                idx_real, rect_original = rects_enemigo[i]
                carta = juego.mazo_enemigo.cartas[idx_real]

                dist_al_centro = abs(i - (cantidad_e - 1) / 2.0)
                dx = (i - (cantidad_e - 1) / 2.0) * ABANICO_SEP_X
                dy = dist_al_centro * ABANICO_OFFSET_Y

                cx = cx_centro + int(dx)
                cy = cy_centro + int(dy)

                if juego.turno == Turno.JUGADOR:
                    surf_dorso = self._superficie_dorso()
                    self.dibujar_carta_rotada(cx, cy, surf_dorso, angulos[i], ola=True)
                else:
                    self.dibujar_carta(cx - Layout.CARTA_W // 2, cy - Layout.CARTA_H // 2,
                                       carta, COLOR_ENEMIGO, ola=True)

        # ---------- Mano jugador ----------
        for idx_real, rect in rects_jugador:
            carta = juego.mazo_jugador.cartas[idx_real]
            hover_j = rect.collidepoint(mouse) and juego.turno == Turno.JUGADOR
            self.dibujar_carta(rect.x, rect.y, carta, COLOR_JUGADOR, hover=hover_j, ola=True)

        # ---------- Zona de duelo ----------
        cx_m = ancho_m // 2
        cy_m = alto_m // 2

        if juego.carta_jugada_enemigo is not None:
            ce = juego.mazo_enemigo[juego.carta_jugada_enemigo]
            self.dibujar_carta((cx_m - 20) * e, (cy_m - 45) * e,
                               ce, COLOR_ENEMIGO, ola=True)

        if juego.carta_jugada_jugador is not None:
            cj = juego.mazo_jugador[juego.carta_jugada_jugador]
            self.dibujar_carta((cx_m - 20) * e, (cy_m + 5) * e,
                               cj, COLOR_JUGADOR, ola=True)

        # ---------- Botones y textos ----------
        hover_re = btn_reiniciar.collidepoint(mouse)
        self.dibujar_boton(btn_reiniciar, "REINICIAR", hover_re,
                           COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF)

        if juego.turno == Turno.RESOLVIENDO:
            hover_sig = btn_siguiente.collidepoint(mouse)
            self.dibujar_boton(btn_siguiente, "SIGUIENTE", hover_sig,
                               COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF)

        if juego.turno == Turno.JUGADOR:
            self._texto_centrado_mundo("TU TURNO", self.f["normal"],
                                       AMARILLO, cx_m, cy_m - 50)
        elif juego.turno == Turno.RESOLVIENDO:
            self._texto_centrado_mundo("¡COMBATE!", self.f["ronda"],
                                       BLANCO, cx_m, cy_m - 55)