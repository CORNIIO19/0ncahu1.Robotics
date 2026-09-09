Ejercicios de motores — mBot2 / CyberPi (Python)

Estos ejercicios están pensados como base para llegar a un código de control de motores como el de MODO SUMO v10. Se enfocan solo en motores: la función cruda drive_power(), el patrón de bucle no-bloqueante, y las secuencias compuestas con constantes configurables. No se tocan sensores todavía.

Ejercicio 1 — drive_power() y el espejo de motores

mbot2.drive_power(p1, p2) es la función cruda de control de motores: fija la potencia de cada motor y no bloquea — el robot sigue así hasta que vuelvas a llamarla. Como los motores suelen estar montados en espejo, ir recto exige signos opuestos entre ambos motores, mientras que girar en el mismo lugar exige el mismo signo en los dos.

python
import mbot2
import time

def recto(p):
    mbot2.drive_power(p, -p)     # signos opuestos = recto

def girar(p, direccion):
    mbot2.drive_power(direccion * p, direccion * p)  # mismo signo = gira en el sitio

def parar():
    mbot2.drive_power(0, 0)

recto(50)
time.sleep(1)
girar(50, 1)
time.sleep(0.5)
parar()

Reto: invierte los signos a propósito y observa qué hace el robot físicamente, hasta confirmar cuál combinación es "recto" en tu armado real (no todos quedan igual). Esa calibración es la base de recto()/girar() en el v10.

Ejercicio 2 — Bucle continuo con fases por tiempo (lógica de "búsqueda")

Como drive_power no bloquea, dentro de un while True hay que "reafirmar" la potencia en cada vuelta y decidir cuándo cambiar de fase usando un timer — exactamente como el bloque girando / cyberpi.timer del código real.

python
import cyberpi
import mbot2
import time

def recto(p):
    mbot2.drive_power(p, -p)

def girar(p, direccion):
    mbot2.drive_power(direccion * p, direccion * p)

girando = True
cyberpi.timer.reset()

while not cyberpi.controller.is_press("a"):
    t = cyberpi.timer.get()
    if girando:
        girar(30, 1)
        if t > 0.3:
            girando = False
            cyberpi.timer.reset()
    else:
        recto(32)
        if t > 0.6:
            girando = True
            cyberpi.timer.reset()
    time.sleep(0.01)

mbot2.drive_power(0, 0)

Reto: agrega una tercera fase (retroceso breve) al ciclo. Este patrón de "alternar según timer sin bloquear" es literalmente el bloque PRIORIDAD 3: buscar del v10.

Ejercicio 3 — Secuencia compuesta con constantes (como evadir())

Une varios pasos de motor en una función con parámetros configurables arriba del archivo, igual que las constantes POT_RETRO, T_RETRO, POT_GIRO_EVA, etc. del código real. Aquí se dispara con un botón en vez del sensor de borde.

python
import cyberpi
import mbot2
import time
import random

POT_RETRO = 40
T_RETRO = 0.45
POT_GIRO = 35
T_GIRO_MIN, T_GIRO_MAX = 0.25, 0.50

def recto(p):
    mbot2.drive_power(p, -p)

def girar(p, direccion):
    mbot2.drive_power(direccion * p, direccion * p)

def parar():
    mbot2.drive_power(0, 0)

def evadir(direccion):
    parar()
    time.sleep(0.05)
    recto(-POT_RETRO)
    time.sleep(T_RETRO)
    girar(POT_GIRO, direccion)
    time.sleep(T_GIRO_MIN + random.random() * (T_GIRO_MAX - T_GIRO_MIN))
    parar()

while True:
    if cyberpi.controller.is_press("a"):
        evadir(1)
    elif cyberpi.controller.is_press("b"):
        evadir(-1)
    time.sleep(0.05)

Reto: mide con el cronómetro cuánto se mueve el robot en T_RETRO a distintas POT_RETRO, para calibrar el sumo real con datos y no a ojo.

Cómo conecta con el v10

Con estos tres ejercicios queda cubierta toda la capa de motores del MODO SUMO v10:

La función cruda drive_power() con su espejo de signos.
El bucle no-bloqueante con fases controladas por timer.
La secuencia compuesta con constantes de configuración.

Lo único que le falta a esto para convertirse en el v10 es sustituir el botón disparador por borde() / rival_cerca() — eso ya pertenece a la capa de sensores, no de motores.