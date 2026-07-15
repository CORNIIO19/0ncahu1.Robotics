# =============================================================
#  MODO SUMO - mBot2 (Upload mode, MicroPython)
#  Arquitectura de 3 comportamientos por prioridad:
#    1. EVASION  -> detecta borde blanco del ring y se aleja
#    2. ATAQUE   -> rival detectado con ultrasonico, empuja a fondo
#    3. BUSQUEDA -> gira y avanza en patron de rastreo
#
#  Instalar el MISMO programa en ambos robots.
#  Inicio: boton A -> cuenta regresiva de 5 s (regla de sumo).
# =============================================================

import cyberpi
import mbot2
import mbuild
import time
import random

# ---------------- CONFIGURACION (calibrar aqui) ----------------
DIST_ATAQUE   = 40    # cm: distancia maxima para considerar "rival visto"
POT_ATAQUE    = 100   # potencia de empuje
POT_BUSQUEDA  = 55    # potencia al girar buscando (>=50 por friccion de orugas)
POT_AVANCE    = 65    # potencia al avanzar en busqueda
POT_RETRO     = 80    # potencia de retroceso en evasion
T_RETRO       = 0.45  # s de retroceso al ver el borde
T_GIRO_MIN    = 0.30  # s minimo de giro tras evadir
T_GIRO_MAX    = 0.60  # s maximo de giro tras evadir (aleatorio entre ambos)
T_GIRO_BUSQ   = 0.35  # s girando en cada ciclo de busqueda
T_AVANCE_BUSQ = 0.50  # s avanzando en cada ciclo de busqueda

# ---------------- MOVIMIENTO ----------------
# Motor derecho montado en espejo: recto = (p, -p)

def recto(p):
    mbot2.drive_power(p, -p)

def girar(p, direccion):
    # direccion = 1 gira a la derecha, -1 gira a la izquierda (sobre su eje)
    mbot2.drive_power(direccion * p, direccion * p)

def parar():
    mbot2.drive_power(0, 0)

# ---------------- SENSORES ----------------

def borde():
    """Devuelve 'izq', 'der' o None segun que lado pisa el borde blanco."""
    izq = (mbuild.quad_rgb_sensor.is_color("L1", "white", 1) or
           mbuild.quad_rgb_sensor.is_color("L2", "white", 1))
    der = (mbuild.quad_rgb_sensor.is_color("R1", "white", 1) or
           mbuild.quad_rgb_sensor.is_color("R2", "white", 1))
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
    """Retrocede y gira hacia el lado contrario al borde detectado."""
    cyberpi.led.on(0, 0, 255)          # azul = evasion
    recto(-POT_RETRO)
    time.sleep(T_RETRO)
    # gira alejandose del borde; duracion aleatoria para
    # que dos robots identicos no queden en bucle espejo
    direccion = 1 if lado == "izq" else -1
    girar(POT_BUSQUEDA + 15, direccion)
    time.sleep(T_GIRO_MIN + random.random() * (T_GIRO_MAX - T_GIRO_MIN))
    parar()

# ---------------- SECUENCIA DE INICIO ----------------

cyberpi.console.clear()
cyberpi.console.println("MODO SUMO")
cyberpi.console.println("Boton A = iniciar")
cyberpi.led.on(255, 255, 255)

while not cyberpi.controller.is_press("a"):
    time.sleep(0.05)

# Cuenta regresiva de 5 s (regla estandar de sumo)
for i in range(5, 0, -1):
    cyberpi.console.clear()
    cyberpi.console.println("Inicio en " + str(i))
    cyberpi.audio.play_tone(700, 0.15)
    time.sleep(0.85)

cyberpi.console.clear()
cyberpi.console.println("LUCHA!")
cyberpi.audio.play_tone(1200, 0.3)

# Direccion inicial de busqueda aleatoria (rompe la simetria entre robots)
dir_busqueda = random.choice([1, -1])
girando = True
estado_prev = ""
cyberpi.timer.reset()

# ---------------- BUCLE PRINCIPAL ----------------

while True:
    lado = borde()

    # PRIORIDAD 1: no salir del ring
    if lado is not None:
        evadir(lado)
        girando = True
        cyberpi.timer.reset()
        estado_prev = "evade"
        continue

    # PRIORIDAD 2: atacar si el rival esta enfrente
    if rival_cerca():
        if estado_prev != "ataque":
            cyberpi.led.on(255, 0, 0)   # rojo = ataque
            estado_prev = "ataque"
        recto(POT_ATAQUE)
        time.sleep(0.01)
        continue

    # PRIORIDAD 3: busqueda (girar / avanzar alternado, sin bloquear)
    if estado_prev != "busca":
        cyberpi.led.on(255, 180, 0)     # amarillo = busqueda
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
