import mbuild
import cyberpi
import time

mbuild.quad_rgb_sensor.color_mode("enhance")

while True:
    offset = mbuild.quad_rgb_sensor.get_offset_track(1)
    cyberpi.console.clear()
    cyberpi.console.println(offset)
    time.sleep(0.3)
