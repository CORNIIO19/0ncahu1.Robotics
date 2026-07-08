import event, time, cyberpi, mbot2
import urequests

# ── Configuración ──────────────────────────────────────────────
WIFI_SSID  = "#WUAMC"
WIFI_PASS  = "wificua6"
DISTANCIA  = 135

# ── Tus datos de CallMeBot ─────────────────────────────────────
TU_NUMERO  = "525548431838"
API_KEY    = "6987656"

alarmando  = False

def set_leds(r, g, b):
    cyberpi.led.on(r, g, b, 0)
    cyberpi.led.on(r, g, b, 1)
    cyberpi.led.on(r, g, b, 2)

def enviar_whatsapp(distancia_detectada):
    try:
        mensaje = "Intruso+detectado+a+" + str(distancia_detectada) + "cm"
        cyberpi.cloud.tts("es", mensaje)
        cyberpi.console.println("Alerta sonora enviada!")
    except Exception as e:
        cyberpi.console.println("Error: " + str(e))

def alarma_on(distancia):
    global alarmando
    if not alarmando:
        alarmando = True
        cyberpi.console.println("INTRUSO: " + str(distancia) + "cm")
        set_leds(255, 0, 0)
        cyberpi.sound.play_tone(880, 0.3)
        time.sleep(0.1)
        set_leds(0, 0, 0)
        cyberpi.sound.play_tone(660, 0.3)
        time.sleep(0.1)
        set_leds(255, 0, 0)
        enviar_whatsapp(distancia)

def alarma_off():
    global alarmando
    alarmando = False
    set_leds(0, 255, 0)
    cyberpi.console.println("Zona despejada")

@event.start
def on_start():
    global alarmando

    cyberpi.console.println("Conectando WiFi...")
    cyberpi.wifi.connect(WIFI_SSID, WIFI_PASS)
    time.sleep(3)

    if cyberpi.wifi.is_connect():
        cyberpi.console.println("WiFi OK!")
        set_leds(0, 255, 0)
    else:
        cyberpi.console.println("Sin WiFi")
        set_leds(255, 0, 0)

    time.sleep(1)
    cyberpi.console.println("Patrullando...")

    while True:
        mbot2.drive_speed(30, -30)
        time.sleep(0.1)
        mbot2.drive_speed(0, 0)
        time.sleep(0.05)

        distancia = cyberpi.ultrasonic2.get()

        if distancia > 0 and distancia <= DISTANCIA:
            alarma_on(distancia)
        else:
            if alarmando:
                alarma_off()
            else:
                set_leds(0, 255, 0)

        time.sleep(0.1)