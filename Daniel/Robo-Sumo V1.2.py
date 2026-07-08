# Robo_Sumo_calibracion_mejor_deteccion.py
# Arranca con A. Calibra línea en centro del ring, luego SUMO.
import mbuild, mbot2, event, time, random, cyberpi

# ---------- CONFIG ajustada ----------
ATTACK_DISTANCE_CM = 20
SEARCH_FORWARD_SPEED = 40
SEARCH_FORWARD_TIME = 0.45    # avance más largo
SEARCH_TURN_SPEED = 45
SEARCH_TURN_TIME = 0.45
BACKWARD_ON_EDGE_SPEED = 50
BACKWARD_ON_EDGE_TIME = 0.30  # retroceso más corto
MAX_ATTACK_SPEED = 100
ATTACK_BURST_TIME = 0.9       # embestida más larga
LOOP_DELAY = 0.06
ULTRA_SAMPLES = 3

# ---------- ESTADOS y LEDs ----------
def led_detection(): cyberpi.led.on(0,255,0)
def led_search():    cyberpi.led.on(255,200,0)
def led_attack():    cyberpi.led.on(255,0,0)
def led_off():       cyberpi.led.off()

def set_state(s, extra=None):
    cyberpi.console.clear()
    cyberpi.console.println("ESTADO: " + s)
    if extra:
        cyberpi.console.println(str(extra))

# ---------- flags / baseline ----------
active = {"value": False}
baseline = {"val": None}   # valor baseline del quad_rgb_sensor cuando está en centro del ring

# ---------- parada de emergencia ----------
@event.is_press('b')
def emergency_stop():
    active["value"] = False
    try: mbot2.EM_stop("ALL")
    except: 
        try: mbot2.drive_speed(0,0)
        except: pass
    cyberpi.console.clear()
    cyberpi.console.println("PARADO (B)")
    led_off()

# ---------- Helpers para detección de línea más robusta (REEMPLAZO) ----------
def parse_line_sta(v):
    """
    Normaliza la salida de get_line_sta("all",1) a un entero 0..15.
    Acepta int, str como '0','15','0000','1111' o '0b1111'.
    """
    if v is None:
        return None
    # si ya es int
    try:
        return int(v)
    except:
        pass
    s = str(v).strip()
    # si viene como '0000' o '1111' -> convertir de binario a entero
    if all(ch in '01' for ch in s) and len(s) <= 4:
        try:
            return int(s, 2)
        except:
            pass
    # si viene con comas o espacios, tomar la primera parte
    if ',' in s:
        s = s.split(',')[0].strip()
    # intentar eliminar prefijos como '0b'
    if s.startswith('0b'):
        try:
            return int(s, 2)
        except:
            pass
    # fallback: intentar parse decimal
    try:
        return int(float(s))
    except:
        return None

# parámetros de ajuste (puedes afinarlos)
EDGE_DEBOUNCE = 2          # lecturas consecutivas necesarias para confirmar borde
MIN_CHANGED_BITS = 1       # cuántos bits distintos (XOR) se consideran borde (1 = cualquiera)
PER_SENSOR_DEBOUNCE = 2    # lecturas consecutivas para cada sensor individual

# contadores de debounce persistentes
_edge_count = 0
_sensor_counts = {"L1":0,"L2":0,"R1":0,"R2":0}

def read_quad_all():
    """Llamada centralizada para leer get_line_sta y devolver entero 0..15 o None."""
    try:
        v = mbuild.quad_rgb_sensor.get_line_sta("all", 1)
    except Exception:
        try:
            v = mbuild.quad_rgb_sensor.get_line_sta()
        except Exception:
            v = None
    return parse_line_sta(v)

def calibrate_line_sensor(samples=10, delay=0.05):
    """
    Mide varias lecturas en el centro del ring y guarda baseline como entero.
    Devuelve True si se calibró correctamente y pone baseline['val'].
    """
    readings = []
    cyberpi.console.clear()
    cyberpi.console.println("Calibrando: coloca robot en CENTRO")
    time.sleep(0.6)
    for i in range(samples):
        v = read_quad_all()
        readings.append(v)
        cyberpi.console.clear()
        cyberpi.console.println("Calibrando... " + str(i+1) + "/" + str(samples))
        cyberpi.console.println(str(v))
        time.sleep(delay)
    # filtrar None y escoger el valor más frecuente
    vals = [x for x in readings if x is not None]
    if not vals:
        baseline["val"] = None
        return False
    baseline_val = max(set(vals), key=vals.count)
    baseline["val"] = int(baseline_val)
    cyberpi.console.clear()
    cyberpi.console.println("Baseline=" + str(baseline["val"]))
    time.sleep(1.2)
    return True

