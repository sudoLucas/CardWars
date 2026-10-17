# card_wars/vista/render.py
import math
import pygame

from config import ANCHO, ALTO, Layout, Botones, Turno, ESCALA_PIXEL, HECHIZOS
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

ESCALA_CARTA_RIVAL = 0.75
MARGEN_INTERNO_REVERSO = 5
GROSOR_PX = 2

COLOR_HECHIZO_BRILLO = (180, 130, 255)

HOVER_LEVANTAR = 14
HOVER_ESCALA = 1.06


class Render:
    def __init__(self, surface_mundo, surface_ui, fuentes):
        self.mundo = surface_mundo
        self.ui = surface_ui
        self.f = fuentes
        self.tiempo = 0.0
        self.e = ESCALA_PIXEL
        self.tiempo_turno_ms = 0

    def tick(self, dt):
        self.tiempo += dt

    def marcar_turno_visible(self):
        self.tiempo_turno_ms = pygame.time.get_ticks()

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
    def _superficie_dorso(self, reverso_img=None, indice=0):
        w, h = Layout.CARTA_W, Layout.CARTA_H
        w_pad = w + PAD_ROTACION * 2
        h_pad = h + PAD_ROTACION * 2

        surf = pygame.Surface((w_pad, h_pad), pygame.SRCALPHA)
        ox, oy = PAD_ROTACION, PAD_ROTACION

        t = self.tiempo * 0.0015 + indice * 0.6

        escala_3d_x = 0.95 + 0.05 * math.sin(t * 1.3)
        escala_3d_y = 0.97 + 0.03 * math.cos(t * 1.7)
        inclinacion = math.sin(t * 0.9) * 2

        w_canto = int(w * escala_3d_x * ESCALA_CARTA_RIVAL)
        h_canto = int(h * escala_3d_y * ESCALA_CARTA_RIVAL)

        offset_x_canto = (w - w_canto) // 2
        offset_y_canto = (h - h_canto) // 2

        for offset_grosor in range(GROSOR_PX, 0, -1):
            canto_color = (15, 10, 15)
            offset_skew = int(inclinacion * offset_grosor / GROSOR_PX)

            rect_canto = pygame.Rect(
                ox + offset_x_canto + offset_grosor + offset_skew,
                oy + offset_y_canto + offset_grosor,
                w_canto, h_canto
            )
            pygame.draw.rect(surf, canto_color, rect_canto)

        w_reverso = w_canto - MARGEN_INTERNO_REVERSO * 2
        h_reverso = h_canto - MARGEN_INTERNO_REVERSO * 2

        if w_reverso > 0 and h_reverso > 0:
            offset_x_reverso = offset_x_canto + MARGEN_INTERNO_REVERSO
            offset_y_reverso = offset_y_canto + MARGEN_INTERNO_REVERSO
            offset_skew = int(inclinacion)

            if reverso_img is not None:
                reverso_escalado = pygame.transform.smoothscale(
                    reverso_img, (w_reverso, h_reverso)
                )

                sombreado = pygame.Surface((w_reverso, h_reverso), pygame.SRCALPHA)
                for y_grad in range(h_reverso):
                    if y_grad > h_reverso // 2:
                        alpha = int(40 * ((y_grad - h_reverso // 2) / (h_reverso // 2)))
                    else:
                        alpha = 0
                    pygame.draw.line(
                        sombreado, (0, 0, 0, alpha),
                        (0, y_grad), (w_reverso, y_grad)
                    )
                reverso_escalado.blit(sombreado, (0, 0))

                surf.blit(reverso_escalado,
                          (ox + offset_x_reverso + offset_skew,
                           oy + offset_y_reverso))

            else:
                MARCO_OSCURO = (60, 8, 20)
                BORDO        = COLOR_DORSO
                ROMBO_OSCURO = (24, 4, 8)
                CONTORNO     = AMARILLO
                GROSOR_MARCO = 2

                rect_reverso = pygame.Rect(
                    ox + offset_x_reverso + offset_skew,
                    oy + offset_y_reverso,
                    w_reverso, h_reverso
                )
                pygame.draw.rect(surf, MARCO_OSCURO, rect_reverso)
                pygame.draw.rect(surf, BORDO,
                                 (rect_reverso.x + GROSOR_MARCO,
                                  rect_reverso.y + GROSOR_MARCO,
                                  w_reverso - GROSOR_MARCO * 2,
                                  h_reverso - GROSOR_MARCO * 2))

                cx = rect_reverso.x + w_reverso // 2
                cy = rect_reverso.y + h_reverso // 2
                pulso = 1.0 + 0.10 * math.sin(self.tiempo * 0.005)
                tam_x = int((w_reverso // 3) * pulso)
                tam_y = int((h_reverso // 3) * pulso)

                pygame.draw.polygon(surf, ROMBO_OSCURO,
                                    [(cx, cy - tam_y), (cx + tam_x, cy),
                                     (cx, cy + tam_y), (cx - tam_x, cy)], 0)
                pygame.draw.polygon(surf, CONTORNO,
                                    [(cx, cy - tam_y + 1), (cx + tam_x - 1, cy),
                                     (cx, cy + tam_y - 1), (cx - tam_x + 1, cy)], 1)

        offset_skew = int(inclinacion)
        brillo_color = (120, 100, 130)
        pygame.draw.line(
            surf, brillo_color,
            (ox + offset_x_canto + offset_skew + 2, oy + offset_y_canto + 1),
            (ox + offset_x_canto + offset_skew + w_canto - 3, oy + offset_y_canto + 1),
            1
        )

        return surf

    # ==================================================
    # CARTA DEL JUGADOR EN EL ABANICO
    # ==================================================
    def _dibujar_carta_abanico(self, cx_m, cy_m, carta, angulo, hover=False):
        w, h = Layout.CARTA_W, Layout.CARTA_H
        factor = 2

        if hover:
            escala = HOVER_ESCALA
            w_draw = int(w * escala)
            h_draw = int(h * escala)
        else:
            w_draw = w
            h_draw = h

        surf = pygame.Surface(
            (w_draw + PAD_ROTACION * 2, h_draw + PAD_ROTACION * 2),
            pygame.SRCALPHA,
        )
        ox = PAD_ROTACION
        oy = PAD_ROTACION

        if not carta.viva:
            color = COLOR_MUERTA
        elif hover:
            color = COLOR_JUGADOR_HOVER
        else:
            color = COLOR_JUGADOR

        es_hechizo = (getattr(carta, "tipo", "criatura") == "hechizo")

        rect = pygame.Rect(ox, oy, w_draw, h_draw)
        pygame.draw.rect(surf, color, rect)

        if es_hechizo:
            pygame.draw.rect(surf, COLOR_HECHIZO_BRILLO, rect, 2)
        else:
            pygame.draw.rect(surf, BLANCO, rect, 1)

        brillo = (
            min(255, color[0] + 60),
            min(255, color[1] + 60),
            min(255, color[2] + 60),
        )
        pygame.draw.line(surf, brillo,
                         (ox + 1, oy + 1), (ox + w_draw - 2, oy + 1), 1)

        sombra = (
            max(0, color[0] - 50),
            max(0, color[1] - 50),
            max(0, color[2] - 50),
        )
        pygame.draw.line(surf, sombra,
                         (ox + 1, oy + h_draw - 2),
                         (ox + w_draw - 2, oy + h_draw - 2), 1)

        if hover:
            def _blit_texto_escalado(superficie, texto, fuente, color, x, y):
                txt = fuente.render(texto, False, color)
                tam = (
                    max(1, txt.get_width() // factor),
                    max(1, txt.get_height() // factor),
                )
                txt = pygame.transform.scale(txt, tam)
                superficie.blit(txt, (x, y))

            _blit_texto_escalado(
                surf, carta.nombre[:10], self.f["mini"], BLANCO,
                ox + 2, oy + 2,
            )

            if es_hechizo:
                _blit_texto_escalado(
                    surf, "HECHIZO", self.f["mini"], COLOR_HECHIZO_BRILLO,
                    ox + w_draw // 2 - 20, oy + 20,
                )
                _blit_texto_escalado(
                    surf, f"{carta.costo_mana} mana", self.f["mini"], AMARILLO,
                    ox + w_draw // 2 - 20, oy + 36,
                )
            else:
                poder_txt = str(carta.poder) if carta.viva else "0"
                poder_color = AMARILLO if carta.viva else GRIS_OSCURO
                poder_surf = self.f["chica"].render(poder_txt, False, poder_color)
                tam_p = (
                    max(1, poder_surf.get_width() // factor),
                    max(1, poder_surf.get_height() // factor),
                )
                poder_surf = pygame.transform.scale(poder_surf, tam_p)
                surf.blit(poder_surf,
                          (ox + w_draw // 2 - poder_surf.get_width() // 2, oy + 20))

                _blit_texto_escalado(
                    surf, "PODER", self.f["mini"], BLANCO,
                    ox + w_draw // 2 - 18, oy + 40,
                )

                if carta.viva:
                    max_ag = getattr(carta, "poder_original", carta.poder)
                    ancho_max = w_draw - 6
                    ancho_actual = int(ancho_max * carta.aguante / max_ag) if max_ag > 0 else 0
                    barra_y = oy + h_draw - 8
                    pygame.draw.rect(surf, COLOR_FONDO_BARRA,
                                     (ox + 3, barra_y, ancho_max, 2))
                    pygame.draw.rect(surf, COLOR_AGUANTE,
                                     (ox + 3, barra_y, ancho_actual, 2))

                    txt_ag = f"{carta.aguante}/{max_ag}"
                    ag_surf = self.f["mini"].render(txt_ag, False, COLOR_AGUANTE)
                    tam_ag = (
                        max(1, ag_surf.get_width() // factor),
                        max(1, ag_surf.get_height() // factor),
                    )
                    ag_surf = pygame.transform.scale(ag_surf, tam_ag)
                    surf.blit(ag_surf,
                              (ox + w_draw // 2 - ag_surf.get_width() // 2,
                               oy + h_draw - 16))
                else:
                    cxm = ox + w_draw // 2
                    cym = oy + h_draw // 2
                    pygame.draw.line(surf, ROJO, (cxm - 5, cym - 5), (cxm + 5, cym + 5), 1)
                    pygame.draw.line(surf, ROJO, (cxm + 5, cym - 5), (cxm - 5, cym + 5), 1)

        rotada = pygame.transform.rotate(surf, angulo)
        rect_final = rotada.get_rect(center=(cx_m, cy_m))
        self.mundo.blit(rotada, rect_final)

    # ==================================================
    # CARTA SUELTA
    # ==================================================
    def dibujar_carta(self, x_m, y_m, carta, color_fondo,
                      hover=False, resaltada=False, ola=False,
                      destacada=False):
        w, h = Layout.CARTA_W, Layout.CARTA_H

        if ola:
            y_m = y_m + self._offset_ola(x_m)

        offset_y_flote = math.sin(self.tiempo * 0.003 + x_m * 0.08) * 2
        y_m += offset_y_flote

        t = self.tiempo * 0.0015 + x_m * 0.05
        escala_3d_x = 0.96 + 0.04 * math.sin(t * 1.3)
        escala_3d_y = 0.97 + 0.03 * math.cos(t * 1.7)
        inclinacion = math.sin(t * 0.9) * 4

        w_3d = int(w * escala_3d_x)
        h_3d = int(h * escala_3d_y)

        x_i = int(round(x_m + (w - w_3d) / 2))
        y_i = int(round(y_m + (h - h_3d) / 2))

        es_hechizo = (getattr(carta, "tipo", "criatura") == "hechizo")

        if not carta.viva:
            color = COLOR_MUERTA
        elif resaltada:
            color = COLOR_ENEMIGO_ACTIVA
        elif hover:
            color = COLOR_JUGADOR_HOVER
        else:
            color = color_fondo

        for offset_grosor in range(GROSOR_PX, 0, -1):
            canto_color = (
                max(0, color[0] - 60 - offset_grosor * 15),
                max(0, color[1] - 60 - offset_grosor * 15),
                max(0, color[2] - 60 - offset_grosor * 15),
            )
            offset_skew = int(inclinacion * offset_grosor / GROSOR_PX)

            rect_canto = pygame.Rect(
                x_i + offset_grosor + offset_skew,
                y_i + offset_grosor,
                w_3d, h_3d
            )
            pygame.draw.rect(self.mundo, canto_color, rect_canto)

        offset_skew = int(inclinacion)
        rect_m = pygame.Rect(x_i + offset_skew, y_i, w_3d, h_3d)
        pygame.draw.rect(self.mundo, color, rect_m)

        if destacada:
            pygame.draw.rect(self.mundo, AMARILLO, rect_m, 2)
        elif es_hechizo:
            pygame.draw.rect(self.mundo, COLOR_HECHIZO_BRILLO, rect_m, 2)
        else:
            borde = AMARILLO if resaltada else BLANCO
            pygame.draw.rect(self.mundo, borde, rect_m, 1)

        brillo_color = (
            min(255, color[0] + 60),
            min(255, color[1] + 60),
            min(255, color[2] + 60),
        )
        pygame.draw.line(
            self.mundo, brillo_color,
            (rect_m.x + 1, rect_m.y + 1),
            (rect_m.x + w_3d - 2, rect_m.y + 1), 1
        )

        sombra_color = (
            max(0, color[0] - 50),
            max(0, color[1] - 50),
            max(0, color[2] - 50),
        )
        pygame.draw.line(
            self.mundo, sombra_color,
            (rect_m.x + 1, rect_m.y + h_3d - 2),
            (rect_m.x + w_3d - 2, rect_m.y + h_3d - 2), 1
        )

        self._texto_mundo(carta.nombre[:10], self.f["mini"], BLANCO,
                          rect_m.x + 2, rect_m.y + 2)

        if es_hechizo:
            cx = rect_m.x + w_3d // 2
            self._texto_centrado_mundo("HECHIZO", self.f["mini"],
                                       COLOR_HECHIZO_BRILLO,
                                       cx, rect_m.y + 20)
            self._texto_centrado_mundo(f"{carta.costo_mana} mana",
                                       self.f["mini"], AMARILLO,
                                       cx, rect_m.y + 34)
        else:
            poder_txt = str(carta.poder) if carta.viva else "0"
            poder_color = AMARILLO if carta.viva else GRIS_OSCURO
            cx = rect_m.x + w_3d // 2
            self._texto_centrado_mundo(poder_txt, self.f["chica"], poder_color,
                                       cx, rect_m.y + 12)
            self._texto_centrado_mundo("PODER", self.f["mini"], BLANCO,
                                       cx, rect_m.y + 26)

            if carta.viva:
                max_ag = getattr(carta, "poder_original", carta.poder)
                ancho_max = w_3d - 6
                ancho_actual = int(ancho_max * carta.aguante / max_ag) if max_ag > 0 else 0
                barra_y = rect_m.y + h_3d - 5
                pygame.draw.rect(self.mundo, COLOR_FONDO_BARRA,
                                 (rect_m.x + 3, barra_y, ancho_max, 2))
                pygame.draw.rect(self.mundo, COLOR_AGUANTE,
                                 (rect_m.x + 3, barra_y, ancho_actual, 2))

                txt_ag = f"R {carta.aguante}/{max_ag}"
                surf = self.f["mini"].render(txt_ag, False, COLOR_AGUANTE)
                sombra = self.f["mini"].render(txt_ag, False, NEGRO)
                x_txt = rect_m.x * self.e + w_3d * self.e - surf.get_width() - 2
                y_txt = rect_m.y * self.e + h_3d * self.e - surf.get_height() - 6
                self.ui.blit(sombra, (x_txt + 1, y_txt + 1))
                self.ui.blit(surf, (x_txt, y_txt))
            else:
                cxm = rect_m.x + w_3d // 2
                cym = rect_m.y + h_3d // 2
                pygame.draw.line(self.mundo, ROJO, (cxm - 5, cym - 5), (cxm + 5, cym + 5), 1)
                pygame.draw.line(self.mundo, ROJO, (cxm + 5, cym - 5), (cxm - 5, cym + 5), 1)

        return rect_m

    # ==================================================
    # TOOLTIP
    # ==================================================
    def dibujar_tooltip(self, carta, x, y):
        es_hechizo = (getattr(carta, "tipo", "criatura") == "hechizo")

        if es_hechizo:
            data = HECHIZOS.get(carta.hechizo_id, {})
            lineas = [
                f"{data.get('nombre', carta.nombre)}",
                data.get("descripcion", ""),
            ]
        else:
            lineas = [
                f"{carta.nombre}",
                f"{carta.poder} dano",
                f"{carta.aguante} vida",
            ]

        ancho = 180
        alto = 12 + len(lineas) * 20
        rect = pygame.Rect(x, y - alto - 6, ancho, alto)
        pygame.draw.rect(self.ui, (20, 20, 30, 230), rect)
        pygame.draw.rect(self.ui, BLANCO, rect, 1)

        for i, linea in enumerate(lineas):
            self._texto_ui(linea, self.f["mini"], BLANCO,
                           x + 8, y - alto - 6 + 6 + i * 20)

    def dibujar_carta_rotada(self, cx_m, cy_m, surf, angulo):
        rotacion_extra = math.sin(self.tiempo * 0.0018 + cx_m * 0.04) * 4
        angulo_total = angulo + rotacion_extra

        rotada = pygame.transform.rotate(surf, angulo_total)
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
        if hp_img is None:
            return

        w, h = hp_img.get_size()

        FACTOR_ANCHO = 1.0
        FACTOR_ALTO = 0.12
        SEPARACION = 0
        MARGEN_IZQ = 150
        MARGEN_DER = 80

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
    # MANA
    # ==================================================
    def dibujar_mana(self, x_m, y_m, mana, mana_max):
        w_m = 22
        h_m = 28

        pygame.draw.rect(self.mundo, (150, 120, 200),
                         (x_m + 4, y_m - 4, w_m - 8, 6))

        pygame.draw.rect(self.mundo, (80, 80, 110),
                         (x_m + 8, y_m + 2, w_m - 16, 6))

        cuerpo_rect = pygame.Rect(x_m, y_m + 8, w_m, h_m - 8)
        pygame.draw.ellipse(self.mundo, (30, 40, 90), cuerpo_rect)

        nivel = max(0, min(1, mana / mana_max)) if mana_max > 0 else 0
        alto_total = h_m - 10
        alto_llenado = int(alto_total * nivel)
        if alto_llenado > 0:
            llenado_rect = pygame.Rect(
                x_m + 2,
                y_m + 8 + (alto_total - alto_llenado) + 2,
                w_m - 4,
                alto_llenado,
            )
            pygame.draw.ellipse(self.mundo, (90, 160, 255), llenado_rect)

        pygame.draw.ellipse(self.mundo, (200, 220, 255),
                            (x_m + 4, y_m + 12, 4, 8))

        pygame.draw.ellipse(self.mundo, BLANCO, cuerpo_rect, 1)

        self._texto_centrado_mundo(str(mana), self.f["chica"], BLANCO,
                                   x_m + w_m // 2, y_m + 12)

        self._texto_ui(f"/{mana_max}", self.f["mini"], (180, 180, 200),
                       int((x_m + w_m + 4) * self.e),
                       int((y_m + 14) * self.e))

    # ==================================================
    # BOTON
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
                       hp_img=None, mesa_img=None, reversos_img=None,
                       posiciones_jugador=None):
        self.mundo.fill(COLOR_FONDO_BARRA)

        if mesa_img is not None:
            MESA_ANCHO = 700
            MESA_ALTO = 500
            mesa_escalada = pygame.transform.smoothscale(
                mesa_img, (MESA_ANCHO, MESA_ALTO)
            )
            mesa_x = (self.mundo.get_width() - MESA_ANCHO) // 2
            mesa_y = (self.mundo.get_height() - MESA_ALTO) // 2
            self.mundo.blit(mesa_escalada, (mesa_x, mesa_y))

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

            RIVAL_X_BASE = 10
            RIVAL_Y_BASE = 30
            JUGADOR_X_MARGEN_DER = 10
            JUGADOR_Y_BASE = 70

            AMPLITUD_X = 4
            AMPLITUD_Y = 4
            VELOCIDAD = 0.003

            t = self.tiempo * VELOCIDAD
            off_x = int(math.sin(t) * AMPLITUD_X)
            off_y = int(math.cos(t) * AMPLITUD_Y)

            rival_x = RIVAL_X_BASE + off_x
            rival_y = RIVAL_Y_BASE + off_y
            self.dibujar_barra_hp(rival_x, rival_y,
                                  juego.hp_enemigo, juego.hp_enemigo_max,
                                  hp_img_chica, (220, 40, 40))

            jugador_x = ANCHO - ancho_hp - JUGADOR_X_MARGEN_DER + off_x
            jugador_y = JUGADOR_Y_BASE + off_y
            self.dibujar_barra_hp(jugador_x, jugador_y,
                                  juego.hp_jugador, juego.hp_jugador_max,
                                  hp_img_chica, (0, 144, 248))
        else:
            hp_w = 70
            hp_h = 8
            self.dibujar_hp(3, 3, juego.hp_enemigo, juego.hp_enemigo_max,
                            "RIVAL", (216, 40, 40), hp_w, hp_h)
            self.dibujar_hp(ancho_m - hp_w - 3, 3,
                            juego.hp_jugador, juego.hp_jugador_max,
                            "TU", (0, 144, 248), hp_w, hp_h)

        # --- Mana (abajo derecha) ---
        mana_disponible = getattr(juego, "mana_jugador", 0)
        self.dibujar_mana(ancho_m - 40, alto_m - 75, mana_disponible, 14)

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

            for pos_visual, i in enumerate(orden):
                dist_al_centro = abs(i - (cantidad_e - 1) / 2.0)
                dx = (i - (cantidad_e - 1) / 2.0) * Layout.ABANICO_SEP_X
                dy = dist_al_centro * Layout.ABANICO_OFFSET_Y

                cx = cx_centro + int(dx)
                cy = cy_centro + int(dy)

                cy_ola = cy + self._offset_ola(cx)

                if reversos_img and len(reversos_img) > 0:
                    reverso_actual = reversos_img[pos_visual % len(reversos_img)]
                else:
                    reverso_actual = None

                surf = self._superficie_dorso(reverso_actual, pos_visual)
                self.dibujar_carta_rotada(cx, cy_ola, surf, angulos[i])

        # --- Mano del jugador (antes del duelo para que las cartas del duelo queden encima) ---
        carta_hover = None
        rect_hover = None

        if posiciones_jugador is not None and len(posiciones_jugador) > 0 and len(posiciones_jugador) == len(rects_jugador):
            cantidad = len(rects_jugador)
            medio = (cantidad - 1) / 2.0

            idx_hover = -1
            for i, (idx_real, rect) in enumerate(rects_jugador):
                if rect.collidepoint(mouse) and juego.turno in (Turno.JUGADOR_TIRA, Turno.JUGADOR_HECHIZOS):
                    idx_hover = i
                    carta_hover = juego.mazo_jugador.cartas[idx_real]
                    rect_hover = rect
                    break

            orden = sorted(range(cantidad),
                           key=lambda i: abs(i - medio),
                           reverse=True)

            for i in orden:
                idx_real, rect = rects_jugador[i]
                carta = juego.mazo_jugador.cartas[idx_real]
                cx, cy, angulo = posiciones_jugador[i]

                if i == idx_hover:
                    cy -= HOVER_LEVANTAR

                self._dibujar_carta_abanico(
                    cx, cy, carta, angulo,
                    hover=(i == idx_hover),
                )
        else:
            for idx_real, rect in rects_jugador:
                carta = juego.mazo_jugador.cartas[idx_real]
                hover_j = rect.collidepoint(mouse) and juego.turno in (Turno.JUGADOR_TIRA, Turno.JUGADOR_HECHIZOS)
                if hover_j:
                    carta_hover = carta
                    rect_hover = rect

                x_m = rect.x // self.e
                y_m = rect.y // self.e
                self.dibujar_carta(x_m, y_m, carta, COLOR_JUGADOR,
                                   hover=hover_j, ola=True)

        # --- Zona de duelo (DESPUES de la mano, para que quede encima) ---
        cx_duelo = ancho_m // 2
        cy_duelo = Layout.Y_CENTRO_DUELO

        if (juego.carta_jugada_enemigo is not None
                and 0 <= juego.carta_jugada_enemigo < len(juego.mazo_enemigo)):
            ce = juego.mazo_enemigo[juego.carta_jugada_enemigo]
            x = cx_duelo - Layout.CARTA_W // 2
            y = cy_duelo - Layout.CARTA_H - Layout.DUELO_SEP_Y - 2
            self.dibujar_carta(x, y, ce, COLOR_ENEMIGO, destacada=True)

        if (juego.carta_jugada_jugador is not None
                and 0 <= juego.carta_jugada_jugador < len(juego.mazo_jugador)):
            cj = juego.mazo_jugador[juego.carta_jugada_jugador]
            if getattr(cj, "tipo", "criatura") == "criatura":
                x = cx_duelo - Layout.CARTA_W // 2
                y = cy_duelo + Layout.DUELO_SEP_Y
                self.dibujar_carta(x, y, cj, COLOR_JUGADOR, destacada=True)

        if juego.carta_jugada_enemigo is not None or juego.carta_jugada_jugador is not None:
            self._texto_centrado_mundo("VS", self.f["chica"], AMARILLO,
                                       cx_duelo, Layout.Y_VS)

        # --- Tooltip (encima de todo) ---
        if carta_hover is not None and rect_hover is not None:
            self.dibujar_tooltip(carta_hover, rect_hover.x, rect_hover.y)

        # --- Botones ---
        if btn_reiniciar is not None:
            hover_re = btn_reiniciar.collidepoint(mouse)
            self.dibujar_boton(btn_reiniciar, "REINICIAR", hover_re,
                               COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF)

        if btn_siguiente is not None and juego.turno == Turno.RESULTADO:
            hover_sig = btn_siguiente.collidepoint(mouse)
            self.dibujar_boton(btn_siguiente, "CONTINUAR", hover_sig,
                               COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF)

        # --- Mensaje de estado ---
        if juego.turno in (Turno.JUGADOR_TIRA, Turno.JUGADOR_HECHIZOS):
            if self.tiempo_turno_ms == 0:
                self.marcar_turno_visible()
            if pygame.time.get_ticks() - self.tiempo_turno_ms < 1000:
                self._texto_centrado_mundo("TU TURNO", self.f["normal"],
                                           AMARILLO, cx_duelo, Layout.Y_MENSAJE)
        else:
            self.tiempo_turno_ms = 0

        if juego.turno == Turno.RESULTADO:
            self._texto_centrado_mundo("COMBATE", self.f["normal"],
                                       (255, 160, 40), cx_duelo, Layout.Y_MENSAJE)

        # ==================================================
        # EMOTES
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