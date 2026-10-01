"""
mBot2 / CyberPi - Mostrar contenido en pantalla
Modo: Upload (MicroPython)

Este script muestra dos cosas en la pantalla del CyberPi:
1. Un mensaje de texto.
2. Un dibujo simple (una carita feliz) hecho con píxeles.

Notas:
- cyberpi.console.println(texto): escribe texto en la pantalla.
- cyberpi.sprite(): crea un "sprite" (lienzo) de 16x16 píxeles que se
  puede dibujar con draw_pixel() y luego mostrar con screen.render().
  Esto es lo que usa el firmware original para sus animaciones de baile.
"""

import cyberpi
import time

# ---- 1. Mostrar un mensaje de texto ----
cyberpi.console.clear()
cyberpi.console.println("Hola, soy mBot2!")
time.sleep(2)

# ---- 2. Dibujar una carita feliz en la pantalla ----
# La pantalla es una cuadrícula de 16x16 = 256 píxeles.
# Cada número es un color en formato hexadecimal (0xRRGGBB).
# 0x000000 = negro (apagado / fondo)
# 0xf8e71c = amarillo (cara)
# 0x101010 = casi negro (ojos y boca)

NEGRO = 0x000000
AMARILLO = 0xf8e71c
OSCURO = 0x101010

# Construimos la imagen fila por fila (16 filas de 16 píxeles cada una)
carita = (
    [NEGRO] * 16 +
    [NEGRO] * 3 + [AMARILLO] * 10 + [NEGRO] * 3 +
    [NEGRO] * 2 + [AMARILLO] * 12 + [NEGRO] * 2 +
    [NEGRO] + [AMARILLO] * 14 + [NEGRO] +
    [NEGRO] + [AMARILLO] * 3 + [OSCURO] * 2 + [AMARILLO] * 4 + [OSCURO] * 2 + [AMARILLO] * 3 + [NEGRO] +
    [NEGRO] + [AMARILLO] * 3 + [OSCURO] * 2 + [AMARILLO] * 4 + [OSCURO] * 2 + [AMARILLO] * 3 + [NEGRO] +
    [NEGRO] + [AMARILLO] * 14 + [NEGRO] +
    [NEGRO] + [AMARILLO] * 4 + [OSCURO] + [AMARILLO] * 6 + [OSCURO] + [AMARILLO] * 3 + [NEGRO] +
    [NEGRO] + [AMARILLO] * 5 + [OSCURO] * 6 + [AMARILLO] * 4 + [NEGRO] +
    [NEGRO] + [AMARILLO] * 14 + [NEGRO] +
    [NEGRO] * 2 + [AMARILLO] * 12 + [NEGRO] * 2 +
    [NEGRO] * 3 + [AMARILLO] * 10 + [NEGRO] * 3 +
    [NEGRO] * 16 +
    [NEGRO] * 16 +
    [NEGRO] * 16
)

# Por si el cálculo de filas no llega exacto a 256, lo completamos/recortamos
carita = (carita + [NEGRO] * 256)[:256]

cara = cyberpi.sprite()
cara.draw_pixel(carita)
cara.set_size(600)
cyberpi.screen.render()

time.sleep(3)

# ---- Limpiar pantalla al final ----
cyberpi.console.clear()
