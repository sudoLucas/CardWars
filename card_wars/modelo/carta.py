# modelo/carta.py

class Carta:
    def __init__(self, nombre, poder, tipo="criatura",
                 hechizo_id=None, costo_mana=0):
        self.nombre = nombre
        self.tipo = tipo
        self.poder = poder
        self.poder_original = poder
        self.aguante = poder
        self.aguante_original = poder
        self.viva = True

        self.hechizo_id = hechizo_id
        self.costo_mana = costo_mana

        self.buff_poder = 0
        self.buff_aguante = 0

    def recibir_golpe(self, cantidad):
        self.aguante -= cantidad
        if self.aguante <= 0:
            self.aguante = 0
            self.viva = False

    def morir(self):
        self.viva = False
        self.aguante = 0

    def resetear_buffs(self):
        self.poder = self.poder_original
        self.aguante = self.aguante_original
        self.buff_poder = 0
        self.buff_aguante = 0

    def __repr__(self):
        return (f"{self.nombre}({self.poder}, aguante {self.aguante}, "
                f"viva={self.viva}, tipo={self.tipo})")