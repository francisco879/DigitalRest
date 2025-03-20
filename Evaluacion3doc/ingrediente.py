class Ingrediente:
    def __init__(self, nombre, cantidad):
     
        self.nombre = nombre  # Nombre del ingrediente
        self.cantidad = cantidad  # Cantidad inicial disponible

    def agregar_stock(self, cantidad):
        self.cantidad += cantidad  # Incrementar el stock con la cantidad proporcionada

    def descontar_stock(self, cantidad):
        if self.cantidad >= cantidad:
            # Hay suficiente stock, proceder a descontar
            self.cantidad -= cantidad
            return True
        else:
            # No hay suficiente stock, operación fallida
            return False
