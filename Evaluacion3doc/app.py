import customtkinter as ctk
from tkinter import ttk
from CTkMessagebox import CTkMessagebox
from database import engine, get_db
from sqlalchemy.orm import Session
from models import Base
from crud.cliente_crud import crear_cliente, obtener_clientes
from crud.pedido_crud import crear_pedido, obtener_pedidos
from crud.ingrediente_crud import crear_ingrediente, obtener_ingredientes
from crud.menu_crud import crear_menu, obtener_menus
from fpdf import FPDF
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from crud.ingrediente_crud import eliminar_ingrediente
from database import get_db
from models import Ingrediente
from models import Menu
from models import Cliente
from models import Cliente
from models import Pedido
from models import PedidoMenu
from graficos import ventas_por_fecha, menus_mas_vendidos, ingredientes_mas_usados
from models import MenuIngrediente, Ingrediente



# Crear las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)


class RestauranteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Restaurante")
        self.geometry("800x700")

        # Crear el contenedor de pestañas usando CTkTabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")

        # Agregar pestañas
        self.tabview.add("Gestión de Ingredientes")
        self.tabview.add("Gestión de Menús")
        self.tabview.add("Gestión de Clientes")
        self.tabview.add("Panel de Compra")
        self.tabview.add("Pedidos")
        self.tabview.add("Gráficos")

        # Crear las pestañas
        self.create_ingredientes_tab()
        self.create_menu_tab()
        self.create_clientes_tab()
        self.create_panel_compra_tab()
        self.create_pedidos_tab()
        self.create_graficos_tab()
        
# ================================================================
#                      GESTION DE INGREDIENTES
# ================================================================

    def cargar_ingredientes(self):
        """Cargar los ingredientes desde la base de datos en el Treeview."""
        try:
            with get_db() as db:
                ingredientes = obtener_ingredientes(db)
                for ingrediente in ingredientes:
                    self.ingredientes_treeview.insert("", "end", values=(
                        ingrediente.id,  # ID del ingrediente
                        ingrediente.nombre,
                        ingrediente.tipo,
                        ingrediente.cantidad,
                        ingrediente.unidad_medida
                    ))
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al cargar ingredientes: {e}", icon="warning", option_1="OK")
    
    def create_ingredientes_tab(self):
        """Crear el contenido de la pestaña Gestión de Ingredientes."""
        tab = self.tabview.tab("Gestión de Ingredientes")
        
        # Frame superior para el formulario
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(pady=10, padx=10, fill="x")

        # Etiquetas y entradas para Nombre, Tipo, Cantidad y Unidad de Medida
        nombre_label = ctk.CTkLabel(form_frame, text="Nombre del Ingrediente:")
        nombre_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nombre_entry = ctk.CTkEntry(form_frame)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=5)

        tipo_label = ctk.CTkLabel(form_frame, text="Tipo:")
        tipo_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.tipo_entry = ctk.CTkEntry(form_frame)
        self.tipo_entry.grid(row=1, column=1, padx=5, pady=5)

        cantidad_label = ctk.CTkLabel(form_frame, text="Cantidad:")
        cantidad_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.cantidad_entry = ctk.CTkEntry(form_frame)
        self.cantidad_entry.grid(row=2, column=1, padx=5, pady=5)

        unidad_label = ctk.CTkLabel(form_frame, text="Unidad de Medida:")
        unidad_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.unidad_entry = ctk.CTkEntry(form_frame)
        self.unidad_entry.grid(row=3, column=1, padx=5, pady=5)

        # Botones CRUD
        agregar_button = ctk.CTkButton(form_frame, text="Agregar Ingrediente", command=self.agregar_ingrediente)
        agregar_button.grid(row=4, column=0, pady=10, padx=10)

        actualizar_button = ctk.CTkButton(form_frame, text="Actualizar Ingrediente", command=self.actualizar_ingrediente)
        actualizar_button.grid(row=4, column=1, pady=10, padx=10)

        eliminar_button = ctk.CTkButton(form_frame, text="Eliminar Ingrediente", command=self.eliminar_ingrediente)
        eliminar_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Treeview para mostrar los ingredientes
        self.ingredientes_treeview = ttk.Treeview(tab, columns=("ID", "Nombre", "Tipo", "Cantidad", "Unidad"), show="headings")
        self.ingredientes_treeview.heading("ID", text="ID")
        self.ingredientes_treeview.heading("Nombre", text="Nombre")
        self.ingredientes_treeview.heading("Tipo", text="Tipo")
        self.ingredientes_treeview.heading("Cantidad", text="Cantidad")
        self.ingredientes_treeview.heading("Unidad", text="Unidad")

        # Opcional: Ocultar la columna ID
        self.ingredientes_treeview.column("ID", width=0, stretch=False)

        self.ingredientes_treeview.pack(pady=10, padx=10, expand=True, fill="both")

        # Cargar ingredientes desde la base de datos al iniciar
        self.cargar_ingredientes()



    
    def actualizar_ingrediente(self):
        """Actualizar un ingrediente seleccionado del Treeview y reflejarlo en la base de datos."""
        selected_item = self.ingredientes_treeview.selection()

        if not selected_item:
            CTkMessagebox(title="Advertencia", message="Seleccione un ingrediente para actualizar.", icon="warning", option_1="OK")
            return

        # Obtener los valores actuales del ingrediente seleccionado
        values = self.ingredientes_treeview.item(selected_item, "values")
        nombre_actual, tipo_actual = values[0], values[1]

        # Obtener los nuevos datos del formulario
        nombre_nuevo = self.nombre_entry.get().strip()
        tipo_nuevo = self.tipo_entry.get().strip()
        cantidad_nueva = self.cantidad_entry.get().strip()
        unidad_nueva = self.unidad_entry.get().strip()

        # Validar los nuevos datos
        if not (nombre_nuevo and tipo_nuevo and cantidad_nueva.isdigit() and unidad_nueva):
            CTkMessagebox(title="Error", message="Ingrese datos válidos en el formulario.", icon="warning", option_1="OK")
            return

        try:
            with get_db() as db:
                # Buscar el ingrediente actual en la base de datos
                ingrediente = db.query(Ingrediente).filter(Ingrediente.nombre == nombre_actual, Ingrediente.tipo == tipo_actual).first()

                if not ingrediente:
                    CTkMessagebox(title="Error", message="No se encontró el ingrediente seleccionado en la base de datos.", icon="warning", option_1="OK")
                    return

                # Actualizar los valores del ingrediente
                ingrediente.nombre = nombre_nuevo
                ingrediente.tipo = tipo_nuevo
                ingrediente.cantidad = int(cantidad_nueva)
                ingrediente.unidad_medida = unidad_nueva

                db.commit()
                db.refresh(ingrediente)

                # Actualizar el Treeview
                self.ingredientes_treeview.item(selected_item, values=(nombre_nuevo, tipo_nuevo, cantidad_nueva, unidad_nueva))

                CTkMessagebox(title="Éxito", message="Ingrediente actualizado correctamente.", icon="check", option_1="OK")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al actualizar el ingrediente: {e}", icon="warning", option_1="OK")



    def agregar_ingrediente(self):
        """Agregar un ingrediente único a la base de datos y mostrarlo en el Treeview."""
        nombre = self.nombre_entry.get().strip()
        tipo = self.tipo_entry.get().strip()
        cantidad = self.cantidad_entry.get().strip()
        unidad = self.unidad_entry.get().strip()

        if nombre and tipo and cantidad.isdigit() and unidad:
            try:
                with get_db() as db:
                    crear_ingrediente(db, nombre=nombre, tipo=tipo, cantidad=int(cantidad), unidad_medida=unidad)
                    CTkMessagebox(title="Éxito", message="Ingrediente agregado correctamente.", icon="check", option_1="OK")
                    self.ingredientes_treeview.insert("", "end", values=(nombre, tipo, cantidad, unidad))
            except ValueError as e:
                CTkMessagebox(title="Error", message=f"{e}", icon="warning", option_1="OK")
        else:
            CTkMessagebox(title="Error", message="Ingrese todos los datos correctamente.", icon="warning", option_1="OK")
            
            
    def eliminar_seleccion(self, treeview, eliminar_db_func, mensaje_exito, mensaje_error):
        """
        Elimina un elemento seleccionado en un Treeview y su correspondiente entrada en la base de datos.
        """
        selected_item = treeview.selection()

        if not selected_item:
            CTkMessagebox(title="Advertencia", message="Seleccione un elemento para eliminar.", icon="warning", option_1="OK")
            return

        try:
            values = treeview.item(selected_item[0], "values")
            item_id = values[0]

            if not item_id:
                CTkMessagebox(title="Error", message="No se pudo identificar el elemento seleccionado.", icon="warning", option_1="OK")
                return

            eliminar_db_func(item_id)

            treeview.delete(selected_item[0])
            CTkMessagebox(title="Éxito", message=mensaje_exito, icon="check", option_1="OK")

        except Exception as e:
            CTkMessagebox(title="Error", message=f"{mensaje_error}: {e}", icon="warning", option_1="OK")
            
            
    def verificar_seleccion(self):
        """Prueba para verificar si el Treeview detecta la selección correctamente."""
        selected_item = self.ingredientes_treeview.selection()
        if not selected_item:
            print("No se seleccionó ningún elemento.")
            return

        values = self.ingredientes_treeview.item(selected_item[0], "values")
        print(f"Elemento seleccionado: {values}")

            
    def eliminar_ingrediente(self):
        selected_item = self.ingredientes_treeview.selection()
        if not selected_item:
            CTkMessagebox(title="Advertencia", message="Seleccione un ingrediente para eliminar.", icon="warning", option_1="OK")
            return

        try:
            values = self.ingredientes_treeview.item(selected_item[0], "values")
            ingrediente_id = values[0]  # Este valor corresponde al id

            with get_db() as db:
                ingrediente = db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
                if not ingrediente:
                    CTkMessagebox(title="Error", message="No se encontró el ingrediente en la base de datos.", icon="warning", option_1="OK")
                    return

                db.delete(ingrediente)
                db.commit()

            self.ingredientes_treeview.delete(selected_item[0])
            CTkMessagebox(title="Éxito", message="Ingrediente eliminado correctamente.", icon="check", option_1="OK")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al eliminar el ingrediente: {e}", icon="warning", option_1="OK")



 # ================================================================
