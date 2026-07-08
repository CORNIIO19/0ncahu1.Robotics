import event, time, cyberpi, mbot2

SILENCIO = 15
CHILL    = 40
GROOVE   = 65
HYPE     = 90

def set_leds(r, g, b):
    cyberpi.led.on(r, g, b, 0)
    cyberpi.led.on(r, g, b, 1)
    cyberpi.led.on(r, g, b, 2)

@event.start
def on_start():
    cyberpi.display.clear()
    cyberpi.console.println("Robot DJ ON")
    time.sleep(1)
    direccion = 1

    while True:
        # Para y espera que baje ruido de motores
        mbot2.drive_speed(0, 0)
        time.sleep(0.12)
        vol = cyberpi.get_loudness()

        if vol <= SILENCIO:
            set_leds(10, 10, 10)
            cyberpi.console.println("silencio: " + str(vol))
            # no hay movimiento, solo espera corta
            time.sleep(0.1)

        elif vol <= CHILL:
            set_leds(0, 100, 255)
            cyberpi.console.println("~ chill ~ " + str(vol))
            if direccion == 1:
                mbot2.drive_speed(25, -25)
            else:
                mbot2.drive_speed(-25, 25)
            time.sleep(0.5)       # ← más tiempo de movimiento
            direccion = -direccion

        elif vol <= GROOVE:
            set_leds(255, 180, 0)
            cyberpi.console.println(">> groove " + str(vol))
            if direccion == 1:
                mbot2.drive_speed(50, 50)
            else:
                mbot2.drive_speed(-50, -50)
            time.sleep(0.5)       # ← más tiempo de movimiento
            direccion = -direccion

        elif vol <= HYPE:
            set_leds(255, 0, 80)
            cyberpi.console.println("!!! HYPE " + str(vol))
            if direccion == 1:
                mbot2.drive_speed(80, -80)
            else:
                mbot2.drive_speed(-80, 80)
            time.sleep(0.4)       # ← un poco menos en hype para que se vea más frenético
            direccion = -direccion