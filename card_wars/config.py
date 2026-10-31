# config.py
"""
Configuracion global del juego.

SISTEMA DE COORDENADAS:
- El "mundo" mide RESOLUCION_INTERNA_W/ESCALA_PIXEL x RESOLUCION_INTERNA_H/ESCALA_PIXEL.
- Todas las constantes de Layout y Botones estan en unidades del MUNDO.
- El render las dibuja tal cual sobre surface_mundo.
- Los textos van al surface_ui en pixeles reales.

SISTEMA DE VENTANA:
- RESOLUCION_INTERNA es la resolucion del juego (nunca cambia).
- VENTANA_W/H es el tamano de la ventana al abrir.
- Pygame escala la resolucion interna a la ventana con SCALED.
"""

import os
from dataclasses import dataclass
import pygame


# ============================================================
# METADATA
# ============================================================
TITULO  = "Card Wars"
VERSION = "0.3.0"
AUTOR   = ""


# ============================================================
# RUTAS (absolutas, relativas a este archivo)
# ============================================================
DIRECTORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# VENTANA / RENDER
# ============================================================
RESOLUCION_INTERNA_W, RESOLUCION_INTERNA_H = 1200, 800

VENTANA_W, VENTANA_H = 900, 600

ANCHO, ALTO = RESOLUCION_INTERNA_W, RESOLUCION_INTERNA_H

FPS = 60

RUTA_FUENTE = os.path.join(DIRECTORIO_RAIZ, "assets", "fuentes", "pixel.ttf")

ESCALA_PIXEL = 4


def inicializar_ventana():
    """
    Devuelve (ancho_ventana, alto_ventana) para crear la ventana.
    La resolucion INTERNA sigue siendo RESOLUCION_INTERNA_W x RESOLUCION_INTERNA_H.
    Si la ventana pedida no entra en el monitor, la achica.
    """
    info = pygame.display.Info()

    ancho_ventana = min(VENTANA_W, int(info.current_w * 0.90))
    alto_ventana = min(VENTANA_H, int(info.current_h * 0.90))

    return ancho_ventana, alto_ventana


# ============================================================
# ESTADOS
# ============================================================
class Turno:
    IA_TIRA          = "ia_tira"
    JUGADOR_TIRA     = "jugador_tira"
    JUGADOR_HECHIZOS = "jugador_hechizos"
    DUELO            = "duelo"
    RESULTADO        = "resultado"
    FIN              = "fin"


class Escena:
    MENU       = "menu"
    DIFICULTAD = "dificultad"
    JUEGO      = "juego"
    FIN        = "fin"
    OPCIONES   = "opciones"