def any_edge_detected():
    """
    Lógica robusta:
     - lee el valor actual (0..15)
     - compara con baseline usando XOR y cuenta bits distintos
     - requiere EDGE_DEBOUNCE lecturas consecutivas para confirmar
     - además usa is_line() por sensor con PER_SENSOR_DEBOUNCE para mayor confiabilidad
    """
    global _edge_count, _sensor_counts
    cur = read_quad_all()
    # 1) si no hay lectura, fallback a checks por sensor individuales
    if cur is None:
        # comprobar sensores individuales con debounce
        for s in ("L1","L2","R1","R2"):
            try:
                r = mbuild.quad_rgb_sensor.is_line(s,1)
            except Exception:
                try:
                    r = mbuild.quad_rgb_sensor.is_line(s)
                except:
                    r = False
            if r is True:
                _sensor_counts[s] = _sensor_counts.get(s,0) + 1
            else:
                _sensor_counts[s] = 0
        # confirmar si algún sensor llegó al umbral
        for s,c in _sensor_counts.items():
            if c >= PER_SENSOR_DEBOUNCE:
                # reseteo parcial para evitar bloqueo
                _edge_count = 0
                for k in _sensor_counts: _sensor_counts[k]=0
                return True
        return False

    # 2) tenemos lectura cur y baseline
    if baseline["val"] is None:
        # si no hay baseline, usar is_line fallback (comportamiento previo)
        for s in ("L1","L2","R1","R2"):
            try:
                r = mbuild.quad_rgb_sensor.is_line(s,1)
            except:
                try:
                    r = mbuild.quad_rgb_sensor.is_line(s)
                except:
                    r = False
            if r is True:
                _sensor_counts[s] = _sensor_counts.get(s,0) + 1
            else:
                _sensor_counts[s] = 0
        for s,c in _sensor_counts.items():
            if c >= PER_SENSOR_DEBOUNCE:
                _edge_count = 0
                for k in _sensor_counts: _sensor_counts[k]=0
                return True
        return False

    # 3) comparar bits con XOR
    try:
        xor = int(cur) ^ int(baseline["val"])
        # contar bits distintos (Hamming weight)
        changed_bits = bin(xor).count("1")
    except Exception:
        changed_bits = 0

    if changed_bits >= MIN_CHANGED_BITS:
        _edge_count += 1
    else:
        _edge_count = 0

    if _edge_count >= EDGE_DEBOUNCE:
        # resetear contadores para siguiente detección
        _edge_count = 0
        for k in _sensor_counts: _sensor_counts[k]=0
        return True

    return False

# ---------- funciones de sensores ----------
def ultrasonic_filtered():
    samples = []
    for _ in range(ULTRA_SAMPLES):
        try:
            v = mbuild.ultrasonic2.get(1)
        except:
            v = None
        if v is None:
            try:
                v = cyberpi.ultrasonic2.get()
            except:
                v = None
        if v is not None:
            try: samples.append(float(v))
            except: pass
        time.sleep(0.025)
    if not samples:
        return None
    return sum(samples)/len(samples)

# ---------- movimientos ----------
def stop_all():
    try: mbot2.EM_stop("ALL")
    except:
        try: mbot2.drive_speed(0,0)
        except: pass

def forward_speed(speed, dur=None):
    try:
        if dur is None:
            mbot2.forward(speed)
        else:
            mbot2.forward(speed, dur); return
    except:
        try:
            mbot2.drive_speed(int(speed), int(speed))
            if dur: time.sleep(dur); stop_all()
        except: pass

def backward_speed(speed, dur=None):
    try:
        if dur is None: mbot2.backward(speed)
        else: mbot2.backward(speed, dur); return
    except:
        try:
            mbot2.drive_speed(-int(speed), -int(speed))
            if dur: time.sleep(dur); stop_all()
        except: pass

