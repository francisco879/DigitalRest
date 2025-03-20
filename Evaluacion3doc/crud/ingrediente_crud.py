from sqlalchemy.orm import Session  # Importa la clase Session de SQLAlchemy para interactuar con la base de datos
from sqlalchemy.exc import IntegrityError  # Importa para manejar errores de integridad (como violaciones de claves únicas)
from models import Ingrediente  # Importa el modelo Ingrediente, que es la representación de los ingredientes en la base de datos

# Función para crear un nuevo ingrediente en la base de datos
def crear_ingrediente(db: Session, nombre: str, tipo: str, cantidad: float, unidad_medida: str):
    """
    Crea un nuevo ingrediente si no existe uno con el mismo nombre y tipo.
    """
    # Verificar si ya existe un ingrediente con el mismo nombre y tipo
    existente = db.query(Ingrediente).filter(Ingrediente.nombre == nombre, Ingrediente.tipo == tipo).first()
    if existente:  # Si ya existe, lanza un error
        raise ValueError(f"El ingrediente '{nombre}' de tipo '{tipo}' ya existe.")
    
    # Crea una nueva instancia de Ingrediente
    nuevo_ingrediente = Ingrediente(nombre=nombre, tipo=tipo, cantidad=cantidad, unidad_medida=unidad_medida)
    db.add(nuevo_ingrediente)  # Añade el nuevo ingrediente a la sesión de la base de datos

    try:
        db.commit()  # Realiza el commit para guardar el nuevo ingrediente en la base de datos
        db.refresh(nuevo_ingrediente)  # Refresca el objeto para obtener los datos actualizados (como el ID)
    except IntegrityError as e:  # Captura errores de integridad (por ejemplo, violación de claves únicas)
        db.rollback()  # Revierte la transacción en caso de error
        raise ValueError(f"Error al crear el ingrediente: {e}")  # Lanza un error con el mensaje correspondiente
    
    return nuevo_ingrediente  # Devuelve el ingrediente creado

# Función para obtener todos los ingredientes registrados en la base de datos
def obtener_ingredientes(db: Session):
    """
    Devuelve todos los ingredientes registrados en la base de datos.
    """
    return db.query(Ingrediente).all()  # Realiza una consulta para obtener todos los ingredientes

# Función para actualizar los datos de un ingrediente por su ID
def actualizar_ingrediente(db: Session, ingrediente_id: int, nuevos_datos: dict):
    """
    Actualiza los campos especificados de un ingrediente por su ID.
    nuevos_datos: Diccionario con los campos a actualizar (por ejemplo, {"cantidad": 10, "unidad_medida": "kg"}).
    """
    # Busca el ingrediente por ID
    ingrediente = db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
    if not ingrediente:  # Si no se encuentra el ingrediente, lanza un error
        raise ValueError(f"No se encontró un ingrediente con ID {ingrediente_id}.")
    
    # Actualiza solo los campos proporcionados en el diccionario
    for campo, valor in nuevos_datos.items():
        if hasattr(ingrediente, campo):  # Verifica si el ingrediente tiene el atributo
            setattr(ingrediente, campo, valor)  # Asigna el nuevo valor al atributo correspondiente

    try:
        db.commit()  # Realiza el commit para guardar los cambios
        db.refresh(ingrediente)  # Refresca el ingrediente con los nuevos datos
    except IntegrityError as e:  # Captura errores de integridad
        db.rollback()  # Revierte la transacción en caso de error
        raise ValueError(f"Error al actualizar el ingrediente: {e}")  # Lanza un error con el mensaje correspondiente
    
    return ingrediente  # Devuelve el ingrediente actualizado

# Función para eliminar un ingrediente de la base de datos por su ID
def eliminar_ingrediente(db: Session, ingrediente_id: int):
    """Eliminar un ingrediente de la base de datos por su ID."""
    # Busca el ingrediente por ID
    ingrediente = db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
    if ingrediente:  # Si el ingrediente existe, lo elimina
        db.delete(ingrediente)  # Elimina el ingrediente de la base de datos
        db.commit()  # Realiza el commit para confirmar la eliminación
        return ingrediente  # Devuelve el ingrediente eliminado
    else:  # Si no se encuentra el ingrediente, lanza un error
        raise ValueError(f"Ingrediente con ID {ingrediente_id} no encontrado.")

# Función para buscar un ingrediente por nombre y tipo (opcional)
def buscar_ingrediente(db: Session, nombre: str, tipo: str = None):
    """
    Busca un ingrediente por nombre y, opcionalmente, por tipo.
    """
    query = db.query(Ingrediente).filter(Ingrediente.nombre == nombre)  # Filtra por nombre
    if tipo:  # Si se proporciona un tipo, filtra también por tipo
        query = query.filter(Ingrediente.tipo == tipo)
    
    return query.first()  # Devuelve el primer ingrediente que coincida con los filtros
