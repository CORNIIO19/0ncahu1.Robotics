mBot2: partes, sensores y casos de uso

1. Introducción

El mBot2 de Makeblock es un robot educativo programable diseñado para aprender robótica, programación, electrónica, automatización, IoT e introducción a la inteligencia artificial.

Su arquitectura se basa principalmente en la CyberPi, el mBot2 Shield, dos motores con encoder, el sensor ultrasónico 2, el sensor Quad RGB y una estructura mecánica de aluminio. Además, puede ampliarse con módulos electrónicos mBuild.

Nota: Esta guía se centra en los componentes principales del kit mBot2. La plataforma mBuild permite agregar muchos sensores y actuadores adicionales.

2. Partes principales del mBot2

2.1 CyberPi

La CyberPi es el cerebro del robot. Es una placa de control basada en un microcontrolador que ejecuta el programa y procesa la información de los sensores.

¿Para qué sirve?

Ejecutar los programas creados en mBlock.

Procesar información de sensores.

Controlar motores y otros actuadores mediante el mBot2 Shield.

Mostrar información en su pantalla.

Emitir sonidos mediante su altavoz.

Utilizar sensores integrados.

Comunicarse mediante Wi-Fi.

Programarse mediante bloques o Python.

Elementos integrados importantes

La CyberPi incorpora, entre otros:

Pantalla a color.

Botones.

Sensor de luz.

Micrófono.

Acelerómetro.

Giroscopio.

Altavoz.

Comunicación Wi-Fi.

Casos de uso

Monitor de luz: medir la iluminación ambiental y mostrar el valor en pantalla.

Detector de movimiento: utilizar el acelerómetro y el giroscopio para detectar si el robot fue inclinado, levantado o golpeado.

Control remoto: utilizar la comunicación inalámbrica para recibir instrucciones desde otro dispositivo.

Estación de datos: mostrar en pantalla los valores obtenidos por diferentes sensores.

3. mBot2 Shield

El mBot2 Shield es la placa de expansión que conecta la CyberPi con los componentes del robot.

Además de proporcionar conexiones, incorpora la batería recargable que alimenta el sistema.

¿Para qué sirve?

Permite conectar y controlar:

Motores con encoder.

Servomotores.

Módulos mBuild.

Otros periféricos compatibles.

También proporciona las conexiones necesarias para convertir la CyberPi en el controlador del vehículo.

Caso de uso

Un programa puede recibir la orden:

"Avanza 50 cm"

La CyberPi procesa la orden y el mBot2 Shield se encarga de enviar las señales correspondientes a los motores.

4. Motores con encoder

El mBot2 utiliza dos motores con encoder para mover sus ruedas.

Un encoder permite conocer información relacionada con la rotación del motor, por lo que el robot puede controlar con mayor precisión su movimiento.

¿Para qué sirven?

Mover el robot hacia adelante y atrás.

Girar.

Controlar la velocidad.

Controlar la posición o cantidad de rotación.

Realizar movimientos más precisos.

¿Qué es un encoder?

Un encoder proporciona información sobre la rotación del motor.

En lugar de decir simplemente:

"Enciende el motor."

el sistema puede trabajar con información como:

"Haz que la rueda gire una determinada cantidad."

Esto permite implementar movimientos mucho más controlados.

Casos de uso

Movimiento por distancia

Programar el robot para avanzar una distancia determinada.

Giro preciso

Hacer que el robot realice un giro controlado, por ejemplo, de aproximadamente 90°.

Control de velocidad

Mantener una velocidad determinada mientras el robot se desplaza.

Competencia de precisión

Programar una ruta en la que el robot tenga que desplazarse entre varios puntos.

5. Sensor ultrasónico 2

El Ultrasonic Sensor 2 utiliza ondas ultrasónicas para estimar la distancia entre el robot y un objeto.

Es uno de los sensores principales utilizados para detectar obstáculos.

¿Para qué sirve?

Medir distancia.

Detectar obstáculos.

Evitar colisiones.

Crear sistemas de navegación.

Detectar objetos delante del robot.

El sensor también incorpora detección de iluminación ambiental.

Caso de uso: evasión de obstáculos

