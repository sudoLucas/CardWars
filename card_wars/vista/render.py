# card_wars/vista/render.py
import math
import pygame

from config import ANCHO, ALTO, Layout, Botones, Turno, ESCALA_PIXEL
from vista.colores import (
    NEGRO, BLANCO, AMARILLO, ROJO, GRIS_OSCURO,
    COLOR_JUGADOR, COLOR_JUGADOR_HOVER, COLOR_ENEMIGO,
    COLOR_ENEMIGO_ACTIVA, COLOR_DORSO, COLOR_MUERTA, COLOR_AGUANTE,
    COLOR_FONDO_BARRA, COLOR_INFO,
    COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF,
    COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF,
)

OLA_AMPLITUD   = 5.0
OLA_FRECUENCIA = 0.15
OLA_VELOCIDAD  = 0.006

PAD_ROTACION = 12


class Render:
    def __init__(self, surface_mundo, surface_ui, fuentes):
        self.mundo = surface_mundo
        self.ui = surface_ui
        self.f = fuentes
        self.tiempo = 0.0
        self.e = ESCALA_PIXEL

    def tick(self, dt):
        self.tiempo += dt

    # ==================================================
    # TEXTO
    # ==================================================
    def _texto_mundo(self, txt, fuente, color, xm, ym):
        x = int(xm * self.e)
        y = int(ym * self.e)
        sombra = fuente.render(str(txt), False, NEGRO)
        self.ui.blit(sombra, (x + 2, y + 2))
        surf = fuente.render(str(txt), False, color)
        self.ui.blit(surf, (x, y))
        return surf.get_rect(topleft=(x, y))

    def _texto_centrado_mundo(self, txt, fuente, color, cx_m, ym):
        cx = int(cx_m * self.e)
        y = int(ym * self.e)
        surf = fuente.render(str(txt), False, color)
        x = cx - surf.get_width() // 2
        sombra = fuente.render(str(txt), False, NEGRO)
        self.ui.blit(sombra, (x + 2, y + 2))
        self.ui.blit(surf, (x, y))
        return surf.get_rect(topleft=(x, y))

    def _texto_ui(self, txt, fuente, color, x, y):
        sombra = fuente.render(str(txt), False, NEGRO)
        self.ui.blit(sombra, (x + 2, y + 2))
        surf = fuente.render(str(txt), False, color)
        self.ui.blit(surf, (x, y))
        return surf.get_rect(topleft=(x, y))

    def _texto_centrado_ui(self, txt, fuente, color, cx, y):
        surf = fuente.render(str(txt), False, color)
        x = cx - surf.get_width() // 2
        sombra = fuente.render(str(txt), False, NEGRO)
        self.ui.blit(sombra, (x + 2, y + 2))
        self.ui.blit(surf, (x, y))
        return surf.get_rect(topleft=(x, y))

    def _offset_ola(self, x_m):
        return math.sin(x_m * OLA_FRECUENCIA + self.tiempo * OLA_VELOCIDAD) * OLA_AMPLITUD

    # ==================================================
    # DORSO
    # ==================================================
    def _superficie_dorso(self):
        w, h = Layout.CARTA_W, Layout.CARTA_H
        w_pad = w + PAD_ROTACION * 2
        h_pad = h + PAD_ROTACION * 2

        surf = pygame.Surface((w_pad, h_pad), pygame.SRCALPHA)
        ox, oy = PAD_ROTACION, PAD_ROTACION

        MARCO_OSCURO = (60, 8, 20)
        BORDO        = COLOR_DORSO
        ROMBO_OSCURO = (24, 4, 8)
        CONTORNO     = AMARILLO
        GROSOR_MARCO = 2

        pygame.draw.rect(surf, MARCO_OSCURO, (ox, oy, w, h))
        pygame.draw.rect(surf, BORDO,
                         (ox + GROSOR_MARCO, oy + GROSOR_MARCO,
                          w - GROSOR_MARCO * 2, h - GROSOR_MARCO * 2))

        cx = ox + w // 2
        cy = oy + h // 2
        pulso = 1.0 + 0.10 * math.sin(self.tiempo * 0.005)
        tam_x = int((w // 3) * pulso)
        tam_y = int((h // 3) * pulso)

        pygame.draw.polygon(surf, ROMBO_OSCURO,
                            [(cx, cy - tam_y), (cx + tam_x, cy),
                             (cx, cy + tam_y), (cx - tam_x, cy)], 0)
        pygame.draw.polygon(surf, CONTORNO,
                            [(cx, cy - tam_y + 1), (cx + tam_x - 1, cy),
                             (cx, cy + tam_y - 1), (cx - tam_x + 1, cy)], 1)

        return surf

    # ==================================================
    # CARTA
    # ==================================================
    def dibujar_carta(self, x_m, y_m, carta, color_fondo,
                      hover=False, resaltada=False, ola=False,
                      destacada=False):
        w, h = Layout.CARTA_W, Layout.CARTA_H

        if ola:
            y_m = y_m + self._offset_ola(x_m)

        x_i = int(round(x_m))
        y_i = int(round(y_m))

        if not carta.viva:
            color = COLOR_MUERTA
        elif resaltada:
            color = COLOR_ENEMIGO_ACTIVA
        elif hover:
            color = COLOR_JUGADOR_HOVER
        else:
            color = color_fondo

        rect_m = pygame.Rect(x_i, y_i, w, h)
        pygame.draw.rect(self.mundo, color, rect_m)

        # Borde: amarillo grueso si esta destacada (carta en duelo),
        # blanco fino si no.
        if destacada:
            pygame.draw.rect(self.mundo, AMARILLO, rect_m, 2)
        else:
            borde = AMARILLO if resaltada else BLANCO
            pygame.draw.rect(self.mundo, borde, rect_m, 1)

        # Nombre
        self._texto_mundo(carta.nombre[:8], self.f["mini"], BLANCO,
                          x_i + 2, y_i + 2)

        # Poder
        poder_txt = str(carta.poder) if carta.viva else "0"
        poder_color = AMARILLO if carta.viva else GRIS_OSCURO
        cx = x_i + w // 2
        self._texto_centrado_mundo(poder_txt, self.f["chica"], poder_color,
                                   cx, y_i + 12)
        self._texto_centrado_mundo("PODER", self.f["mini"], BLANCO,
                                   cx, y_i + 26)

        if carta.viva:
            max_ag = carta.poder
            ancho_max = w - 6
            ancho_actual = int(ancho_max * carta.aguante / max_ag) if max_ag > 0 else 0
            barra_y = y_i + h - 5
            pygame.draw.rect(self.mundo, COLOR_FONDO_BARRA,
                             (x_i + 3, barra_y, ancho_max, 2))
            pygame.draw.rect(self.mundo, COLOR_AGUANTE,
                             (x_i + 3, barra_y, ancho_actual, 2))

            txt_ag = f"R {carta.aguante}/{max_ag}"
            surf = self.f["mini"].render(txt_ag, False, COLOR_AGUANTE)
            sombra = self.f["mini"].render(txt_ag, False, NEGRO)
            x_txt = x_i * self.e + w * self.e - surf.get_width() - 2
            y_txt = y_i * self.e + h * self.e - surf.get_height() - 6
            self.ui.blit(sombra, (x_txt + 1, y_txt + 1))
            self.ui.blit(surf, (x_txt, y_txt))
        else:
            cxm, cym = x_i + w // 2, y_i + h // 2
            pygame.draw.line(self.mundo, ROJO, (cxm - 5, cym - 5), (cxm + 5, cym + 5), 1)
            pygame.draw.line(self.mundo, ROJO, (cxm + 5, cym - 5), (cxm - 5, cym + 5), 1)

        return rect_m

    def dibujar_carta_rotada(self, cx_m, cy_m, surf, angulo):
        rotada = pygame.transform.rotate(surf, angulo)
        rect = rotada.get_rect(center=(cx_m, cy_m))
        self.mundo.blit(rotada, rect)

    # ==================================================
    # HP
    # ==================================================
    def dibujar_hp(self, x_m, y_m, hp, hp_max, etiqueta, color, w_m, h_m):
        pygame.draw.rect(self.mundo, COLOR_FONDO_BARRA, (x_m, y_m, w_m, h_m))
        ancho = max(0, int(w_m * hp / hp_max))
        if ancho > 0:
            pygame.draw.rect(self.mundo, color, (x_m, y_m, ancho, h_m))
        pygame.draw.rect(self.mundo, BLANCO, (x_m, y_m, w_m, h_m), 1)

        self._texto_centrado_mundo(f"{etiqueta}: {max(0, hp)}",
                                   self.f["mini"], BLANCO,
                                   x_m + w_m // 2, y_m + h_m // 2 - 3)

    # ==================================================
    # BOTON
    # ==================================================
    def dibujar_boton(self, rect, texto, hover, color_on, color_off):
        x_m = rect[0] // self.e
        y_m = rect[1] // self.e
        w_m = rect[2] // self.e
        h_m = rect[3] // self.e

        color_base = color_on if hover else color_off
        rect_m = pygame.Rect(x_m, y_m, w_m, h_m)
        pygame.draw.rect(self.mundo, color_base, rect_m)
        pygame.draw.rect(self.mundo, BLANCO, rect_m, 1)

        self._texto_centrado_mundo(texto, self.f["mini"], BLANCO,
                                   x_m + w_m // 2, y_m + h_m // 2 - 4)
        return rect

    # ==================================================
    # ESCENA COMPLETA
    # ==================================================
    def dibujar_escena(self, juego, rects_jugador, rects_enemigo, mouse,
                       btn_reiniciar, btn_siguiente):
        self.mundo.fill(COLOR_FONDO_BARRA)

        ancho_m = self.mundo.get_width()
        alto_m = self.mundo.get_height()

        # ==================================================
        # HP (rival izq, jugador der)
        # ==================================================
        hp_w = 70
        hp_h = 8
        self.dibujar_hp(3, 3, juego.hp_enemigo, juego.hp_enemigo_max,
                        "RIVAL", (216, 40, 40), hp_w, hp_h)
        self.dibujar_hp(ancho_m - hp_w - 3, 3,
                        juego.hp_jugador, juego.hp_jugador_max,
                        "TU", (0, 144, 248), hp_w, hp_h)

        # ==================================================
        # ABANICO DEL RIVAL
        # ==================================================
        cantidad_e = len(rects_enemigo)
        cx_centro = ancho_m // 2
        cy_centro = Layout.Y_CENTRO_RIVAL

        if cantidad_e > 0:
            if cantidad_e > 1:
                medio = (cantidad_e - 1) / 2.0
                angulos = [-Layout.ABANICO_ANGULO * (i - medio) / medio
                           for i in range(cantidad_e)]
            else:
                angulos = [0]

            orden = sorted(range(cantidad_e),
                           key=lambda i: abs(i - (cantidad_e - 1) / 2.0),
                           reverse=True)

            for i in orden:
                dist_al_centro = abs(i - (cantidad_e - 1) / 2.0)
                dx = (i - (cantidad_e - 1) / 2.0) * Layout.ABANICO_SEP_X
                dy = dist_al_centro * Layout.ABANICO_OFFSET_Y

                cx = cx_centro + int(dx)
                cy = cy_centro + int(dy)

                cy_ola = cy + self._offset_ola(cx)

                surf = self._superficie_dorso()
                self.dibujar_carta_rotada(cx, cy_ola, surf, angulos[i])

        # ==================================================
        # ZONA DE DUELO
        # ==================================================
        cx_duelo = ancho_m // 2
        cy_duelo = Layout.Y_CENTRO_DUELO

        # Carta del rival (arriba)
        if juego.carta_jugada_enemigo is not None:
            ce = juego.mazo_enemigo[juego.carta_jugada_enemigo]
            x = cx_duelo - Layout.CARTA_W // 2
            y = cy_duelo - Layout.CARTA_H - Layout.DUELO_SEP_Y - 2
            self.dibujar_carta(x, y, ce, COLOR_ENEMIGO, destacada=True)

        # Carta del jugador (abajo, la ultima en dibujarse = queda adelante)
        if juego.carta_jugada_jugador is not None:
            cj = juego.mazo_jugador[juego.carta_jugada_jugador]
            x = cx_duelo - Layout.CARTA_W // 2
            y = cy_duelo + Layout.DUELO_SEP_Y
            self.dibujar_carta(x, y, cj, COLOR_JUGADOR, destacada=True)

        # VS en el medio
        if juego.carta_jugada_enemigo is not None or juego.carta_jugada_jugador is not None:
            self._texto_centrado_mundo("VS", self.f["chica"], AMARILLO,
                                       cx_duelo, Layout.Y_VS)

        # ==================================================
        # MANO DEL JUGADOR
        # ==================================================
        for idx_real, rect in rects_jugador:
            carta = juego.mazo_jugador.cartas[idx_real]
            hover_j = rect.collidepoint(mouse) and juego.turno == Turno.JUGADOR

            x_m = rect.x // self.e
            y_m = rect.y // self.e
            self.dibujar_carta(x_m, y_m, carta, COLOR_JUGADOR,
                               hover=hover_j, ola=True)

        # ==================================================
        # BOTONES (abajo, uno de cada lado)
        # ==================================================
        hover_re = btn_reiniciar.collidepoint(mouse)
        self.dibujar_boton(btn_reiniciar, "REINICIAR", hover_re,
                           COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF)

        if juego.turno == Turno.RESOLVIENDO:
            hover_sig = btn_siguiente.collidepoint(mouse)
            self.dibujar_boton(btn_siguiente, "SIGUIENTE", hover_sig,
                               COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF)

        # ==================================================
        # MENSAJE DE ESTADO (entre el duelo y la mano, con color llamativo)
        # ==================================================
        if juego.turno == Turno.JUGADOR:
            self._texto_centrado_mundo("TU TURNO", self.f["normal"],
                                       AMARILLO, cx_duelo, Layout.Y_MENSAJE)
        elif juego.turno == Turno.RESOLVIENDO:
            # Naranja brillante para que se lea sobre cualquier cosa
            self._texto_centrado_mundo("COMBATE", self.f["normal"],
                                       (255, 160, 40), cx_duelo, Layout.Y_MENSAJE)