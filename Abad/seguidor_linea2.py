# =============================================================
#  SEGUIDOR DE LINEA PD v2 - mBot2 + CyberPi, chasis con RUEDAS
#
#  Por que cambia respecto a v1:
#    get_offset_track() devolvia 0.0 siempre. Esa funcion depende
#    de la calibracion INTERNA del sensor; si no reconoce la linea
#    en tu superficie, reporta "sin desvio" para siempre y el PD
#    no tiene nada que corregir.
#
#  Aqui calculamos el error NOSOTROS, con los valores crudos de
#  gris de las 4 sondas (lo mismo que ya funciono en el sumo).
#
#  ARRANQUE:
#    A -> sondas sobre el FONDO (fuera de la linea)
#    B -> sondas sobre la LINEA negra
#    A -> a seguir la linea
#  Boton B durante la marcha = paro.
# =============================================================

import cyberpi
import mbot2
import mbuild
import time

# ---------------- PARAMETROS ----------------
BASE   = 30     # potencia de crucero (ruedas: 25-35)
KP     = 0.45   # proporcional
KD     = 60     # derivativo (sube si serpentea)
MAX    = 70     # recorte de potencia por motor

UMBRAL_LINEA = 0.30  # cuanta "negrura" total hace falta para
                     # considerar que si hay linea debajo
POT_BUSCAR   = 30    # potencia al girar buscando la linea perdida
DT           = 0.01

SONDAS = ["L2", "L1", "R1", "R2"]
PESOS  = {"L2": -3.0, "L1": -1.0, "R1": 1.0, "R2": 3.0}

fondo = {}
linea = {}

# ---------------- MOVIMIENTO ----------------
# Motor derecho en espejo

def motores(izq, der):
    if izq > MAX:  izq = MAX
    if izq < -MAX: izq = -MAX
    if der > MAX:  der = MAX
    if der < -MAX: der = -MAX
    mbot2.drive_power(izq, -der)

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
    """0.0 = igual que el fondo, 1.0 = igual que la linea."""
    f = fondo[sonda]
    l = linea[sonda]
    if f == l:
        return 0.0
    v = (f - leer(sonda)) / (f - l)
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v

def error_linea():
    """Devuelve (error, hay_linea).
    error: -100 (linea a la izquierda) a +100 (a la derecha), 0 = centrado."""
    b = {}
    total = 0.0
    for s in SONDAS:
        b[s] = negrura(s)
        total += b[s]

    if total < UMBRAL_LINEA:
        return 0.0, False

    suma = 0.0
    for s in SONDAS:
        suma += PESOS[s] * b[s]
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
    global fondo, linea

    cyberpi.console.clear()
    cyberpi.console.println("SEGUIDOR PD v2")
    cyberpi.console.println("Sondas en el FONDO")
    cyberpi.console.println("A = medir")
    cyberpi.led.on(255, 255, 255)
    esperar("a")
    fondo = promediar()
    cyberpi.audio.play_tone(1000, 0.2)

    cyberpi.console.clear()
    cyberpi.console.println("Sondas en la LINEA")
    cyberpi.console.println("B = medir")
    cyberpi.led.on(0, 0, 255)
    esperar("b")
    linea = promediar()
    cyberpi.audio.play_tone(500, 0.2)

    cyberpi.console.clear()
    cyberpi.console.println("fondo: " + fila(fondo))
    cyberpi.console.println("linea: " + fila(linea))
    cyberpi.console.println("Deben ser MUY")
    cyberpi.console.println("distintos.")
    cyberpi.console.println("A = seguir linea")
    cyberpi.led.on(0, 255, 0)
    esperar("a")

# ---------------- INICIO ----------------

parar()
calibrar()
cyberpi.audio.play_tone(1200, 0.2)

error_ant = 0.0
ultimo_lado = 1     # por donde se perdio la linea
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
        continue

    error, hay = error_linea()

    # --- Linea perdida: gira hacia el lado por donde se fue ---
    if not hay:
        cyberpi.led.on(255, 180, 0)
        girar(POT_BUSCAR, ultimo_lado)
        ciclos += 1
        if ciclos >= 30:
            ciclos = 0
            cyberpi.console.clear()
            cyberpi.console.println("LINEA PERDIDA")
            cyberpi.console.println(fila({s: leer(s) for s in SONDAS}))
        time.sleep(DT)
        continue

    if error > 5:
        ultimo_lado = 1
    elif error < -5:
        ultimo_lado = -1

    # --- PD ---
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
