# =============================================================
#  MODO SUMO v8 - mBot2 (Upload mode, MicroPython)
#  Igual que v7, pero afinado para RUEDAS (sin orugas):
#   - Sin orugas hay mucha menos friccion: el robot se mueve
#     con potencias bajas y a la misma potencia va MAS RAPIDO.
#     Por eso todo baja al rango 30-40 en vez de 50-60.
#   - Al girar sobre ruedas derrapa menos: giros mas cortos.
#
#  Boton A = iniciar. Boton B durante la pelea = paro.
# =============================================================

import cyberpi
import mbot2
import mbuild
import time
import random

# ---------------- CONFIGURACION ----------------
UMBRAL_NEGRO  = 15    # gris < esto = cinta negra (piso 27-31, cinta 5-7)

DIST_ATAQUE   = 40    # cm para considerar "rival visto"

# Potencias para RUEDAS. Si algun motor no arranca, sube de 5 en 5.
POT_ATAQUE    = 40    # empuje
POT_BUSQUEDA  = 30    # giro buscando
POT_AVANCE    = 32    # avance buscando
POT_RETRO     = 40    # retroceso al ver la cinta
POT_GIRO_EVA  = 35    # giro al evadir

T_RETRO       = 0.45
T_GIRO_MIN    = 0.25
T_GIRO_MAX    = 0.50
T_GIRO_BUSQ   = 0.30
T_AVANCE_BUSQ = 0.60

# ---------------- MOVIMIENTO ----------------
# Motor derecho en espejo: recto = (p, -p)

def recto(p):
    mbot2.drive_power(p, -p)

def girar(p, direccion):
    mbot2.drive_power(direccion * p, direccion * p)

def parar():
    mbot2.drive_power(0, 0)

# ---------------- SENSORES ----------------

def leer(sonda):
    return mbuild.quad_rgb_sensor.get_gray(sonda, 1)

def borde():
    """'izq', 'der' o None segun que lado pisa la cinta negra."""
    izq = (leer("L1") < UMBRAL_NEGRO or leer("L2") < UMBRAL_NEGRO)
    der = (leer("R1") < UMBRAL_NEGRO or leer("R2") < UMBRAL_NEGRO)
    if izq:
        return "izq"
    if der:
        return "der"
    return None

def rival_cerca():
    d = mbuild.ultrasonic2.get(1)
    return 0 < d < DIST_ATAQUE

# ---------------- COMPORTAMIENTOS ----------------

def evadir(lado):
    cyberpi.led.on(0, 0, 255)          # azul = evasion
    parar()
    time.sleep(0.05)
    recto(-POT_RETRO)
    time.sleep(T_RETRO)
    direccion = 1 if lado == "izq" else -1
    girar(POT_GIRO_EVA, direccion)
    time.sleep(T_GIRO_MIN + random.random() * (T_GIRO_MAX - T_GIRO_MIN))
    parar()

# ---------------- INICIO ----------------

parar()
cyberpi.console.clear()
cyberpi.console.println("MODO SUMO v8")
cyberpi.console.println("Boton A = iniciar")
cyberpi.led.on(255, 255, 255)

while not cyberpi.controller.is_press("a"):
    time.sleep(0.05)

for i in range(5, 0, -1):
    cyberpi.console.clear()
    cyberpi.console.println("Inicio en " + str(i))
    cyberpi.audio.play_tone(700, 0.15)
    time.sleep(0.85)

cyberpi.console.clear()
cyberpi.console.println("LUCHA!")
cyberpi.audio.play_tone(1200, 0.3)

dir_busqueda = random.choice([1, -1])
girando = True
estado_prev = ""
cyberpi.timer.reset()

# ---------------- BUCLE PRINCIPAL ----------------

while True:

    if cyberpi.controller.is_press("b"):
        parar()
        cyberpi.led.on(255, 255, 255)
        cyberpi.console.clear()
        cyberpi.console.println("PARO - A = seguir")
        while not cyberpi.controller.is_press("a"):
            time.sleep(0.05)
        time.sleep(0.3)
        cyberpi.timer.reset()
        estado_prev = ""
        continue

    lado = borde()

    # PRIORIDAD 1: no salir del ring
    if lado is not None:
        evadir(lado)
        girando = True
        cyberpi.timer.reset()
        estado_prev = "evade"
        continue

    # PRIORIDAD 2: atacar
    if rival_cerca():
        if estado_prev != "ataque":
            cyberpi.led.on(255, 0, 0)
            estado_prev = "ataque"
        recto(POT_ATAQUE)
        time.sleep(0.01)
        continue

    # PRIORIDAD 3: buscar
    if estado_prev != "busca":
        cyberpi.led.on(255, 180, 0)
        estado_prev = "busca"

    t = cyberpi.timer.get()
    if girando:
        girar(POT_BUSQUEDA, dir_busqueda)
        if t > T_GIRO_BUSQ:
            girando = False
            cyberpi.timer.reset()
    else:
        recto(POT_AVANCE)
        if t > T_AVANCE_BUSQ:
            girando = True
            dir_busqueda = random.choice([1, -1])
            cyberpi.timer.reset()

    time.sleep(0.01)
