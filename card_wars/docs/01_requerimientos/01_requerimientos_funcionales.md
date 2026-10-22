# Requerimientos funcionales

## Modulo: Gestion de partida

### RF-01: Iniciar el juego
El sistema debe arrancar en el menu principal al ejecutarse.

### RF-02: Elegir dificultad
El sistema debe permitir elegir entre tres dificultades:
Facil, Normal y Dificil. Cada una define:
- Cantidad de cartas en mano (3, 4, 6).
- HP inicial del jugador y de la IA.
- Estrategia de la IA.

### RF-03: Iniciar partida
El sistema debe permitir iniciar una partida nueva desde el menu,
usando la dificultad elegida.

### RF-04: Reiniciar partida
El sistema debe permitir reiniciar la partida actual, reseteando HP,
mazos y ronda al estado inicial.

### RF-05: Volver al menu
El sistema debe permitir volver al menu principal desde cualquier escena.

### RF-06: Alternar pantalla completa
El sistema debe permitir alternar entre ventana y pantalla completa.

### RF-07: Salir del juego
El sistema debe permitir cerrar la aplicacion desde el menu.

## Modulo: Turno

### RF-08: Turno de la IA primero
Al iniciar cada ronda, la IA debe tirar su criatura a la mesa antes
que el jugador. La criatura de la IA se muestra boca arriba.

### RF-09: Tirar criatura
El jugador debe poder tirar una criatura de su mano a la zona de duelo.
Solo se puede tirar una criatura por turno.

### RF-10: Aplicar hechizos
Despues de tirar la criatura y antes de terminar el turno, el jugador
debe poder aplicar hechizos usando mana. Se pueden aplicar multiples
hechizos mientras haya mana disponible.

### RF-11: Terminar turno
El jugador debe poder terminar su turno haciendo click sobre la
criatura que bajo a la mesa.

### RF-12: Turno de la IA
Despues de que el jugador termina el turno, la IA debe aplicar sus
hechizos si tiene mana y decide usarlos.

### RF-13: Resolucion del duelo
El sistema debe resolver el enfrentamiento 1v1 entre la criatura
del jugador y la de la IA.

## Modulo: Mana

### RF-14: Inicializacion de mana
El sistema debe iniciar el mana del jugador y de la IA en 7.

### RF-15: Incremento de mana
Al terminar cada turno, el sistema debe sumar al mana actual un valor
aleatorio entre 1 y 2.

### RF-16: Tope de mana
El mana no puede superar 14. Si el incremento lo supera, se queda en 14.

### RF-17: Gasto de mana
El sistema debe restar el costo del hechizo al mana disponible al
momento de usarlo.

### RF-18: Validacion de mana
El sistema debe impedir usar un hechizo si el mana disponible es
menor al costo del hechizo.

## Modulo: Criaturas

### RF-19: Propiedades de criatura
Cada criatura debe tener: nombre, poder, aguante y estado (viva/muerta).

### RF-20: Combate 1v1
Al resolver un duelo, el sistema debe comparar los poderes de las dos
criaturas enfrentadas.

### RF-21: Resolucion del combate
- Si el poder del jugador es mayor: la criatura de la IA muere.
  El sobrante de poder se resta al HP de la IA.
- Si el poder de la IA es mayor: la criatura del jugador muere.
  El sobrante se resta al HP del jugador.
- Si empatan: ambas criaturas mueren.

### RF-22: Descarte de criaturas
Las criaturas que mueren se descartan y no vuelven a la mano.

## Modulo: Hechizos

### RF-23: Tipos de hechizos
El sistema debe soportar 8 tipos de hechizos:
- Vision (costo 1)
- Pocion de fuerza (costo 2)
- Pocion de defensa (costo 2)
- Curacion (costo 3)
- Rayo (costo 3)
- Debilidad (costo 3)
- Robo (costo 3)
- Inmovilizar (costo 4)

