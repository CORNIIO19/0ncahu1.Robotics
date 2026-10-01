# Práctica 1 — ¿Qué mide realmente el sensor?

**Sensor Quad RGB del mBot2**

---

## Objetivos

- Distinguir entre "color" y "reflectancia"
- Determinar el umbral que separa la línea del fondo
- Medir cómo la altura del sensor afecta el contraste

## Material

- mBot2 con sensor Quad RGB conectado
- mBlock5 en modo Upload (MicroPython)
- Cinta negra mate de 2 cm sobre fondo blanco
- Muestras de superficies: papel blanco, cinta negra brillante, cartulina gris, papel rojo, papel azul
- Espaciadores de cartón o tuercas para variar la altura
- Regla y hoja de registro

> **Método:** el robot permanece con los motores apagados y se mueve **a mano**. Se usa como instrumento de medición, no como vehículo.

---

## Programa

```python
import cyberpi
import mbuild

mbuild.quad_rgb_sensor.color_mode("enhance")

while True:
    v1 = mbuild.quad_rgb_sensor.get_gray(1, 1)
    v2 = mbuild.quad_rgb_sensor.get_gray(2, 1)
    v3 = mbuild.quad_rgb_sensor.get_gray(3, 1)
    v4 = mbuild.quad_rgb_sensor.get_gray(4, 1)
    cyberpi.console.println(str(v1) + " " + str(v2) + " " + str(v3) + " " + str(v4))
    cyberpi.timer.reset()
    while cyberpi.timer.get() < 0.5:
        pass
```

---

## Ejercicio A — Tabla de superficies

Colocar el robot sobre cada superficie y anotar el valor del sensor L1 (segundo canal).

| Superficie | Lectura | ¿Se ve claro u oscuro? |
|---|---|---|
| Papel blanco | | |
| Cinta negra mate | | |
| Cinta negra brillante | | |
| Cartulina gris | | |
| Madera de la mesa | | |
| Papel rojo | | |
| Papel azul | | |

---

## Ejercicio B — Cálculo del umbral

1. Umbral = (lectura sobre blanco + lectura sobre negro) / 2 = __________

2. Colocar el robot justo en el borde de la línea. ¿La lectura queda arriba o abajo del umbral?

   __________

3. Deslizar lentamente el robot cruzando la línea. ¿El cambio es brusco o gradual?

   __________

---

## Ejercicio C — Efecto de la altura

Medir sobre blanco y sobre negro a distintas alturas. El contraste es la diferencia entre ambas lecturas.

| Altura extra (mm) | Lectura blanco | Lectura negro | Contraste |
|---|---|---|---|
| 0 (original) | | | |
| +2 | | | |
| +5 | | | |
| +10 | | | |

**Graficar** contraste contra altura en papel milimétrico o en una hoja de cálculo.

---

## Preguntas de cierre

1. El papel rojo y el azul, ¿dieron lecturas parecidas o distintas? ¿Qué dice eso sobre lo que mide el sensor en modo `enhance`?

2. ¿Por qué la cinta negra brillante puede leerse como si fuera clara?

3. Según tu gráfica, ¿cuál es la altura donde conviene montar el sensor? ¿Qué pasa si el chasis va demasiado bajo?

4. Repite una medición con la luz del salón apagada. ¿Cambió el valor? ¿Qué implica para el día de la competencia?

---

## Anexo: verificación de la API

Antes de subir el programa, confirmar la firma exacta en la vista bloque-a-Python de mBlock5, ya que varía entre versiones de firmware:

- `mbuild.quad_rgb_sensor.get_gray(index, id)` — verificar el orden de los argumentos y si el índice empieza en 0 o en 1

Si `get_gray()` no existe en tu firmware, la alternativa es `get_grayscale()` o leer los canales de color por separado con `get_red()` / `get_green()` / `get_blue()`.
