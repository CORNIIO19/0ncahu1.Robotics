# =============================================================
#  MODO SUMO v9 - mBot2 + CyberPi, chasis con RUEDAS
#  Cambios respecto a v8 (que ya evade el ring perfecto):
#   - ATAQUE EN 2 ETAPAS:
#       lejos  -> se acerca a potencia media
#       cerca  -> EMBESTIDA a fondo (ya no da "toquesitos")
#   - ENGANCHE: una vez que embiste, sigue empujando un minimo
#     de tiempo aunque el sonar parpadee. Los toquesitos venian
#     de que perdia al rival un instante y se iba a buscar.
#   - Evasion y busqueda intactas (esas ya quedaron bien)
# =============================================================

import cyberpi
import mbot2
import mbuild
import time
import random

# ---------------- CONFIGURACION ----------------
UMBRAL_NEGRO  = 15    # gris < esto = cinta negra

# --- Ataque ---
DIST_VISTA    = 60    # cm: lo veo, me acerco
DIST_EMBESTIR = 20    # cm: ya lo tengo, empujo a fondo
POT_ACERCARSE = 45    # potencia al acercarse
POT_EMBESTIDA = 90    # potencia de empuje real
T_ENGANCHE    = 0.5   # s minimo empujando aunque pierda la lectura

# --- Busqueda y evasion (no tocar, ya funcionan) ---
POT_BUSQUEDA  = 30
POT_AVANCE    = 32
POT_RETRO     = 40
POT_GIRO_EVA  = 35
T_RETRO       = 0.45
T_GIRO_MIN    = 0.25
T_GIRO_MAX    = 0.50
T_GIRO_BUSQ   = 0.30
T_AVANCE_BUSQ = 0.60

# ---------------- MOVIMIENTO ----------------

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
    izq = (leer("L1") < UMBRAL_NEGRO or leer("L2") < UMBRAL_NEGRO)
    der = (leer("R1") < UMBRAL_NEGRO or leer("R2") < UMBRAL_NEGRO)
    if izq:
        return "izq"
    if der:
        return "der"
    return None

def distancia():
    return mbuild.ultrasonic2.get(1)

# ---------------- COMPORTAMIENTOS ----------------

def evadir(lado):
    cyberpi.led.on(0, 0, 255)
    parar()
    time.sleep(0.05)
    recto(-POT_RETRO)
    time.sleep(T_RETRO)
    direccion = 1 if lado == "izq" else -1
    girar(POT_GIRO_EVA, direccion)
    time.sleep(T_GIRO_MIN + random.random() * (T_GIRO_MAX - T_GIRO_MIN))
    parar()

def embestir():
    """Empuja a fondo. Sale solo si pisa la cinta (no perder el ring)
    o si se acaba el enganche sin rival enfrente."""
    cyberpi.led.on(255, 0, 0)
    cyberpi.timer.reset()
    while True:
        if borde() is not None:      # el ring manda sobre el ataque
            return
        recto(POT_EMBESTIDA)
        d = distancia()
        if 0 < d < DIST_EMBESTIR:
            cyberpi.timer.reset()    # sigue en contacto: renueva enganche
        elif cyberpi.timer.get() > T_ENGANCHE:
            return                   # lo perdio de verdad
        time.sleep(0.01)

# ---------------- INICIO ----------------

parar()
cyberpi.console.clear()
cyberpi.console.println("MODO SUMO v9")
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

    d = distancia()

    # PRIORIDAD 2a: rival encima -> embestida a fondo
    if 0 < d < DIST_EMBESTIR:
        embestir()
        girando = True
        cyberpi.timer.reset()
        estado_prev = "embiste"
        continue

    # PRIORIDAD 2b: rival a la vista -> acercarse
    if 0 < d < DIST_VISTA:
        if estado_prev != "acerca":
            cyberpi.led.on(255, 80, 0)
            estado_prev = "acerca"
        recto(POT_ACERCARSE)
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