#                      GESTION DE MENÚS
# ================================================================




    def create_menu_tab(self):
        """Crear el contenido de la pestaña Gestión de Menús."""
        tab = self.tabview.tab("Gestión de Menús")

        # Frame para el formulario
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(pady=10, padx=10, fill="x")

        # Campos para Nombre, Descripción y Precio del menú
        nombre_label = ctk.CTkLabel(form_frame, text="Nombre del Menú:")
        nombre_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nombre_menu_entry = ctk.CTkEntry(form_frame)
        self.nombre_menu_entry.grid(row=0, column=1, padx=5, pady=5)

        descripcion_label = ctk.CTkLabel(form_frame, text="Descripción:")
        descripcion_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.descripcion_menu_entry = ctk.CTkEntry(form_frame)
        self.descripcion_menu_entry.grid(row=1, column=1, padx=5, pady=5)

        precio_label = ctk.CTkLabel(form_frame, text="Precio:")
        precio_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.precio_menu_entry = ctk.CTkEntry(form_frame)
        self.precio_menu_entry.grid(row=2, column=1, padx=5, pady=5)

        # Botón para agregar menú
        agregar_button = ctk.CTkButton(form_frame, text="Agregar Menú", command=self.agregar_menu)
        agregar_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Tabla para mostrar los menús
        self.menu_treeview = ttk.Treeview(tab, columns=("Nombre", "Descripción", "Precio"), show="headings")
        self.menu_treeview.heading("Nombre", text="Nombre")
        self.menu_treeview.heading("Descripción", text="Descripción")
        self.menu_treeview.heading("Precio", text="Precio")
        self.menu_treeview.pack(pady=10, padx=10, expand=True, fill="both")


    def agregar_menu(self):
        """Agregar un menú a la lista y mostrarlo en el Treeview."""
        nombre = self.nombre_menu_entry.get().strip()
        descripcion = self.descripcion_menu_entry.get().strip()
        precio = self.precio_menu_entry.get().strip()

        if nombre and descripcion and precio.isdigit():
            try:
                with get_db() as db:
                    # Crear el menú en la base de datos
                    crear_menu(
                        db,
                        nombre=nombre,
                        descripcion=descripcion,
                        precio=float(precio),
                        ingredientes={}  # Ingredientes se pueden añadir luego
                    )

                    # Mostrar en el Treeview
                    self.menu_treeview.insert("", "end", values=(nombre, descripcion, f"${precio:.2f}"))
                    self.nombre_menu_entry.delete(0, "end")
                    self.descripcion_menu_entry.delete(0, "end")
                    self.precio_menu_entry.delete(0, "end")
                    CTkMessagebox(title="Éxito", message="Menú agregado correctamente.", icon="check", option_1="OK")
            except ValueError as ve:
                CTkMessagebox(title="Error", message=str(ve), icon="warning", option_1="OK")
            except Exception as e:
                CTkMessagebox(title="Error", message=f"Error al agregar menú: {e}", icon="warning", option_1="OK")
        else:
            CTkMessagebox(title="Error", message="Ingrese datos válidos.", icon="warning", option_1="OK")

            
    def eliminar_menu(self):
        """Eliminar un menú seleccionado del Treeview y la base de datos."""
        selected_item = self.menu_treeview.selection()

        if not selected_item:
            CTkMessagebox(title="Advertencia", message="Seleccione un menú para eliminar.", icon="warning", option_1="OK")
            return

        # Obtener el ID del menú seleccionado desde el Treeview
        values = self.menu_treeview.item(selected_item, "values")
        menu_id = values[0]  # El ID del menú está en la primera columna (oculta)

        try:
            with get_db() as db:
                # Buscar el menú en la base de datos y eliminarlo
                menu = db.query(Menu).filter(Menu.id == menu_id).first()

                if not menu:
                    CTkMessagebox(title="Error", message="No se encontró el menú en la base de datos.", icon="warning", option_1="OK")
                    return

                # Eliminar el menú
                db.delete(menu)
                db.commit()

                # Eliminar el menú del Treeview
                self.menu_treeview.delete(selected_item)

                CTkMessagebox(title="Éxito", message="Menú eliminado correctamente.", icon="check", option_1="OK")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al eliminar el menú: {e}", icon="warning", option_1="OK")



    def create_menu_tab(self):
        """Crear el contenido de la pestaña Gestión de Menús."""
        tab = self.tabview.tab("Gestión de Menús")

        # Frame para el formulario
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(pady=10, padx=10, fill="x")

        # Campos para Nombre, Descripción y Precio del menú
        nombre_label = ctk.CTkLabel(form_frame, text="Nombre del Menú:")
        nombre_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nombre_menu_entry = ctk.CTkEntry(form_frame)
        self.nombre_menu_entry.grid(row=0, column=1, padx=5, pady=5)

        descripcion_label = ctk.CTkLabel(form_frame, text="Descripción:")
        descripcion_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.descripcion_menu_entry = ctk.CTkEntry(form_frame)
        self.descripcion_menu_entry.grid(row=1, column=1, padx=5, pady=5)

        precio_label = ctk.CTkLabel(form_frame, text="Precio:")
        precio_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.precio_menu_entry = ctk.CTkEntry(form_frame)
        self.precio_menu_entry.grid(row=2, column=1, padx=5, pady=5)

        # Frame para seleccionar ingredientes
        ingredientes_frame = ctk.CTkFrame(tab)
        ingredientes_frame.pack(pady=10, padx=10, fill="both")

        ingredientes_label = ctk.CTkLabel(ingredientes_frame, text="Seleccionar Ingredientes:")
        ingredientes_label.pack(pady=5)

        # Treeview para mostrar los ingredientes disponibles con selección múltiple
        self.ingredientes_treeview = ttk.Treeview(
            ingredientes_frame,
            columns=("ID", "Nombre", "Cantidad Disponible", "Unidad"),
            show="headings",
            selectmode="extended"  # Permitir selección múltiple
        )
        self.ingredientes_treeview.heading("ID", text="ID")
        self.ingredientes_treeview.heading("Nombre", text="Nombre")
        self.ingredientes_treeview.heading("Cantidad Disponible", text="Cantidad Disponible")
        self.ingredientes_treeview.heading("Unidad", text="Unidad")
        self.ingredientes_treeview.column("ID", width=0, stretch=False)  # Ocultar columna ID
        self.ingredientes_treeview.pack(pady=10, padx=10, expand=True, fill="both")

        # Frame para acciones
        actions_frame = ctk.CTkFrame(tab)
        actions_frame.pack(pady=10, padx=10, fill="x")

        # Botones para agregar y editar menú
        agregar_button = ctk.CTkButton(actions_frame, text="Crear Menú", command=self.crear_menu)
        agregar_button.pack(side="left", padx=10)

        eliminar_button = ctk.CTkButton(actions_frame, text="Eliminar Menú", command=self.eliminar_menu)
        eliminar_button.pack(side="left", padx=10)

        # Treeview para mostrar los menús creados
        self.menu_treeview = ttk.Treeview(tab, columns=("ID", "Nombre", "Descripción", "Ingredientes"), show="headings")
        self.menu_treeview.heading("ID", text="ID")
        self.menu_treeview.heading("Nombre", text="Nombre")
        self.menu_treeview.heading("Descripción", text="Descripción")
        self.menu_treeview.heading("Ingredientes", text="Ingredientes")
        self.menu_treeview.column("ID", width=0, stretch=False)  # Ocultar columna ID
        self.menu_treeview.pack(pady=10, padx=10, expand=True, fill="both")

        # Cargar ingredientes y menús desde la base de datos
        self.cargar_ingredientes_menu()
        self.cargar_menus()

    def crear_menu(self):
        """Crear un nuevo menú utilizando ingredientes seleccionados."""
        nombre = self.nombre_menu_entry.get().strip()
        descripcion = self.descripcion_menu_entry.get().strip()
        precio = self.precio_menu_entry.get().strip()

        if not (nombre and descripcion and precio.isdigit()):
            CTkMessagebox(title="Error", message="Ingrese nombre, descripción y precio válidos para el menú.", icon="warning", option_1="OK")
            return

        # Obtener ingredientes seleccionados y sus cantidades
        seleccionados = self.ingredientes_treeview.selection()
        if not seleccionados:
            CTkMessagebox(title="Error", message="Seleccione al menos un ingrediente.", icon="warning", option_1="OK")
            return

        ingredientes = {}
        for item in seleccionados:
            values = self.ingredientes_treeview.item(item, "values")
            ingrediente_id = int(values[0])
            cantidad_requerida = 1  # Ajustar para pedir cantidades específicas (puedes agregar un input adicional)
            ingredientes[ingrediente_id] = cantidad_requerida

        try:
            with get_db() as db:
                # Crear menú en la base de datos
                nuevo_menu = crear_menu(
                    db,
                    nombre=nombre,
                    descripcion=descripcion,
                    precio=float(precio),  # Pasar el precio como argumento
                    ingredientes=ingredientes
                )
                # Mostrar en el Treeview
                ingredientes_str = ", ".join([f"{ingrediente_id} ({cantidad})" for ingrediente_id, cantidad in ingredientes.items()])
                self.menu_treeview.insert("", "end", values=(nuevo_menu.id, nombre, descripcion, ingredientes_str))
                CTkMessagebox(title="Éxito", message="Menú creado correctamente.", icon="check", option_1="OK")
                self.nombre_menu_entry.delete(0, "end")
                self.descripcion_menu_entry.delete(0, "end")
                self.precio_menu_entry.delete(0, "end")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al crear el menú: {e}", icon="warning", option_1="OK")

            
    def cargar_ingredientes_menu(self):
        """Cargar ingredientes disponibles en la pestaña de Gestión de Menús."""
        try:
            with get_db() as db:
                ingredientes = obtener_ingredientes(db)
                for ingrediente in ingredientes:
                    self.ingredientes_treeview.insert("", "end", values=(
                        ingrediente.id,
                        ingrediente.nombre,
                        ingrediente.cantidad,
                        ingrediente.unidad_medida
                    ))
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al cargar ingredientes: {e}", icon="warning", option_1="OK")
    
    def cargar_menus(self):
        """Cargar menús desde la base de datos."""
        try:
            with get_db() as db:
                menus = obtener_menus(db)
                for menu in menus:
                    ingredientes_str = ", ".join([
                        f"{ing.ingrediente.nombre} ({ing.cantidad})"
                        for ing in menu.ingredientes
                    ])
                    self.menu_treeview.insert("", "end", values=(
                        menu.id, menu.nombre, menu.descripcion, ingredientes_str
                    ))
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al cargar menús: {e}", icon="warning", option_1="OK")

            
    def editar_menu(self):
        """Editar un menú seleccionado en el Treeview y actualizarlo en la base de datos."""
        selected_item = self.menu_treeview.selection()
        
        if not selected_item:
            CTkMessagebox(title="Advertencia", message="Seleccione un menú para editar.", icon="warning", option_1="OK")
            return

        # Obtener los datos actuales del menú seleccionado
        values = self.menu_treeview.item(selected_item, "values")
        menu_id, nombre_actual, descripcion_actual = values[0], values[1], values[2]

        # Mostrar los valores actuales en los campos de entrada para editarlos
        self.nombre_menu_entry.delete(0, "end")
        self.nombre_menu_entry.insert(0, nombre_actual)

        self.descripcion_menu_entry.delete(0, "end")
        self.descripcion_menu_entry.insert(0, descripcion_actual)

        # Confirmar edición
        confirmar = CTkMessagebox(
            title="Confirmar Edición",
            message="¿Está seguro de guardar los cambios en este menú?",
            icon="question",
            option_1="Sí",
            option_2="No"
        )

        if confirmar.get() == "Sí":
            # Obtener los nuevos valores del formulario
            nuevo_nombre = self.nombre_menu_entry.get().strip()
            nueva_descripcion = self.descripcion_menu_entry.get().strip()

            if not (nuevo_nombre and nueva_descripcion):
                CTkMessagebox(title="Error", message="Ingrese datos válidos.", icon="warning", option_1="OK")
                return

            try:
                with get_db() as db:
                    # Actualizar el menú en la base de datos
                    menu = db.query(Menu).filter(Menu.id == menu_id).first()
                    if menu:
                        menu.nombre = nuevo_nombre
                        menu.descripcion = nueva_descripcion
                        db.commit()
                        db.refresh(menu)

                        # Actualizar el Treeview con los nuevos valores
                        self.menu_treeview.item(selected_item, values=(menu_id, nuevo_nombre, nueva_descripcion))
                        CTkMessagebox(title="Éxito", message="Menú actualizado correctamente.", icon="check", option_1="OK")
                    else:
                        CTkMessagebox(title="Error", message="No se encontró el menú en la base de datos.", icon="warning", option_1="OK")
            except Exception as e:
                CTkMessagebox(title="Error", message=f"Error al actualizar el menú: {e}", icon="warning", option_1="OK")
                

                
                
