# =============================================================
#  MODO SUMO v4 - mBot2 (Upload mode, MicroPython)
#  Cambios respecto a v3:
#   - SENTIDO: si el robot camina "de reversa" (los sensores
#     quedan atras), pon SENTIDO = -1 y todo se invierte.
#   - PARAR_EN_BORDE: al pisar la linea negra el robot se
#     DETIENE, suena, muestra que lado la vio y espera el
#     boton A para continuar. Sirve para verificar deteccion.
#     Para competir de verdad, pon PARAR_EN_BORDE = False.
# =============================================================

import cyberpi
import mbot2
import mbuild
import time
import random

# ---------------- CONFIGURACION ----------------
MODO_DEBUG     = False # True = imprime sensores, motores apagados
PARAR_EN_BORDE = True  # True = se detiene al ver la linea (prueba)
SENTIDO        = 1     # -1 si el robot avanza al reves de lo esperado
FACTOR_NEGRO   = 0.5   # umbral = fondo * factor
DIST_ATAQUE    = 40
POT_ATAQUE     = 85
POT_BUSQUEDA   = 50
POT_AVANCE     = 60
POT_RETRO      = 80
T_RETRO        = 0.50
T_GIRO_MIN     = 0.35
T_GIRO_MAX     = 0.65
T_GIRO_BUSQ    = 0.40
T_AVANCE_BUSQ  = 0.80

SONDAS = ["L2", "L1", "R1", "R2"]

# ---------------- MOVIMIENTO ----------------
# Motor derecho en espejo. SENTIDO invierte que lado es "el frente":
# el frente correcto es donde estan el quad RGB y el ultrasonico.

def recto(p):
    if not MODO_DEBUG:
        mbot2.drive_power(SENTIDO * p, -SENTIDO * p)

def girar(p, direccion):
    if not MODO_DEBUG:
        mbot2.drive_power(direccion * p, direccion * p)

def parar():
    mbot2.drive_power(0, 0)

# ---------------- SENSORES ----------------

def leer_gris(sonda):
    return mbuild.quad_rgb_sensor.get_gray(sonda, 1)

umbral = {}

def calibrar():
    """Con el robot sobre el FONDO CLARO (dentro del ring, sin pisar
    la linea), mide cada sonda y fija el umbral de negro."""
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
        umbral[s] = (suma[s] / N) * FACTOR_NEGRO
    cyberpi.console.println("Umbrales:")
    cyberpi.console.println(str(int(umbral["L2"])) + " " +
                            str(int(umbral["L1"])) + " " +
                            str(int(umbral["R1"])) + " " +
                            str(int(umbral["R2"])))

def borde():
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

def prueba_borde(lado):
    """Se detiene al ver la linea y espera el boton A."""
    parar()
    cyberpi.led.on(0, 255, 0)           # verde = linea detectada
    cyberpi.audio.play_tone(900, 0.2)
    cyberpi.console.clear()
    cyberpi.console.println("BORDE: " + lado)
    cyberpi.console.println("L2 L1 R1 R2")
    cyberpi.console.println(str(leer_gris("L2")) + " " +
                            str(leer_gris("L1")) + " " +
                            str(leer_gris("R1")) + " " +
                            str(leer_gris("R2")))
    cyberpi.console.println("A = continuar")
    while not cyberpi.controller.is_press("a"):
        time.sleep(0.05)
    cyberpi.console.clear()

# ---------------- SECUENCIA DE INICIO ----------------

cyberpi.console.clear()
cyberpi.console.println("MODO SUMO v4")
cyberpi.console.println("Robot DENTRO del")
cyberpi.console.println("ring, fondo claro,")
cyberpi.console.println("presiona A")
cyberpi.led.on(255, 255, 255)

while not cyberpi.controller.is_press("a"):
    time.sleep(0.05)

calibrar()

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
        if PARAR_EN_BORDE:
            prueba_borde(lado)          # se detiene y espera A
            recto(-POT_RETRO)           # se aparta de la linea
            time.sleep(T_RETRO)
            parar()
        else:
            dir_busqueda = evadir(lado)
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
