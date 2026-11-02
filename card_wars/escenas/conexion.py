# escenas/conexion.py
import os
import math
import socket
import threading
import pygame
from config import (
    ANCHO, ALTO, TITULO, Botones, DIRECTORIO_RAIZ, ESCALA_PIXEL
)
from escenas.base import Escena
from vista.colores import NEGRO, BLANCO, AMARILLO, GRIS, VERDE, ROJO

# Rutas de las imágenes del fondo (las mismas del menú)
RUTA_COLINA_FRENTE = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "colina1.png")
RUTA_COLINA_MEDIO  = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "colina2.png")
RUTA_COLINA_FONDO  = os.path.join(DIRECTORIO_RAIZ, "assets", "imagenes", "colina3.png")

# Configuración de las capas del fondo
FONDO_ZOOM        = 1.25
FONDO_VELOCIDAD   = 0.0001
FONDO_OFFSET_X    = 0
FONDO_OFFSET_Y    = 0

MEDIO_ZOOM        = 1.25
MEDIO_VELOCIDAD   = 0.0002
MEDIO_OFFSET_X    = 25
MEDIO_OFFSET_Y    = -100

FRENTE_ZOOM       = 1.5
FRENTE_VELOCIDAD  = 0.00009
FRENTE_OFFSET_X   = 0
FRENTE_OFFSET_Y   = -320

SUBRAYADO_DURACION = 2.0
ESCALA_SELECCIONADO = 1.4


