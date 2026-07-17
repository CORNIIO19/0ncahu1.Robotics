# =============================================================
#  SEGUIDOR DE LINEA PD v3 - mBot2 + CyberPi, ruedas
#  Afinado para el TAPETE OFICIAL DE MAKEBLOCK:
#    - fondo BLANCO, linea negra ancha
#    - la recta tiene TRAMOS DE COLOR (rojo, amarillo, verde, azul)
#      que son parte de la linea: el amarillo refleja casi como el
#      blanco, asi que hay que tolerarlo o el robot "pierde" la linea
#
#  El error se calcula con los valores crudos de gris (get_gray),
#  no con get_offset_track (que devolvia 0.0 siempre).
#
#  ARRANQUE:
#    A -> sondas sobre el BLANCO
#    B -> sondas sobre la LINEA NEGRA
#    A -> a correr
#  Boton B en marcha = paro.
# =============================================================

import cyberpi
import mbot2
import mbuild
import time

# ---------------- PARAMETROS ----------------
BASE   = 30     # potencia de crucero (ruedas: 25-35)
KP     = 0.45   # proporcional
KD     = 60     # derivativo (sube si serpentea)
MAX    = 70     # recorte por motor

UMBRAL_LINEA = 0.25  # negrura total minima para decir "hay linea".
                     # BAJO a proposito: los tramos de color reflejan
                     # mas que el negro y no deben contar como perdida.
T_GRACIA     = 0.30  # s de seguir DERECHO al perder la linea antes
                     # de ponerse a buscar (cubre color y cruces)
POT_BUSCAR   = 28
DT           = 0.01

SONDAS = ["L2", "L1", "R1", "R2"]
PESOS  = {"L2": -3.0, "L1": -1.0, "R1": 1.0, "R2": 3.0}

blanco = {}
negro  = {}

# ---------------- MOVIMIENTO ----------------

def motores(izq, der):
    if izq > MAX:  izq = MAX
    if izq < -MAX: izq = -MAX
    if der > MAX:  der = MAX
    if der < -MAX: der = -MAX
    mbot2.drive_power(izq, -der)

def recto(p):
    mbot2.drive_power(p, -p)

def girar(p, direccion):
    mbot2.drive_power(direccion * p, direccion * p)

def parar():
    mbot2.drive_power(0, 0)

# ---------------- SENSOR ----------------

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

def negrura(sonda):
    """0.0 = blanco del tapete, 1.0 = negro de la linea.
    Un tramo de color cae en medio (0.3-0.7) y aun cuenta."""
    b = blanco[sonda]
    n = negro[sonda]
    if b == n:
        return 0.0
    v = (b - leer(sonda)) / (b - n)
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v

def error_linea():
    """(error, hay_linea). error de -100 (linea a la izq) a +100 (der)."""
    val = {}
    total = 0.0
    for s in SONDAS:
        val[s] = negrura(s)
        total += val[s]

    if total < UMBRAL_LINEA:
        return 0.0, False

    suma = 0.0
    for s in SONDAS:
        suma += PESOS[s] * val[s]
    return (suma / total) * 33.0, True

def esperar(boton):
    while not cyberpi.controller.is_press(boton):
        time.sleep(0.05)
    time.sleep(0.3)

def fila(d):
    return (str(int(d["L2"])) + " " + str(int(d["L1"])) + " " +
            str(int(d["R1"])) + " " + str(int(d["R2"])))

# ---------------- CALIBRACION ----------------

def calibrar():
    global blanco, negro

    cyberpi.console.clear()
    cyberpi.console.println("SEGUIDOR v3")
    cyberpi.console.println("Sondas en BLANCO")
    cyberpi.console.println("A = medir")
    cyberpi.led.on(255, 255, 255)
    esperar("a")
    blanco = promediar()
    cyberpi.audio.play_tone(1000, 0.2)

    cyberpi.console.clear()
    cyberpi.console.println("Sondas en NEGRO")
    cyberpi.console.println("B = medir")
    cyberpi.led.on(0, 0, 255)
    esperar("b")
    negro = promediar()
    cyberpi.audio.play_tone(500, 0.2)

    cyberpi.console.clear()
    cyberpi.console.println("blanco: " + fila(blanco))
    cyberpi.console.println("negro : " + fila(negro))
    cyberpi.console.println("A = correr")
    cyberpi.led.on(0, 255, 0)
    esperar("a")

# ---------------- INICIO ----------------

parar()
calibrar()
cyberpi.audio.play_tone(1200, 0.2)

error_ant = 0.0
ultimo_lado = 1
perdida = False
ciclos = 0

# ---------------- BUCLE DE CONTROL ----------------

while True:

    if cyberpi.controller.is_press("b"):
        parar()
        cyberpi.led.on(255, 255, 255)
        cyberpi.console.clear()
        cyberpi.console.println("PARO")
        cyberpi.console.println("A = seguir")
        esperar("a")
        error_ant = 0.0
        perdida = False
        continue

    error, hay = error_linea()

    # ---- LINEA PERDIDA ----
    if not hay:
        if not perdida:              # acaba de perderla: arranca el reloj
            perdida = True
            cyberpi.timer.reset()

        if cyberpi.timer.get() < T_GRACIA:
            cyberpi.led.on(255, 180, 0)   # amarillo: sigo derecho, ya volvera
            recto(BASE)
        else:
            cyberpi.led.on(255, 0, 255)   # morado: ahora si, a buscarla
            girar(POT_BUSCAR, ultimo_lado)

        ciclos += 1
        if ciclos >= 30:
            ciclos = 0
            cyberpi.console.clear()
            cyberpi.console.println("SIN LINEA")
            cyberpi.console.println(fila({s: leer(s) for s in SONDAS}))
        time.sleep(DT)
        continue

    perdida = False

    if error > 5:
        ultimo_lado = 1
    elif error < -5:
        ultimo_lado = -1

    # ---- PD ----
    correccion = KP * error + KD * (error - error_ant)
    error_ant = error

    motores(BASE + correccion, BASE - correccion)

    if error < -10:
        cyberpi.led.on(0, 0, 255)
    elif error > 10:
        cyberpi.led.on(255, 0, 0)
    else:
        cyberpi.led.on(0, 255, 0)

    ciclos += 1
    if ciclos >= 30:
        ciclos = 0
        cyberpi.console.clear()
        cyberpi.console.println("error: " + str(int(error)))
        cyberpi.console.println("corr : " + str(int(correccion)))
        cyberpi.console.println(fila({s: leer(s) for s in SONDAS}))

    time.sleep(DT)