Una lógica sencilla podría ser:

Si distancia < 20 cm
    detenerse
    girar
Si no
    avanzar

Esto permite construir un robot que recorra un espacio sin chocar con objetos.

Caso de uso: estacionamiento

El robot puede avanzar hacia una pared y detenerse cuando detecte que está a una distancia determinada.

Caso de uso: radar

El sensor puede montarse sobre un servo para medir distancias en diferentes direcciones y construir una representación sencilla de los obstáculos.

6. Sensor Quad RGB

El Quad RGB Sensor incorpora cuatro elementos de detección de color.

Una de sus funciones principales es detectar colores y realizar seguimiento de líneas.

¿Para qué sirve?

Seguir líneas.

Detectar colores.

Determinar la posición de una línea debajo del robot.

Crear sistemas de clasificación por color.

Al utilizar cuatro puntos de detección, el robot puede obtener información más precisa sobre la posición de una línea.

Caso de uso: seguimiento de línea

Un circuito puede tener una línea negra sobre una superficie clara.

El robot puede:

Detectar la línea.

Determinar si está desplazada hacia la izquierda o derecha.

Ajustar la velocidad de los motores.

Mantenerse sobre la trayectoria.

Ejemplo conceptual:

Línea hacia la izquierda → corregir hacia la izquierda
Línea al centro          → avanzar
Línea hacia la derecha   → corregir hacia la derecha

Caso de uso: clasificación por color

El robot puede recorrer diferentes objetos y detectar su color.

Por ejemplo:

Rojo   → detenerse
Verde  → avanzar
Azul   → girar

7. Sensor de luz de CyberPi

La CyberPi incorpora un sensor de luz que permite detectar el nivel de iluminación ambiental.

¿Para qué sirve?

Medir iluminación.

Detectar cambios entre ambientes claros y oscuros.

Crear sistemas automáticos de iluminación.

Caso de uso

El robot puede mostrar en pantalla:

Iluminación:
72%

También podría activar una luz cuando el ambiente sea demasiado oscuro.

8. Micrófono

La CyberPi incorpora un micrófono.

¿Para qué sirve?

Detectar sonidos.

Medir aproximadamente la intensidad sonora.

Crear interacciones mediante sonidos.

Utilizar proyectos relacionados con reconocimiento de voz cuando se combinan las capacidades de comunicación y software apropiadas.

Caso de uso

Crear una alarma que reaccione ante un sonido fuerte:

Si sonido > límite
    reproducir alarma

Otro proyecto puede hacer que el robot reaccione a una palmada.

9. Acelerómetro

El acelerómetro permite detectar cambios de movimiento y aceleración en diferentes ejes.

¿Para qué sirve?

Detectar inclinación.

Detectar movimientos bruscos.

Saber si el robot fue levantado.

Crear controles mediante movimiento.

Caso de uso: robot antirrobo

Si el robot detecta que fue levantado:

Detectar movimiento/inclinación
        ↓
Activar alarma
        ↓
Mostrar mensaje en CyberPi

10. Giroscopio

El giroscopio permite detectar cambios de orientación y rotación.

¿Para qué sirve?

Detectar giros.

Medir cambios de orientación.

Crear sistemas de control basados en movimiento.

Caso de uso

Programar el robot para que detecte cuando fue girado manualmente y muestre el ángulo aproximado en la pantalla.

También puede utilizarse como parte de proyectos educativos de física para estudiar rotación y movimiento.

11. Pantalla de CyberPi

La CyberPi incluye una pantalla a color.

¿Para qué sirve?

Permite mostrar:

Texto.

Números.

Valores de sensores.

Imágenes.

Estados del robot.

Mensajes para el usuario.

Caso de uso

Crear un panel de diagnóstico:

mBot2

Distancia: 35 cm
Velocidad: 40%
Luz: 68%
Estado: AVANZANDO

Esto resulta especialmente útil para depurar programas.

12. Altavoz

La CyberPi tiene un altavoz integrado.

¿Para qué sirve?

Reproducir sonidos.

Crear alarmas.

Emitir avisos.

Crear interfaces interactivas.

Caso de uso

