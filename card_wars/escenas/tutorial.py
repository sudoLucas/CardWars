# escenas/tutorial.py
import os
import pygame
from config import (
    ANCHO, ALTO, Layout, Turno, ESCALA_PIXEL, DUELO_DURACION,
    get_dificultad, DIALOGOS_TUTORIAL, TUTORIAL_ROUNDS, HECHIZOS,
    DIRECTORIO_RAIZ,
)
from escenas.base import Escena
from modelo.juego import Juego


DELAY_IA_TIRA = 800

# Rutas de imagenes
RUTA_HP = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "HP.png")
RUTA_MESA = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "mesa.png")
CARPETA_REVERSOS = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "Objetos", "cartas")


class EscenaTutorial(Escena):
    def __init__(self, app):
        super().__init__(app)
        self.dificultad = get_dificultad("tutorial")
        self.juego = Juego(self.dificultad)
        self.tiempo_fase = pygame.time.get_ticks()
        self.tiempo_resolucion = 0
        self.paso_dialogo = 0
        self.ronda_tutorial = 1

        self.rects_jugador = []
        self.posiciones_jugador = []
        self.rects_enemigo = []
        self.rects_cartas_rival_clickeables = []
        self.mouse = (0, 0)

        self.hechizo_seleccionado = None
        self.mensaje_hechizo_temporal = ""
        self.tiempo_mensaje_hechizo = 0

        # --- Cargar imagenes para que el render se vea igual que en el juego ---
        self.hp_img = self._cargar(RUTA_HP)
        self.mesa_img = self._cargar(RUTA_MESA)
        
        # Elegir 3 reversos random
        numeros = [1, 2, 3] 
        self.reversos_img = []
        for n in numeros:
            ruta = os.path.join(CARPETA_REVERSOS, f"reversoCarta{n}.png")
            img = self._cargar(ruta)
            if img is not None:
                self.reversos_img.append(img)

        # Rect del panel de dialogo (izquierda)
        ancho_m = ANCHO // ESCALA_PIXEL
        alto_m = ALTO // ESCALA_PIXEL
        
        PANEL_W_M = 70
        PANEL_H_M = 110
        PANEL_X_M = 5
        PANEL_Y_M = (alto_m // 2) - (PANEL_H_M // 2)
        
        self.panel_rect = pygame.Rect(
            PANEL_X_M * ESCALA_PIXEL,
            PANEL_Y_M * ESCALA_PIXEL,
            PANEL_W_M * ESCALA_PIXEL,
            PANEL_H_M * ESCALA_PIXEL
        )

        self._calcular_rects()

    def _cargar(self, ruta):
        if os.path.isfile(ruta):
            try:
                return pygame.image.load(ruta).convert_alpha()
            except Exception as e:
                print(f"[tutorial] No se pudo cargar {ruta}: {e}")
        return None

    def _calcular_rects(self):
        e = ESCALA_PIXEL
        ancho_m = ANCHO // e

        vivas_j = [(i, c) for i, c in enumerate(self.juego.mazo_jugador.cartas) if c.viva]
        cantidad_j = len(vivas_j)

        self.posiciones_jugador = []
        if cantidad_j > 0:
            cx_centro = ancho_m // 2
            alto_m = ALTO // e
            cy_centro = alto_m - 2 - (Layout.CARTA_H // 2)
            medio = (cantidad_j - 1) / 2.0
            
            for i in range(cantidad_j):
                dx = (i - medio) * Layout.ABANICO_SEP_X_JUGADOR
                # ACÁ: Coordenadas del mundo (sin * e) para el render
                self.posiciones_jugador.append((
                    (cx_centro + dx), 
                    cy_centro, 
                    0
                ))

        self.rects_jugador = []
        for pos, (idx_real, _) in enumerate(vivas_j):
            if pos >= len(self.posiciones_jugador):
                break
            cx_m, cy_m, _ = self.posiciones_jugador[pos]
            w = Layout.CARTA_W * e
            h = Layout.CARTA_H * e
            # ACÁ: Rect en píxeles reales para los clicks
            rect = pygame.Rect(
                int(cx_m * e - w // 2), 
                int(cy_m * e - h // 2), 
                w, h
            )
            self.rects_jugador.append((idx_real, rect))

        vivas_e = [(i, c) for i, c in enumerate(self.juego.mazo_enemigo.cartas) if c.viva]
        self.rects_enemigo = [(idx_real, pygame.Rect(0, 0, 0, 0))
                              for idx_real, _ in vivas_e]

        self.rects_cartas_rival_clickeables = []
        if len(vivas_e) > 0:
            cx_centro = ancho_m // 2
            cy_centro = Layout.Y_CENTRO_RIVAL
            medio = (len(vivas_e) - 1) / 2.0
            for i in range(len(vivas_e)):
                dist = abs(i - medio)
                dx = (i - medio) * Layout.ABANICO_SEP_X
                dy = dist * Layout.ABANICO_OFFSET_Y
                cx = (cx_centro + int(dx)) * e
                cy = (cy_centro + int(dy)) * e
                rect = pygame.Rect(cx - 60, cy - 60, 120, 120)
                self.rects_cartas_rival_clickeables.append((i, rect))

    def handle_event(self, evento, mouse):
        self.mouse = mouse

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                from escenas.dificultad import EscenaDificultad
                self.app.cambiar_escena(EscenaDificultad(self.app))
                return
            if evento.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.hechizo_seleccionado = None
                return

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 3:
                self.hechizo_seleccionado = None
                return
            if evento.button != 1:
                return

            # Click en el panel izquierdo -> Avanzar
            if self.panel_rect.collidepoint(mouse):
                self._avanzar_dialogo()
                return

            # Click en el hechizo ya seleccionado
            if self.hechizo_seleccionado is not None:
                carta = self.juego.mazo_jugador[self.hechizo_seleccionado]
                data = HECHIZOS.get(carta.hechizo_id, {})
                target = data.get("target", "")
                if target == "carta_rival":
                    for idx_slot, rect_rival in self.rects_cartas_rival_clickeables:
                        if rect_rival.collidepoint(mouse):
                            self.juego.usar_hechizo(self.hechizo_seleccionado, target_idx=idx_slot)
                            self.hechizo_seleccionado = None
                            return
                    self.hechizo_seleccionado = None
                    return
                else:
                    self.juego.usar_hechizo(self.hechizo_seleccionado, target_idx=None)
                    self.hechizo_seleccionado = None
                    return

            # Click en tu criatura en la mesa -> pelear
            rect_mesa = self._rect_criatura_mesa()
            if rect_mesa is not None and rect_mesa.collidepoint(mouse):
                self.juego.iniciar_duelo()
                self.tiempo_resolucion = pygame.time.get_ticks()
                return

            # Click en las cartas de tu mano
            for idx, rect in self.rects_jugador:
                if rect.collidepoint(mouse):
                    carta = self.juego.mazo_jugador[idx]
                    if getattr(carta, "tipo", "criatura") == "hechizo":
                        data = HECHIZOS.get(carta.hechizo_id, {})
                        target = data.get("target", "")
                        if target == "carta_rival":
                            self.hechizo_seleccionado = idx
                        else:
                            self.juego.usar_hechizo(idx, target_idx=None)
                    else:
                        self.juego.jugador_tira_carta(idx)
                    return

    def _rect_criatura_mesa(self):
        if self.juego.carta_jugada_jugador is None:
            return None
        
        e = ESCALA_PIXEL
        # La carta en duelo está en el centro
        cx_duelo = (ANCHO // e) // 2
        cy_duelo = Layout.Y_CENTRO_DUELO
        
        x_m = cx_duelo - Layout.CARTA_W // 2
        y_m = cy_duelo + Layout.DUELO_SEP_Y
        
        # Multiplicamos por la escala
        return pygame.Rect(
            x_m * e, 
            y_m * e, 
            Layout.CARTA_W * e, 
            Layout.CARTA_H * e
        )
    def _avanzar_dialogo(self):
        dialogos = DIALOGOS_TUTORIAL.get(self.ronda_tutorial, [])
        if self.paso_dialogo < len(dialogos) - 1:
            self.paso_dialogo += 1

    def update(self, dt):
        self.render.tick(dt)
        self._calcular_rects()
        ahora = pygame.time.get_ticks()

        if self.juego.turno == Turno.IA_TIRA:
            if ahora - self.tiempo_fase > DELAY_IA_TIRA:
                self.juego.ia_tira_carta()
                self.tiempo_fase = ahora

        if self.juego.turno == Turno.RESULTADO:
            if ahora - self.tiempo_resolucion > DUELO_DURACION:
                if self.ronda_tutorial >= TUTORIAL_ROUNDS:
                    from escenas.dificultad import EscenaDificultad
                    self.app.cambiar_escena(EscenaDificultad(self.app))
                else:
                    self.ronda_tutorial += 1
                    self.paso_dialogo = 0
                    self.juego.siguiente_ronda()
                    self.tiempo_fase = ahora
                    self.tiempo_resolucion = 0

    def draw(self):
        # Le pasamos las imagenes para que use el mismo render que el juego
        self.render.dibujar_escena(
            self.juego, self.rects_jugador, self.rects_enemigo, self.mouse,
            None, None,
            emote_rival=None,
            emote_jugador=None,
            emote_activo=False,
            quien_recibio_dano=None,
            hp_img=self.hp_img,         # <--- Pasamos la imagen
            mesa_img=self.mesa_img,     # <--- Pasamos la imagen
            reversos_img=self.reversos_img, # <--- Pasamos los reversos
            posiciones_jugador=self.posiciones_jugador,
            hechizo_seleccionado=self.hechizo_seleccionado,
            rects_cartas_rival_clickeables=self.rects_cartas_rival_clickeables,
            mensaje_hechizo=None,
            carta_vision_idx=self.juego.carta_vision_idx,
            vision_activa_hasta=self.juego.vision_activa_hasta,
        )

        # Dibujamos el panel de dialogo encima
        pygame.draw.rect(self.render.ui, (20, 20, 30, 230), self.panel_rect)
        pygame.draw.rect(self.render.ui, (200, 200, 200), self.panel_rect, 2)

        dialogos = DIALOGOS_TUTORIAL.get(self.ronda_tutorial, [])
        if 0 <= self.paso_dialogo < len(dialogos):
            texto = dialogos[self.paso_dialogo].replace("zz ", "")
            
            font = self.fuentes["chica"]
            palabras = texto.split(' ')
            lineas = []
            linea_actual = ""
            ancho_max_texto = self.panel_rect.width - 20 
            
            for p in palabras:
                test_linea = linea_actual + p + " "
                if font.size(test_linea)[0] < ancho_max_texto:
                    linea_actual = test_linea
                else:
                    lineas.append(linea_actual)
                    linea_actual = p + " "
            lineas.append(linea_actual)

            y_offset = self.panel_rect.y + 10
            for linea in lineas:
                self.render._texto_ui(linea, font, (220, 220, 220), self.panel_rect.x + 10, y_offset)
                y_offset += font.get_height() + 2

            self.render._texto_ui("click", self.fuentes["mini"], (140, 140, 140),
                                  self.panel_rect.x + 10, self.panel_rect.bottom - 20)