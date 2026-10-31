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
HOVER_ESCALA = 1.0


class Render:
    def __init__(self, surface_mundo, surface_ui, fuentes):
        self.mundo = surface_mundo
        self.ui = surface_ui
        self.f = fuentes
        self.tiempo = 0.0
        self.e = ESCALA_PIXEL
        self.tiempo_turno_ms = 0
        self._mesa_imagen_original = None
        self._mesa_imagen_escalada = None
        self.fondo_tablero = None

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
    def _dibujar_carta_abanico(self, cx_m, cy_m, carta, angulo, hover=False,
                               seleccionada=False, escala_base=None):
        w, h = Layout.CARTA_W, Layout.CARTA_H
        es_hechizo = (getattr(carta, "tipo", "criatura") == "hechizo")
        if escala_base is None:
            escala_base = Layout.escala_carta_mano(carta)

        if hover:
            escala = escala_base * HOVER_ESCALA
            w_draw = int(w * escala)
            h_draw = int(h * escala)
        else:
            w_draw = int(w * escala_base)
            h_draw = int(h * escala_base)

        surf = pygame.Surface(
            (w_draw + PAD_ROTACION * 2, h_draw + PAD_ROTACION * 2),
            pygame.SRCALPHA,
        )
        ox = PAD_ROTACION
        oy = PAD_ROTACION

        if not carta.viva:
            color = COLOR_MUERTA
        elif hover or seleccionada:
            color = COLOR_JUGADOR_HOVER
        else:
            color = COLOR_JUGADOR

        rect = pygame.Rect(ox, oy, w_draw, h_draw)
        pygame.draw.rect(surf, color, rect)

        if es_hechizo:
            pygame.draw.rect(surf, COLOR_HECHIZO_BRILLO, rect, 2)
        else:
            pygame.draw.rect(surf, BLANCO, rect, 1)

        if seleccionada:
            intensidad = 0.5 + 0.5 * math.sin(self.tiempo * 0.01)
            color_sel = (int(255 * intensidad), int(200 + 55 * intensidad), 0)
            pygame.draw.rect(surf, color_sel, rect, 3)

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

        def texto_ajustado(texto, color, centro_x, y, ancho_max):
            texto_surf = self.f["mini"].render(texto, False, color)
            ancho = min(max(1, texto_surf.get_width() // 2), ancho_max)
            alto = max(1, texto_surf.get_height() // 2)
            if ancho < texto_surf.get_width() // 2:
                alto = max(
                    1,
                    int(alto * ancho / max(1, texto_surf.get_width() // 2)),
                )
            texto_surf = pygame.transform.scale(texto_surf, (ancho, alto))
            surf.blit(texto_surf, (centro_x - ancho // 2, y))

        centro_x = ox + w_draw // 2
        pygame.draw.rect(
            surf,
            (min(255, color[0] + 18), min(255, color[1] + 18),
             min(255, color[2] + 18)),
            (ox + 2, oy + 2, w_draw - 4, max(7, h_draw // 5)),
        )
        pygame.draw.line(
            surf, (min(255, color[0] + 55), min(255, color[1] + 55),
                   min(255, color[2] + 55)),
            (ox + 2, oy + h_draw - 2), (ox + w_draw - 3, oy + h_draw - 2), 1,
        )
        texto_ajustado(
            carta.nombre[:14], BLANCO, centro_x, oy + 3, w_draw - 6,
        )

        if es_hechizo:
            pygame.draw.polygon(
                surf, COLOR_HECHIZO_BRILLO,
                [(centro_x, oy + h_draw // 2 - 7),
                 (centro_x + 6, oy + h_draw // 2),
                 (centro_x, oy + h_draw // 2 + 7),
                 (centro_x - 6, oy + h_draw // 2)],
            )
            texto_ajustado(
                f"{carta.costo_mana} MANA", AMARILLO, centro_x,
                oy + h_draw - 12, w_draw - 6,
            )
        else:
            poder_txt = str(carta.poder) if carta.viva else "0"
            texto_ajustado(
                poder_txt, AMARILLO if carta.viva else GRIS_OSCURO,
                centro_x, oy + h_draw // 2 - 8, w_draw - 6,
            )
            texto_ajustado(
                "PODER", BLANCO, centro_x, oy + h_draw // 2 + 1,
                w_draw - 6,
            )

            if carta.viva:
                max_ag = getattr(carta, "poder_original", carta.poder)
                ancho_barra = w_draw - 8
                ancho_actual = (
                    int(ancho_barra * carta.aguante / max_ag)
                    if max_ag > 0 else 0
                )
                # Barra de vida bien abajo
                barra_y = oy + h_draw - 6
                pygame.draw.rect(
                    surf, COLOR_FONDO_BARRA,
                    (ox + 4, barra_y, ancho_barra, 4),
                )
                pygame.draw.rect(
                    surf, COLOR_AGUANTE,
                    (ox + 4, barra_y, ancho_actual, 4),
                )
                # Texto de vida un poco más arriba para que no pise la barra
                texto_ajustado(
                    f"{carta.aguante}/{max_ag}", COLOR_AGUANTE,
                    centro_x, oy + h_draw - 20, w_draw - 6,
                )
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
        data = HECHIZOS.get(carta.hechizo_id, {}) if es_hechizo else {}
        fuente = self.f["mini"]
        titulo = data.get("nombre", carta.nombre) if es_hechizo else carta.nombre
        ancho = max(240, min(360, fuente.size(titulo)[0] + 20))
        ancho_texto = ancho - 20

        def envolver(texto):
            lineas = []
            actual = ""
            for palabra in texto.split():
                candidato = f"{actual} {palabra}".strip()
                if actual and fuente.size(candidato)[0] > ancho_texto:
                    lineas.append(actual)
                    actual = palabra
                else:
                    actual = candidato
            if actual:
                lineas.append(actual)
            return lineas

        lineas_titulo = envolver(titulo)
        lineas_detalle = (
            envolver(data.get("descripcion", ""))[:3]
            if es_hechizo else
            [f"{carta.poder} dano", f"{carta.aguante} vida"]
        )
        alto = 16 + 22 * (len(lineas_titulo) + len(lineas_detalle))
        rect = pygame.Rect(
            max(4, min(x, self.ui.get_width() - ancho - 4)),
            max(4, y - alto - 10),
            ancho,
            alto,
        )

        pygame.draw.rect(self.ui, (20, 20, 30, 240), rect)
        pygame.draw.rect(self.ui, BLANCO, rect, 2)

        texto_y = rect.y + 8
        for linea in lineas_titulo:
            self._texto_ui(linea, fuente, AMARILLO, rect.x + 8, texto_y)
            texto_y += 22
        for linea in lineas_detalle:
            self._texto_ui(linea, fuente, BLANCO, rect.x + 8, texto_y)
            texto_y += 22

    def dibujar_carta_rotada(self, cx_m, cy_m, surf, angulo):
        rotacion_extra = math.sin(self.tiempo * 0.0018 + cx_m * 0.04) * 4
        angulo_total = angulo + rotacion_extra

        rotada = pygame.transform.rotate(surf, angulo_total)
        rect = rotada.get_rect(center=(cx_m, cy_m))
        self.mundo.blit(rotada, rect)

    # ==================================================
    # HP
    # ==================================================

    def dibujar_puntos_hp(self, cx, cy, hp, hp_max, color_lleno,
                          cantidad=5, radio=5, radio_arco=75,
                          apertura_grados=90.0, grosor=2, angulo_centro=-45.0):
        if hp_max <= 0:
            return

        # --- BOOST DE SATURACIÓN Y BRILLO ---
        # Aumentamos el canal máximo y bajamos el mínimo para saturar
        r, g, b = color_lleno
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        
        # Si el color es rojo (r es el mayor)
        if r == max_c:
            r = min(255, int(r * 1.15) + 10)
            g = max(0, int(g * 0.8))
            b = max(0, int(b * 0.8))
        # Si el color es azul (b es el mayor)
        elif b == max_c:
            b = min(255, int(b * 1.15) + 10)
            r = max(0, int(r * 0.8))
            g = max(0, int(g * 0.8))
            
        color_brillante = (r, g, b)
        color_glow = (r, g, b, 80) # Halo semitransparente

        mitad = apertura_grados / 2.0
        ang_ini = angulo_centro - mitad
        ang_fin = angulo_centro + mitad

        hp_por_punto = hp_max / cantidad

        for i in range(cantidad):
            if cantidad == 1:
                ang = angulo_centro
            else:
                t = i / (cantidad - 1)
                ang = ang_ini + (ang_fin - ang_ini) * t

            rad = math.radians(ang)
            px = cx + math.cos(rad) * radio_arco
            py = cy + math.sin(rad) * radio_arco

            hp_ini = i * hp_por_punto
            hp_restante = hp - hp_ini

            # Dibujar halo de fondo si el punto está lleno o parcial
            if hp_restante > 0:
                surf_glow = pygame.Surface((radio*4, radio*4), pygame.SRCALPHA)
                pygame.draw.circle(surf_glow, color_glow, (radio*2, radio*2), radio*1.5)
                self.ui.blit(surf_glow, (int(px) - radio*2, int(py) - radio*2))

            if hp_restante >= hp_por_punto:
                pygame.draw.circle(self.ui, color_brillante, (int(px), int(py)), radio)
            elif hp_restante <= 0:
                pygame.draw.circle(self.ui, color_lleno, (int(px), int(py)), radio, grosor)
            else:
                frac = hp_restante / hp_por_punto
                surf = pygame.Surface((radio * 2 + 2, radio * 2 + 2), pygame.SRCALPHA)
                alpha = int(255 * frac)
                pygame.draw.circle(surf, (*color_brillante, alpha), (radio + 1, radio + 1), radio)
                self.ui.blit(surf, (int(px) - radio - 1, int(py) - radio - 1))
                pygame.draw.circle(self.ui, color_brillante, (int(px), int(py)), radio, 1)

    # ==================================================
    # MANA
    # ==================================================
    def dibujar_mana(self, x_m, y_m, mana, mana_max):
        w_m = 34
        h_m = 44
        nivel = max(0, min(1, mana / mana_max)) if mana_max > 0 else 0
        botella = [
            (x_m + 13, y_m), (x_m + 21, y_m),
            (x_m + 21, y_m + 6), (x_m + 25, y_m + 9),
            (x_m + 29, y_m + 15), (x_m + 32, y_m + 23),
            (x_m + 32, y_m + 34), (x_m + 28, y_m + 41),
            (x_m + 23, y_m + 44), (x_m + 11, y_m + 44),
            (x_m + 6, y_m + 41), (x_m + 2, y_m + 34),
            (x_m + 2, y_m + 23), (x_m + 5, y_m + 15),
            (x_m + 9, y_m + 9), (x_m + 13, y_m + 6),
        ]
        pygame.draw.polygon(self.mundo, (15, 20, 48), botella)
        pygame.draw.polygon(
            self.mundo, (115, 175, 235),
            [(x_m + 13, y_m + 2), (x_m + 21, y_m + 2),
             (x_m + 21, y_m + 8), (x_m + 25, y_m + 11),
             (x_m + 28, y_m + 17), (x_m + 30, y_m + 24),
             (x_m + 30, y_m + 33), (x_m + 26, y_m + 39),
             (x_m + 22, y_m + 42), (x_m + 12, y_m + 42),
             (x_m + 8, y_m + 39), (x_m + 4, y_m + 33),
             (x_m + 4, y_m + 24), (x_m + 6, y_m + 17),
             (x_m + 9, y_m + 11), (x_m + 13, y_m + 8)],
        )

        superficie_mana = y_m + 39 - int(nivel * 19)
        pygame.draw.polygon(
            self.mundo, (92, 105, 255),
            [(x_m + 7, superficie_mana + 3),
             (x_m + 12, superficie_mana),
             (x_m + 22, superficie_mana),
             (x_m + 27, superficie_mana + 3),
             (x_m + 27, y_m + 34), (x_m + 23, y_m + 39),
             (x_m + 11, y_m + 39), (x_m + 7, y_m + 34)],
        )
        pygame.draw.line(
            self.mundo, (165, 205, 255),
            (x_m + 8, y_m + 18), (x_m + 6, y_m + 29), 2,
        )
        pygame.draw.line(
            self.mundo, (205, 225, 255),
            (x_m + 13, y_m + 3), (x_m + 21, y_m + 3), 2,
        )
        pygame.draw.rect(
            self.mundo, (95, 65, 155),
            (x_m + 11, y_m - 2, 12, 5),
        )
        pygame.draw.rect(
            self.mundo, (205, 175, 255),
            (x_m + 10, y_m - 3, 14, 2),
        )

        self._texto_centrado_mundo(str(mana), self.f["chica"], BLANCO,
                                   x_m + w_m // 2, y_m + 24)

        self._texto_ui(f"/{mana_max}", self.f["mini"], (180, 180, 200),
                       int((x_m + w_m - 8) * self.e),
                       int((y_m + 21) * self.e))

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
                       btn_reiniciar, btn_siguiente, btn_siguiente_nivel=None,
                       emote_rival=None, emote_jugador=None,
                       emote_activo=False, quien_recibio_dano=None,
                       hp_img=None, mesa_img=None, reversos_img=None,
                       posiciones_jugador=None,
                       escalas_jugador=None,
                       foco_mano=None,
                       foco_objetivo=None,
                       slots_rival_objetivo=None,
                       hechizo_seleccionado=None,
                       rects_cartas_rival_clickeables=None,
                       mensaje_hechizo=None,
                       carta_vision_idx=None,
                       vision_activa_hasta=0,
                       foco_teclado=0,
                       factor_espaciado_rival=1):
        self.fondo_tablero = None
        self.mundo.fill((0, 0, 0, 0) if mesa_img is not None else COLOR_FONDO_BARRA)

        if mesa_img is not None:
            if mesa_img is not self._mesa_imagen_original:
                self._mesa_imagen_original = mesa_img
                self._mesa_imagen_escalada = pygame.transform.smoothscale(
                    mesa_img, (ANCHO, ALTO),
                )
            self.fondo_tablero = self._mesa_imagen_escalada

        ancho_m = self.mundo.get_width()
        alto_m = self.mundo.get_height()

        # --- HP con puntos minimalistas en arco diagonal ---
        TAM_NORMAL = 140
        TAM_AGRANDADO = 200
        MARGEN_X = 10
        MARGEN_Y_BASE = 50
        
        tam = TAM_AGRANDADO if emote_activo else TAM_NORMAL
        offset_flote = math.sin(self.tiempo * 0.002) * 6

        # Rival: Pivote en el centro del emote, arco apuntando hacia arriba-derecha (-45°)
        rival_cx = MARGEN_X + tam // 2
        rival_cy = MARGEN_Y_BASE + tam // 2 + int(offset_flote)
        self.dibujar_puntos_hp(
            rival_cx, rival_cy,
            juego.hp_enemigo, juego.hp_enemigo_max,
            (220, 40, 40),          # Rojo base
            cantidad=6, radio=5, radio_arco=75,
            angulo_centro=-45.0     # <-- Abarca de abajo-izq a arriba-der
        )

        # Jugador: Pivote en el centro del emote, arco apuntando hacia arriba-izquierda (-135°)
        jugador_cx = self.ui.get_width() - tam // 2 - MARGEN_X
        jugador_cy = self.ui.get_height() - MARGEN_Y_BASE - tam // 2 + int(offset_flote)
        self.dibujar_puntos_hp(
            jugador_cx, jugador_cy,
            juego.hp_jugador, juego.hp_jugador_max,
            (0, 144, 248),          # Azul base
            cantidad=6, radio=5, radio_arco=75,
            angulo_centro=-135.0    # <-- Abarca de abajo-der a arriba-izq
        )

        # --- Mana (abajo derecha) ---
        mana_disponible = getattr(juego, "mana_jugador", 0)
        self.dibujar_mana(ancho_m - 46, alto_m - 100, mana_disponible, 14)

        # --- Vision activa? ---
        ahora_ms = pygame.time.get_ticks()
        vision_activa = (vision_activa_hasta > ahora_ms
                         and carta_vision_idx is not None)

        # --- Abanico del rival ---
        cantidad_e = len(rects_enemigo)

        esperando_target = hechizo_seleccionado is not None
        intensidad = 0.5 + 0.5 * math.sin(self.tiempo * 0.01)
        color_resaltado = (int(255 * intensidad), int(200 + 55 * intensidad), 0)
        posiciones_rival = Layout.posiciones_rival(
            cantidad_e, ancho_m, factor_espaciado_rival,
        )
        slots_rival_objetivo = slots_rival_objetivo or []
        foco_visual_objetivo = (
            slots_rival_objetivo[foco_objetivo]
            if foco_objetivo is not None
            and 0 <= foco_objetivo < len(slots_rival_objetivo)
            else None
        )

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
                cx, cy = posiciones_rival[i]

                cy_ola = cy + self._offset_ola(cx)

                idx_real = rects_enemigo[i][0]
                mostrar_vision = vision_activa and idx_real == carta_vision_idx

                if mostrar_vision and reversos_img is not None:
                    carta_rival = juego.mazo_enemigo.cartas[idx_real]
                    self.dibujar_carta(cx - Layout.CARTA_W // 2,
                                       cy_ola - Layout.CARTA_H // 2,
                                       carta_rival, COLOR_ENEMIGO,
                                       destacada=True)
                else:
                    if reversos_img and len(reversos_img) > 0:
                        reverso_actual = reversos_img[pos_visual % len(reversos_img)]
                    else:
                        reverso_actual = None

                    surf = self._superficie_dorso(reverso_actual, pos_visual)
                    self.dibujar_carta_rotada(cx, cy_ola, surf, angulos[i])

                    if esperando_target and i in slots_rival_objetivo:
                        rect_rival = next(
                            rect for target_idx, rect
                            in rects_cartas_rival_clickeables
                            if slots_rival_objetivo[target_idx] == i
                        )
                        pygame.draw.rect(
                            self.ui, color_resaltado, rect_rival, 3,
                        )
                        if i == foco_visual_objetivo:
                            pygame.draw.rect(
                                self.ui, (100, 255, 255),
                                rect_rival.inflate(-8, -8), 4,
                            )

        # --- Mano del jugador ---
        carta_hover = None
        rect_hover = None

        if posiciones_jugador is not None and len(posiciones_jugador) > 0 and len(posiciones_jugador) == len(rects_jugador):
            cantidad = len(rects_jugador)
            escalas_mano = escalas_jugador
            if escalas_mano is None:
                cartas_mano = [
                    juego.mazo_jugador.cartas[idx_real]
                    for idx_real, _ in rects_jugador
                ]
                _, escalas_mano = Layout.distribucion_mano(
                    cartas_mano, ancho_m, alto_m,
                    reservar_hueco=juego.carta_jugada_jugador is not None,
                )

            orden = list(range(cantidad))
            idx_hover = -1
            for i in reversed(orden):
                idx_real, rect = rects_jugador[i]
                if rect.collidepoint(mouse) and juego.turno in (Turno.JUGADOR_TIRA, Turno.JUGADOR_HECHIZOS):
                    idx_hover = i
                    carta_hover = juego.mazo_jugador.cartas[idx_real]
                    rect_hover = rect
                    break

            for i in orden:
                idx_real, rect = rects_jugador[i]
                carta = juego.mazo_jugador.cartas[idx_real]
                cx, cy, angulo = posiciones_jugador[i]

                es_hover = (i == idx_hover) or (foco_mano == i)
                
                if foco_mano == i and carta_hover is None:
                    carta_hover = carta
                    rect_hover = rect

                if es_hover:
                    cy -= HOVER_LEVANTAR
                cy += math.sin(self.tiempo * 0.002 + i * 0.9) * 1.5

                es_seleccionada = (hechizo_seleccionado is not None
                                   and idx_real == hechizo_seleccionado)

                self._dibujar_carta_abanico(
                    cx, cy, carta, angulo,
                    hover=es_hover,
                    seleccionada=es_seleccionada,
                    escala_base=escalas_mano[i],
                )
                
        # --- Zona de duelo ---
        cx_duelo = ancho_m // 2
        cy_duelo = Layout.Y_CENTRO_DUELO

        if (juego.carta_jugada_enemigo is not None
                and 0 <= juego.carta_jugada_enemigo < len(juego.mazo_enemigo.cartas)):
            ce = juego.mazo_enemigo[juego.carta_jugada_enemigo]
            x = cx_duelo - Layout.CARTA_W // 2
            y = cy_duelo - Layout.CARTA_H - Layout.DUELO_SEP_Y - 2
            self.dibujar_carta(x, y, ce, COLOR_ENEMIGO, destacada=True)

        if (juego.carta_jugada_jugador is not None
                and 0 <= juego.carta_jugada_jugador < len(juego.mazo_jugador.cartas)):
            cj = juego.mazo_jugador[juego.carta_jugada_jugador]
            if getattr(cj, "tipo", "criatura") == "criatura":
                x = cx_duelo - Layout.CARTA_W // 2
                y = cy_duelo + Layout.DUELO_SEP_Y
                self.dibujar_carta(x, y, cj, COLOR_JUGADOR, destacada=True)

        if juego.carta_jugada_enemigo is not None or juego.carta_jugada_jugador is not None:
            self._texto_centrado_mundo("VS", self.f["chica"], AMARILLO,
                                       cx_duelo, Layout.Y_VS)

        # --- Tooltip ---
        if carta_hover is not None and rect_hover is not None:
            self.dibujar_tooltip(carta_hover, rect_hover.x, rect_hover.y)

        # --- Mensaje de hechizo ---
        if mensaje_hechizo:
            self._texto_centrado_ui(
                mensaje_hechizo.replace("zz ", ""),
                self.f["chica"], AMARILLO,
                ANCHO // 2, ALTO - 40
            )

        if esperando_target:
            self._texto_centrado_ui(
                "Elegi una carta del rival",
                self.f["chica"], (255, 230, 100),
                ANCHO // 2, ALTO - 70
            )

        # --- Botones ---
        if btn_reiniciar is not None:
            hover_re = btn_reiniciar.collidepoint(mouse)
            self.dibujar_boton(btn_reiniciar, "REINICIAR", hover_re,
                               COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF)

        if btn_siguiente is not None and juego.turno == Turno.RESULTADO:
            hover_sig = btn_siguiente.collidepoint(mouse)
            self.dibujar_boton(btn_siguiente, "CONTINUAR", hover_sig,
                               COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF)

        # --- Mensajes de estado ---
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

        # ==================================================
        # PANTALA DE GANADOR 
        # ==================================================
        if juego.hp_enemigo <= 0:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.ui.blit(overlay, (0, 0))

            self._texto_centrado_ui("¡VICTORIA!", self.f["grande"], AMARILLO, ANCHO // 2, ALTO // 2 - 40)
            self._texto_centrado_ui("Has derrotado a tu rival", self.f["chica"], BLANCO, ANCHO // 2, ALTO // 2 + 10)