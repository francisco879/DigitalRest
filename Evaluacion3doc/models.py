from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime  # Tipos de columnas y relaciones
from sqlalchemy.orm import relationship  # Para definir relaciones entre tablas
from database import Base  # Base heredada para los modelos
from datetime import datetime  # Manejo de fechas y tiempos

# Modelo para representar ingredientes
class Ingrediente(Base):
    __tablename__ = 'ingredientes'  # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)  # ID único, clave primaria
    nombre = Column(String, unique=True, nullable=False)  # Nombre del ingrediente, debe ser único
    tipo = Column(String, nullable=False)  # Tipo de ingrediente (ejemplo: Vegetal, Proteína)
    cantidad = Column(Float, nullable=False)  # Cantidad disponible
    unidad_medida = Column(String, nullable=False)  # Unidad de medida (ejemplo: gramos, litros)
    menus = relationship("MenuIngrediente", back_populates="ingrediente")  # Relación con la tabla `menu_ingredientes`

# Modelo para representar menús
class Menu(Base):
    __tablename__ = 'menus'  # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)  # ID único, clave primaria
    nombre = Column(String, unique=True, nullable=False)  # Nombre del menú, debe ser único
    descripcion = Column(String)  # Descripción del menú (opcional)
    precio = Column(Float, nullable=False)  # Precio del menú
    ingredientes = relationship("MenuIngrediente", back_populates="menu")  # Relación con la tabla `menu_ingredientes`
    pedidos = relationship("PedidoMenu", back_populates="menu")  # Relación con la tabla `pedido_menus`

# Modelo intermedio para asociar menús e ingredientes
class MenuIngrediente(Base):
    __tablename__ = 'menu_ingredientes'  # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)  # ID único, clave primaria
    menu_id = Column(Integer, ForeignKey('menus.id'))  # Relación con la tabla `menus`
    ingrediente_id = Column(Integer, ForeignKey('ingredientes.id'))  # Relación con la tabla `ingredientes`
    cantidad = Column(Float, nullable=False)  # Cantidad requerida del ingrediente en un menú

    # Relaciones bidireccionales
    menu = relationship("Menu", back_populates="ingredientes")  # Relación con el menú
    ingrediente = relationship("Ingrediente", back_populates="menus")  # Relación con el ingrediente


#SECUNDARY

# Modelo para representar clientes
class Cliente(Base):
    __tablename__ = 'clientes'  # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)  # ID único, clave primaria
    nombre = Column(String, nullable=False)  # Nombre del cliente
    correo = Column(String, unique=True, nullable=False)  # Correo electrónico único del cliente
    pedidos = relationship("Pedido", back_populates="cliente")  # Relación con la tabla `pedidos`

# Modelo para representar pedidos
class Pedido(Base):
    __tablename__ = 'pedidos'  # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)  # ID único, clave primaria
    cliente_id = Column(Integer, ForeignKey('clientes.id'))  # Relación con la tabla `clientes`
    fecha_creacion = Column(DateTime, default=datetime.utcnow)  # Fecha de creación del pedido
    total = Column(Float, nullable=False)  # Total del pedido

    cliente = relationship("Cliente", back_populates="pedidos")  # Relación con el cliente
    menus = relationship("PedidoMenu", back_populates="pedido")  # Relación con la tabla `pedido_menus`

# Modelo intermedio para asociar pedidos y menús
class PedidoMenu(Base):
    __tablename__ = 'pedido_menus'  # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)  # ID único, clave primaria
    pedido_id = Column(Integer, ForeignKey('pedidos.id'))  # Relación con la tabla `pedidos`
    menu_id = Column(Integer, ForeignKey('menus.id'))  # Relación con la tabla `menus`
    cantidad = Column(Integer, nullable=False)  # Cantidad de menús en el pedido

    pedido = relationship("Pedido", back_populates="menus")  # Relación con el pedido
    menu = relationship("Menu")  # Relación con el menú
