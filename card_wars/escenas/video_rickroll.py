# escenas/video_rickroll.py
import pygame
import cv2
import os
from config import ANCHO, ALTO, DIRECTORIO_RAIZ
from escenas.base import Escena

class EscenaVideoRickroll(Escena):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        
        # Ruta del video ajustada a tu estructura de carpetas
        self.ruta_video = os.path.join(DIRECTORIO_RAIZ, "assets", "videos", "pvp.mp4")
        
        # Cargar video
        self.cap = None
        self.delay_frame = 33 # ~30 fps por defecto
        self.ultimo_frame_ms = 0
        
        if os.path.exists(self.ruta_video):
            self.cap = cv2.VideoCapture(self.ruta_video)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            if fps and fps > 0:
                self.delay_frame = 1000 / fps
        else:
            print(f"[video] No se encontró el video en: {self.ruta_video}")
            # Si no hay video, volvemos al menú
            from escenas.menu import EscenaMenu
            self.app.cambiar_escena(EscenaMenu(self.app))

    def handle_event(self, evento, mouse):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self._volver_al_menu()
        if evento.type == pygame.MOUSEBUTTONDOWN:
            self._volver_al_menu()

    def update(self, dt):
        pass

    def draw(self):
        # Fondo negro
        self.render.ui.fill((0, 0, 0))
        
        if self.cap and self.cap.isOpened():
            ahora = pygame.time.get_ticks()
            # Solo avanzamos de frame si pasó el tiempo correspondiente
            if ahora - self.ultimo_frame_ms >= self.delay_frame:
                ret, frame = self.cap.read()
                if ret:
                    # Convertir BGR (OpenCV) a RGB (Pygame)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Redimensionar al tamaño de la ventana
                    frame = cv2.resize(frame, (ANCHO, ALTO))
                    
                    # Convertir a superficie de Pygame y dibujar
                    surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                    self.render.ui.blit(surf, (0, 0))
                    self.ultimo_frame_ms = ahora
                else:
                    # El video terminó, loopeamos
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def _volver_al_menu(self):
        if self.cap:
            self.cap.release()
        from escenas.menu import EscenaMenu
        self.app.cambiar_escena(EscenaMenu(self.app))