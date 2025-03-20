from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# Configuración de la base de datos
DATABASE_URL = "sqlite:///restaurante.db"

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL, echo=True)

# Crear una clase base para los modelos
Base = declarative_base()

# Crear la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función para obtener una sesión como un context manager
@contextmanager
def get_db():
    """
    Proporciona una sesión de base de datos usando un context manager.
    """
    db = SessionLocal()  # Crea la sesión
    try:
        yield db  # Entrega la sesión para ser usada
    finally:
        db.close()  
