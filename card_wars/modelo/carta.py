# modelo/carta.py

class Carta:
    def __init__(self, nombre, poder):
        self.nombre = nombre
        self.poder = poder
        self.aguante = poder
        self.viva = True

    def recibir_golpe(self, cantidad):
        self.aguante -= cantidad
        if self.aguante <= 0:
            self.aguante = 0
            self.viva = False

    def morir(self):
        self.viva = False
        self.aguante = 0

    def __repr__(self):
        return f"{self.nombre}({self.poder}, aguante {self.aguante}, viva={self.viva})"