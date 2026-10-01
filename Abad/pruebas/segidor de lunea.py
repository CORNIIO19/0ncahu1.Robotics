from mbot2 import mbot2
from mbuild import quad_rgb_sensor
import time

mbot2.forward(30)

# Configuración del sensor quad RGB
quad_rgb_sensor.set_led_color("off") # Apaga el LED integrado
quad_rgb_sensor.set_report_mode(2, 20) # Configura modo de reporte en offset y frecuencia 20 Hz
quad_rgb_sensor.set_offset_k1(0.45, 0.45, 0.45, 0.45) # Ajusta los coeficientes de offset
quad_rgb_sensor.set_offset_k2(0.2, 0.2, 0.2, 0.2) # Ajusta los coeficientes de offset
quad_rgb_sensor.set_report_mode(1, 20)

# Constantes PD
kp = 1.5 # Constante proporcional
kd = 0.5 # Constante derivativa
base_speed = 50 # Velocidad base de los motores
last_error = 0 # Inicializa el error previo

while True:
    try:
        offset = quad_rgb_sensor.get_offset_track(4) # Lee el offset del sensor
        error = 0 - offset # Calcula el error de posición
        
        # Calcula la corrección PD
        correction = (kp * error) + (kd * (error - last_error))
        last_error = error
        
        # Aplica la corrección a los motores
        left_speed = int(base_speed + correction)
        right_speed = int(base_speed - correction)
        
        mbot2.set_motor_speed(left_speed, right_speed) # Establece las velocidades
        
    except KeyboardInterrupt:
        mbot2.stop() # Para el robot si se presiona Ctrl-C
        break