def turn_right(speed, dur=None):
    try:
        mbot2.turn(speed)
        if dur: time.sleep(dur); stop_all()
        return
    except:
        try:
            mbot2.drive_speed(int(speed), -int(speed))
            if dur: time.sleep(dur); stop_all()
        except: pass

def turn_left(speed, dur=None):
    try:
        mbot2.turn_left(speed)
        if dur: time.sleep(dur); stop_all()
        return
    except:
        try:
            mbot2.turn(-speed)
            if dur: time.sleep(dur); stop_all()
            return
        except:
            try:
                mbot2.drive_speed(-int(speed), int(speed))
                if dur: time.sleep(dur); stop_all()
            except: pass

# ---------- comportamientos ----------
def handle_edge():
    set_state("DETECCION")
    led_detection()
    # repetir hasta salir del borde
    repeat_limit = 6
    while active["value"] and any_edge_detected() and repeat_limit>0:
        stop_all()
        backward_speed(BACKWARD_ON_EDGE_SPEED, BACKWARD_ON_EDGE_TIME)
        stop_all()
        dur = random.uniform(0.4, 1.6)
        if random.choice([True, False]):
            turn_left(SEARCH_TURN_SPEED, dur)
        else:
            turn_right(SEARCH_TURN_SPEED, dur)
        stop_all()
        forward_speed(int(SEARCH_FORWARD_SPEED * 0.9), 0.35)
        stop_all()
        time.sleep(0.08)
        repeat_limit -= 1
    led_off()

def search_opponent_once():
    set_state("BUSQUEDA")
    led_search()
    if any_edge_detected(): return "BORDE"
    forward_speed(SEARCH_FORWARD_SPEED, SEARCH_FORWARD_TIME)
    stop_all()
    if any_edge_detected(): return "BORDE"
    if random.choice([True, False]):
        turn_left(SEARCH_TURN_SPEED, SEARCH_TURN_TIME)
    else:
        turn_right(SEARCH_TURN_SPEED, SEARCH_TURN_TIME)
    stop_all()
    if any_edge_detected(): return "BORDE"
    return "OK"

def attack_opponent():
    set_state("ATAQUE")
    led_attack()
    start = time.time()
    # disparos de ataque con timeout global
    while active["value"]:
        if any_edge_detected():
            stop_all()
            return "BORDE"
        dist = ultrasonic_filtered()
        if dist is None:
            # si no detecta a la presa al atacar, salimos
            stop_all()
            return "NO_TARGET"
        try: d = float(dist)
        except: 
            stop_all()
            return "NO_TARGET"
        # si se alejó, salir
        if d > ATTACK_DISTANCE_CM + 6:
            stop_all()
            return "NO_TARGET"
        # embestida sostenida
        forward_speed(MAX_ATTACK_SPEED, ATTACK_BURST_TIME)
        stop_all()
        time.sleep(0.08)
        if time.time() - start > 6.0: 
            stop_all()
            return "TIMEOUT"
    return "STOPPED"

# ---------- inicio / eventos ----------
@event.is_press('a')
def start_sumo():
    if not active["value"]:
        ok = calibrate_line_sensor()
        active["value"] = True
        cyberpi.console.clear()
        cyberpi.console.println("SUMO: INICIADO (A)")
        time.sleep(0.25)

@event.start
def main():
    cyberpi.console.clear()
    cyberpi.console.println("SUMO: listo - pulsa A")
    cyberpi.timer.reset()
    while True:
        if not active["value"]:
            time.sleep(0.06)
            continue
        try:
            if any_edge_detected():
                handle_edge()
                continue
            dist = ultrasonic_filtered()
            if dist is not None:
                try: d = float(dist)
                except: d = None
            else: d = None
            if d is not None and d > 0 and d <= ATTACK_DISTANCE_CM:
                attack_opponent()
                continue
            res = search_opponent_once()
            if res == "BORDE":
                continue
        except Exception as e:
            stop_all()
            cyberpi.console.clear()
            cyberpi.console.println("ERR: " + type(e).__name__)
            cyberpi.console.println(str(e))
            time.sleep(1.0)
        time.sleep(LOOP_DELAY)