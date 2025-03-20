from sqlalchemy.orm import Session  # Importa la clase Session de SQLAlchemy para interactuar con la base de datos
from models import Menu, MenuIngrediente  # Importa los modelos Menu y MenuIngrediente que representan las tablas en la base de datos
from sqlalchemy.exc import IntegrityError  # Importa para manejar errores de integridad, como violaciones de claves únicas

# Función para crear un nuevo menú y asociar ingredientes con sus cantidades
def crear_menu(db: Session, nombre: str, descripcion: str, precio: float, ingredientes: dict):
    """
    Crear un menú y asociar ingredientes con sus cantidades.

    :param db: Sesión de la base de datos
    :param nombre: Nombre del menú
    :param descripcion: Descripción del menú
    :param precio: Precio del menú
    :param ingredientes: Diccionario con {ingrediente_id: cantidad}
    """
    # Verifica si ya existe un menú con el mismo nombre
    if db.query(Menu).filter(Menu.nombre == nombre).first():
        raise ValueError(f"Ya existe un menú con el nombre '{nombre}'.")  # Lanza error si ya existe un menú con el mismo nombre

    # Crea una nueva instancia de menú con los datos proporcionados
    nuevo_menu = Menu(nombre=nombre, descripcion=descripcion, precio=precio)
    db.add(nuevo_menu)  # Añade el nuevo menú a la sesión de la base de datos
    db.commit()  # Realiza el commit para guardar el nuevo menú
    db.refresh(nuevo_menu)  # Refresca el objeto menú con los datos actualizados, como el ID generado por la base de datos

    # Asociar ingredientes al menú utilizando el modelo MenuIngrediente
    for ingrediente_id, cantidad in ingredientes.items():
        nuevo_menu_ingrediente = MenuIngrediente(
            menu_id=nuevo_menu.id,  # Relaciona el menú con el ingrediente
            ingrediente_id=ingrediente_id,  # Relaciona el ingrediente
            cantidad=cantidad  # Define la cantidad del ingrediente en el menú
        )
        db.add(nuevo_menu_ingrediente)  # Añade la asociación a la sesión de la base de datos

    db.commit()  # Realiza el commit para guardar las asociaciones de ingredientes
    return nuevo_menu  # Devuelve el nuevo menú creado

# Función para obtener todos los menús registrados en la base de datos
def obtener_menus(db: Session):
    """
    Obtener todos los menús con sus ingredientes.
    """
    return db.query(Menu).all()  # Realiza una consulta para obtener todos los menús registrados

# Función para obtener un menú específico por su ID
def obtener_menu_por_id(db: Session, menu_id: int):
    """Obtiene un menú por su ID."""
    return db.query(Menu).filter(Menu.id == menu_id).first()  # Filtra por el ID del menú y devuelve el primero encontrado

# Función para actualizar los datos de un menú existente
def actualizar_menu(db: Session, menu_id: int, nuevos_datos: dict):
    """Actualiza los datos de un menú existente."""
    # Busca el menú por su ID
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if menu:  # Si el menú existe
        # Actualiza los atributos del menú con los nuevos datos proporcionados
        for key, value in nuevos_datos.items():
            if hasattr(menu, key):  # Verifica si el atributo existe en el menú
                setattr(menu, key, value)  # Asigna el nuevo valor al atributo
        db.commit()  # Realiza el commit para guardar los cambios
        db.refresh(menu)  # Refresca el objeto con los datos actualizados
        return menu  # Devuelve el menú actualizado
    else:  # Si no se encuentra el menú, lanza un error
        raise ValueError(f"El menú con ID {menu_id} no existe.")

# Función para eliminar un menú de la base de datos
def eliminar_menu(db: Session, menu_id: int):
    """Elimina un menú de la base de datos."""
    # Busca el menú por su ID
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if menu:  # Si el menú existe, lo elimina
        db.delete(menu)  # Elimina el menú de la base de datos
        db.commit()  # Realiza el commit para confirmar la eliminación
        return menu  # Devuelve el menú eliminado
    else:  # Si no se encuentra el menú, lanza un error
        raise ValueError(f"El menú con ID {menu_id} no existe.")