# ================================================================
#                      GESTION DE CLIENTES
# ================================================================


    def create_clientes_tab(self):
        """Crear el contenido de la pestaña Gestión de Clientes."""
        tab = self.tabview.tab("Gestión de Clientes")

        # Frame para el formulario
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(pady=10, padx=10, fill="x")

        # Campos para Nombre y Correo del cliente
        nombre_label = ctk.CTkLabel(form_frame, text="Nombre del Cliente:")
        nombre_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nombre_cliente_entry = ctk.CTkEntry(form_frame)
        self.nombre_cliente_entry.grid(row=0, column=1, padx=5, pady=5)

        correo_label = ctk.CTkLabel(form_frame, text="Correo Electrónico:")
        correo_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.correo_cliente_entry = ctk.CTkEntry(form_frame)
        self.correo_cliente_entry.grid(row=1, column=1, padx=5, pady=5)

        # Botones para Agregar, Editar y Eliminar clientes
        acciones_frame = ctk.CTkFrame(tab)
        acciones_frame.pack(pady=10, padx=10, fill="x")

        agregar_button = ctk.CTkButton(acciones_frame, text="Agregar Cliente", command=self.agregar_cliente)
        agregar_button.pack(side="left", padx=10)

        editar_button = ctk.CTkButton(acciones_frame, text="Editar Cliente", command=self.editar_cliente)
        editar_button.pack(side="left", padx=10)

        eliminar_button = ctk.CTkButton(acciones_frame, text="Eliminar Cliente", command=self.eliminar_cliente)
        eliminar_button.pack(side="left", padx=10)

        # Tabla para mostrar los clientes
        self.clientes_treeview = ttk.Treeview(tab, columns=("ID", "Nombre", "Correo"), show="headings")
        self.clientes_treeview.heading("ID", text="ID")
        self.clientes_treeview.heading("Nombre", text="Nombre")
        self.clientes_treeview.heading("Correo", text="Correo")
        self.clientes_treeview.column("ID", width=0, stretch=False)  # Ocultar columna ID
        self.clientes_treeview.pack(pady=10, padx=10, expand=True, fill="both")

        # Cargar clientes desde la base de datos
        self.cargar_clientes()





    def agregar_cliente(self):
        """Agregar un nuevo cliente a la base de datos y al Treeview."""
        nombre = self.nombre_cliente_entry.get().strip()
        correo = self.correo_cliente_entry.get().strip()

        if not (nombre and correo):
            CTkMessagebox(title="Error", message="Ingrese nombre y correo válidos.", icon="warning", option_1="OK")
            return

        try:
            with get_db() as db:
                nuevo_cliente = crear_cliente(db, nombre=nombre, correo=correo)
                self.clientes_treeview.insert("", "end", values=(nuevo_cliente.id, nuevo_cliente.nombre, nuevo_cliente.correo))
                CTkMessagebox(title="Éxito", message="Cliente agregado correctamente.", icon="check", option_1="OK")
                self.nombre_cliente_entry.delete(0, "end")
                self.correo_cliente_entry.delete(0, "end")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al agregar cliente: {e}", icon="warning", option_1="OK")
            
            
    def editar_cliente(self):
        """Editar un cliente seleccionado en el Treeview y actualizarlo en la base de datos."""
        selected_item = self.clientes_treeview.selection()

        if not selected_item:
            CTkMessagebox(title="Advertencia", message="Seleccione un cliente para editar.", icon="warning", option_1="OK")
            return

        # Obtener los valores actuales del cliente seleccionado
        values = self.clientes_treeview.item(selected_item, "values")
        cliente_id, nombre_actual, correo_actual = values[0], values[1], values[2]

        # Mostrar los valores actuales en los campos de entrada para editarlos
        self.nombre_cliente_entry.delete(0, "end")
        self.nombre_cliente_entry.insert(0, nombre_actual)

        self.correo_cliente_entry.delete(0, "end")
        self.correo_cliente_entry.insert(0, correo_actual)

        # Confirmar la edición
        confirmar = CTkMessagebox(
            title="Confirmar Edición",
            message=f"¿Está seguro de guardar los cambios para el cliente con ID {cliente_id}?",
            icon="question",
            option_1="Sí",
            option_2="No"
        )

        if confirmar.get() == "Sí":
            # Obtener los nuevos valores del formulario
            nuevo_nombre = self.nombre_cliente_entry.get().strip()
            nuevo_correo = self.correo_cliente_entry.get().strip()

            if not (nuevo_nombre and nuevo_correo):
                CTkMessagebox(title="Error", message="Ingrese datos válidos.", icon="warning", option_1="OK")
                return

            try:
                with get_db() as db:
                    # Actualizar el cliente en la base de datos
                    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
                    if cliente:
                        cliente.nombre = nuevo_nombre
                        cliente.correo = nuevo_correo
                        db.commit()
                        db.refresh(cliente)

                        # Actualizar los valores en el Treeview
                        self.clientes_treeview.item(selected_item, values=(cliente_id, nuevo_nombre, nuevo_correo))
                        CTkMessagebox(title="Éxito", message="Cliente actualizado correctamente.", icon="check", option_1="OK")
                    else:
                        CTkMessagebox(title="Error", message="No se encontró el cliente en la base de datos.", icon="warning", option_1="OK")
            except Exception as e:
                CTkMessagebox(title="Error", message=f"Error al actualizar cliente: {e}", icon="warning", option_1="OK")

                
    def eliminar_cliente(self):
        """Eliminar un cliente seleccionado del Treeview y la base de datos."""
        selected_item = self.clientes_treeview.selection()

        if not selected_item:
            CTkMessagebox(title="Advertencia", message="Seleccione un cliente para eliminar.", icon="warning", option_1="OK")
            return

        # Obtener el ID del cliente seleccionado
        values = self.clientes_treeview.item(selected_item, "values")
        cliente_id = values[0]

        try:
            with get_db() as db:
                cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

                if not cliente:
                    CTkMessagebox(title="Error", message="No se encontró el cliente en la base de datos.", icon="warning", option_1="OK")
                    return

                db.delete(cliente)
                db.commit()

                # Eliminar del Treeview
                self.clientes_treeview.delete(selected_item)
                CTkMessagebox(title="Éxito", message="Cliente eliminado correctamente.", icon="check", option_1="OK")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al eliminar cliente: {e}", icon="warning", option_1="OK")
            
    def cargar_clientes(self):
        """Cargar clientes existentes en el Treeview."""
        try:
            with get_db() as db:
                clientes = obtener_clientes(db)
                for cliente in clientes:
                    self.clientes_treeview.insert("", "end", values=(cliente.id, cliente.nombre, cliente.correo))
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al cargar clientes: {e}", icon="warning", option_1="OK")
            
    def cargar_menus_para_compra(self):
        """Cargar menús en el combobox para seleccionarlos."""
        try:
            with get_db() as db:
                menus = obtener_menus(db)
                # Crear tuplas como cadenas para cada menú
                self.menu_combobox['values'] = [f"({menu.id}, '{menu.nombre}')" for menu in menus]
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al cargar menús: {e}", icon="warning", option_1="OK")
            
