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
    COLOR_BORDE_BOTON, COLOR_BORDE_BOTON_HOVER,
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

        if destacada:
            pygame.draw.rect(self.mundo, AMARILLO, rect_m, 2)
        else:
            borde = AMARILLO if resaltada else BLANCO
            pygame.draw.rect(self.mundo, borde, rect_m, 1)

        self._texto_mundo(carta.nombre[:8], self.f["mini"], BLANCO,
                          x_i + 2, y_i + 2)

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

    def dibujar_barra_hp(self, x, y, hp, hp_max, hp_img, color_lleno):
        """
        Dibuja la barra de HP con HP.png como CONTORNO.
        """
        if hp_img is None:
            return

        w, h = hp_img.get_size()

        # ================================================
        # AJUSTES DEL CUADRADO PINTADO
        # ================================================
        FACTOR_ANCHO = 1.0
        FACTOR_ALTO = 0.12
        SEPARACION = 0
        MARGEN_IZQ = 150
        MARGEN_DER = 80
        # ================================================

        ancho_util = w - MARGEN_IZQ - MARGEN_DER
        slot_w = ancho_util // 5
        slot_h = h

        ancho_cuadro = int(slot_w * FACTOR_ANCHO)
        alto_cuadro = int(slot_h * FACTOR_ALTO)

        offset_x_cuadro = (slot_w - ancho_cuadro) // 2
        offset_y_cuadro = (slot_h - alto_cuadro) // 2

        hp_por_cuadro = hp_max / 5.0 if hp_max > 0 else 0
        if hp_por_cuadro <= 0:
            return

        cuadros_llenos = int(hp // hp_por_cuadro)
        cuadros_llenos = max(0, min(5, cuadros_llenos))

        cuadros_con_hp = math.ceil(hp / hp_por_cuadro)
        cuadros_con_hp = max(0, min(5, cuadros_con_hp))

        capa = pygame.Surface((w, h), pygame.SRCALPHA)

        for i in range(cuadros_llenos):
            x_cuadro = (
                MARGEN_IZQ
                + i * (slot_w + SEPARACION)
                + offset_x_cuadro
            )
            rect_cuadro = pygame.Rect(
                x_cuadro, offset_y_cuadro, ancho_cuadro, alto_cuadro
            )
            capa.fill(color_lleno, rect_cuadro)

        if cuadros_llenos < cuadros_con_hp:
            i = cuadros_llenos

            hp_restante = hp - (cuadros_llenos * hp_por_cuadro)
            fraccion = hp_restante / hp_por_cuadro
            fraccion = max(0.0, min(1.0, fraccion))

            bordo = (60, 0, 0)
            r = int(bordo[0] + (color_lleno[0] - bordo[0]) * fraccion)
            g = int(bordo[1] + (color_lleno[1] - bordo[1]) * fraccion)
            b = int(bordo[2] + (color_lleno[2] - bordo[2]) * fraccion)
            color_cuadro = (r, g, b)

            ancho_pintado = int(ancho_cuadro * fraccion)
            if ancho_pintado > 0:
                x_cuadro = (
                    MARGEN_IZQ
                    + i * (slot_w + SEPARACION)
                    + offset_x_cuadro
                )
                rect_parcial = pygame.Rect(
                    x_cuadro, offset_y_cuadro, ancho_pintado, alto_cuadro
                )
                capa.fill(color_cuadro, rect_parcial)

        capa.blit(hp_img, (0, 0))
        self.ui.blit(capa, (x, y))

    # ==================================================
    # BOTON (con borde de color)
    # ==================================================
    def dibujar_boton(self, rect, texto, hover, color_on, color_off,
                      borde_color=None, borde_grosor=2):
        x_m = rect[0] // self.e
        y_m = rect[1] // self.e
        w_m = rect[2] // self.e
        h_m = rect[3] // self.e

        color_base = color_on if hover else color_off

        if borde_color is None:
            borde_color = COLOR_BORDE_BOTON_HOVER if hover else COLOR_BORDE_BOTON

        rect_m = pygame.Rect(x_m, y_m, w_m, h_m)
        pygame.draw.rect(self.mundo, color_base, rect_m)

        if borde_grosor > 0:
            for i in range(borde_grosor):
                borde_rect = pygame.Rect(
                    x_m + i, y_m + i,
                    w_m - i * 2, h_m - i * 2
                )
                pygame.draw.rect(self.mundo, borde_color, borde_rect, 1)

        self._texto_centrado_mundo(texto, self.f["mini"], BLANCO,
                                   x_m + w_m // 2, y_m + h_m // 2 - 4)
        return rect

    # ==================================================
    # ESCENA COMPLETA
    # ==================================================
    def dibujar_escena(self, juego, rects_jugador, rects_enemigo, mouse,
                       btn_reiniciar, btn_siguiente,
                       emote_rival=None, emote_jugador=None,
                       emote_activo=False, quien_recibio_dano=None,
                       hp_img=None):
        self.mundo.fill(COLOR_FONDO_BARRA)

        ancho_m = self.mundo.get_width()
        alto_m = self.mundo.get_height()

        # --- HP con HP.png ---
        if hp_img is not None:
            ancho_orig, alto_orig = hp_img.get_size()
            escala_hp = 1
            ancho_hp = int(ancho_orig * escala_hp)
            alto_hp = int(alto_orig * escala_hp)
            hp_img_chica = pygame.transform.smoothscale(
                hp_img, (ancho_hp, alto_hp)
            )

            # ============================================
            # AJUSTES DE POSICION Y MOVIMIENTO
            # ============================================
            # Posicion base de cada barra
            RIVAL_X_BASE = 10
            RIVAL_Y_BASE = 4       # mas chico = mas arriba
            JUGADOR_X_MARGEN_DER = 10
            JUGADOR_Y_BASE = 30    # mas grande = mas abajo

            # Amplitud del vaiven (en pixeles)
            AMPLITUD_X = 4
            AMPLITUD_Y = 4
            VELOCIDAD = 0.003      # mas alto = mas rapido
            # ============================================

            # Vaiven diagonal suave
            t = self.tiempo * VELOCIDAD
            off_x = int(math.sin(t) * AMPLITUD_X)
            off_y = int(math.cos(t) * AMPLITUD_Y)

            # Rival: arriba izquierda
            rival_x = RIVAL_X_BASE + off_x
            rival_y = RIVAL_Y_BASE + off_y
            self.dibujar_barra_hp(rival_x, rival_y,
                                  juego.hp_enemigo, juego.hp_enemigo_max,
                                  hp_img_chica, (220, 40, 40))
            self._texto_ui(f"RIVAL: {max(0, juego.hp_enemigo)}",
                           self.f["mini"], BLANCO,
                           rival_x, rival_y + alto_hp + 4)

            # Jugador: arriba derecha
            jugador_x = ANCHO - ancho_hp - JUGADOR_X_MARGEN_DER + off_x
            jugador_y = JUGADOR_Y_BASE + off_y
            self.dibujar_barra_hp(jugador_x, jugador_y,
                                  juego.hp_jugador, juego.hp_jugador_max,
                                  hp_img_chica, (0, 144, 248))
            self._texto_ui(f"TU: {max(0, juego.hp_jugador)}",
                           self.f["mini"], BLANCO,
                           jugador_x, jugador_y + alto_hp + 4)
        else:
            hp_w = 70
            hp_h = 8
            self.dibujar_hp(3, 3, juego.hp_enemigo, juego.hp_enemigo_max,
                            "RIVAL", (216, 40, 40), hp_w, hp_h)
            self.dibujar_hp(ancho_m - hp_w - 3, 3,
                            juego.hp_jugador, juego.hp_jugador_max,
                            "TU", (0, 144, 248), hp_w, hp_h)

        # --- Abanico del rival ---
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

        # --- Zona de duelo ---
        cx_duelo = ancho_m // 2
        cy_duelo = Layout.Y_CENTRO_DUELO

        if juego.carta_jugada_enemigo is not None:
            ce = juego.mazo_enemigo[juego.carta_jugada_enemigo]
            x = cx_duelo - Layout.CARTA_W // 2
            y = cy_duelo - Layout.CARTA_H - Layout.DUELO_SEP_Y - 2
            self.dibujar_carta(x, y, ce, COLOR_ENEMIGO, destacada=True)

        if juego.carta_jugada_jugador is not None:
            cj = juego.mazo_jugador[juego.carta_jugada_jugador]
            x = cx_duelo - Layout.CARTA_W // 2
            y = cy_duelo + Layout.DUELO_SEP_Y
            self.dibujar_carta(x, y, cj, COLOR_JUGADOR, destacada=True)

        if juego.carta_jugada_enemigo is not None or juego.carta_jugada_jugador is not None:
            self._texto_centrado_mundo("VS", self.f["chica"], AMARILLO,
                                       cx_duelo, Layout.Y_VS)

        # --- Mano del jugador ---
        for idx_real, rect in rects_jugador:
            carta = juego.mazo_jugador.cartas[idx_real]
            hover_j = rect.collidepoint(mouse) and juego.turno == Turno.JUGADOR

            x_m = rect.x // self.e
            y_m = rect.y // self.e
            self.dibujar_carta(x_m, y_m, carta, COLOR_JUGADOR,
                               hover=hover_j, ola=True)

        # --- Botones ---
        hover_re = btn_reiniciar.collidepoint(mouse)
        self.dibujar_boton(btn_reiniciar, "REINICIAR", hover_re,
                           COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF)

        if juego.turno == Turno.RESOLVIENDO:
            hover_sig = btn_siguiente.collidepoint(mouse)
            self.dibujar_boton(btn_siguiente, "SIGUIENTE", hover_sig,
                               COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF)

        # --- Mensaje de estado ---
        if juego.turno == Turno.JUGADOR:
            self._texto_centrado_mundo("TU TURNO", self.f["normal"],
                                       AMARILLO, cx_duelo, Layout.Y_MENSAJE)
        elif juego.turno == Turno.RESOLVIENDO:
            self._texto_centrado_mundo("COMBATE", self.f["normal"],
                                       (255, 160, 40), cx_duelo, Layout.Y_MENSAJE)

        # ==================================================
        # EMOTES (mas grandes, con flotacion, sacudida y risa)
        # ==================================================
        TAM_NORMAL = 140
        TAM_AGRANDADO = 200
        MARGEN_X = 10
        MARGEN_Y_BASE = 50
        FLOTACION_AMPLITUD = 6
        FLOTACION_VELOCIDAD = 0.002

        tam = TAM_AGRANDADO if emote_activo else TAM_NORMAL

        offset_flote = math.sin(
            self.tiempo * FLOTACION_VELOCIDAD
        ) * FLOTACION_AMPLITUD

        mov_rival_x = 0
        mov_rival_y = 0
        mov_jug_x = 0
        mov_jug_y = 0

        if emote_activo:
            if quien_recibio_dano == "rival":
                mov_rival_x = int(math.sin(self.tiempo * 0.08) * 8)
                mov_rival_y = int(math.cos(self.tiempo * 0.09) * 8)
                mov_jug_y = -int(abs(math.sin(self.tiempo * 0.012)) * 12)

            elif quien_recibio_dano == "jugador":
                mov_jug_x = int(math.sin(self.tiempo * 0.08) * 8)
                mov_jug_y = int(math.cos(self.tiempo * 0.09) * 8)
                mov_rival_y = -int(abs(math.sin(self.tiempo * 0.012)) * 12)

            elif quien_recibio_dano == "empate":
                mov_rival_x = int(math.sin(self.tiempo * 0.08) * 8)
                mov_rival_y = int(math.cos(self.tiempo * 0.09) * 8)
                mov_jug_x = int(math.sin(self.tiempo * 0.08) * 8)
                mov_jug_y = int(math.cos(self.tiempo * 0.09) * 8)

        if emote_rival is not None:
            emote_r = pygame.transform.smoothscale(emote_rival, (tam, tam))
            x_r = MARGEN_X + mov_rival_x
            y_r = MARGEN_Y_BASE + int(offset_flote) + mov_rival_y
            self.ui.blit(emote_r, (x_r, y_r))

        if emote_jugador is not None:
            emote_j = pygame.transform.smoothscale(emote_jugador, (tam, tam))
            x_j = self.ui.get_width() - tam - MARGEN_X + mov_jug_x
            y_j = (self.ui.get_height() - tam - MARGEN_Y_BASE
                   + int(offset_flote) + mov_jug_y)
            self.ui.blit(emote_j, (x_j, y_j))