# ============================================================
# LAYOUT (en unidades del MUNDO)
# ============================================================
class Layout:
    # Cartas
    CARTA_W, CARTA_H = 55, 68
    ESCALA_CARTA_MANO = 0.84
    ESCALA_CARTA_HECHIZO = 0.95
    ESPACIO_CARTAS   = 14

    # --- Abanico del rival ---
    Y_CENTRO_RIVAL = 28
    ABANICO_SEP_X = 38
    ABANICO_OFFSET_Y = 12
    ABANICO_ANGULO = 8

    # --- Abanico del jugador ---
    ABANICO_SEP_X_JUGADOR = 48
    ABANICO_OFFSET_Y_JUGADOR = 10
    ABANICO_ANGULO_JUGADOR = 8

    # --- Zona de duelo ---
    Y_CENTRO_DUELO = 100
    Y_VS = 78
    DUELO_SEP_Y = 4

    # --- Mano del jugador ---
    Y_TOP_MANO = 148

    # --- Mensajes de estado ---
    Y_MENSAJE = 138

    @classmethod
    def x_inicio_cartas(cls, cantidad, ancho_mundo):
        total = cantidad * cls.CARTA_W + (cantidad - 1) * cls.ESPACIO_CARTAS
        return (ancho_mundo - total) // 2

    @classmethod
    def escala_carta_mano(cls, carta):
        escala = cls.ESCALA_CARTA_MANO
        if getattr(carta, "tipo", "criatura") == "hechizo":
            escala *= cls.ESCALA_CARTA_HECHIZO
        return escala

    @classmethod
    def escalas_mano(cls, cartas, ancho_mundo):
        _, escalas = cls.distribucion_mano(
            cartas, ancho_mundo, 200,
        )
        return escalas

    @classmethod
    def posiciones_mano(cls, cartas, ancho_mundo, alto_mundo,
                        reservar_hueco=False):
        posiciones, _ = cls.distribucion_mano(
            cartas, ancho_mundo, alto_mundo, reservar_hueco,
        )
        return posiciones

    @classmethod
    def distribucion_mano(cls, cartas, ancho_mundo, alto_mundo, reservar_hueco=False):
        cantidad = len(cartas)
        if cantidad == 0:
            return [], []

        escalas = [cls.escala_carta_mano(c) for c in cartas]
        
        # Ancho base y espaciado (ajustá estos valores si querés que estén más juntas o separadas)
        ancho_base = cls.CARTA_W
        espaciado = cls.ABANICO_SEP_X_JUGADOR 
        
        # Si hay una carta seleccionada (reservar_hueco), sumamos espacio extra para el "hueco"
        ancho_extra_hueco = 20 if reservar_hueco else 0
        
        # Calculamos el ancho total que ocupa la mano
        ancho_total = sum(int(ancho_base * e) for e in escalas) + (espaciado * (cantidad - 1)) + ancho_extra_hueco
        
        # Empezamos a dibujar desde la izquierda para que no se muevan todas al centro
        x_actual = (ancho_mundo - ancho_total) // 2
        y_base = alto_mundo - 2 - int(cls.CARTA_H * escalas[0] * 0.5)

        posiciones = []
        for i in range(cantidad):
            w_carta = int(ancho_base * escalas[i])
            cx = x_actual + w_carta // 2
            posiciones.append((cx, y_base, 0))
            
            # Avanzamos para la siguiente carta
            x_actual += w_carta + espaciado
            
            # Si la carta actual es la seleccionada, agregamos el espacio extra antes de la próxima
            if reservar_hueco and i == reservar_hueco:
                x_actual += ancho_extra_hueco

        return posiciones, escalas

    @classmethod
    def posiciones_rival(cls, cantidad, ancho_mundo, factor_espaciado=1):
        medio = (cantidad - 1) / 2 if cantidad > 0 else 0
        cx_centro = ancho_mundo // 2
        posiciones = []
        for indice in range(cantidad):
            distancia = abs(indice - medio)
            dx = (indice - medio) * cls.ABANICO_SEP_X * factor_espaciado
            dy = distancia * cls.ABANICO_OFFSET_Y
            posiciones.append(
                (cx_centro + int(dx), cls.Y_CENTRO_RIVAL + int(dy))
            )
        return posiciones

    @staticmethod
    def factor_animacion_objetivo(elapsed_ms):
        def suavizar(t):
            return t * t * (3 - 2 * t)

        if elapsed_ms < 150:
            t = max(0, elapsed_ms / 150)
            return 1 - 0.18 * suavizar(t)
        if elapsed_ms < 420:
            t = (elapsed_ms - 150) / 270
            return 0.82 + 0.36 * suavizar(t)
        return 1.18


# ============================================================
# BOTONES (en unidades del MUNDO)
# ============================================================
class Botones:
    REINICIAR_W, REINICIAR_H = 60, 12
    REINICIAR_X = 8
    REINICIAR_Y = 185

    SIGUIENTE_W, SIGUIENTE_H = 70, 12
    SIGUIENTE_X = 300 - 78
    SIGUIENTE_Y = 185

    MENU_W, MENU_H = 80, 8
    MENU_ESPACIO_Y = 3
    MENU_X_MARGEN = 12
    MENU_Y_MARGEN = 12
    MENU_BORDE_GROSOR = 1

    DIFICULTAD_W, DIFICULTAD_H = 90, 14
    DIFICULTAD_ESPACIO_Y       = 35


# ============================================================
# MANA
# ============================================================
MANA_INICIAL  = 7
MANA_MAXIMO   = 14
MANA_SUMA_MIN = 1
MANA_SUMA_MAX = 2


