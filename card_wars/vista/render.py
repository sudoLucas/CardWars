# vista/render.py
import math
import pygame
from config import ANCHO, Layout, Turno
from vista.colores import (
    NEGRO, BLANCO, AMARILLO, VERDE, ROJO, GRIS_OSCURO,
    COLOR_JUGADOR, COLOR_JUGADOR_HOVER, COLOR_ENEMIGO,
    COLOR_ENEMIGO_ACTIVA, COLOR_DORSO, COLOR_MUERTA, COLOR_AGUANTE,
    COLOR_FONDO_BARRA, COLOR_LINEA_DUELO, COLOR_INFO,
    COLOR_ETIQ_RIVAL, COLOR_ETIQ_JUGADOR,
    COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF,
    COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF,
)


# ---------- Parametros de la ola ----------
OLA_AMPLITUD   = 4.0
OLA_FRECUENCIA = 0.015
OLA_VELOCIDAD  = 0.005

# ---------- Parametros del abanico ----------
ABANICO_ANGULO    = 5
ABANICO_SEP_X     = 100
ABANICO_OFFSET_Y  = 18


class Render:
    def __init__(self, pantalla, fuentes):
        self.pantalla = pantalla
        self.f = fuentes
        self.tiempo = 0.0

    def tick(self, dt):
        self.tiempo += dt

    # ---------- Helpers ----------
    def _texto_centrado(self, txt, fuente, color, cx, y):
        surf = fuente.render(txt, True, color)
        self.pantalla.blit(surf, (cx - surf.get_width() // 2, y))
        return surf.get_rect(topleft=(cx - surf.get_width() // 2, y))

    def _offset_ola(self, x):
        return math.sin(x * OLA_FRECUENCIA + self.tiempo * OLA_VELOCIDAD) * OLA_AMPLITUD

    # ---------- Superficie de una carta (para poder rotarla) ----------
    def _superficie_carta(self, carta, color_fondo):
        w, h = Layout.CARTA_W, Layout.CARTA_H
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        if not carta.viva:
            color = COLOR_MUERTA
        else:
            color = color_fondo

        pygame.draw.rect(surf, color, (0, 0, w, h), border_radius=10)
        pygame.draw.rect(surf, BLANCO, (0, 0, w, h), 2, border_radius=10)

        nombre = self.f["chica"].render(carta.nombre, True, BLANCO)
        surf.blit(nombre, (8, 6))

        if carta.viva:
            poder_txt = self.f["grande"].render(str(carta.poder), True, AMARILLO)
        else:
            poder_txt = self.f["grande"].render("0", True, (120, 40, 40))
        surf.blit(poder_txt, (w // 2 - poder_txt.get_width() // 2, 40))

        lbl = self.f["chica"].render("zz PODER", True, BLANCO)
        surf.blit(lbl, (w // 2 - lbl.get_width() // 2, 80))

        if carta.viva:
            lbl_a = self.f["chica"].render("zz AGUANTE", True, COLOR_AGUANTE)
            surf.blit(lbl_a, (w // 2 - lbl_a.get_width() // 2, 105))

            max_ag = carta.poder
            ancho_max = w - 24
            ancho_actual = int(ancho_max * carta.aguante / max_ag) if max_ag > 0 else 0
            pygame.draw.rect(surf, COLOR_FONDO_BARRA, (12, 125, ancho_max, 10), border_radius=3)
            pygame.draw.rect(surf, COLOR_AGUANTE, (12, 125, ancho_actual, 10), border_radius=3)

            num_ag = self.f["chica"].render(f"{carta.aguante}/{max_ag}", True, BLANCO)
            surf.blit(num_ag, (w // 2 - num_ag.get_width() // 2, 140))
        else:
            equis = self.f["icono"].render("X", True, (200, 60, 60))
            surf.blit(equis, (w // 2 - equis.get_width() // 2, 115))

        return surf

    def _superficie_dorso(self):
        w, h = Layout.CARTA_W, Layout.CARTA_H
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        pygame.draw.rect(surf, COLOR_DORSO, (0, 0, w, h), border_radius=10)
        pygame.draw.rect(surf, BLANCO, (0, 0, w, h), 2, border_radius=10)

        cx = w // 2
        cy = h // 2
        pulso = 1.0 + 0.08 * math.sin(self.tiempo * 0.004)
        tam = int(30 * pulso)

        # Rombo bordo mas oscuro, para que contraste con el COLOR_DORSO
        pygame.draw.polygon(surf, (60, 15, 25), [
            (cx, cy - tam),
            (cx + tam, cy),
            (cx, cy + tam),
            (cx - tam, cy),
        ])
        pygame.draw.polygon(surf, BLANCO, [
            (cx, cy - tam),
            (cx + tam, cy),
            (cx, cy + tam),
            (cx - tam, cy),
        ], 2)

        return surf

    # ---------- Carta grande (dibujo directo, sin rotar) ----------
    def dibujar_carta(self, x, y, carta, color_fondo, hover=False, resaltada=False, ola=False):
        w, h = Layout.CARTA_W, Layout.CARTA_H
        if ola:
            y = y + self._offset_ola(x)

        if not carta.viva:
            color = COLOR_MUERTA
        elif resaltada:
            color = COLOR_ENEMIGO_ACTIVA
        elif hover:
            color = COLOR_JUGADOR_HOVER
        else:
            color = color_fondo

        pygame.draw.rect(self.pantalla, color, (x, y, w, h), border_radius=10)
        borde = AMARILLO if resaltada else BLANCO
        pygame.draw.rect(self.pantalla, borde, (x, y, w, h), 2, border_radius=10)

        nombre = self.f["chica"].render(carta.nombre, True, BLANCO)
        self.pantalla.blit(nombre, (x + 8, y + 6))

        if carta.viva:
            poder_txt = self.f["grande"].render(str(carta.poder), True, AMARILLO)
        else:
            poder_txt = self.f["grande"].render("0", True, (120, 40, 40))
        self.pantalla.blit(poder_txt, (x + w // 2 - poder_txt.get_width() // 2, y + 40))

        self._texto_centrado("zz PODER", self.f["chica"], BLANCO, x + w // 2, y + 80)

        if carta.viva:
            self._texto_centrado("zz AGUANTE", self.f["chica"], COLOR_AGUANTE, x + w // 2, y + 105)
            max_ag = carta.poder
            ancho_max = w - 24
            ancho_actual = int(ancho_max * carta.aguante / max_ag) if max_ag > 0 else 0
            pygame.draw.rect(self.pantalla, COLOR_FONDO_BARRA,
                             (x + 12, y + 125, ancho_max, 10), border_radius=3)
            pygame.draw.rect(self.pantalla, COLOR_AGUANTE,
                             (x + 12, y + 125, ancho_actual, 10), border_radius=3)
            self._texto_centrado(f"{carta.aguante}/{max_ag}",
                                 self.f["chica"], BLANCO, x + w // 2, y + 140)
        else:
            equis = self.f["icono"].render("X", True, (200, 60, 60))
            self.pantalla.blit(equis, (x + w // 2 - equis.get_width() // 2, y + 115))

        return pygame.Rect(x, y, w, h)

    # ---------- Carta rotada ----------
    def dibujar_carta_rotada(self, cx, cy, surf, angulo, ola=False):
        if ola:
            cy += self._offset_ola(cx)

        rotada = pygame.transform.rotate(surf, angulo)
        rect = rotada.get_rect(center=(cx, cy))
        self.pantalla.blit(rotada, rect)

    # ---------- Barra de HP ----------
    def dibujar_hp(self, x, y, hp, hp_max, etiqueta, color):
        w, h = Layout.HP_BAR_W, Layout.HP_BAR_H
        pygame.draw.rect(self.pantalla, COLOR_FONDO_BARRA, (x, y, w, h), border_radius=6)
        ancho = max(0, int(w * hp / hp_max))
        pygame.draw.rect(self.pantalla, color, (x, y, ancho, h), border_radius=6)
        txt = self.f["normal"].render(f"{etiqueta}: {max(0,hp)} HP", True, BLANCO)
        self.pantalla.blit(txt, (x + w // 2 - txt.get_width() // 2, y + 6))

    # ---------- Mini carta ----------
    def dibujar_mini(self, x, y, carta, color_fondo, activa=False):
        w, h = Layout.MINI_W, Layout.MINI_H
        if not carta.viva:
            color = COLOR_MUERTA
        elif activa:
            color = COLOR_ENEMIGO_ACTIVA
        else:
            color = color_fondo
        pygame.draw.rect(self.pantalla, color, (x, y, w, h), border_radius=8)
        pygame.draw.rect(self.pantalla, BLANCO, (x, y, w, h), 2, border_radius=8)

        nombre = self.f["mini"].render(carta.nombre, True, BLANCO)
        self.pantalla.blit(nombre, (x + 8, y + 5))

        if carta.viva:
            txt = self.f["mini"].render(f"zz P {carta.poder}", True, AMARILLO)
            self.pantalla.blit(txt, (x + 8, y + 27))
            txt2 = self.f["chica"].render(f"zz AGU {carta.aguante}", True, COLOR_AGUANTE)
            self.pantalla.blit(txt2, (x + 8, y + 52))
        else:
            txt = self.f["normal"].render("zz MUERTA", True, (200, 60, 60))
            self.pantalla.blit(txt, (x + 15, y + 28))

    # ---------- Boton ----------
    def dibujar_boton(self, rect, texto, hover, color_on, color_off):
        color = color_on if hover else color_off
        pygame.draw.rect(self.pantalla, color, rect, border_radius=6)
        pygame.draw.rect(self.pantalla, BLANCO, rect, 2, border_radius=6)
        surf = self.f["chica"].render(texto, True, BLANCO)
        self.pantalla.blit(surf, (rect.x + rect.w // 2 - surf.get_width() // 2,
                                  rect.y + rect.h // 2 - surf.get_height() // 2))

    # ---------- Escena completa ----------
    def dibujar_escena(self, juego, rects_jugador, rects_enemigo, mouse,
                       boton_reiniciar, boton_siguiente):
        self.pantalla.fill(NEGRO)

        # HP
        self.dibujar_hp(Layout.HP_BAR_X_IZQ, Layout.HP_BAR_Y,
                        juego.hp_jugador, juego.hp_jugador_max, "zz TU", VERDE)
        self.dibujar_hp(Layout.HP_BAR_X_DER, Layout.HP_BAR_Y,
                        juego.hp_enemigo, juego.hp_enemigo_max, "zz MAQUINA", ROJO)

        # Ronda
        self._texto_centrado(f"zz RONDA {juego.ronda}",
                             self.f["ronda"], AMARILLO, ANCHO // 2, 12)

        # Rebarajes (solo del jugador)
        reb_j = juego.mazo_jugador.rebarajes
        if reb_j:
            self._texto_centrado(
                f"zz Rebarajes - Tu: {reb_j}",
                self.f["chica"], COLOR_INFO, ANCHO // 2, 38)

        # Etiqueta
        self._texto_centrado("zz CARTAS DEL RIVAL",
                             self.f["chica"], COLOR_ETIQ_RIVAL,
                             ANCHO // 2, Layout.Y_CARTAS_RIVAL - 15)

        # ---------- Cartas rival en ABANICO ROTADO (solo las vivas) ----------
        cantidad = len(rects_enemigo)   # solo cartas vivas
        cx_centro = ANCHO // 2
        cy_centro = Layout.Y_CARTAS_RIVAL + Layout.CARTA_H // 2

        # Todas las cartas del abanico son dorsos
        superficies = [self._superficie_dorso() for _ in range(cantidad)]

        if cantidad > 1:
            medio = (cantidad - 1) / 2.0
            angulos = [-ABANICO_ANGULO * (i - medio) / medio for i in range(cantidad)]
        else:
            angulos = [0]

        # Orden: primero las puntas, ultima la del medio (queda encima)
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

        # Linea zona duelo
        pygame.draw.line(self.pantalla, COLOR_LINEA_DUELO,
                         (40, Layout.Y_ZONA_DUELO - 5),
                         (ANCHO - 40, Layout.Y_ZONA_DUELO - 5), 1)

        # Mini cartas
        if juego.carta_jugada_jugador is not None:
            cj = juego.mazo_jugador[juego.carta_jugada_jugador]
            self.dibujar_mini(
                ANCHO // 2 + Layout.MINI_JUGADOR_X_OFFSET,
                Layout.Y_ZONA_DUELO + Layout.MINI_Y_OFFSET,
                cj, COLOR_JUGADOR)

        self._texto_centrado("zz VS", self.f["grande"], AMARILLO,
                             ANCHO // 2, Layout.Y_ZONA_DUELO + 30)

        if juego.carta_jugada_enemigo is not None:
            ce = juego.mazo_enemigo[juego.carta_jugada_enemigo]
            self.dibujar_mini(
                ANCHO // 2 + Layout.MINI_ENEMIGO_X_OFFSET,
                Layout.Y_ZONA_DUELO + Layout.MINI_Y_OFFSET,
                ce, COLOR_ENEMIGO, activa=True)

        # Mensaje
        self._texto_centrado(juego.mensaje, self.f["mensaje"], AMARILLO,
                             ANCHO // 2, Layout.Y_MENSAJE)

        # Etiqueta tus cartas
        self._texto_centrado("zz TUS CARTAS (click para tirar a la mesa)",
                             self.f["chica"], COLOR_ETIQ_JUGADOR,
                             ANCHO // 2, Layout.Y_CARTAS_TU - 15)

        # Cartas jugador (solo vivas, ya filtradas en rects_jugador)
        for idx, rect in rects_jugador:
            carta = juego.mazo_jugador[idx]
            seleccionable = (juego.turno == Turno.JUGADOR and carta.viva)
            hover = seleccionable and rect.collidepoint(mouse)
            self.dibujar_carta(rect.x, rect.y, carta, COLOR_JUGADOR, hover=hover, ola=True)

        # Boton SIGUIENTE RONDA
        if juego.turno == Turno.RESOLVIENDO:
            self.dibujar_boton(boton_siguiente, "zz SIGUIENTE RONDA (ESPACIO)",
                               boton_siguiente.collidepoint(mouse),
                               COLOR_BTN_VERDE, COLOR_BTN_VERDE_OFF)

        # Boton REINICIAR
        self.dibujar_boton(boton_reiniciar, "zz REINICIAR (R)",
                           boton_reiniciar.collidepoint(mouse),
                           COLOR_BTN_AZUL, COLOR_BTN_AZUL_OFF)

        pygame.display.flip()