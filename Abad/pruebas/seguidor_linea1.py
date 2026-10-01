# =============================================================
#  SEGUIDOR DE LINEA PD - mBot2 + CyberPi, chasis con RUEDAS
#  (Upload mode, MicroPython)
#
#  Control PD sobre el desvio que reporta el Quad RGB Sensor:
#     correccion = kp*error + kd*(error - error_anterior)
#     izquierda = base + correccion
#     derecha   = base - correccion
#
#  Boton A = arrancar / reanudar
#  Boton B = paro
#
#  OJO: los parametros vienen afinados para RUEDAS. Con orugas
#  hay que subir BASE (~50) porque la friccion se come todo.
# =============================================================

import cyberpi
import mbot2
import mbuild
import time

# ---------------- PARAMETROS DEL CONTROL ----------------
BASE   = 30     # potencia de crucero (con ruedas 25-35 va bien)
KP     = 0.45   # proporcional: cuanto corrige segun el desvio actual
KD     = 60     # derivativo: frena la oscilacion (sube si serpentea)
MAX    = 70     # potencia maxima por motor (recorte de seguridad)

DT     = 0.01   # s entre ciclos de control

# ---------------- MOVIMIENTO ----------------
# Motor derecho en espejo: recto = (p, -p)

def motores(izq, der):
    # recorta al rango permitido
    if izq > MAX:  izq = MAX
    if izq < -MAX: izq = -MAX
    if der > MAX:  der = MAX
    if der < -MAX: der = -MAX
    mbot2.drive_power(izq, -der)

def parar():
    mbot2.drive_power(0, 0)

# ---------------- SENSOR ----------------
# get_offset_track devuelve el desvio respecto a la linea:
#   0 = centrado, negativo = linea a un lado, positivo = al otro
# Requiere poner el sensor en modo "enhance" antes de usarlo.

def preparar_sensor():
    mbuild.quad_rgb_sensor.color_mode("enhance")
    time.sleep(0.2)

def desvio():
    return mbuild.quad_rgb_sensor.get_offset_track(1)

def esperar(boton):
    while not cyberpi.controller.is_press(boton):
        time.sleep(0.05)
    time.sleep(0.3)

# ---------------- INICIO ----------------

parar()
preparar_sensor()

cyberpi.console.clear()
cyberpi.console.println("SEGUIDOR PD")
cyberpi.console.println("Robot sobre la")
cyberpi.console.println("linea. A = seguir")
cyberpi.led.on(255, 255, 255)
esperar("a")

cyberpi.audio.play_tone(1000, 0.2)
cyberpi.led.on(0, 255, 0)

error_ant = 0
ciclos = 0

# ---------------- BUCLE DE CONTROL ----------------

while True:

    # Paro de emergencia
    if cyberpi.controller.is_press("b"):
        parar()
        cyberpi.led.on(255, 255, 255)
        cyberpi.console.clear()
        cyberpi.console.println("PARO")
        cyberpi.console.println("A = seguir")
        esperar("a")
        error_ant = 0
        cyberpi.led.on(0, 255, 0)
        continue

    # --- LEER ---
    error = desvio()

    # --- CALCULAR (PD) ---
    correccion = KP * error + KD * (error - error_ant)
    error_ant = error

    # --- ACTUAR ---
    motores(BASE + correccion, BASE - correccion)

    # --- LEDs: verde centrado, azul/rojo segun a donde corrige ---
    if error < -10:
        cyberpi.led.on(0, 0, 255)
    elif error > 10:
        cyberpi.led.on(255, 0, 0)
    else:
        cyberpi.led.on(0, 255, 0)

    # --- Pantalla cada ~30 ciclos (no en cada vuelta: la frena) ---
    ciclos += 1
    if ciclos >= 30:
        ciclos = 0
        cyberpi.console.clear()
        cyberpi.console.println("error: " + str(error))
        cyberpi.console.println("corr : " + str(int(correccion)))

    time.sleep(DT)