Un robot que detecta un obstáculo podría emitir un sonido diferente dependiendo de la distancia:

> 50 cm  → sin sonido
30 cm    → beep lento
15 cm    → beep rápido
< 10 cm  → alarma

13. Botones de CyberPi

La CyberPi incorpora botones físicos que pueden utilizarse como entradas.

¿Para qué sirven?

Permiten crear controles directamente sobre el robot.

Caso de uso

Botón A → iniciar recorrido
Botón B → detener robot
Botón C → cambiar modo

Por ejemplo, se pueden crear varios modos:

Modo 1: seguimiento de línea
Modo 2: evasión de obstáculos
Modo 3: control manual

14. Batería

El mBot2 Shield incorpora una batería recargable de ion-litio/polímero de litio que proporciona energía al robot.

¿Para qué sirve?

Permite que el mBot2 funcione sin estar conectado permanentemente a una fuente de alimentación externa.

Caso de uso

El robot puede realizar un recorrido autónomo por un aula o laboratorio sin necesidad de un cable de alimentación.

15. Chasis

El chasis de aluminio proporciona la estructura física del robot.

¿Para qué sirve?

Mantener unidos los componentes.

Soportar motores.

Servir como plataforma para sensores y accesorios.

Proporcionar resistencia mecánica.

Caso de uso

El chasis puede utilizarse como base para agregar:

Soportes impresos en 3D.

Cámaras.

Servos.

Sensores adicionales.

Mecanismos personalizados.

16. Ruedas

Las ruedas transmiten el movimiento de los motores al suelo.

El kit utiliza ruedas principales conectadas a los motores y una rueda pequeña de apoyo.

¿Para qué sirven?

Permiten:

Avanzar.

Retroceder.

Girar.

Realizar movimientos diferenciales.

Caso de uso

Al aumentar la velocidad de una rueda respecto a la otra, el robot puede cambiar su dirección.

Izquierda rápida + derecha lenta → gira a la derecha
Izquierda lenta + derecha rápida → gira a la izquierda

17. Rueda de apoyo

La rueda pequeña de apoyo ayuda a mantener estable el robot mientras las ruedas principales proporcionan la tracción.

Caso de uso

Permite que el robot mantenga una posición estable durante movimientos hacia adelante, atrás y giros.

18. Puertos y conexiones

El mBot2 Shield dispone de diferentes puertos para conectar motores, servos y módulos.

Entre ellos se encuentran conexiones para:

Motores con encoder.

Servomotores.

Módulos mBuild.

Otros periféricos.

La conexión entre módulos permite ampliar las capacidades del robot sin tener que diseñar desde cero toda la electrónica.

19. Sistema mBuild

mBuild es el sistema modular de Makeblock para sensores y dispositivos electrónicos.

Los módulos pueden conectarse mediante cables mBuild y combinarse para crear proyectos más complejos.

Existen módulos adicionales como:

Sensores de temperatura.

Sensores de humedad.

Sensor de gas MQ2.

Sensor de sonido.

Sensor PIR.

Sensor de luz.

Sensor de llama.

Joystick.

Botones.

Servodrivers.

Motor drivers.

Matrices LED.

Altavoces.

Sensores de distancia.

Sensores de color.

Caso de uso

Se puede convertir el mBot2 en una estación móvil de monitoreo:

Temperatura
     +
Humedad
     +
Calidad del aire
     +
Distancia
     ↓
CyberPi
     ↓
Mostrar información

20. Casos de uso integrando varias partes

20.1 Robot evita-obstáculos

Componentes

CyberPi

mBot2 Shield

Motores con encoder

Sensor ultrasónico

Funcionamiento

      Sensor ultrasónico
              ↓
       Detectar distancia
              ↓
       ¿Hay obstáculo?
          /        \
        Sí          No
        ↓            ↓
     Detener       Avanzar
        ↓
      Girar

20.2 Robot sigue-líneas

Componentes

CyberPi

mBot2 Shield

Motores con encoder

Quad RGB Sensor

Funcionamiento

El Quad RGB detecta la posición de la línea y el programa modifica la velocidad de cada motor para mantener al robot sobre la trayectoria.

Aplicaciones

