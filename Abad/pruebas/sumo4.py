# =============================================================
#  MODO SUMO v6 - mBot2 (Upload mode, MicroPython)
#  Fuerza max 60%. Cambios respecto a v5:
#   - SENTIDO = -1 por defecto (el robot iba de reversa)
#   - Umbral mas cerca de la cinta (MEZCLA) para que las manchas
#     y sombras del piso no disparen la evasion en falso
#   - Anti-rebote: se necesitan 2 lecturas seguidas de negro
#   - Pantalla en vivo: estado actual, sondas y distancia
#   - Chequeo del ultrasonico antes de arrancar
# =============================================================

import cyberpi
import mbot2
import mbuild
import time
import random

# ---------------- CONFIGURACION ----------------
SENTIDO       = -1    # 1 o -1. El frente = lado del quad RGB + ultrasonico.
                      # Si sale de reversa, cambia el signo.

MEZCLA        = 0.35  # umbral = cinta + MEZCLA*(piso - cinta)
                      # 0.35 -> pegado a la cinta = menos falsos positivos
                      # subelo (0.5) si no alcanza a ver la cinta

POT_ATAQUE    = 60
POT_AVANCE    = 55
POT_BUSQUEDA  = 50
POT_RETRO     = 60
POT_GIRO_EVA  = 55

DIST_ATAQUE   = 40    # cm para considerar "rival visto"
T_RETRO       = 0.55
T_GIRO_MIN    = 0.35
T_GIRO_MAX    = 0.70
T_GIRO_BUSQ   = 0.45
T_AVANCE_BUSQ = 0.90

SONDAS = ["L2", "L1", "R1", "R2"]

piso   = {}
cinta  = {}
umbral = {}

# ---------------- MOVIMIENTO ----------------

def recto(p):
    mbot2.drive_power(SENTIDO * p, -SENTIDO * p)

def girar(p, direccion):
    mbot2.drive_power(direccion * p, direccion * p)

def parar():
    mbot2.drive_power(0, 0)

# ---------------- SENSORES ----------------

def leer(sonda):
    return mbuild.quad_rgb_sensor.get_gray(sonda, 1)

def distancia():
    return mbuild.ultrasonic2.get(1)

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
    time.sleep(0.3)

def lee_borde():
    """'izq', 'der' o None. Lectura cruda, sin anti-rebote."""
    izq = (leer("L1") < umbral["L1"] or leer("L2") < umbral["L2"])
    der = (leer("R1") < umbral["R1"] or leer("R2") < umbral["R2"])
    if izq:
        return "izq"
    if der:
        return "der"
    return None

def borde():
    """Confirma con 2 lecturas seguidas: evita falsos por manchas."""
    a = lee_borde()
    if a is None:
        return None
    time.sleep(0.008)
    b = lee_borde()
    if b is None:
        return None
    return a

def rival_cerca():
    d = distancia()
    return 0 < d < DIST_ATAQUE

# ---------------- CALIBRACION ----------------

def calibrar():
    global piso, cinta, umbral

    cyberpi.console.clear()
    cyberpi.console.println("SUMO v6")
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
        umbral[s] = cinta[s] + MEZCLA * (piso[s] - cinta[s])

    cyberpi.console.clear()
    cyberpi.console.println("piso : " + fila(piso))
    cyberpi.console.println("cinta: " + fila(cinta))
    cyberpi.console.println("umbr : " + fila(umbral))
    cyberpi.console.println("A = probar sonar")
    cyberpi.led.on(0, 255, 0)
    esperar("a")

def probar_sonar():
    """Muestra la distancia en vivo. Acerca la mano/el rival.
    Verde = detecta. A = continuar."""
    cyberpi.console.clear()
    while not cyberpi.controller.is_press("a"):
        d = distancia()
        cyberpi.console.clear()
        cyberpi.console.println("SONAR")
        cyberpi.console.println("dist: " + str(d))
        cyberpi.console.println("borde: " + str(lee_borde()))
        cyberpi.console.println("A = LUCHAR")
        if 0 < d < DIST_ATAQUE:
            cyberpi.led.on(255, 0, 0)
        else:
            cyberpi.led.on(0, 40, 0)
        time.sleep(0.2)
    time.sleep(0.3)

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
    return direccion

# ---------------- INICIO ----------------

parar()
calibrar()
probar_sonar()

for i in range(5, 0, -1):
    cyberpi.console.clear()
    cyberpi.console.println("Inicio en " + str(i))
    cyberpi.audio.play_tone(700, 0.15)
    time.sleep(0.85)

cyberpi.audio.play_tone(1200, 0.3)

dir_busqueda = random.choice([1, -1])
girando = True
estado = ""
estado_prev = ""
ciclos = 0
cyberpi.timer.reset()

# ---------------- BUCLE PRINCIPAL ----------------

while True:

    # Boton B = paro de emergencia
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
    d = distancia()

    # --- Pantalla de diagnostico (cada ~20 ciclos) ---
    ciclos += 1
    if ciclos >= 20:
        ciclos = 0
        cyberpi.console.clear()
        cyberpi.console.println(estado)
        cyberpi.console.println("dist: " + str(d))
        cyberpi.console.println("borde: " + str(lado))
        cyberpi.console.println(fila({s: leer(s) for s in SONDAS}))

    # PRIORIDAD 1: no salir del ring
    if lado is not None:
        estado = "EVADE"
        dir_busqueda = evadir(lado)
        girando = False
        cyberpi.timer.reset()
        estado_prev = "evade"
        continue

    # PRIORIDAD 2: atacar
    if 0 < d < DIST_ATAQUE:
        estado = "ATAQUE"
        if estado_prev != "ataque":
            cyberpi.led.on(255, 0, 0)
            estado_prev = "ataque"
        recto(POT_ATAQUE)
        time.sleep(0.01)
        continue

    # PRIORIDAD 3: buscar
    estado = "BUSCA"
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
