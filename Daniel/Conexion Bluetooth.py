import cyberpi

# CyberPi 1 "trata de realizar conexión"
cyberpi.bluetooth.broadcast_string("Hola desde el robot 1")

# CyberPi que recibe "realiza conexion correcta"
mensaje = cyberpi.bluetooth.recv_string()
cyberpi.console.println(mensaje)
cyberpi.display.show_label(mensaje, 12, "blue")