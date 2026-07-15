# =============================================================
#  MODO SUMO v3 - mBot2 (Upload mode, MicroPython)
#  Cambio clave respecto a v2:
#   is_line() devolvia True todo el tiempo (evasion permanente).
#   Ahora se usan los valores CRUDOS de gris (get_gray) con
#   AUTOCALIBRACION al inicio: al presionar A, el robot lee el
#   fondo claro del ring y fija su propio umbral por sonda.
#   Linea negra = valor de gris muy por debajo del fondo.
# =============================================================

import cyberpi
import mbot2
import mbuild
import time
import random

# ---------------- CONFIGURACION ----------------
MODO_DEBUG    = False # True = imprime sensores, motores apagados
FACTOR_NEGRO  = 0.5   # umbral = fondo * factor (0.5 = mitad del brillo)
DIST_ATAQUE   = 40    # cm para considerar "rival visto"
POT_ATAQUE    = 85
POT_BUSQUEDA  = 50
POT_AVANCE    = 60
POT_RETRO     = 80
T_RETRO       = 0.50
T_GIRO_MIN    = 0.35
T_GIRO_MAX    = 0.65
T_GIRO_BUSQ   = 0.40
T_AVANCE_BUSQ = 0.80

SONDAS = ["L2", "L1", "R1", "R2"]

# ---------------- MOVIMIENTO ----------------

def recto(p):
    if not MODO_DEBUG:
        mbot2.drive_power(p, -p)

def girar(p, direccion):
    if not MODO_DEBUG:
        mbot2.drive_power(direccion * p, direccion * p)

def parar():
    mbot2.drive_power(0, 0)

# ---------------- SENSORES ----------------

def leer_gris(sonda):
    # Valor de reflejo 0-255 aprox. Fondo claro = alto, negro = bajo.
    return mbuild.quad_rgb_sensor.get_gray(sonda, 1)

umbral = {}  # umbral por sonda, se llena en la calibracion

def calibrar():
    """Con el robot sobre el FONDO CLARO del ring, mide cada sonda
    varias veces y fija el umbral de negro por sonda."""
    global umbral
    suma = {}
    for s in SONDAS:
        suma[s] = 0
    N = 10
    for _ in range(N):
        for s in SONDAS:
            suma[s] += leer_gris(s)
        time.sleep(0.02)
    for s in SONDAS:
        fondo = suma[s] / N
        umbral[s] = fondo * FACTOR_NEGRO
    cyberpi.console.println("Umbrales:")
    cyberpi.console.println(str(int(umbral["L2"])) + " " +
                            str(int(umbral["L1"])) + " " +
                            str(int(umbral["R1"])) + " " +
                            str(int(umbral["R2"])))

def borde():
    """'izq', 'der' o None segun que lado pisa la linea negra."""
    izq = (leer_gris("L1") < umbral["L1"] or
           leer_gris("L2") < umbral["L2"])
    der = (leer_gris("R1") < umbral["R1"] or
           leer_gris("R2") < umbral["R2"])
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
    cyberpi.led.on(0, 0, 255)
    parar()
    time.sleep(0.05)
    recto(-POT_RETRO)
    time.sleep(T_RETRO)
    direccion = 1 if lado == "izq" else -1
    girar(POT_BUSQUEDA + 15, direccion)
    time.sleep(T_GIRO_MIN + random.random() * (T_GIRO_MAX - T_GIRO_MIN))
    parar()
    return direccion

# ---------------- SECUENCIA DE INICIO ----------------

cyberpi.console.clear()
cyberpi.console.println("MODO SUMO v3")
cyberpi.console.println("Pon el robot sobre")
cyberpi.console.println("el fondo claro y")
cyberpi.console.println("presiona A")
cyberpi.led.on(255, 255, 255)

while not cyberpi.controller.is_press("a"):
    time.sleep(0.05)

calibrar()

# --- MODO DEBUG: valores crudos en pantalla, sin motores ---
if MODO_DEBUG:
    while True:
        cyberpi.console.clear()
        cyberpi.console.println("L2 L1 R1 R2")
        cyberpi.console.println(str(leer_gris("L2")) + " " +
                                str(leer_gris("L1")) + " " +
                                str(leer_gris("R1")) + " " +
                                str(leer_gris("R2")))
        cyberpi.console.println("borde: " + str(borde()))
        cyberpi.console.println("dist: " + str(mbuild.ultrasonic2.get(1)))
        time.sleep(0.3)

# Cuenta regresiva de 5 s
for i in range(5, 0, -1):
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
    lado = borde()

    if lado is not None:
        d = evadir(lado)
        dir_busqueda = d
        girando = False
        cyberpi.timer.reset()
        estado_prev = "evade"
        continue

    if rival_cerca():
        if estado_prev != "ataque":
            cyberpi.led.on(255, 0, 0)
            estado_prev = "ataque"
        recto(POT_ATAQUE)
        time.sleep(0.01)
        continue

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
