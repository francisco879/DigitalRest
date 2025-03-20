# Importaciones necesarias para las funciones
import matplotlib.pyplot as plt  # Para la creación de gráficos
from sqlalchemy.orm import Session  # Para manejar sesiones de la base de datos con SQLAlchemy
from models import Pedido, Menu, MenuIngrediente, PedidoMenu  # Modelos de la base de datos
from collections import Counter  # Herramienta para contar elementos en listas
from datetime import datetime, timedelta  # Manejo de fechas y tiempos
from models import MenuIngrediente, Ingrediente

def ventas_por_fecha(db: Session, intervalo="diarias"):
    """
    Generar gráfico de ventas por fecha según el intervalo seleccionado.
    
    Parámetros:
        db (Session): Sesión activa de la base de datos.
        intervalo (str): Intervalo para agrupar las ventas. Valores posibles:
                         "diarias", "semanales", "mensuales", "anuales".
    """
    # Obtener todos los pedidos y sus fechas de creación
    pedidos = db.query(Pedido).all()
    fechas = [pedido.fecha_creacion.date() for pedido in pedidos]

    # Agrupar las fechas según el intervalo seleccionado
    if intervalo == "diarias":
        agrupado = Counter(fechas)  # Agrupar por día
    elif intervalo == "semanales":
        # Agrupar por semana (primer día de la semana como referencia)
        semanas = [fecha - timedelta(days=fecha.weekday()) for fecha in fechas]
        agrupado = Counter(semanas)
    elif intervalo == "mensuales":
        # Agrupar por mes (primer día del mes)
        meses = [fecha.replace(day=1) for fecha in fechas]
        agrupado = Counter(meses)
    elif intervalo == "anuales":
        # Agrupar por año (primer día del año)
        años = [fecha.replace(month=1, day=1) for fecha in fechas]
        agrupado = Counter(años)
    else:
        # Manejo de errores para intervalos no válidos
        raise ValueError("Intervalo no válido. Usa: diarias, semanales, mensuales o anuales.")

    # Crear gráfico de barras
    plt.bar(agrupado.keys(), agrupado.values(), color="blue")
    plt.title(f"Ventas por Fecha ({intervalo.capitalize()})")  # Título dinámico según el intervalo
    plt.xlabel("Fecha")  # Etiqueta del eje X
    plt.ylabel("Número de Ventas")  # Etiqueta del eje Y
    plt.xticks(rotation=45)  # Rotar las etiquetas de las fechas para mejor legibilidad
    plt.tight_layout()  # Ajustar el diseño del gráfico
    plt.show()  # Mostrar el gráfico


def menus_mas_vendidos(db: Session):
    """
    Generar gráfico de los menús más vendidos.

    Parámetros:
        db (Session): Sesión activa de la base de datos.
    """
    # Recuperar todas las relaciones entre pedidos y menús
    pedido_menus = db.query(PedidoMenu).all()

    # Crear una lista con los nombres de los menús vendidos, omitiendo valores None
    menus_vendidos = [pedido_menu.menu.nombre for pedido_menu in pedido_menus if pedido_menu.menu is not None]

    if not menus_vendidos:
        # Mostrar mensaje si no hay datos suficientes
        CTkMessagebox(title="Sin datos", message="No hay datos suficientes para generar el gráfico.", icon="info", option_1="OK")
        return

    # Contar cuántas veces se ha vendido cada menú
    menus_contados = {menu: menus_vendidos.count(menu) for menu in set(menus_vendidos)}

    # Crear gráfico de barras
    plt.figure(figsize=(8, 6))
    plt.bar(menus_contados.keys(), menus_contados.values(), color='blue')
    plt.title("Menús Más Vendidos")
    plt.xlabel("Menú")  # Etiqueta del eje X
    plt.ylabel("Cantidad Vendida")  # Etiqueta del eje Y
    plt.xticks(rotation=45)  # Rotar etiquetas de los menús
    plt.tight_layout()  # Ajustar diseño
    plt.show()  # Mostrar el gráfico


def ingredientes_mas_usados(db: Session):
    """
    Generar gráfico de los ingredientes más usados en los menús.

    Parámetros:
        db (Session): Sesión activa de la base de datos.
    """
    try:
        # Obtener relaciones válidas entre menús e ingredientes
        ingredientes_usados = db.query(MenuIngrediente).join(MenuIngrediente.ingrediente).filter(Ingrediente.id.isnot(None)).all()

        # Crear una lista con los nombres de los ingredientes usados
        ingredientes = [item.ingrediente.nombre for item in ingredientes_usados if item.ingrediente is not None]

        if not ingredientes:
            print("No hay datos para mostrar en el gráfico.")
            return

        # Contar cuántas veces se ha usado cada ingrediente
        ingredientes_contados = Counter(ingredientes)

        # Crear gráfico de barras
        plt.bar(ingredientes_contados.keys(), ingredientes_contados.values(), color="green")
        plt.title("Ingredientes Más Usados")
        plt.xlabel("Ingrediente")  # Etiqueta del eje X
        plt.ylabel("Cantidad de Uso")  # Etiqueta del eje Y
        plt.xticks(rotation=45)  # Rotar etiquetas de los ingredientes
        plt.tight_layout()  # Ajustar diseño
        plt.show()  # Mostrar el gráfico

    except Exception as e:
        print(f"Error al generar el gráfico: {e}")