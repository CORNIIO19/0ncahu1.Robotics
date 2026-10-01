# Práctica 2 — ¿Pasos para correr?

**Sensor dos motores paso a paso del mBot2**

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
```import mbot2
    import time

mbot2.drive_power(100, -100)
time.sleep(2)
mbot2.drive_power(0, 0)
```