# ============================================================
# HECHIZOS
# ============================================================
HECHIZOS = {
    "vision": {
        "nombre": "Vision",
        "nombre_carta": "Vision",
        "costo": 1,
        "target": "carta_rival",
        "descripcion": "Ver una carta del rival por 1.5s",
    },
    "fuerza": {
        "nombre": "Pocion de fuerza",
        "nombre_carta": "Fuerza",
        "costo": 2,
        "target": "criatura_propia",
        "bonus_poder": 5,
        "descripcion": "+5 poder a tu criatura",
    },
    "defensa": {
        "nombre": "Pocion de defensa",
        "nombre_carta": "Defensa",
        "costo": 2,
        "target": "criatura_propia",
        "bonus_aguante": 5,
        "descripcion": "+5 vida a tu criatura",
    },
    "curacion": {
        "nombre": "Curacion",
        "nombre_carta": "Curacion",
        "costo": 3,
        "target": "jugador",
        "bonus_hp": 20,
        "descripcion": "+20 HP al jugador",
    },
    "rayo": {
        "nombre": "Rayo",
        "nombre_carta": "Rayo",
        "costo": 3,
        "target": "criatura_rival",
        "daño": 10,
        "descripcion": "10 de daño a una criatura rival",
    },
    "debilidad": {
        "nombre": "Debilidad",
        "nombre_carta": "Debilidad",
        "costo": 3,
        "target": "criatura_rival",
        "bonus_poder": -5,
        "descripcion": "-5 poder a una criatura rival",
    },
    "robo": {
        "nombre": "Robo",
        "nombre_carta": "Robo",
        "costo": 3,
        "target": "carta_rival",
        "descripcion": "Robar una carta del rival",
    },
    "drenaje": {
        "nombre": "Drenaje",
        "nombre_carta": "Drenaje",
        "costo": 3,
        "target": "criatura_rival",
        "daño": 8,
        "curacion": 8,
        "descripcion": "Drena 8 de HP del rival",
    },
    "inmovilizar": {
        "nombre": "Inmovilizar",
        "nombre_carta": "Inmovilizar",
        "costo": 4,
        "target": "criatura_rival",
        "daño_aguante": 10,
        "descripcion": "Resta 10 de aguante a la criatura rival",
    },
}

POOL_HECHIZOS = [

    "vision", "fuerza", "defensa", "curacion",
    "rayo", "debilidad", "robo", "inmovilizar",
    "drenaje",
]


# ============================================================
# DIFICULTAD
# ============================================================
@dataclass(frozen=True)
class ConfigDificultad:
    nombre:           str
    hp_jugador:       int
    hp_enemigo:       int
    tamano_mazo:      int
    estrategia_ia:    str
    descripcion:      str


DIFICULTAD_FACIL = ConfigDificultad(
    nombre        = "Fácil",
    hp_jugador    = 70,
    hp_enemigo    = 60,
    tamano_mazo   = 3,
    estrategia_ia = "IARandom",
    descripcion   = "",
)

DIFICULTAD_NORMAL = ConfigDificultad(
    nombre        = "Normal",
    hp_jugador    = 80,
    hp_enemigo    = 100,
    tamano_mazo   = 4,
    estrategia_ia = "IAConservadora",
    descripcion   = "",
)

DIFICULTAD_DURO = ConfigDificultad(
    nombre        = "Duro de cojones",
    hp_jugador    = 90,
    hp_enemigo    = 140,
    tamano_mazo   = 6,
    estrategia_ia = "IAAdaptativa",
    descripcion   = "",
)

# ============================================================
# TUTORIAL
# ============================================================
TUTORIAL_ROUNDS = 4

