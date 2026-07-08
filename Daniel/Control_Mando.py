import event, time, cyberpi, gamepad, mbot2

@event.start
def on_start():
    cyberpi.wifi.connect('#WUAMC', 'wificua6')
    time.sleep(3)

    if cyberpi.wifi.is_connect():
        cyberpi.display.show_label("WiFi OK!", 12, "center", index=0)
        cyberpi.led.on(0, 255, 0)
    else:
        cyberpi.display.show_label("Sin WiFi", 12, "center", index=0)
        cyberpi.led.on(255, 0, 0)

    time.sleep(1)
    cyberpi.led.off()

    while True:
        # ─── Leer entradas ───
        r1 = gamepad.is_key_pressed('R1')
        l1 = gamepad.is_key_pressed('L1')
        lx = gamepad.get_joystick('Lx')
        l_thumb = gamepad.is_key_pressed('L_Thumb')

        # ─── Sonido con stick izquierdo ───
        if l_thumb:
            cyberpi.audio.play_drum('snare', 0.25)

        # ─── Velocidad base (adelante/atrás) ───
        if r1:
            base = 100
            direccion = ">> ADELANTE"
            cyberpi.display.set_brush(0, 255, 0)
        elif l1:
            base = -80
            direccion = "<< ATRAS"
            cyberpi.display.set_brush(255, 0, 0)
        else:
            base = 0
            direccion = "-- STOP --"
            cyberpi.display.set_brush(255, 255, 255)

        # ─── Giro del joystick ───
        if lx > 20:
            giro = int((lx / 100) * 50)
            if base == 0:
                direccion = "> GIRANDO D"
                cyberpi.display.set_brush(0, 150, 255)
        elif lx < -20:
            giro = int((lx / 100) * 50)
            if base == 0:
                direccion = "< GIRANDO I"
                cyberpi.display.set_brush(0, 150, 255)
        else:
            giro = 0

        # ─── Combinar base + giro ───
        vel_em1 = base + giro
        vel_em2 = -base + giro

        # ─── Aplicar o parar ───
        if vel_em1 == 0 and vel_em2 == 0:
            mbot2.EM_stop("ALL")
        else:
            mbot2.EM_set_speed(vel_em1, "EM1")
            mbot2.EM_set_speed(vel_em2, "EM2")

        # ─── Velocímetro en pantalla ───
        velocidad_display = min(abs(base), 100)
        cyberpi.console.clear()
        cyberpi.display.show_label(direccion, 12, "center", index=0)
        cyberpi.barchart.add(velocidad_display)

        time.sleep(0.05)