class EscenaConexion(Escena):
    def __init__(self, app):
        super().__init__(app)
        
        # --- Estado de la conexión ---
        self.estado = "menu" # "menu", "esperando", "conectado", "error", "ingresando_ip"
        self.mensaje = "Elegi una opcion"
        self.puerto = 5555
        
        # --- Variables para el Host ---
        self.es_host = False
        self.ip_local_host = ""
        
        # --- Variables para el Cliente ---
        self.ip_input = ""  # IP que escribe el cliente
        self.conexion = None
        
        # --- Botones con el mismo estilo del menú ---
        w = Botones.MENU_W * ESCALA_PIXEL
        h = Botones.MENU_H * ESCALA_PIXEL
        sep = Botones.MENU_ESPACIO_Y * ESCALA_PIXEL
        margen_x = Botones.MENU_X_MARGEN * ESCALA_PIXEL
        margen_y = Botones.MENU_Y_MARGEN * ESCALA_PIXEL

        claves = ["host", "cliente", "volver"]
        textos = ["CREAR SALA (HOST)", "UNIRSE (CLIENTE)", "VOLVER"]
        n = len(claves)

        y_ultimo = ALTO - margen_y - h

        self.botones = []
        for i in range(n):
            y_px = y_ultimo - (n - 1 - i) * (h + sep)
            x_px = margen_x
            rect = pygame.Rect(x_px, y_px, w, h)
            self.botones.append((claves[i], textos[i], rect))

        self.hover = None
        self.indice = 0
        self.timers_subrayado = [0.0] * len(self.botones)
        self.indice_anterior = 0

        # --- Cargar fondo ---
        self.capa_fondo = self._cargar(RUTA_COLINA_FONDO, "colina3")
        self.capa_medio = self._cargar(RUTA_COLINA_MEDIO, "colina2")
        self.capa_frente = self._cargar(RUTA_COLINA_FRENTE, "colina1")

    def _cargar(self, ruta, nombre):
        if os.path.isfile(ruta):
            try:
                return pygame.image.load(ruta).convert_alpha()
            except Exception as e:
                print(f"[conexion] No se pudo cargar {nombre}: {e}")
        else:
            print(f"[conexion] Imagen NO ENCONTRADA: {ruta}")
        return None

    # ============================================================
    # OBTENER IP LOCAL (TRUCO UDP)
    # ============================================================
    def _obtener_ip_local(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    # ============================================================
    # LÓGICA DE RED
    # ============================================================
    def _iniciar_host(self):
        self.es_host = True
        self.estado = "esperando"
        self.ip_local_host = self._obtener_ip_local()
        
        def esperar():
            try:
                servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                servidor.bind(("0.0.0.0", self.puerto))
                servidor.listen(1)
                self.conexion, addr = servidor.accept()
                self.estado = "conectado"
                self.mensaje = f"Conectado con {addr[0]}!"
                pygame.time.wait(500) 
                self.app.iniciar_video_rickroll()
            except Exception as e:
                self.estado = "error"
                self.mensaje = f"Error al hostear: {e}"
                
        threading.Thread(target=esperar, daemon=True).start()

    def _iniciar_cliente(self):
        # Pasamos a un estado donde el usuario escribe la IP
        self.estado = "ingresando_ip"
        self.ip_input = "127.0.0.1" # Default para probar en la misma PC

    def _conectar_cliente(self, ip):
        self.es_host = False
        self.estado = "esperando"
        self.mensaje = f"Conectando a {ip}:{self.puerto}..."
        
        def conectar():
            try:
                self.conexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.conexion.connect((ip, self.puerto))
                self.estado = "conectado"
                self.mensaje = "Conectado al Host!"
                pygame.time.wait(500)
                self.app.iniciar_video_rickroll()
            except Exception as e:
                self.estado = "error"
                self.mensaje = f"Error al conectar: {e}"
                
        threading.Thread(target=conectar, daemon=True).start()

    # ============================================================
    # MANEJO DE EVENTOS Y DIBUJADO
    # ============================================================
    def handle_event(self, evento, mouse):
        self.hover = None
        
        # --- ESC funciona SIEMPRE ---
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self._accion("volver")
            return

        # --- Input de IP ---
        if self.estado == "ingresando_ip":
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    if self.ip_input.strip():
                        self._conectar_cliente(self.ip_input.strip())
                elif evento.key == pygame.K_BACKSPACE:
                    self.ip_input = self.ip_input[:-1]
                else:
                    # Solo permitir números, puntos y letras (por si usan hostname)
                    if evento.unicode in "0123456789.":
                        self.ip_input += evento.unicode
            return

        # --- Eventos del menú principal ---
        if self.estado == "menu":
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

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for clave, _, rect in self.botones:
                    if rect.collidepoint(mouse):
                        self._accion(clave)
                        break

    def _accion(self, clave):
        if clave == "host":
            self._iniciar_host()
        elif clave == "cliente":
            self._iniciar_cliente()
        elif clave == "volver":
            # Cerramos el socket si estaba abierto para liberar el puerto
            if self.conexion is not None:
                try:
                    self.conexion.close()
                except:
                    pass
                self.conexion = None
            from escenas.menu import EscenaMenu
            self.app.cambiar_escena(EscenaMenu(self.app))

    def _dibujar_capa(self, imagen, zoom, velocidad, fase, offset_x=0, offset_y=0):
        if imagen is None:
            return
        ancho_z = int(ANCHO * zoom)
        alto_z = int(ALTO * zoom)
        img_zoom = pygame.transform.smoothscale(imagen, (ancho_z, alto_z))
        margen_x = ancho_z - ANCHO
        margen_y = alto_z - ALTO
        t = self.app.tiempo_fondo * velocidad + fase
        off_x = (math.sin(t) * 0.5 + 0.5) * 0.30 * margen_x
        off_y = (math.cos(t * 0.7) * 0.5 + 0.5) * 0.20 * margen_y
        self.render.ui.blit(img_zoom, (-int(off_x) + offset_x, -int(off_y) + offset_y))

    def _dibujar_fondo(self):
        self._dibujar_capa(self.capa_fondo, FONDO_ZOOM, FONDO_VELOCIDAD, 0.0, FONDO_OFFSET_X, FONDO_OFFSET_Y)
        self._dibujar_capa(self.capa_medio, MEDIO_ZOOM, MEDIO_VELOCIDAD, 1.3, MEDIO_OFFSET_X, MEDIO_OFFSET_Y)
        self._dibujar_capa(self.capa_frente, FRENTE_ZOOM, FRENTE_VELOCIDAD, 2.7, FRENTE_OFFSET_X, FRENTE_OFFSET_Y)

    def draw(self):
        self.pantalla.fill(NEGRO)
        self._dibujar_fondo()

        # Título
        self.render._texto_mundo(
            "MULTIJUGADOR PVP", self.fuentes["grande"], AMARILLO,
            Botones.MENU_X_MARGEN, 14
        )

        # --- Lógica de dibujado de mensajes según el estado ---
        if self.estado == "menu":
            self.render._texto_centrado_ui(
                self.mensaje, self.fuentes["normal"], BLANCO,
                ANCHO // 2, 250
            )
        elif self.estado == "ingresando_ip":
            self.render._texto_centrado_ui(
                "INGRESA LA IP DEL HOST:", self.fuentes["normal"], BLANCO,
                ANCHO // 2, 250
            )
            # Cuadro de texto para la IP
            pygame.draw.rect(self.render.ui, BLANCO, (ANCHO//2 - 200, 300, 400, 50), 2)
            self.render._texto_centrado_ui(
                self.ip_input, self.fuentes["grande"], AMARILLO,
                ANCHO // 2, 310
            )
            self.render._texto_centrado_ui(
                "Presiona ENTER para conectar, ESC para volver", self.fuentes["mini"], GRIS,
                ANCHO // 2, 380
            )
        elif self.estado == "esperando" and self.es_host:
            self.render._texto_centrado_ui(
                "COMPARTI ESTA IP CON TU AMIGO:", self.fuentes["normal"], BLANCO,
                ANCHO // 2, 250
            )
            self.render._texto_centrado_ui(
                self.ip_local_host, self.fuentes["grande"], VERDE,
                ANCHO // 2, 320
            )
            self.render._texto_centrado_ui(
                f"Puerto: {self.puerto}", self.fuentes["normal"], AMARILLO,
                ANCHO // 2, 400
            )
            self.render._texto_centrado_ui(
                "Esperando conexion...", self.fuentes["mini"], GRIS,
                ANCHO // 2, 460
            )
        else:
            color_msg = VERDE if self.estado == "conectado" else (BLANCO if self.estado == "esperando" else ROJO)
            self.render._texto_centrado_ui(
                self.mensaje, self.fuentes["normal"], color_msg,
                ANCHO // 2, 300
            )

        # Dibujar botones (solo si estamos en el menú de opciones)
        if self.estado == "menu":
            for i, (clave, texto, rect) in enumerate(self.botones):
                seleccionado = (i == self.indice)

                fuente = self.fuentes["mini"]
                surf = fuente.render(texto, False, BLANCO)

                if seleccionado:
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

                if seleccionado:
                    progreso = self.timers_subrayado[i]
                    ancho_total = surf.get_width()
                    ancho_actual = int(ancho_total * progreso)
                    if ancho_actual > 0:
                        x_sub = cx - ancho_total // 2
                        y_sub = y + surf.get_height() + 4
                        pygame.draw.rect(self.render.ui, BLANCO, (x_sub, y_sub, ancho_actual, 3))

        # Instrucción de ESC
        self.render._texto_centrado_ui(
            "ESC para volver", self.fuentes["chica"], GRIS,
            ANCHO // 2, ALTO - 30
        )

    def update(self, dt):
        self.app.tiempo_fondo += dt

        if self.indice != self.indice_anterior:
            self.timers_subrayado[self.indice_anterior] = 0.0
            self.indice_anterior = self.indice

        for i in range(len(self.botones)):
            if i == self.indice and self.estado == "menu":
                self.timers_subrayado[i] = min(
                    self.timers_subrayado[i] + dt / (SUBRAYADO_DURACION * 150.0),
                    1.0
                )
            else:
                self.timers_subrayado[i] = 0.0