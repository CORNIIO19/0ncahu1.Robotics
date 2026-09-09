Bibliotecas usadas en MODO SUMO v10

El código importa 5 bibliotecas: cyberpi, mbot2, mbuild, time y random. Las primeras tres son específicas de Makeblock (cada una controla una parte distinta del hardware); las últimas dos son de Python estándar. A continuación, para qué sirve cada una, qué funciones del código las usan y para qué se usan puntualmente en el sumo.

cyberpi

Para qué es: es la biblioteca que controla la placa CyberPi en sí — el "cerebro" del mBot2. Todo lo que no sea mover las ruedas (LEDs, pantalla, botones/joystick, consola, audio, cronómetro, sensores integrados de la placa) vive acá.

Funciones que integra el código:

cyberpi.led.on(r, g, b) — enciende los 5 LEDs RGB frontales con un color. En el sumo se usa como señal visual del estado actual: azul al evadir, rojo al atacar, naranja al buscar, blanco en pausa/inicio. No afecta el movimiento, es solo feedback visual para quien esté mirando la pelea.
cyberpi.console.clear() / cyberpi.console.println(texto) — limpian e imprimen texto en el panel de consola de mBlock (visible en modo conectado/live). Se usan para mensajes como "Inicio en 5", "LUCHA!" o "PARO - A = seguir", útiles para depurar sin necesitar la pantalla.
cyberpi.controller.is_press(boton) — lee si un botón físico (A o B) o el joystick están presionados; devuelve True/False. Es lo que arranca la pelea (botón A), la pausa (botón B) y la reanuda.
cyberpi.audio.play_tone(frecuencia, duracion) — reproduce un tono por el parlante integrado. Se usa en la cuenta regresiva y en el "bip" de inicio de pelea; puramente sonoro.
cyberpi.timer.reset() / cyberpi.timer.get() — un cronómetro interno; reset() lo pone en cero y get() devuelve los segundos transcurridos. Se usa para medir cuánto lleva una fase (girando vs. avanzando) sin bloquear el bucle, es decir, sin dejar de revisar sensores mientras se cuenta el tiempo.
mbot2

Para qué es: biblioteca específica del chasis/shield del mBot2 — todo lo relacionado con mover físicamente el robot (los dos motores) y leer los puertos de extensión S1-S4. Es distinta de cyberpi porque apunta al shield del mBot2, no a la placa CyberPi.

Funciones que integra el código:

mbot2.drive_power(potencia_izq, potencia_der) — es la única función de motor que usa el v10, y de ella se construye todo el movimiento. Fija la potencia de cada rueda por separado y no bloquea: el robot sigue así hasta la próxima llamada. recto(), girar() y parar() del código son solo distintas combinaciones de signos pasadas a esta única función.
mbuild

Para qué es: biblioteca para los módulos externos que se conectan por el puerto mBuild — sensores y accesorios que no vienen soldados en el chasis base, como el Sensor Ultrasónico 2 o el Sensor Quad RGB (el de línea/color de 4 canales).

Funciones que integra el código:

mbuild.quad_rgb_sensor.get_gray(puerto, indice) — lee el nivel de gris/brillo de uno de los 4 sensores del Quad RGB, identificado por posición ("L1", "L2", "R1", "R2"). Es la base de borde(): compara ese valor contra UMBRAL_NEGRO para saber si el robot está pisando piso blanco o la cinta negra del borde del ring.
mbuild.ultrasonic2.get(indice) — devuelve la distancia en cm que detecta el sensor ultrasónico. Es la base de rival_cerca(): si esa distancia es menor a DIST_ATAQUE, el código asume que hay un rival enfrente y activa el modo ataque.
time (estándar de Python)

Para qué es: utilidades de tiempo de propósito general, no es de Makeblock.

Funciones que integra el código:

time.sleep(segundos) — pausa la ejecución del script el tiempo indicado. Se usa en todos lados: para no saturar el bucle principal (time.sleep(0.01) en cada vuelta), para las pausas de la cuenta regresiva, y dentro de evadir() para sostener el retroceso y el giro durante un tiempo fijo.
random (estándar de Python)

Para qué es: generación de números pseudoaleatorios, tampoco es de Makeblock.

Funciones que integra el código:

random.choice(lista) — elige un elemento al azar de una lista. Se usa para sortear la dirección inicial de búsqueda (dir_busqueda) y para volver a sortearla cada vez que termina una fase de avance, así el patrón de búsqueda no es siempre igual y un rival no puede anticiparlo.
random.random() — devuelve un decimal aleatorio entre 0.0 y 1.0. Se usa para variar la duración del giro dentro de evadir() (T_GIRO_MIN + random.random() * (T_GIRO_MAX - T_GIRO_MIN)), de modo que la maniobra de evasión no dure siempre exactamente lo mismo.
Resumen rápido
Biblioteca	Controla	Funciones usadas en v10
cyberpi	Placa CyberPi (LEDs, botones, consola, audio, timer)	led.on, console.clear/println, controller.is_press, audio.play_tone, timer.reset/get
mbot2	Motores del chasis	drive_power
mbuild	Sensores externos (línea y ultrasonido)	quad_rgb_sensor.get_gray, ultrasonic2.get
time	Pausas / temporización	sleep
random	Aleatoriedad	choice, random