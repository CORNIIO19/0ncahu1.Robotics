import gamepad, event, time, cyberpi, mbot2

@event.start
def on_start():
    cyberpi.wifi.connect('#WUAMC', 'wificua6')
    time.sleep(3)

    if cyberpi.wifi.is_connect():
        cyberpi.console.println("WiFi OK!")
        cyberpi.led.on(0, 255, 0)
    else:
        cyberpi.console.println("Sin WiFi")
        cyberpi.led.on(255, 0, 0)

    time.sleep(1)
    cyberpi.led.off()

    while True:
        # ─── AVANZAR — R1 ───
        if gamepad.is_key_pressed('R1'):
            mbot2.forward(70, 0.2)
            cyberpi.console.println("Avanzando")

        # ─── RETROCEDER — L1 ───
        elif gamepad.is_key_pressed('L1'):
            mbot2.backward(70, 0.2)
            cyberpi.console.println("Retrocediendo")

        else:
            # ─── JOYSTICK IZQUIERDO — GIROS ───
            lx = gamepad.get_joystick('Lx')

            if lx > 20:
                velocidad = int((lx / 100) * 80)
                mbot2.turn_right(velocidad, 0.2)
                cyberpi.console.println("Der: " + str(velocidad))

            elif lx < -20:
                velocidad = int((abs(lx) / 100) * 80)
                mbot2.turn_left(velocidad, 0.2)
                cyberpi.console.println("Izq: " + str(velocidad))

            else:
                mbot2.stop()

        time.sleep(0.1)