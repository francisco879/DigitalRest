from sqlalchemy.orm import Session  # Importa la clase Session de SQLAlchemy para interactuar con la base de datos
from models import Pedido  # Importa el modelo Pedido, que representa la tabla de pedidos en la base de datos
from sqlalchemy.exc import IntegrityError  # Importa para manejar errores de integridad, como violaciones de restricciones

# Función para crear un nuevo pedido en la base de datos
def crear_pedido(db: Session, cliente_id: int, total: float):
    """Crea un nuevo pedido en la base de datos."""
    try:
        # Crea una nueva instancia de Pedido con los datos proporcionados
        nuevo_pedido = Pedido(cliente_id=cliente_id, total=total)
        db.add(nuevo_pedido)  # Añade el nuevo pedido a la sesión de la base de datos
        db.commit()  # Realiza el commit para guardar el nuevo pedido
        db.refresh(nuevo_pedido)  # Refresca el objeto pedido con los datos actualizados (como el ID generado por la base de datos)
        return nuevo_pedido  # Devuelve el nuevo pedido creado
    except IntegrityError:
        db.rollback()  # Si ocurre un error, realiza un rollback para deshacer la transacción
        raise ValueError("Error al crear el pedido. Verifique los datos.")  # Lanza un error si ocurre un problema de integridad

# Función para obtener todos los pedidos registrados en la base de datos
def obtener_pedidos(db: Session):
    """Obtiene todos los pedidos de la base de datos."""
    return db.query(Pedido).all()  # Realiza una consulta para obtener todos los pedidos registrados

# Función para obtener un pedido específico por su ID
def obtener_pedido_por_id(db: Session, pedido_id: int):
    """Obtiene un pedido por su ID."""
    return db.query(Pedido).filter(Pedido.id == pedido_id).first()  # Filtra por el ID del pedido y devuelve el primero encontrado

# Función para obtener todos los pedidos asociados a un cliente específico
def obtener_pedidos_por_cliente(db: Session, cliente_id: int):
    """Obtiene todos los pedidos asociados a un cliente específico."""
    return db.query(Pedido).filter(Pedido.cliente_id == cliente_id).all()  # Filtra por el ID del cliente y devuelve los pedidos asociados

# Función para actualizar los datos de un pedido existente
def actualizar_pedido(db: Session, pedido_id: int, nuevos_datos: dict):
    """Actualiza los datos de un pedido existente."""
    # Busca el pedido por su ID
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido:  # Si el pedido existe
        # Actualiza solo los campos proporcionados en el diccionario
        for key, value in nuevos_datos.items():
            if hasattr(pedido, key):  # Verifica si el atributo existe en el pedido
                setattr(pedido, key, value)  # Asigna el nuevo valor al atributo
        db.commit()  # Realiza el commit para guardar los cambios
        db.refresh(pedido)  # Refresca el objeto pedido con los datos actualizados
        return pedido  # Devuelve el pedido actualizado
    else:  # Si no se encuentra el pedido, lanza un error
        raise ValueError(f"El pedido con ID {pedido_id} no existe.")

# Función para eliminar un pedido de la base de datos
def eliminar_pedido(db: Session, pedido_id: int):
    """Elimina un pedido de la base de datos."""
    # Busca el pedido por su ID
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido:  # Si el pedido existe, lo elimina
        db.delete(pedido)  # Elimina el pedido de la base de datos
        db.commit()  # Realiza el commit para confirmar la eliminación
        return pedido  # Devuelve el pedido eliminado
    else:  # Si no se encuentra el pedido, lanza un error
        raise ValueError(f"El pedido con ID {pedido_id} no existe.")
