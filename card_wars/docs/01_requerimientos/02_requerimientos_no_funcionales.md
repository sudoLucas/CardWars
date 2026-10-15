# Requerimientos no funcionales

## Portabilidad

### RNF-01: Sistema operativo
El juego debe funcionar en Windows, Linux y macOS sin cambios en el
codigo fuente.

### RNF-02: Version de Python
El juego debe funcionar con Python 3.10 o superior.

### RNF-03: Dependencias externas
El juego solo debe depender de:
- pygame-ce (para el motor grafico)
- biblioteca estandar de Python (os, sys, math, random, dataclasses)

No debe requerir instalaciones adicionales mas alla de las mencionadas.

### RNF-04: Sin instalador
El juego debe poder ejecutarse directamente con `python main.py` sin
requerir un proceso de instalacion (mas alla de las dependencias).

## Rendimiento

### RNF-05: Cuadros por segundo
El juego debe mantener 60 FPS estables en hardware moderno.

### RNF-06: Tiempo de carga
El juego debe cargar y mostrar el menu principal en menos de 2 segundos
desde su ejecucion.

### RNF-07: Animaciones
Las animaciones de fondo (colinas) y de cartas (ola) deben ejecutarse
sin tirones visibles.

## Compatibilidad

### RNF-08: Resolucion de pantalla
El juego debe adaptarse a distintas resoluciones de monitor.

### RNF-09: Pantalla completa y ventana
El juego debe permitir alternar entre pantalla completa y modo ventana
sin reiniciar la aplicacion.

### RNF-10: Proporcion de aspecto
El juego mantiene una proporcion de aspecto 3:2. En pantallas con otra
proporcion, el contenido se escala sin deformarse (letterbox si es
necesario).

### RNF-11: Rutas absolutas
Todas las rutas de archivos (fuentes, imagenes) deben calcularse
relativas al directorio del proyecto, para que el juego funcione
independientemente del directorio desde donde se ejecute.

## Usabilidad

### RNF-12: Idioma
Toda la interfaz del juego debe estar en español.

### RNF-13: Fuente pixelada
El juego debe usar la fuente pixelada provista (pixel.ttf) para
mantener la estetica retro.

### RNF-14: Colores diferenciados
Los elementos visuales deben tener colores que los diferencien
claramente:
- Cartas del jugador: azul.
- Cartas del rival: bordo (dorso).
- Cartas de hechizo: brillo violeta.
- Cartas muertas: gris oscuro.

### RNF-15: Feedback visual
El juego debe dar feedback visual claro ante acciones del usuario
(hover sobre cartas, hover sobre botones, seleccion de carta, etc.).

### RNF-16: Jugabilidad con mouse o teclado
El juego debe poder jugarse completamente con el mouse, o
completamente con el teclado. Ambos esquemas deben estar siempre
activos y poder usarse de forma alternada en cualquier momento sin
reiniciar ni cambiar configuracion.

### RNF-16.1: Esquema de teclado principal
El control por teclado debe soportar las siguientes teclas:
- Navegacion entre cartas y opciones: flechitas (arriba, abajo,
  izquierda, derecha) o W, A, S, D.
- Confirmar seleccion / avanzar: barra espaciadora, o Enter, o Z
  como alternativa.
- Cancelar accion / volver atras / deseleccionar: ESC o Shift.

### RNF-16.2: Coherencia entre esquemas
Cualquier accion que se pueda hacer con el mouse debe poder hacerse
con el teclado, y viceversa.

### RNF-17: Indicadores de estado
El sistema debe mostrar en todo momento:
- HP actual del jugador y de la IA.
- Mana actual del jugador.
- Ronda actual.
- Mensaje del estado del turno.

### RNF-17.1: Indicador de foco de teclado
Cuando el jugador navega con el teclado, debe haber un indicador
visual claro de que elemento esta seleccionado (por ejemplo, un
borde de color, un highlight, o un cursor).

## Mantenibilidad

### RNF-18: Estructura modular
El codigo debe estar separado en modulos claros:
- `modelo/` para la logica de negocio.
- `vista/` para el renderizado.
- `escenas/` para las pantallas del juego.
- `config.py` para configuracion global.

### RNF-19: Idioma del codigo
Los nombres de variables, funciones y clases deben estar en español
para mantener coherencia con el dominio del juego.

### RNF-20: Constantes centralizadas
Los valores configurables (velocidades, colores, tamanos, costos de
hechizos) deben estar centralizados en `config.py` o en modulos
especificos, no dispersos en el codigo.

### RNF-21: Comentarios
El codigo debe tener comentarios en los lugares clave: constantes
de configuracion, logica compleja, y puntos de integracion entre
modulos.

## Escalabilidad

### RNF-22: Agregar cartas
Agregar nuevas cartas debe ser tan simple como agregar una linea al
`POOL_CARTAS` en `config.py`.

### RNF-23: Agregar hechizos
Agregar nuevos hechizos debe ser posible sin modificar la logica
de combate ni el motor de turnos.

### RNF-24: Agregar escenas
Agregar nuevas pantallas (por ejemplo, opciones, estadisticas) debe
ser posible creando una nueva clase que herede de `Escena`.

### RNF-25: Agregar dificultades
Agregar un nuevo nivel de dificultad debe ser posible creando una
nueva instancia de `ConfigDificultad` en `config.py`.

## Robustez

### RNF-26: Manejo de errores de archivos
Si una imagen o fuente no se encuentra, el juego debe continuar
funcionando con un fallback (color plano o fuente del sistema).

### RNF-27: Validacion de datos
El sistema debe validar que las cartas y hechizos usados cumplan
las reglas antes de aplicarlos (mana suficiente, objetivo valido).

### RNF-28: Sin crashes
El juego no debe crashear ante clicks rapidos, teclas al azar, o
combinaciones de acciones no previstas.

## Estetica

### RNF-29: Estilo pixel art
El juego debe mantener un estilo visual pixel art consistente,
inspirado en Game Boy Advance.

### RNF-30: Paleta centralizada
Todos los colores deben provenir de `vista/colores.py`, sin valores
RGB hardcodeados en otros archivos.

### RNF-31: Animacion de fondo
El fondo del menu debe tener animacion parallax con las 3 capas de
colinas (frente, medio, fondo) moviendose a distintas velocidades.

### RNF-32: Sombra en cartas
Las cartas del abanico del rival deben tener sombras que refuercen
la sensacion de profundidad.