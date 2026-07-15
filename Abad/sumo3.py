# =============================================================
#  MODO SUMO v5 - mBot2 (Upload mode, MicroPython)
#  Programa completo con movimiento autonomo. Fuerza max = 60%.
#
#  Calibracion de 2 puntos (piso y cinta) al inicio:
#    A -> mide el PISO claro
#    B -> mide la CINTA negra
#    A -> confirma y arranca la cuenta regresiva
#
#  Comportamientos por prioridad:
#    1. EVASION (azul)    -> pisa la cinta, retrocede y gira
#    2. ATAQUE  (rojo)    -> rival a la vista, empuja
#    3. BUSQUEDA(amarillo)-> gira y avanza rastreando
# =============================================================

import cyberpi
import mbot2
import mbuild
import time
import random

# ---------------- CONFIGURACION ----------------
SENTIDO       = 1     # -1 si el robot avanza al reves
                      # (el frente = lado del quad RGB + ultrasonico)

# Fuerza al 60%. Ojo: por debajo de ~50 las orugas no vencen la friccion.
POT_ATAQUE    = 60
POT_AVANCE    = 55
POT_BUSQUEDA  = 50    # giro en busqueda
POT_RETRO     = 60
POT_GIRO_EVA  = 55    # giro al evadir

DIST_ATAQUE   = 40    # cm para considerar "rival visto"
T_RETRO       = 0.55  # s de retroceso al pisar la cinta
T_GIRO_MIN    = 0.35  # s minimo de giro tras evadir
T_GIRO_MAX    = 0.70  # s maximo de giro tras evadir
T_GIRO_BUSQ   = 0.45  # s girando en cada ciclo de busqueda
T_AVANCE_BUSQ = 0.90  # s avanzando en cada ciclo de busqueda

SONDAS = ["L2", "L1", "R1", "R2"]

piso   = {}
cinta  = {}
umbral = {}

# ---------------- MOVIMIENTO ----------------
# Motor derecho montado en espejo: recto = (p, -p)

def recto(p):
    mbot2.drive_power(SENTIDO * p, -SENTIDO * p)

def girar(p, direccion):
    # direccion = 1 derecha, -1 izquierda (sobre su eje)
    mbot2.drive_power(direccion * p, direccion * p)

def parar():
    mbot2.drive_power(0, 0)

# ---------------- SENSORES ----------------

def leer(sonda):
    return mbuild.quad_rgb_sensor.get_gray(sonda, 1)

def promediar(n=12):
    suma = {}
    for s in SONDAS:
        suma[s] = 0
    for _ in range(n):
        for s in SONDAS:
            suma[s] += leer(s)
        time.sleep(0.02)
    r = {}
    for s in SONDAS:
        r[s] = suma[s] / n
    return r

def fila(d):
    return (str(int(d["L2"])) + " " + str(int(d["L1"])) + " " +
            str(int(d["R1"])) + " " + str(int(d["R2"])))

def esperar(boton):
    while not cyberpi.controller.is_press(boton):
        time.sleep(0.05)
    time.sleep(0.3)     # anti-rebote

def borde():
    """'izq', 'der' o None segun que lado pisa la cinta negra."""
    izq = (leer("L1") < umbral["L1"] or leer("L2") < umbral["L2"])
    der = (leer("R1") < umbral["R1"] or leer("R2") < umbral["R2"])
    if izq:
        return "izq"
    if der:
        return "der"
    return None

def rival_cerca():
    d = mbuild.ultrasonic2.get(1)
    return 0 < d < DIST_ATAQUE

# ---------------- CALIBRACION ----------------

def calibrar():
    global piso, cinta, umbral

    cyberpi.console.clear()
    cyberpi.console.println("SUMO v5")
    cyberpi.console.println("Sondas en el PISO")
    cyberpi.console.println("A = medir")
    cyberpi.led.on(255, 255, 255)
    esperar("a")
    piso = promediar()
    cyberpi.audio.play_tone(1000, 0.2)

    cyberpi.console.clear()
    cyberpi.console.println("Sondas en la CINTA")
    cyberpi.console.println("B = medir")
    cyberpi.led.on(0, 0, 255)
    esperar("b")
    cinta = promediar()
    cyberpi.audio.play_tone(500, 0.2)

    for s in SONDAS:
        umbral[s] = (piso[s] + cinta[s]) / 2

    cyberpi.console.clear()
    cyberpi.console.println("piso : " + fila(piso))
    cyberpi.console.println("cinta: " + fila(cinta))
    cyberpi.console.println("umbr : " + fila(umbral))
    cyberpi.console.println("Robot al ring")
    cyberpi.console.println("A = LUCHAR")
    cyberpi.led.on(0, 255, 0)
    esperar("a")

# ---------------- COMPORTAMIENTOS ----------------

def evadir(lado):
    """Frena, retrocede y gira alejandose de la cinta."""
    cyberpi.led.on(0, 0, 255)
    parar()
    time.sleep(0.05)
    recto(-POT_RETRO)
    time.sleep(T_RETRO)
    direccion = 1 if lado == "izq" else -1
    girar(POT_GIRO_EVA, direccion)
    time.sleep(T_GIRO_MIN + random.random() * (T_GIRO_MAX - T_GIRO_MIN))
    parar()
    return direccion

# ---------------- INICIO ----------------

parar()
calibrar()

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

    # Boton B en cualquier momento = paro de emergencia
    if cyberpi.controller.is_press("b"):
        parar()
        cyberpi.led.on(255, 255, 255)
        cyberpi.console.clear()
        cyberpi.console.println("PARO")
        cyberpi.console.println("A = seguir")
        esperar("a")
        cyberpi.timer.reset()
        estado_prev = ""
        continue

    lado = borde()

    # PRIORIDAD 1: no salir del ring
    if lado is not None:
        dir_busqueda = evadir(lado)
        girando = False
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
            cyberpi.timer.reset()

    time.sleep(0.01)
