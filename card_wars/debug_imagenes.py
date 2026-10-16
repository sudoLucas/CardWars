# debug_imagenes.py
"""
Script para diagnosticar las imagenes de colinas.
"""
import os
import sys
import pygame


# --- Ruta directa a la carpeta de imagenes ---
CARPETA_IMAGENES = r"C:\Users\Usuario\Desktop\s\CardWars\card_wars\assets\imagenes"

ARCHIVOS = ["colina1.png", "colina2.png", "colina3.png"]

ANCHO, ALTO = 1200, 800


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Debug imagenes")
    reloj = pygame.time.Clock()

    print("=" * 60)
    print(f"Buscando imagenes en: {CARPETA_IMAGENES}")
    print(f"La carpeta existe: {os.path.isdir(CARPETA_IMAGENES)}")
    print("=" * 60)

    if os.path.isdir(CARPETA_IMAGENES):
        print("\nArchivos en la carpeta:")
        for f in os.listdir(CARPETA_IMAGENES):
            print(f"  - {f}")

    imagenes = []
    for nombre in ARCHIVOS:
        ruta = os.path.join(CARPETA_IMAGENES, nombre)
        print(f"\n--- {nombre} ---")
        print(f"Ruta: {ruta}")
        print(f"Existe: {os.path.isfile(ruta)}")

        if not os.path.isfile(ruta):
            imagenes.append((nombre, None, ruta, "NO EXISTE"))
            continue

        try:
            img = pygame.image.load(ruta).convert_alpha()
            w, h = img.get_size()
            print(f"Tamano: {w} x {h}")

            # Muestreamos pixeles clave
            puntos = [
                ("esquina sup-izq", (0, 0)),
                ("centro", (w // 2, h // 2)),
                ("esquina inf-izq", (0, h - 1)),
                ("esquina sup-der", (w - 1, 0)),
                ("esquina inf-der", (w - 1, h - 1)),
            ]
            for etiqueta, (px, py) in puntos:
                try:
                    color = img.get_at((px, py))
                    print(f"  {etiqueta} ({px},{py}): RGBA={tuple(color)}")
                except Exception as e:
                    print(f"  {etiqueta} ({px},{py}): ERROR {e}")

            # Contamos pixeles opacos
            opacos = 0
            total = 0
            muestreo = 20
            for y in range(0, h, muestreo):
                for x in range(0, w, muestreo):
                    total += 1
                    if img.get_at((x, y))[3] > 0:
                        opacos += 1
            porcentaje = (opacos / total * 100) if total > 0 else 0
            print(f"  Pixeles opacos: {opacos}/{total} ({porcentaje:.1f}%)")

            imagenes.append((nombre, img, ruta, "OK"))

        except Exception as e:
            print(f"ERROR al cargar: {e}")
            imagenes.append((nombre, None, ruta, f"ERROR: {e}"))

    print("\n" + "=" * 60)
    print("Controles:")
    print("  0 = las 3 superpuestas")
    print("  1 = colina1  |  2 = colina2  |  3 = colina3")
    print("  F = fondo blanco (para ver transparencia)")
    print("  ESC = salir")
    print("=" * 60)

    modo = 0
    fondo_blanco = False

    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    corriendo = False
                elif evento.key == pygame.K_0:
                    modo = 0
                elif evento.key == pygame.K_1:
                    modo = 1
                elif evento.key == pygame.K_2:
                    modo = 2
                elif evento.key == pygame.K_3:
                    modo = 3
                elif evento.key == pygame.K_f:
                    fondo_blanco = not fondo_blanco

        if fondo_blanco:
            pantalla.fill((255, 255, 255))
        else:
            pantalla.fill((30, 30, 30))
            # Grilla para ver transparencia
            for x in range(0, ANCHO, 40):
                pygame.draw.line(pantalla, (60, 60, 60), (x, 0), (x, ALTO))
            for y in range(0, ALTO, 40):
                pygame.draw.line(pantalla, (60, 60, 60), (0, y), (ANCHO, y))

        # Texto de ayuda
        fuente = pygame.font.SysFont("Arial", 18)
        modo_txt = "TODAS" if modo == 0 else ARCHIVOS[modo - 1]
        textos = [
            f"Modo: {modo_txt}    Fondo: {'BLANCO' if fondo_blanco else 'GRILLA'}",
            "0=todas  1=colina1  2=colina2  3=colina3  F=fondo  ESC=salir",
        ]
        for i, t in enumerate(textos):
            surf = fuente.render(t, True, (255, 255, 0) if fondo_blanco else (255, 255, 255))
            pantalla.blit(surf, (10, 10 + i * 22))

        # Dibujamos
        if modo == 0:
            for nombre, img, _, _ in imagenes:
                if img is not None:
                    escalada = pygame.transform.smoothscale(img, (ANCHO, ALTO))
                    pantalla.blit(escalada, (0, 0))
        else:
            nombre, img, ruta, estado = imagenes[modo - 1]
            if img is not None:
                w, h = img.get_size()
                escala = min(ANCHO / w, ALTO / h) * 0.9
                nuevo_w = max(1, int(w * escala))
                nuevo_h = max(1, int(h * escala))
                escalada = pygame.transform.smoothscale(img, (nuevo_w, nuevo_h))
                x = (ANCHO - nuevo_w) // 2
                y = (ALTO - nuevo_h) // 2
                pantalla.blit(escalada, (x, y))
            else:
                surf = fuente.render(f"{nombre}: {estado}", True, (255, 80, 80))
                pantalla.blit(surf, (ANCHO // 2 - 100, ALTO // 2))

        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()