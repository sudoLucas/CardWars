# Manual de instalacion - Card Wars

## Indice

1. Requisitos del sistema
2. Instalacion de Python
3. Instalacion de pygame-ce
4. Descarga del proyecto
5. Verificacion de la estructura
6. Ejecucion del juego
7. Solucion de problemas
8. Desinstalacion

---

## 1. Requisitos del sistema

### Hardware minimo

- Procesador: 1 GHz o superior.
- Memoria RAM: 2 GB.
- Espacio en disco: 50 MB libres.
- Resolucion de pantalla: 1024x768 o superior.

### Software

- Sistema operativo: Windows 10 o superior, Linux, o macOS.
- Python 3.10 o superior.
- Biblioteca pygame-ce.
- Git (opcional, solo si vas a clonar el repositorio).

---

## 2. Instalacion de Python

Si no tenes Python instalado, segui estos pasos.

### Windows

1. Anda a la pagina oficial: https://www.python.org/downloads/
2. Descarga el instalador de la ultima version estable (3.12 o superior).
3. Ejecuta el instalador.
4. IMPORTANTE: en la primera pantalla, tilda la casilla "Add python.exe to PATH" antes de hacer click en "Install Now".
5. Espera a que termine la instalacion.
6. Abri una terminal (busca "cmd" o "PowerShell" en el menu inicio) y verifica la instalacion escribiendo:

   ```
   python --version
   ```

   Deberia mostrar algo como `Python 3.12.x`.

### Linux

En la mayoria de distribuciones, Python ya viene preinstalado. Para verificar, abri una terminal y ejecuta:

```
python3 --version
```

Si no esta instalado:

- Ubuntu / Debian:
  ```
  sudo apt update
  sudo apt install python3 python3-pip
  ```

- Fedora:
  ```
  sudo dnf install python3 python3-pip
  ```

- Arch:
  ```
  sudo pacman -S python python-pip
  ```

### macOS

1. Anda a https://www.python.org/downloads/
2. Descarga el instalador para macOS.
3. Ejecuta el archivo `.pkg` y segui los pasos.
4. Verifica en una terminal:

   ```
   python3 --version
   ```

---

## 3. Instalacion de pygame-ce

El juego usa `pygame-ce` (Community Edition), una version mejorada y mantenida de pygame.

### En Windows, Linux o macOS

Abre una terminal y ejecuta:

```
pip install pygame-ce
```

Si estas en Linux o macOS y usas `python3` en vez de `python`:

```
pip3 install pygame-ce
```

Para verificar que se instalo correctamente:

```
python -c "import pygame; print(pygame.ver)"
```

Deberia mostrar la version de pygame-ce (por ejemplo, `2.5.8`).

### Notas sobre pygame-ce

- `pygame-ce` es compatible con el antiguo `pygame`. Si ya tenias `pygame` instalado, podes desinstalarlo:

  ```
  pip uninstall pygame
  ```

  Y despues instalar pygame-ce.

- No instales los dos a la vez, pueden entrar en conflicto.

### Alternativa: entorno virtual (recomendado)

Para no ensuciar la instalacion global de Python, es recomendable usar un entorno virtual:

**Windows:**
```
python -m venv .venv
.venv\Scripts\activate
pip install pygame-ce
```

**Linux / macOS:**
```
python3 -m venv .venv
source .venv/bin/activate
pip install pygame-ce
```

Una vez activado el entorno, todos los `pip install` van a ese entorno y no al sistema.

Para desactivar el entorno cuando termines:

```
deactivate
```

---

## 4. Descarga del proyecto

Tenes dos opciones para descargar el juego.

### Opcion A: Clonar con Git (recomendado)

Si tenes Git instalado, abri una terminal y ejecuta:

```
git clone https://github.com/sudolucas/cardwars.git
```

Esto va a crear una carpeta llamada `cardwars` con todo el proyecto.

Para actualizar el proyecto mas adelante:

```
cd cardwars
git pull
```

### Opcion B: Descargar el ZIP

1. Anda al repositorio en GitHub:
   https://github.com/sudolucas/cardwars
2. Hace click en el boton verde "Code".
3. Elegi "Download ZIP".
4. Descomprimi el archivo ZIP en la carpeta que quieras.

---

## 5. Verificacion de la estructura

Despues de descargar el proyecto, la estructura de carpetas deberia verse asi:

```
cardwars/
└── card_wars/
    ├── main.py
    ├── config.py
    ├── assets/
    │   ├── fuentes/
    │   │   └── pixel.ttf
    │   └── imagenes/
    │       ├── colina1.png
    │       ├── colina2.png
    │       └── colina3.png
    ├── escenas/
    │   ├── base.py
    │   ├── menu.py
    │   ├── dificultad.py
    │   ├── juego.py
    │   └── fin.py
    ├── modelo/
    │   ├── carta.py
    │   ├── mazo.py
    │   ├── ia.py
    │   └── juego.py
    └── vista/
        ├── render.py
        ├── colores.py
        └── fuentes.py
```

Importante: verifica que estos archivos existan:

- `card_wars/main.py` (el archivo principal).
- `card_wars/config.py` (la configuracion).
- `card_wars/assets/fuentes/pixel.ttf` (la fuente del juego).
- Al menos una imagen en `card_wars/assets/imagenes/`.

Si falta alguno, volve a descargar el proyecto.

---

## 6. Ejecucion del juego

Con todo instalado, para ejecutar el juego:

1. Abri una terminal.
2. Navega a la carpeta del proyecto:

   **Windows:**
   ```
   cd C:\ruta\donde\descargaste\cardwars\card_wars
   ```

   **Linux / macOS:**
   ```
   cd /ruta/donde/descargaste/cardwars/card_wars
   ```

3. Ejecuta:

   ```
   python main.py
   ```

   O si estas en Linux/macOS:

   ```
   python3 main.py
   ```

4. El juego deberia arrancar en modo pantalla completa mostrando el menu principal.

Para salir del juego: apreta ESC en el menu principal, o cerra la ventana con la X.

---

## 7. Solucion de problemas

### El juego no arranca: "No module named 'pygame'"

Significa que pygame-ce no esta instalado o no esta en el Python correcto.

Solucion: verifica que estas usando el Python correcto:

```
python -c "import pygame; print(pygame.ver)"
```

Si tira error, instala pygame-ce:

```
pip install pygame-ce
```

Si tenes varios Python instalados, puede que necesites usar `python3` en vez de `python`, o el path completo.

### El juego arranca pero no carga la fuente

Vas a ver en la consola un mensaje del tipo:

```
[fuentes] NO ENCONTRADA: /ruta/card_wars/assets/fuentes/pixel.ttf
```

Solucion: verifica que el archivo `pixel.ttf` este en `card_wars/assets/fuentes/`. Si no esta, el juego sigue funcionando pero con la fuente por defecto (Arial).

### No se ve el fondo animado

Solucion: verifica que las imagenes `colina1.png`, `colina2.png` y `colina3.png` esten en `card_wars/assets/imagenes/`. Si faltan, el juego arranca con fondo negro.

### El juego se ve borroso o muy chico

Solucion: apreta F11 para alternar entre pantalla completa y modo ventana. En algunos monitores, el modo ventana se ve mejor.

### Error: "No space left on device" al instalar pygame

Significa que no tenes espacio en disco.

Solucion: libera espacio en el disco donde esta Python, o instala en otro disco.

### El juego va lento (menos de 60 FPS)

Solucion: verifica que no tengas otros programas pesados abiertos. Si persiste, baja la resolucion de pantalla o cerra el juego y volve a abrirlo.

### El juego se ve estirado en mi monitor

Solucion: el juego esta disenado para una proporcion de aspecto 3:2. Si tu monitor es 16:9, el contenido puede aparecer estirado. Es una limitacion conocida que se puede mejorar con letterbox.

### "Permission denied" en Linux al ejecutar

Solucion: proba con:

```
python3 main.py
```

Si el error es por permisos de archivo, verifica con:

```
ls -la card_wars/
```

Y asegurate de tener permisos de lectura.

### Otros errores

Si ves un error distinto:

1. Copia el mensaje completo de la consola.
2. Verifica que tengas Python 3.10+ y pygame-ce instalado.
3. Abri un issue en el repositorio de GitHub con el mensaje de error.

---

## 8. Desinstalacion

Si queres desinstalar el juego:

### Borrar los archivos

Simplemente borra la carpeta `cardwars` completa.

### Desinstalar pygame-ce (opcional)

Si queres desinstalar pygame-ce tambien:

```
pip uninstall pygame-ce
```

### Borrar el entorno virtual (si lo usaste)

Si creaste un entorno virtual en `.venv/`, borralo con:

**Windows:**
```
rmdir /s .venv
```

**Linux / macOS:**
```
rm -rf .venv
```

### Python

Si queres desinstalar Python completamente, usa el panel de control de tu sistema (Windows), el gestor de paquetes (Linux), o el instalador de macOS.

Cuidado: desinstalar Python puede afectar otros programas que lo usen. Solo hacelo si estas seguro.