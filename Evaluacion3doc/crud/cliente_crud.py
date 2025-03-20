
# crud/cliente_crud.py

# Importación de módulos necesarios para el manejo de base de datos
from sqlalchemy.orm import Session  # Para interactuar con la base de datos usando SQLAlchemy
from sqlalchemy.exc import IntegrityError  # Para manejar errores relacionados con la integridad de los datos
from models import Cliente  # Importa el modelo Cliente para manipular los datos de clientes

# Función para crear un nuevo cliente en la base de datos
def crear_cliente(db: Session, nombre: str, correo: str):
    """
    Crea un nuevo cliente en la base de datos.
    
    Args:
        db (Session): Sesión de la base de datos.
        nombre (str): Nombre del cliente.
        correo (str): Correo del cliente.

    Returns:
        Cliente: El cliente creado.

    Raises:
        ValueError: Si el correo ya está registrado.
    """
    try:
        # Crea una instancia del cliente con los datos proporcionados
        nuevo_cliente = Cliente(nombre=nombre, correo=correo)
        db.add(nuevo_cliente)  # Añade el cliente a la sesión
        db.commit()  # Realiza la operación de commit en la base de datos
        db.refresh(nuevo_cliente)  # Refresca el objeto para obtener los datos actualizados (como el ID)
        return nuevo_cliente  # Devuelve el cliente creado
    except IntegrityError:  # Captura errores de integridad, como violaciones de clave única
        db.rollback()  # Revierte la transacción en caso de error
        raise ValueError("El correo electrónico ya está registrado.")  # Lanza un error si el correo ya existe

# Función para obtener todos los clientes de la base de datos
def obtener_clientes(db: Session):
    """
    Obtiene todos los clientes de la base de datos.
    
    Args:
        db (Session): Sesión de la base de datos.

    Returns:
        List[Cliente]: Lista de clientes.
    """
    return db.query(Cliente).all()  # Realiza una consulta que devuelve todos los clientes

# Función para obtener un cliente por su ID
def obtener_cliente_por_id(db: Session, cliente_id: int):
    """
    Obtiene un cliente por su ID.

    Args:
        db (Session): Sesión de la base de datos.
        cliente_id (int): ID del cliente.

    Returns:
        Cliente | None: El cliente encontrado o None si no existe.
    """
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()  # Consulta por ID y devuelve el primer resultado

# Función para actualizar los datos de un cliente existente
def actualizar_cliente(db: Session, cliente_id: int, nuevos_datos: dict):
    """
    Actualiza los datos de un cliente existente.
    
    Args:
        db (Session): Sesión de la base de datos.
        cliente_id (int): ID del cliente a actualizar.
        nuevos_datos (dict): Diccionario con los campos y valores a actualizar.

    Returns:
        Cliente: El cliente actualizado.

    Raises:
        ValueError: Si el cliente no existe o el correo ya está en uso.
    """
    # Llama a la función que obtiene el cliente por ID
    cliente = obtener_cliente_por_id(db, cliente_id)
    if not cliente:  # Si no se encuentra el cliente, lanza un error
        raise ValueError(f"El cliente con ID {cliente_id} no existe.")

    try:
        # Itera sobre los nuevos datos y actualiza los atributos del cliente
        for key, value in nuevos_datos.items():
            if hasattr(cliente, key):  # Verifica si el atributo existe en el cliente
                setattr(cliente, key, value)  # Asigna el nuevo valor al atributo
        db.commit()  # Realiza la operación de commit para guardar los cambios
        db.refresh(cliente)  # Refresca el cliente actualizado con los datos nuevos
        return cliente  # Devuelve el cliente actualizado
    except IntegrityError:  # Captura errores de integridad, como violaciones de clave única
        db.rollback()  # Revierte la transacción en caso de error
        raise ValueError("El correo electrónico ya está registrado.")  # Lanza un error si el correo ya existe

# Función para eliminar un cliente de la base de datos
def eliminar_cliente(db: Session, cliente_id: int):
    """
    Elimina un cliente de la base de datos.
    
    Args:
        db (Session): Sesión de la base de datos.
        cliente_id (int): ID del cliente a eliminar.

    Returns:
        Cliente: El cliente eliminado.

    Raises:
        ValueError: Si el cliente no existe.
    """
    # Llama a la función que obtiene el cliente por ID
    cliente = obtener_cliente_por_id(db, cliente_id)
    if not cliente:  # Si no se encuentra el cliente, lanza un error
        raise ValueError(f"El cliente con ID {cliente_id} no existe.")
    db.delete(cliente)  # Elimina el cliente de la base de datos
    db.commit()  # Realiza la operación de commit para confirmar la eliminación
    return cliente  # Devuelve el cliente eliminado

