import cyberpi

# Conectar el CyberPi a una red WiFi en esoecifico
cyberpi.wifi.connect("NOMBRE_DE_TU_RED", "CONTRASEÑA")

cyberpi.console.println("Conectando...")

if cyberpi.wifi.is_connect():
    cyberpi.console.println("¡Conectado al WiFi!")
    cyberpi.display.show_label("WiFi OK", 16, "green")
else:
    cyberpi.console.println("No se pudo conectar")
    cyberpi.display.show_label("Sin WiFi", 16, "red")