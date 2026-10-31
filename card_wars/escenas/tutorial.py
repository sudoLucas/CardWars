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

# Rutas de imagenes y sonidos
RUTA_MUSICA_TUTORIAL = os.path.join(DIRECTORIO_RAIZ, "assets", "sfx", "tutorialSL.mp3")
RUTA_HP = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "HP.png")
RUTA_MESA = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "panio.png")
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
        self.escalas_jugador = []
        self.rects_enemigo = []
        self.rects_cartas_rival_clickeables = []
        self.slots_rival_objetivo = []
        self.mouse = (0, 0)
        self.foco_teclado = 0
        self.foco_zona = "mano"
        self.foco_objetivo = 0

        self.hechizo_seleccionado = None
        self.animacion_target_inicio = None
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
        PANEL_H_M = 65
        PANEL_X_M = 5
        PANEL_Y_M = 45
        
        self.panel_rect = pygame.Rect(
            PANEL_X_M * ESCALA_PIXEL,
            PANEL_Y_M * ESCALA_PIXEL,
            PANEL_W_M * ESCALA_PIXEL,
            PANEL_H_M * ESCALA_PIXEL
        )

        self._calcular_rects()

    def on_enter(self):
        """Arranca la musica del tutorial al entrar."""
        self.app.cambiar_musica(RUTA_MUSICA_TUTORIAL)

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

        vivas_j = [
            (i, carta)
            for i, carta in enumerate(self.juego.mazo_jugador.cartas)
            if carta.viva and i != self.juego.carta_jugada_jugador
        ]
        cartas_mano = [carta for _, carta in vivas_j]
        self.posiciones_jugador, self.escalas_jugador = (
            Layout.distribucion_mano(
                cartas_mano, ancho_m, ALTO // e,
                reservar_hueco=self.juego.carta_jugada_jugador is not None,
            )
        )

        self.rects_jugador = []
        for pos, (idx_real, carta) in enumerate(vivas_j):
            if pos >= len(self.posiciones_jugador):
                break
            cx_m, cy_m, _ = self.posiciones_jugador[pos]
            escala = self.escalas_jugador[pos]
            w = int(Layout.CARTA_W * escala * e)
            h = int(Layout.CARTA_H * escala * e)
            rect = pygame.Rect(
                int(cx_m * e - w // 2),
                int(cy_m * e - h // 2),
                w,
                h,
            )
            self.rects_jugador.append((idx_real, rect))

        vivas_e = [
            (i, carta)
            for i, carta in enumerate(self.juego.mazo_enemigo.cartas)
            if carta.viva
        ]
        self.rects_enemigo = [(idx_real, pygame.Rect(0, 0, 0, 0))
                              for idx_real, _ in vivas_e]

        posiciones = Layout.posiciones_rival(
            len(vivas_e), ancho_m, self._factor_espaciado_rival(),
        )
        indices_objetivo = {
            indice: objetivo
            for objetivo, (indice, _) in enumerate(
                self.juego._cartas_rivales_objetivo()
            )
        }
        self.rects_cartas_rival_clickeables = []
        self.slots_rival_objetivo = []
        for visual, ((indice_real, _), (cx_m, cy_m)) in enumerate(
            zip(vivas_e, posiciones)
        ):
            if indice_real not in indices_objetivo:
                continue
            cx = cx_m * e
            cy = cy_m * e
            rect = pygame.Rect(cx - 60, cy - 60, 120, 120)
            self.rects_cartas_rival_clickeables.append(
                (indices_objetivo[indice_real], rect),
            )
            self.slots_rival_objetivo.append(visual)

        if self.rects_jugador:
            self.foco_teclado = min(self.foco_teclado, len(self.rects_jugador) - 1)
        else:
            self.foco_teclado = 0
        if self.rects_cartas_rival_clickeables:
            objetivos = [idx for idx, _ in self.rects_cartas_rival_clickeables]
            if self.foco_objetivo not in objetivos:
                self.foco_objetivo = objetivos[0]
        elif self.foco_zona == "objetivo":
            self.foco_zona = "mano"

    def _factor_espaciado_rival(self):
        if self.hechizo_seleccionado is None or self.animacion_target_inicio is None:
            return 1
        carta = self.juego.mazo_jugador[self.hechizo_seleccionado]
        if HECHIZOS.get(carta.hechizo_id, {}).get("target") != "carta_rival":
            return 1
        elapsed = pygame.time.get_ticks() - self.animacion_target_inicio
        return Layout.factor_animacion_objetivo(elapsed)

    def _seleccionar_hechizo_target(self, idx_hechizo):
        self.hechizo_seleccionado = idx_hechizo
        self.animacion_target_inicio = pygame.time.get_ticks()
        self.foco_zona = "objetivo"
        if self.rects_cartas_rival_clickeables:
            self.foco_objetivo = self.rects_cartas_rival_clickeables[0][0]

    def _mover_foco_objetivo(self, dx, dy):
        rects = dict(self.rects_cartas_rival_clickeables)
        actual = rects.get(self.foco_objetivo)
        if actual is None:
            if self.rects_cartas_rival_clickeables:
                self.foco_objetivo = self.rects_cartas_rival_clickeables[0][0]
            return

        cx, cy = actual.center
        candidatos = []
        for indice, rect in self.rects_cartas_rival_clickeables:
            if indice == self.foco_objetivo:
                continue
            vx, vy = rect.centerx - cx, rect.centery - cy
            avance = vx * dx + vy * dy
            if avance > 0:
                lateral = abs(vx * dy - vy * dx)
                candidatos.append((lateral + avance * 0.2, indice))
        if candidatos:
            self.foco_objetivo = min(candidatos)[1]
        else:
            self.foco_objetivo = min(
                (
                    (rect.centerx - cx) * dx + (rect.centery - cy) * dy,
                    indice,
                )
                for indice, rect in self.rects_cartas_rival_clickeables
            )[1]

    def _confirmar_foco_teclado(self):
        if self.foco_zona == "objetivo":
            self.juego.usar_hechizo(
                self.hechizo_seleccionado,
                target_idx=self.foco_objetivo,
            )
            self.hechizo_seleccionado = None
            self.animacion_target_inicio = None
            self.foco_zona = "mano"
            self._calcular_rects()
            return

        if self.foco_zona == "mesa":
            if self._inmovilizar_pendiente():
                self.paso_dialogo = len(
                    DIALOGOS_TUTORIAL[self.ronda_tutorial]
                ) - 1
                return
            self.juego.iniciar_duelo()
            self.tiempo_resolucion = pygame.time.get_ticks()
            self.foco_zona = "mano"
            return

        if not self.rects_jugador:
            self._avanzar_dialogo()
            return
        idx, _ = self.rects_jugador[self.foco_teclado]
        carta = self.juego.mazo_jugador[idx]
        if self.juego.turno == Turno.JUGADOR_TIRA:
            if getattr(carta, "tipo", "criatura") == "criatura":
                self.juego.jugador_tira_carta(idx)
                self.foco_zona = "mesa"
                self._calcular_rects()
        elif (self.juego.turno == Turno.JUGADOR_HECHIZOS
              and getattr(carta, "tipo", "criatura") == "hechizo"
              and self._hechizos_habilitados()):
            if not self.juego.hechizo_es_usable(idx):
                self.juego.usar_hechizo(idx, target_idx=None)
                return
            target = HECHIZOS[carta.hechizo_id].get("target", "")
            if target == "carta_rival":
                if self.juego.hechizo_es_usable(idx):
                    self._seleccionar_hechizo_target(idx)
            else:
                self.juego.usar_hechizo(idx, target_idx=None)
                self._calcular_rects()

    def _cancelar_foco_teclado(self):
        if self.hechizo_seleccionado is not None:
            self.hechizo_seleccionado = None
            self.animacion_target_inicio = None
            self.foco_zona = "mano"
            return True
        if self.foco_zona == "mesa":
            self.foco_zona = "mano"
            return True
        return False

    def handle_event(self, evento, mouse):
        self.mouse = mouse

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if self._cancelar_foco_teclado():
                    return
                from escenas.dificultad import EscenaDificultad
                self.app.cambiar_escena(EscenaDificultad(self.app))
                return
            if evento.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                self._cancelar_foco_teclado()
                return
            if evento.key in (pygame.K_a, pygame.K_LEFT):
                if self.foco_zona == "objetivo":
                    self._mover_foco_objetivo(-1, 0)
                elif self.foco_zona == "mano" and self.rects_jugador:
                    self.foco_teclado = (self.foco_teclado - 1) % len(self.rects_jugador)
                return
            if evento.key in (pygame.K_d, pygame.K_RIGHT):
                if self.foco_zona == "objetivo":
                    self._mover_foco_objetivo(1, 0)
                elif self.foco_zona == "mano" and self.rects_jugador:
                    self.foco_teclado = (self.foco_teclado + 1) % len(self.rects_jugador)
                return
            if evento.key in (pygame.K_w, pygame.K_UP):
                if self.foco_zona == "objetivo":
                    self._mover_foco_objetivo(0, -1)
                elif (self.foco_zona == "mano"
                      and self.juego.turno == Turno.JUGADOR_HECHIZOS
                      and self.juego.carta_jugada_jugador is not None):
                    self.foco_zona = "mesa"
                return
            if evento.key in (pygame.K_s, pygame.K_DOWN):
                if self.foco_zona == "objetivo":
                    self._mover_foco_objetivo(0, 1)
                elif self.foco_zona == "mesa" and self.rects_jugador:
                    self.foco_zona = "mano"
                return
            if evento.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_z):
                self._confirmar_foco_teclado()
                return

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 3:
                self._cancelar_foco_teclado()
                return
            if evento.button != 1:
                return

            # Click en el panel izquierdo -> Avanzar
            if self.panel_rect.collidepoint(mouse):
                self._avanzar_dialogo()
                return

            if (self.hechizo_seleccionado is not None
                    and not self._hechizos_habilitados()):
                self.hechizo_seleccionado = None
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
                            self.animacion_target_inicio = None
                            self.foco_zona = "mano"
                            self._calcular_rects()
                            return
                    self.hechizo_seleccionado = None
                    self.animacion_target_inicio = None
                    self.foco_zona = "mano"
                    self._calcular_rects()
                    return
                else:
                    self.juego.usar_hechizo(self.hechizo_seleccionado, target_idx=None)
                    self.hechizo_seleccionado = None
                    self.animacion_target_inicio = None
                    self.foco_zona = "mano"
                    self._calcular_rects()
                    return

            # Click en tu criatura en la mesa -> pelear
            rect_mesa = self._rect_criatura_mesa()
            if rect_mesa is not None and rect_mesa.collidepoint(mouse):
                if self._inmovilizar_pendiente():
                    dialogos = DIALOGOS_TUTORIAL.get(self.ronda_tutorial, [])
                    self.paso_dialogo = len(dialogos) - 1
                    return
                self.juego.iniciar_duelo()
                self.tiempo_resolucion = pygame.time.get_ticks()
                self.foco_zona = "mano"
                return

            # Click en las cartas de tu mano
            for idx, rect in self._cartas_mano_en_orden_de_clic():
                if rect.collidepoint(mouse):
                    carta = self.juego.mazo_jugador[idx]
                    if getattr(carta, "tipo", "criatura") == "hechizo":
                        if not self._hechizos_habilitados():
                            return
                        data = HECHIZOS.get(carta.hechizo_id, {})
                        target = data.get("target", "")
                        if target == "carta_rival":
                            if self.juego.hechizo_es_usable(idx):
                                self.foco_teclado = next(
                                    (pos for pos, (real, _) in enumerate(self.rects_jugador)
                                     if real == idx),
                                    self.foco_teclado,
                                )
                                self._seleccionar_hechizo_target(idx)
                        else:
                            self.foco_teclado = next(
                                (pos for pos, (real, _) in enumerate(self.rects_jugador)
                                 if real == idx),
                                self.foco_teclado,
                            )
                            self.juego.usar_hechizo(idx, target_idx=None)
                            self._calcular_rects()
                    else:
                        self.foco_teclado = next(
                            (pos for pos, (real, _) in enumerate(self.rects_jugador)
                             if real == idx),
                            self.foco_teclado,
                        )
                        self.juego.jugador_tira_carta(idx)
                        self.foco_zona = "mesa"
                        self._calcular_rects()
                    return

    def _cartas_mano_en_orden_de_clic(self):
        return list(reversed(self.rects_jugador))

    def _rect_criatura_mesa(self):
        if self.juego.carta_jugada_jugador is None:
            return None
        
        e = ESCALA_PIXEL
        cx_duelo = (ANCHO // e) // 2
        cy_duelo = Layout.Y_CENTRO_DUELO
        
        x_m = cx_duelo - Layout.CARTA_W // 2
        y_m = cy_duelo + Layout.DUELO_SEP_Y
        
        # Cubre el desplazamiento de flotacion e inclinacion de la carta.
        margen = 5 * e
        return pygame.Rect(
            x_m * e - margen,
            y_m * e - margen,
            Layout.CARTA_W * e + margen * 2,
            Layout.CARTA_H * e + margen * 2,
        )

    def _hechizos_habilitados(self):
        return self.ronda_tutorial >= 2

    def _inmovilizar_pendiente(self):
        if self.ronda_tutorial not in (3, 4):
            return False
        return any(
            carta.viva and carta.hechizo_id == "inmovilizar"
            for carta in self.juego.mazo_jugador.cartas
            if getattr(carta, "tipo", "criatura") == "hechizo"
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
                    self.hechizo_seleccionado = None
                    self.animacion_target_inicio = None
                    self.foco_zona = "mano"
                    self.foco_objetivo = 0
                    self._calcular_rects()

    def draw(self):
        # Le pasamos las imagenes para que use el mismo render que el juego
        self.render.dibujar_escena(
            self.juego, self.rects_jugador, self.rects_enemigo, self.mouse,
            None, None,
            emote_rival=None,
            emote_jugador=None,
            emote_activo=False,
            quien_recibio_dano=None,
            hp_img=self.hp_img,
            mesa_img=self.mesa_img,
            reversos_img=self.reversos_img,
            posiciones_jugador=self.posiciones_jugador,
            escalas_jugador=self.escalas_jugador,
            foco_mano=self.foco_teclado if self.foco_zona == "mano" else None,
            foco_objetivo=self.foco_objetivo if self.foco_zona == "objetivo" else None,
            slots_rival_objetivo=self.slots_rival_objetivo,
            hechizo_seleccionado=self.hechizo_seleccionado,
            rects_cartas_rival_clickeables=self.rects_cartas_rival_clickeables,
            mensaje_hechizo=None,
            carta_vision_idx=self.juego.carta_vision_idx,
            vision_activa_hasta=self.juego.vision_activa_hasta,
            factor_espaciado_rival=self._factor_espaciado_rival(),
        )

        # Dibujamos el panel de dialogo encima
        pygame.draw.rect(self.render.ui, (20, 20, 30, 230), self.panel_rect)
        pygame.draw.rect(self.render.ui, (200, 200, 200), self.panel_rect, 2)

        dialogos = DIALOGOS_TUTORIAL.get(self.ronda_tutorial, [])
        if 0 <= self.paso_dialogo < len(dialogos):
            texto = dialogos[self.paso_dialogo].replace("zz ", "")

            font = self.fuentes["mini"]
            palabras = texto.split()
            lineas = []
            linea_actual = ""
            area_texto = self.panel_rect.inflate(-20, -52)
            
            for p in palabras:
                test_linea = f"{linea_actual} {p}".strip()
                if font.size(test_linea)[0] <= area_texto.width:
                    linea_actual = test_linea
                else:
                    if linea_actual:
                        lineas.append(linea_actual)
                    linea_actual = p
            if linea_actual:
                lineas.append(linea_actual)

            clip_anterior = self.render.ui.get_clip()
            self.render.ui.set_clip(area_texto)
            y_offset = area_texto.y
            for linea in lineas:
                if y_offset + font.get_height() > area_texto.bottom:
                    break
                self.render._texto_ui(
                    linea, font, (220, 220, 220),
                    area_texto.x, y_offset,
                )
                y_offset += font.get_height() + 4
            self.render.ui.set_clip(clip_anterior)

            self.render._texto_ui("click", self.fuentes["mini"], (140, 140, 140),
                                  self.panel_rect.x + 10, self.panel_rect.bottom - 20)