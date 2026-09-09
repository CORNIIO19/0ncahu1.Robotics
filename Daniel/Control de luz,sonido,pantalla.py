import cyberpi

cyberpi.display.show_label("Soy el cerebro", 16, "yellow")

while True:
    luz = cyberpi.light.get_value()          # sensor de luz integrado
    cyberpi.console.println("Luz: " + str(luz))

    if cyberpi.controller.is_press("a"):      # botón A del CyberPi
        cyberpi.audio.play_tone(440, 0.3)     # emite un tono
        cyberpi.led.on(0, 255, 0)             # enciende LEDs en verde