# Textos por ronda
DIALOGOS_TUTORIAL = {
    1: [
        "Cada criatura tiene fuerza y vida (o aguante). La fuerza indica cuanto dano hace; la vida, cuanto puede resistir.",
        "Pasa el cursor por una carta para ver sus valores. El numero grande es la fuerza; la barra inferior muestra su vida actual.",
        "La criatura rival ya esta en la mesa. Baja una criatura de tu mano para enfrentarte a ella.",
        "Con la criatura en la mesa, podes revisar sus datos antes de decidir si iniciar el duelo.",
        "En este primer cruce, Perro tiene fuerza y vida 10; Gato y Slime tienen 5. Proba bajar Perro y luego inicia el duelo.",
        "Si una criatura golpea primero y su fuerza alcanza la vida rival, la derrota antes de recibir un contraataque.",
    ],
    2: [
        "Ahora hay dos hechizos para probar: Vision y Robo. Los hechizos cuestan mana; el frasco muestra cuanto tenes.",
        "Vision revela por un momento una carta rival. Seleccionala y despues elegi una carta elegible; la criatura en mesa no se puede elegir.",
        "Cuando termines de mirar, proba Robo: elegi esa otra carta rival y la sumaras a tu mazo.",
        "El mana se recupera y aumenta un poco al comenzar cada ronda. Podes usar mas de un hechizo si te alcanza.",
        "Cuando quieras cerrar la ronda, inicia el duelo con tu criatura.",
    ],
    3: [
        "Hagamos una prueba de aguante. Tu Perro tiene fuerza 10 y vida 10; el Dragon rival, fuerza 15 y vida 15.",
        "Inmovilizar le quita 10 de vida actual al Dragon: queda con 5. Su fuerza sigue siendo 15.",
        "La prioridad depende de la vida actual: tu Perro tiene 10 y el Dragon 5, asi que Perro golpea primero.",
        "Sus 10 de fuerza alcanzan para quitar los 5 de vida que le quedan al Dragon. Al caer antes, el Dragon no llega a contraatacar.",
        "Baja a Perro, usa Inmovilizar sobre el Dragon y despues inicia el duelo. Esta vez el hechizo es parte de la jugada.",
    ],
    4: [
        "Repetimos la idea con valores mayores: tu Fenix tiene fuerza y vida 20; el Golem rival, 25.",
        "Inmovilizar deja al Golem con 15 de vida, pero conserva sus 25 de fuerza.",
        "Fenix tiene 20 de vida frente a 15: vuelve a tener prioridad. Sus 20 de fuerza alcanzan para derrotar al Golem antes del contraataque.",
        "Baja a Fenix, usa Inmovilizar sobre el Golem y confirma el resultado iniciando el duelo.",
        "La regla no depende de que sean numeros chicos: compara la vida actual para saber quien actua primero y la fuerza para saber si ese golpe alcanza.",
    ],
}


@dataclass(frozen=True)
class ConfigTutorial:
    nombre:           str
    hp_jugador:       int
    hp_enemigo:       int
    tamano_mazo:      int
    estrategia_ia:    str
    descripcion:      str
    es_tutorial:      bool = True


DIFICULTAD_TUTORIAL = ConfigTutorial(
    nombre="Tutorial",
    hp_jugador=250,
    hp_enemigo=250,
    tamano_mazo=3,
    estrategia_ia="IATutorial",
    descripcion="Aprende las reglas con cuatro duelos guiados.",
)

DIFICULTADES = {
    "tutorial": DIFICULTAD_TUTORIAL,
    "facil":    DIFICULTAD_FACIL,
    "normal":   DIFICULTAD_NORMAL,
    "duro":     DIFICULTAD_DURO,
}

DIFICULTAD_DEFAULT = "normal"


# ============================================================
# GAMEPLAY
# ============================================================
DUELO_DURACION = 1500


# ============================================================
# POOL DE CARTAS
# ============================================================
POOL_CARTAS = [
    ("Gato",    5),
    ("Slime",   5),
    ("Perro",  10),
    ("Lobo",   10),
    ("Dragon", 15),
    ("Tigre",  15),
    ("Fenix",  20),
    ("Titan",  20),
    ("Golem",  25),
    ("Vampiro", 25),
]


# ============================================================
# HELPERS
# ============================================================
def get_dificultad(clave):
    return DIFICULTADES.get(clave, DIFICULTADES[DIFICULTAD_DEFAULT])