Competencias de robótica.

Transporte autónomo.

Simulación de robots industriales.

Enseñanza de control automático.

20.3 Robot repartidor

Componentes

Quad RGB Sensor

Sensor ultrasónico

Motores con encoder

CyberPi

Pantalla

Funcionamiento

El robot puede seguir una ruta marcada en el suelo y utilizar el sensor ultrasónico para evitar obstáculos.

Por ejemplo:

Inicio
  ↓
Seguir línea
  ↓
Detectar obstáculo
  ↓
Esperar
  ↓
Obstáculo desaparece
  ↓
Continuar ruta
  ↓
Llegar al destino
  ↓
Mostrar "Entrega completada"

21. Robot de seguridad

Componentes

Acelerómetro

Giroscopio

Micrófono

Sensor ultrasónico

Altavoz

Pantalla

Funcionamiento

El robot puede detectar:

Movimiento inesperado.

Golpes.

Sonidos fuertes.

Objetos acercándose.

Al detectar una condición determinada puede:

Emitir una alarma.

Mostrar un mensaje.

Cambiar su comportamiento.

Enviar información mediante comunicación inalámbrica.

22. Robot explorador

Componentes

Sensor ultrasónico

Motores con encoder

Acelerómetro

Giroscopio

CyberPi

Pantalla

Funcionamiento

El robot puede recorrer un espacio y detectar obstáculos.

Los encoders ayudan a controlar el movimiento, mientras que el sensor ultrasónico detecta objetos.

El acelerómetro y giroscopio pueden proporcionar información adicional sobre el movimiento y orientación.

23. Estación móvil de monitoreo

Se pueden agregar módulos mBuild para convertir el mBot2 en una plataforma de medición.

Ejemplo

          ┌───────────────┐
          │    CyberPi    │
          └───────┬───────┘
                  │
        ┌─────────┼─────────┐
        ↓         ↓         ↓
   Temperatura  Humedad    Gas
        │         │         │
        └─────────┼─────────┘
                  ↓
             Mostrar datos

El robot podría desplazarse por diferentes zonas y registrar mediciones.

24. Tabla rápida de componentes

Componente

Tipo

Función principal

CyberPi

Controlador

Ejecuta el programa y procesa datos

mBot2 Shield

Placa de expansión

Conecta y controla los componentes

Motor con encoder

Actuador

Mueve el robot con control de rotación

Ultrasonic Sensor 2

Sensor

Mide distancia y detecta obstáculos

Quad RGB Sensor

Sensor

Detecta colores y sigue líneas

Acelerómetro

Sensor

Detecta aceleración y movimiento

Giroscopio

Sensor

Detecta rotación y orientación

Sensor de luz

Sensor

Mide iluminación

Micrófono

Sensor

Detecta sonidos

Pantalla

Salida

Muestra información

Altavoz

Salida

Reproduce sonidos

Botones

Entrada

Permiten interacción física

Batería

Alimentación

Proporciona energía al robot

Chasis

Estructura

Soporta los componentes

Ruedas

Mecánico

Permiten el desplazamiento

Rueda de apoyo

Mecánico

Mantiene la estabilidad

mBuild

Sistema modular

Permite agregar sensores y actuadores

25. Conclusión

El mBot2 no es solamente un automóvil pequeño controlado por código. Es una plataforma robótica modular en la que cada componente cumple una función dentro de un sistema:

                 SENSORES
                    ↓
        ┌─────────────────────┐
        │       CyberPi       │
        │   Procesamiento     │
        │      Programa       │
        └──────────┬──────────┘
                   ↓
             mBot2 Shield
                   ↓
              ACTUADORES
                   ↓
              Movimiento

Los sensores permiten que el robot perciba el entorno, la CyberPi permite procesar la información, y los motores, pantalla, altavoz y otros dispositivos permiten actuar y comunicarse.

La verdadera ventaja del mBot2 está en combinar estos elementos. Por ejemplo, el sensor ultrasónico puede detectar un obstáculo, la CyberPi puede decidir qué hacer y los motores con encoder pueden ejecutar un giro preciso. De esta manera se pueden construir sistemas autónomos cada vez más complejos.