### RF-24: Hechizo Vision
Debe revelar una carta del medio del rival durante 1.5 segundos.

### RF-25: Hechizo Pocion de fuerza
Debe aumentar el ataque de una criatura propia durante el turno actual.

### RF-26: Hechizo Pocion de defensa
Debe aumentar el aguante de una criatura propia durante el turno actual.

### RF-27: Hechizo Curacion
Debe aumentar el HP del jugador.

### RF-28: Hechizo Rayo
Debe restar HP a una criatura rival.

### RF-29: Hechizo Debilidad
Debe restar ataque a una criatura rival durante el turno actual.

### RF-30: Hechizo Robo
Debe tomar una carta al azar de la mano del rival. La carta pasa
a la mano del jugador. El rival pierde esa carta.

### RF-31: Hechizo Inmovilizar
Debe restar 10 de aguante a la criatura rival activa. El aguante perdido
permanece en la carta y solo puede recuperarse con Pocion de defensa.

### RF-32: Prioridad de ataque por aguante
En un duelo, la criatura con mayor aguante actual ataca primero. Si su ataque
reduce el aguante rival a cero, gana el duelo sin recibir contraataque. Si la
rival sobrevive, contraataca; el resultado posterior se resuelve por el poder
de ataque, conservando el dano a HP por diferencia de poder.

### RF-32: Descarte de hechizos
Los hechizos se descartan despues de usarse.

## Modulo: Mano y mazo

### RF-33: Cantidad de cartas en mano
La cantidad de cartas en mano depende de la dificultad:
- Facil: 3
- Normal: 4
- Dificil: 6

### RF-34: Mezcla de tipos
La mano puede contener criaturas y hechizos mezclados.

### RF-35: RebaraJe
Cuando al jugador no le quedan cartas vivas en la mano y su HP es
mayor a cero, el sistema debe rebarajar la cantidad original de
cartas (3, 4 o 6 segun dificultad).

### RF-36: RebaraJe de la IA
La misma regla de rebaraje aplica para la IA.

### RF-37: Sin robo del mazo
El sistema no debe agregar cartas por turno. Solo se rebaraja cuando
la mano se queda sin cartas vivas.

### RF-38: Tope de cartas tras robo del rival
Si el jugador usa el hechizo Robo y ya tiene la cantidad maxima de
cartas en mano, debe jugar una carta sobrante antes de terminar el
turno. Nunca puede tener mas de la cantidad maxima.

## Modulo: Estrategias de IA

### RF-39: Estrategia aleatoria
En dificultad Facil, la IA elige su criatura al azar.

### RF-40: Estrategia conservadora
En dificultad Normal, la IA guarda sus cartas fuertes.

### RF-41: Estrategia adaptativa
En dificultad Dificil, la IA reacciona al estado de la partida.

## Modulo: Fin de partida

### RF-42: Deteccion de fin
El sistema debe terminar la partida cuando el HP del jugador o de
la IA llegue a 0.

### RF-43: Pantalla de resultado
Al terminar la partida, el sistema debe mostrar la pantalla de
resultado (GANASTE o PERDISTE) con estadisticas.

### RF-44: Revancha
La pantalla de resultado debe permitir iniciar una revancha.

### RF-45: Volver al menu desde resultado
La pantalla de resultado debe permitir volver al menu principal.

## Modulo: Interfaz grafica

### RF-46: Mostrar HP
El sistema debe mostrar el HP del jugador y de la IA en pantalla.

### RF-47: Mostrar mana
El sistema debe mostrar el mana actual del jugador con forma de
frasco y un numero encima.

### RF-48: Cartas de hechizo con brillo
Las cartas de hechizo deben tener un brillo violeta para
distinguirlas de las criaturas.

### RF-49: Cartas del rival en abanico
Las cartas del rival deben mostrarse en forma de abanico con
hasta 6 cartas visibles.

### RF-50: Mano del jugador compacta
Las cartas de la mano del jugador deben estar juntas, con poco
espacio entre si.