# ================================================================
#                      PANEL DE COMPRA
# ================================================================
            
            
    def agregar_menu_al_pedido(self):
        """Agregar un menú al pedido actual."""
        menu_seleccionado = self.menu_combobox.get()
        if not menu_seleccionado:
            CTkMessagebox(title="Advertencia", message="Seleccione un menú.", icon="warning", option_1="OK")
            return

        try:
            # Validar que el valor tenga el formato correcto
            if not menu_seleccionado.startswith("(") or not menu_seleccionado.endswith(")"):
                raise ValueError("El formato del menú seleccionado es inválido.")

            # Convertir la cadena seleccionada en una tupla
            menu_id, menu_nombre = eval(menu_seleccionado)

            # Buscar el menú en la base de datos y agregar al Treeview
            with get_db() as db:
                menu = db.query(Menu).filter(Menu.id == menu_id).first()
                if not menu:
                    CTkMessagebox(title="Error", message="No se encontró el menú en la base de datos.", icon="warning", option_1="OK")
                    return

                self.pedido_treeview.insert("", "end", values=(menu.nombre, 1, menu.precio))
                self.actualizar_total()
        except ValueError as ve:
            CTkMessagebox(title="Error", message=f"Error de formato: {ve}", icon="warning", option_1="OK")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al agregar menú: {e}", icon="warning", option_1="OK")

      

    def create_panel_compra_tab(self):
        """Crear el contenido de la pestaña Panel de Compra."""
        tab = self.tabview.tab("Panel de Compra")

        # Frame para la selección del cliente
        cliente_frame = ctk.CTkFrame(tab)
        cliente_frame.pack(pady=10, padx=10, fill="x")

        cliente_label = ctk.CTkLabel(cliente_frame, text="Seleccione Cliente:")
        cliente_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.cliente_combobox = ttk.Combobox(cliente_frame, state="readonly")
        self.cliente_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Frame para la selección del menú
        menu_frame = ctk.CTkFrame(tab)
        menu_frame.pack(pady=10, padx=10, fill="x")

        menu_label = ctk.CTkLabel(menu_frame, text="Seleccione Menú:")
        menu_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.menu_combobox = ttk.Combobox(menu_frame, state="readonly")
        self.menu_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Botón para agregar menú al pedido
        agregar_menu_button = ctk.CTkButton(menu_frame, text="Agregar al Pedido", command=self.agregar_menu_al_pedido)
        agregar_menu_button.grid(row=0, column=2, padx=10)

        # Tabla para mostrar el pedido actual
        self.pedido_treeview = ttk.Treeview(tab, columns=("Nombre", "Cantidad", "Precio"), show="headings")
        self.pedido_treeview.heading("Nombre", text="Nombre")
        self.pedido_treeview.heading("Cantidad", text="Cantidad")
        self.pedido_treeview.heading("Precio", text="Precio")
        self.pedido_treeview.pack(pady=10, padx=10, expand=True, fill="both")

        # Frame para acciones (generar boleta y mostrar total)
        acciones_frame = ctk.CTkFrame(tab)
        acciones_frame.pack(pady=10, padx=10, fill="x")

        self.total_label = ctk.CTkLabel(acciones_frame, text="Total: $0.00", font=("Arial", 16))
        self.total_label.pack(side="left", padx=10)

        generar_boleta_button = ctk.CTkButton(acciones_frame, text="Generar Boleta", command=self.generar_boleta)
        generar_boleta_button.pack(side="right", padx=10)

        # Cargar clientes y menús desde la base de datos
        self.cargar_clientes_para_compra()
        self.cargar_menus_para_compra()
        
    def cargar_clientes_para_compra(self):
        """Cargar clientes en el combobox para seleccionarlos en Panel de Compra."""
        try:
            with get_db() as db:
                clientes = obtener_clientes(db)
                # Formato del combobox: "ID, Nombre"
                self.cliente_combobox['values'] = [f"{cliente.id}, {cliente.nombre}" for cliente in clientes]
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al cargar clientes: {e}", icon="warning", option_1="OK")
            
    def cargar_clientes_para_pedidos(self):
        """Cargar clientes en el combobox para seleccionarlos en Pedidos."""
        try:
            with get_db() as db:
                clientes = obtener_clientes(db)
                # Usar el formato "ID, Nombre"
                self.cliente_pedidos_combobox['values'] = [f"{cliente.id}, {cliente.nombre}" for cliente in clientes]
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al cargar clientes: {e}", icon="warning", option_1="OK")

  
            
    def actualizar_total(self):
        """Actualizar el total del pedido."""
        total = 0
        for item in self.pedido_treeview.get_children():
            _, _, precio = self.pedido_treeview.item(item, "values")
            total += float(precio)
        self.total_label.configure(text=f"Total: ${total:.2f}")
        
    def guardar_pedido(self):
        """Guardar el pedido actual en la base de datos."""
        if not self.pedido_treeview.get_children():
            CTkMessagebox(title="Advertencia", message="No hay elementos en el pedido para guardar.", icon="warning", option_1="OK")
            return

        # Verificar cliente seleccionado
        cliente_seleccionado = self.cliente_combobox.get()
        if not cliente_seleccionado:
            CTkMessagebox(title="Advertencia", message="Seleccione un cliente para el pedido.", icon="warning", option_1="OK")
            return

        # Extraer ID del cliente desde el combobox
        try:
            cliente_id, _ = eval(cliente_seleccionado)  # Convertir la cadena a una tupla (id, nombre)
        except ValueError:
            CTkMessagebox(title="Error", message="Formato de cliente inválido.", icon="warning", option_1="OK")
            return

        # Preparar datos del pedido
        total = 0
        menus_seleccionados = []
        for item in self.pedido_treeview.get_children():
            nombre, cantidad, precio = self.pedido_treeview.item(item, "values")
            menus_seleccionados.append((nombre, int(cantidad), float(precio)))
            total += int(cantidad) * float(precio)

        try:
            with get_db() as db:
                # Crear el pedido
                nuevo_pedido = Pedido(cliente_id=cliente_id, total=total, fecha_creacion=datetime.utcnow())
                db.add(nuevo_pedido)
                db.commit()
                db.refresh(nuevo_pedido)  # Obtener el ID del pedido recién creado

                # Agregar los menús al pedido
                for nombre_menu, cantidad, precio in menus_seleccionados:
                    menu = db.query(Menu).filter_by(nombre=nombre_menu).first()
                    if menu:
                        pedido_menu = PedidoMenu(pedido_id=nuevo_pedido.id, menu_id=menu.id, cantidad=cantidad)
                        db.add(pedido_menu)

                db.commit()
                CTkMessagebox(title="Éxito", message="Pedido guardado correctamente.", icon="check", option_1="OK")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al guardar el pedido: {e}", icon="warning", option_1="OK")

        
        
    def generar_boleta(self):
        """Generar boleta detallada en PDF desde el pedido actual y guardar el pedido en la base de datos."""
        if not self.pedido_treeview.get_children():
            CTkMessagebox(title="Advertencia", message="No hay elementos en el pedido", icon="warning", option_1="OK")
            return

        # Capturar el cliente seleccionado
        cliente_seleccionado = self.cliente_combobox.get()
        if not cliente_seleccionado:
            CTkMessagebox(title="Advertencia", message="Por favor, seleccione un cliente", icon="warning", option_1="OK")
            return

        try:
            # Separar ID y nombre del cliente
            cliente_id, cliente_nombre = cliente_seleccionado.split(", ", 1)
            cliente_id = int(cliente_id)
        except ValueError:
            CTkMessagebox(title="Error", message="Formato de cliente inválido.", icon="warning", option_1="OK")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Boleta Restaurante", ln=True, align='C')

        # Información del negocio
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "Razón Social del Negocio", ln=True, align='L')
        pdf.cell(0, 10, "RUT: 12345678-9", ln=True, align='L')
        pdf.cell(0, 10, "Dirección: Calle Falsa 123", ln=True, align='L')
        pdf.cell(0, 10, "Teléfono: +56 9 1234 5678", ln=True, align='L')
        pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align='R')

        # Agregar el nombre del comprador
        pdf.cell(0, 10, f"Cliente: {cliente_nombre}", ln=True, align='L')
        pdf.ln(10)

        # Encabezado de la tabla
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(60, 10, "Nombre", border=1, align='C')
        pdf.cell(30, 10, "Cantidad", border=1, align='C')
        pdf.cell(40, 10, "Precio Unitario", border=1, align='C')
        pdf.cell(40, 10, "Subtotal", border=1, align='C')
        pdf.ln()

        # Detalles del pedido
        pdf.set_font("Arial", size=12)
        total = 0
        menus_pedido = []  # Guardará los menús para asociarlos al pedido en la BD
        for item in self.pedido_treeview.get_children():
            # Recuperar los valores de cada fila del Treeview
            nombre_menu, cantidad, precio = self.pedido_treeview.item(item)['values']
            cantidad = int(cantidad)
            precio = float(precio)
            subtotal = precio * cantidad

            # Agregar detalles al PDF
            pdf.cell(60, 10, nombre_menu, border=1)
            pdf.cell(30, 10, str(cantidad), border=1, align='C')
            pdf.cell(40, 10, f"${precio:.2f}", border=1, align='C')
            pdf.cell(40, 10, f"${subtotal:.2f}", border=1, align='C')
            pdf.ln()

            total += subtotal
            menus_pedido.append((nombre_menu, cantidad))

        # Subtotal, IVA y Total
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(130, 10, "Subtotal:", 0, 0, 'R')
        pdf.cell(40, 10, f"${total:.2f}", border=1, align='C')
        pdf.ln()

        iva = total * 0.19  # IVA del 19%
        pdf.cell(130, 10, "IVA (19%):", 0, 0, 'R')
        pdf.cell(40, 10, f"${iva:.2f}", border=1, align='C')
        pdf.ln()

        total_con_iva = total + iva
        pdf.cell(130, 10, "Total:", 0, 0, 'R')
        pdf.cell(40, 10, f"${total_con_iva:.2f}", border=1, align='C')
        pdf.ln(10)

        # Pie de página
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, "Gracias por su compra. Para cualquier consulta, llámenos al +56 9 1234 5678.", 0, 1, 'C')
        pdf.cell(0, 10, "Los productos adquiridos no tienen garantía.", 0, 1, 'C')

        # Guardar el archivo PDF
        pdf_filename = "boleta.pdf"
        pdf.output(pdf_filename)

        # Guardar el pedido en la base de datos
        with get_db() as db:
            # Crear el pedido
            nuevo_pedido = Pedido(cliente_id=cliente_id, total=total_con_iva)
            db.add(nuevo_pedido)
            db.commit()
            db.refresh(nuevo_pedido)

            # Asociar los menús al pedido
            for nombre_menu, cantidad in menus_pedido:
                menu = db.query(Menu).filter(Menu.nombre == nombre_menu).first()
                if menu:
                    pedido_menu = PedidoMenu(pedido_id=nuevo_pedido.id, menu_id=menu.id, cantidad=cantidad)
                    db.add(pedido_menu)

            db.commit()

        # Mostrar mensaje de confirmación
        CTkMessagebox(title="Boleta Generada", message=f"Boleta guardada como {pdf_filename} y pedido registrado.", icon="info", option_1="OK")

        # Limpiar el pedido actual
        self.pedido_treeview.delete(*self.pedido_treeview.get_children())
        self.total_label.configure(text="Total: $0.00")

        
    def obtener_nombres_clientes(self):
        """Obtener los nombres de los clientes registrados en la base de datos."""
        with get_db() as db:
            # Obtener todos los clientes
            clientes = obtener_clientes(db)  # Función definida en cliente_crud.py
            # Extraer solo los nombres
            nombres_clientes = [cliente.nombre for cliente in clientes]
        return nombres_clientes
    
