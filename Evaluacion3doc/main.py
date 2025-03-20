# main.py

# Importaciones necesarias para la base de datos y la aplicación
from database import engine, get_db  # Motor de base de datos y sesión
from models import Base, Ingrediente, Cliente, Menu  # Modelos definidos en el sistema
from app import RestauranteApp  # Importar la clase principal de la aplicación gráfica

# Importar funciones CRUD para la manipulación de datos
from crud.ingrediente_crud import crear_ingrediente  # Función para crear ingredientes
from crud.cliente_crud import crear_cliente  # Función para crear clientes
from crud.menu_crud import crear_menu  # Función para crear menús

# Crear todas las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

# Función para agregar datos de prueba a la base de datos
def agregar_datos_de_prueba():
    """
    Agrega datos de ejemplo a la base de datos si las tablas están vacías.
    Incluye ingredientes, clientes y menús.
    """
    try:
        with get_db() as db:  # Iniciar sesión con la base de datos
            # Verificar si hay datos existentes antes de agregar ingredientes
            if not db.query(Ingrediente).first():
                print("Agregando ingredientes de prueba...")
                crear_ingrediente(db, nombre="Tomate", tipo="Vegetal", cantidad=10, unidad_medida="unidades")
                crear_ingrediente(db, nombre="Pan de Completo", tipo="Carbohidrato", cantidad=20, unidad_medida="unidades")
                crear_ingrediente(db, nombre="Vienesa", tipo="Proteína", cantidad=15, unidad_medida="unidades")
                print("Ingredientes de prueba agregados.")

            # Verificar si hay datos existentes antes de agregar clientes
            if not db.query(Cliente).first():
                print("Agregando clientes de prueba...")
                crear_cliente(db, nombre="Juan Pérez", correo="juan.perez@example.com")
                crear_cliente(db, nombre="María López", correo="maria.lopez@example.com")
                print("Clientes de prueba agregados.")

            # Verificar si hay datos existentes antes de agregar menús
            if not db.query(Menu).first():
                print("Agregando menús de prueba...")
                ingredientes = {1: 1, 2: 1, 3: 1}  # IDs de ingredientes y sus cantidades
                crear_menu(db, nombre="Completo Italiano", descripcion="Completo con tomate, pan y vienesa", ingredientes=ingredientes)
                print("Menús de prueba agregados.")
    except Exception as e:
        # Manejar errores y mostrar un mensaje de diagnóstico
        print(f"Error al agregar datos de prueba: {e}")

# Punto de entrada de la aplicación
if __name__ == "__main__":
    # Crear las tablas en la base de datos
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas.")

    # Inicializar datos de prueba
    print("Inicializando datos de prueba...")
    agregar_datos_de_prueba()  # Comentar esta línea si no se requieren datos de prueba cada vez
    print("Inicialización completada.")

    # Iniciar la aplicación gráfica
    print("Iniciando la aplicación...")
    app = RestauranteApp()  # Crear una instancia de la aplicación
    app.mainloop()  # Ejecutar el bucle principal de la GUI
