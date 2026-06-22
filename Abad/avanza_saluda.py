"""
mBot2 - Avanzar y mover brazos al mismo tiempo
Modo: Upload (MicroPython)

Funcionamiento:
- El robot avanza en línea recta durante 5 segundos.
- Mientras avanza, los brazos (servos S1 y S3) se mueven de un lado a otro
  como si estuviera saludando/agitando los brazos.
- Al terminar, los motores se detienen y los servos se sueltan
  (igual que hace 'initial_state()' en el firmware original).

Notas de hardware confirmadas en pruebas:
- mbot2.drive_power(izquierda, derecha): para ir recto hacia adelante,
  el motor derecho necesita signo invertido (motor montado en espejo).
  Por eso usamos drive_power(power, -power).
- mbot2.servo_set(angulo, "S1"/"S3"/"all"): mueve los servos de los brazos.
"""

import mbot2
import cyberpi
import time

# ---- Parámetros configurables ----
DURACION_SEGUNDOS = 5      # Cuánto tiempo avanza el robot
POTENCIA_MOTOR = 60        # Potencia de avance (rango -100 a 100)
ANGULO_BRAZO_A = 60        # Posición "abajo" del brazo
ANGULO_BRAZO_B = 130       # Posición "arriba" del brazo
INTERVALO_MOVIMIENTO = 0.4 # Segundos entre cada cambio de posición del brazo

# ---- Inicio del movimiento ----
cyberpi.timer.reset()

# Empieza a avanzar (corrección de signo: derecho invertido para ir recto)
mbot2.drive_power(POTENCIA_MOTOR, -POTENCIA_MOTOR)

# Variable para alternar entre las dos posiciones del brazo
posicion_actual = ANGULO_BRAZO_A

# Bucle que dura DURACION_SEGUNDOS, moviendo los brazos mientras avanza
while cyberpi.timer.get() < DURACION_SEGUNDOS:
    # Alterna la posición del brazo
    mbot2.servo_set(posicion_actual, "all")

    # Cambia a la otra posición para la siguiente iteración
    if posicion_actual == ANGULO_BRAZO_A:
        posicion_actual = ANGULO_BRAZO_B
    else:
        posicion_actual = ANGULO_BRAZO_A

    # Pequeña pausa antes del siguiente movimiento de brazo
    # (los motores siguen girando durante esta pausa, ya que
    # drive_power no necesita llamarse de nuevo para seguir activo)
    time.sleep(INTERVALO_MOVIMIENTO)

# ---- Fin del movimiento ----
# Detiene los motores
mbot2.drive_power(0, 0)

# Suelta los servos (deja de aplicar fuerza, como en el firmware original)
mbot2.servo_release("all")