# ================================================================
#                      PEDIDOS (MOSTRAR PEDIDOS)
# ================================================================


    def create_pedidos_tab(self):
        """Crear el contenido de la pestaña Gestión de Pedidos."""
        tab = self.tabview.tab("Pedidos")
        
        # Frame superior para seleccionar cliente
        cliente_frame = ctk.CTkFrame(tab)
        cliente_frame.pack(pady=10, padx=10, fill="x")

        cliente_label = ctk.CTkLabel(cliente_frame, text="Seleccionar Cliente:")
        cliente_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Combobox para seleccionar cliente
        self.cliente_pedidos_combobox = ttk.Combobox(cliente_frame, state="readonly")
        self.cliente_pedidos_combobox.grid(row=0, column=1, padx=5, pady=5)

        # Botón para mostrar pedidos del cliente seleccionado
        mostrar_pedidos_button = ctk.CTkButton(cliente_frame, text="Mostrar Pedidos", command=self.mostrar_pedidos_cliente)
        mostrar_pedidos_button.grid(row=0, column=2, padx=5, pady=5)

        # Tabla para mostrar los pedidos
        self.pedidos_treeview = ttk.Treeview(tab, columns=("Descripción", "Total", "Fecha", "Cantidad Menús"), show="headings")
        self.pedidos_treeview.heading("Descripción", text="Descripción")
        self.pedidos_treeview.heading("Total", text="Total")
        self.pedidos_treeview.heading("Fecha", text="Fecha")
        self.pedidos_treeview.heading("Cantidad Menús", text="Cantidad Menús")
        self.pedidos_treeview.pack(pady=10, padx=10, expand=True, fill="both")

        # Opcional: Botones para eliminar o actualizar pedidos
        acciones_frame = ctk.CTkFrame(tab)
        acciones_frame.pack(pady=10, padx=10, fill="x")

        # Botón para eliminar un pedido
        eliminar_pedido_button = ctk.CTkButton(acciones_frame, text="Eliminar Pedido", command=self.eliminar_pedido)
        eliminar_pedido_button.pack(side="left", padx=10)

        # Botón para editar un pedido (opcional)
        editar_pedido_button = ctk.CTkButton(acciones_frame, text="Editar Pedido", command=self.editar_pedido)
        editar_pedido_button.pack(side="left", padx=10)

        # Cargar clientes en el combobox
        self.cargar_clientes_para_pedidos()

        
    def mostrar_pedidos_cliente(self):
        """Mostrar los pedidos asociados al cliente seleccionado."""
        cliente_seleccionado = self.cliente_pedidos_combobox.get()
        if not cliente_seleccionado:
            CTkMessagebox(title="Advertencia", message="Seleccione un cliente para mostrar sus pedidos.", icon="warning", option_1="OK")
            return

        try:
            # Separar ID y nombre del cliente
            cliente_id, cliente_nombre = cliente_seleccionado.split(", ", 1)
            cliente_id = int(cliente_id)
        except ValueError:
            CTkMessagebox(title="Error", message="Formato de cliente inválido.", icon="warning", option_1="OK")
            return

        # Obtener pedidos desde la base de datos
        with get_db() as db:
            from sqlalchemy.orm import joinedload

            # Cargar el cliente y sus pedidos con sus menús
            cliente = db.query(Cliente).options(
                joinedload(Cliente.pedidos).joinedload(Pedido.menus)
            ).filter(Cliente.id == cliente_id).first()

            if not cliente or not cliente.pedidos:
                CTkMessagebox(title="Información", message="No se encontraron pedidos para este cliente.", icon="info", option_1="OK")
                return

            # Limpiar la tabla antes de agregar nuevos datos
            for item in self.pedidos_treeview.get_children():
                self.pedidos_treeview.delete(item)

            # Agregar pedidos al Treeview
            for pedido in cliente.pedidos:
                total = pedido.total
                fecha = pedido.fecha_creacion.strftime("%d/%m/%Y %H:%M:%S")
                cantidad_menus = sum(menu.cantidad for menu in pedido.menus)  # Sumar las cantidades de los menús
                descripcion = f"Pedido de {cliente.nombre}"

                self.pedidos_treeview.insert("", "end", values=(descripcion, total, fecha, cantidad_menus))



            
    def eliminar_pedido(self):
        """Eliminar el pedido seleccionado."""
        seleccionado = self.pedidos_treeview.selection()
        if not seleccionado:
            CTkMessagebox(title="Advertencia", message="Seleccione un pedido para eliminar.", icon="warning", option_1="OK")
            return

        # Obtener datos del pedido seleccionado
        pedido_valores = self.pedidos_treeview.item(seleccionado[0])['values']
        descripcion, total, fecha, cantidad_menus = pedido_valores

        # Confirmar eliminación
        confirmacion = CTkMessagebox(title="Confirmación", message=f"¿Está seguro de eliminar el pedido '{descripcion}'?", icon="question", option_1="Sí", option_2="No")
        if confirmacion.get() != "Sí":
            return

        # Eliminar de la base de datos
        with get_db() as db:
            pedido = db.query(Pedido).filter(Pedido.fecha_creacion == datetime.strptime(fecha, "%d/%m/%Y %H:%M:%S")).first()
            if pedido:
                db.delete(pedido)
                db.commit()
                CTkMessagebox(title="Éxito", message="Pedido eliminado correctamente.", icon="check", option_1="OK")

        # Actualizar la tabla
        self.mostrar_pedidos_cliente()
    
    # En tu archivo cliente_crud.py
    def obtener_clientes(self):
        """Devuelve un diccionario de IDs a nombres de clientes."""
        with get_db() as db:
            clientes = db.query(Cliente).all()
            return {cliente.id: cliente.nombre for cliente in clientes}




    def editar_pedido(self):
        """Editar un pedido seleccionado."""
        seleccionado = self.pedidos_treeview.selection()
        if not seleccionado:
            CTkMessagebox(title="Advertencia", message="Seleccione un pedido para editar.", icon="warning", option_1="OK")
            return

        # Implementar formulario de edición para actualizar datos
        CTkMessagebox(title="En desarrollo", message="Función de editar pedidos aún no implementada.", icon="info", option_1="OK")


    def filtrar_pedidos(self):
        """Filtrar pedidos por cliente o fecha."""
        cliente = self.filtro_cliente_combobox.get()
        fecha = self.filtro_fecha_entry.get()

        # Lógica para filtrar pedidos (adaptar según los datos reales)
        # Por ahora, solo imprime el filtro seleccionado
        print(f"Filtrando por cliente: {cliente}, fecha: {fecha}")

    def ver_detalles_pedido(self):
        """Ver los detalles de un pedido seleccionado."""
        selected_item = self.pedidos_treeview.selection()
        if selected_item:
            pedido = self.pedidos_treeview.item(selected_item)['values']
            CTkMessagebox(title="Detalles del Pedido", message=f"Detalles del pedido: {pedido}", icon="info", option_1="OK")
        else:
            CTkMessagebox(title="Advertencia", message="Seleccione un pedido para ver los detalles", icon="warning", option_1="OK")
            
            
