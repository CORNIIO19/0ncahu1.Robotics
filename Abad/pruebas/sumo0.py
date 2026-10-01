# =============================================================
#  MODO SUMO v2 - mBot2 (Upload mode, MicroPython)
#  Cambios respecto a v1:
#   - El limite del ring es una LINEA NEGRA sobre fondo claro:
#     ahora se detecta con is_line() (grises), no con is_color()
#   - Busqueda mas calmada: giro mas lento, direccion constante
#   - MODO_DEBUG para verificar sensores sin mover motores
# =============================================================

import cyberpi
import mbot2
import mbuild
import time
import random

# ---------------- CONFIGURACION ----------------
MODO_DEBUG    = False # True = solo imprime sensores, motores apagados
DIST_ATAQUE   = 40    # cm para considerar "rival visto"
POT_ATAQUE    = 85    # potencia de empuje (100 llega muy lanzado al borde)
POT_BUSQUEDA  = 50    # potencia al girar buscando
POT_AVANCE    = 60    # potencia al avanzar en busqueda
POT_RETRO     = 80    # potencia de retroceso en evasion
T_RETRO       = 0.50  # s de retroceso al pisar la linea
T_GIRO_MIN    = 0.35  # s minimo de giro tras evadir
T_GIRO_MAX    = 0.65  # s maximo de giro tras evadir
T_GIRO_BUSQ   = 0.40  # s girando en cada ciclo de busqueda
T_AVANCE_BUSQ = 0.80  # s avanzando en cada ciclo de busqueda

# ---------------- MOVIMIENTO ----------------
# Motor derecho en espejo: recto = (p, -p)

def recto(p):
    if not MODO_DEBUG:
        mbot2.drive_power(p, -p)

def girar(p, direccion):
    # direccion = 1 derecha, -1 izquierda (giro sobre su eje)
    if not MODO_DEBUG:
        mbot2.drive_power(direccion * p, direccion * p)

def parar():
    mbot2.drive_power(0, 0)

# ---------------- SENSORES ----------------
# El limite es una LINEA NEGRA: is_line() da True cuando la sonda
# ve oscuro (usa la misma calibracion de grises del seguidor de linea).

def borde():
    """Devuelve 'izq', 'der' o None segun que lado pisa la linea negra."""
    izq = (mbuild.quad_rgb_sensor.is_line("L1", 1) or
           mbuild.quad_rgb_sensor.is_line("L2", 1))
    der = (mbuild.quad_rgb_sensor.is_line("R1", 1) or
           mbuild.quad_rgb_sensor.is_line("R2", 1))
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
    """Frena, retrocede y gira alejandose de la linea."""
    cyberpi.led.on(0, 0, 255)          # azul = evasion
    parar()
    time.sleep(0.05)                    # micro-freno para no derrapar
    recto(-POT_RETRO)
    time.sleep(T_RETRO)
    direccion = 1 if lado == "izq" else -1
    girar(POT_BUSQUEDA + 15, direccion)
    time.sleep(T_GIRO_MIN + random.random() * (T_GIRO_MAX - T_GIRO_MIN))
    parar()
    return direccion

# ---------------- SECUENCIA DE INICIO ----------------

cyberpi.console.clear()
cyberpi.console.println("MODO SUMO v2")
cyberpi.console.println("Boton A = iniciar")
cyberpi.led.on(255, 255, 255)

while not cyberpi.controller.is_press("a"):
    time.sleep(0.05)

# --- MODO DEBUG: imprime sensores en pantalla, sin motores ---
if MODO_DEBUG:
    while True:
        cyberpi.console.clear()
        cyberpi.console.println("borde: " + str(borde()))
        cyberpi.console.println("dist: " + str(mbuild.ultrasonic2.get(1)))
        cyberpi.console.println("L2 L1 R1 R2")
        cyberpi.console.println(
            str(int(mbuild.quad_rgb_sensor.is_line("L2", 1))) + "  " +
            str(int(mbuild.quad_rgb_sensor.is_line("L1", 1))) + "  " +
            str(int(mbuild.quad_rgb_sensor.is_line("R1", 1))) + "  " +
            str(int(mbuild.quad_rgb_sensor.is_line("R2", 1))))
        time.sleep(0.3)

# Cuenta regresiva de 5 s (regla estandar de sumo)
for i in range(5, 0, -1):
    cyberpi.console.clear()
    cyberpi.console.println("Inicio en " + str(i))
    cyberpi.audio.play_tone(700, 0.15)
    time.sleep(0.85)

cyberpi.console.clear()
cyberpi.console.println("LUCHA!")
cyberpi.audio.play_tone(1200, 0.3)

# Direccion de busqueda: se elige una vez y solo cambia al evadir,
# asi el movimiento es mucho mas predecible (menos "loco")
dir_busqueda = random.choice([1, -1])
girando = True
estado_prev = ""
cyberpi.timer.reset()

# ---------------- BUCLE PRINCIPAL ----------------

while True:
    lado = borde()

    # PRIORIDAD 1: no salir del ring
    if lado is not None:
        d = evadir(lado)
        dir_busqueda = d
        girando = False              # tras evadir, avanza recto primero
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

    # PRIORIDAD 3: busqueda calmada (girar / avanzar alternado)
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
            cyberpi.timer.reset()

    time.sleep(0.01)
