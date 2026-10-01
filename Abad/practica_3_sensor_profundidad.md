# Práctica 2 — ¿Que tan profundo es?

**Sensor Ultrasonico del mBot2**

---

## Objetivos

- Distinguir entre "color" y "reflectancia"
- Determinar el umbral que separa la línea del fondo
- Medir cómo la altura del sensor afecta el contraste

## Material

- mBot2 con motoroes conectados
- mBlock5 en modo Upload (MicroPython)
- Espaciadores de cartón o tuercas para variar la altura
- Regla y hoja de registro

> **Método:** el robot permanece con los motores apagados y se mueve **a mano**. Se usa como instrumento de medición, no como vehículo.

---

## Programa
```
import mbuild
import cyberpi
import time

mbuild.quad_rgb_sensor.color_mode("enhance")

while True:
    offset = mbuild.quad_rgb_sensor.get_offset_track(1)
    cyberpi.console.clear()
    cyberpi.console.println(offset)
    time.sleep(0.3)
```

---

## Ejercicio A — 


---

## Ejercicio B — 



---

## Ejercicio C — 



---

## Preguntas de cierre


---

## Anexo: verificación de la API

Antes de subir el programa, confirmar la firma exacta en la vista bloque-a-Python de mBlock5, ya que varía entre versiones de firmware:

- `mbuild.quad_rgb_sensor.get_gray(index, id)` — verificar el orden de los argumentos y si el índice empieza en 0 o en 1

Si `get_gray()` no existe en tu firmware, la alternativa es `get_grayscale()` o leer los canales de color por separado con `get_red()` / `get_green()` / `get_blue()`.