# ================================================================
#                      GRAFICOS
# ================================================================

    def create_graficos_tab(self):
        """Crear el contenido de la pestaña Gráficos."""
        tab = self.tabview.tab("Gráficos")

        # Selección del tipo de gráfico
        grafico_label = ctk.CTkLabel(tab, text="Seleccionar Tipo de Gráfico:")
        grafico_label.pack(pady=10)

        self.tipo_grafico_combobox = ttk.Combobox(tab, values=["Ventas por Fecha", "Menús Más Vendidos", "Ingredientes Más Usados"])
        self.tipo_grafico_combobox.pack(pady=5)

        # Botón para generar gráfico
        generar_button = ctk.CTkButton(tab, text="Generar Gráfico", command=self.generar_grafico)
        generar_button.pack(pady=10)

        # Frame para mostrar el gráfico
        self.grafico_frame = ctk.CTkFrame(tab)
        self.grafico_frame.pack(pady=10, padx=10, expand=True, fill="both")

    def generar_grafico(self):
        """Generar y mostrar el gráfico seleccionado."""
        tipo_grafico = self.tipo_grafico_combobox.get()

        if not tipo_grafico:
            CTkMessagebox(title="Error", message="Seleccione un tipo de gráfico", icon="warning", option_1="OK")
            return

        # Limpiar el frame del gráfico
        for widget in self.grafico_frame.winfo_children():
            widget.destroy()

        # Conectar a la base de datos para obtener los datos necesarios
        with get_db() as db:
            if tipo_grafico == "Ventas por Fecha":
                ventas_por_fecha(db, intervalo="diarias")  # Cambiar el intervalo según sea necesario
            elif tipo_grafico == "Menús Más Vendidos":
                menus_mas_vendidos(db)
            elif tipo_grafico == "Ingredientes Más Usados":
                ingredientes_mas_usados(db)




if __name__ == "__main__":
    app = RestauranteApp()
    app.mainloop()
