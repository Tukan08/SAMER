"""
Módulo de Vistas para el Sistema SAMER
Maneja todas las interfaces visuales del dashboard y las tablas
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import db_manager


class EditRecordWindow(ctk.CTkToplevel):
    """
    Ventana emergente para editar o eliminar registros
    """
    
    def __init__(self, parent, table_name, record_data, column_names, on_success):
        """
        Args:
            parent: Ventana padre
            table_name: Nombre de la tabla
            record_data: Tupla con los datos del registro seleccionado
            column_names: Lista con los nombres de las columnas
            on_success: Callback a ejecutar cuando se guarde o elimine exitosamente
        """
        super().__init__(parent)
        
        self.table_name = table_name
        self.record_data = record_data
        self.column_names = column_names
        self.on_success = on_success
        
        # Obtener la PK de la tabla
        try:
            self.pk_name = db_manager.obtener_pk(table_name)
            self.pk_value = record_data[0]  # Asumimos que la PK es la primera columna
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener la llave primaria: {e}")
            self.destroy()
            return
        
        # Diccionario para almacenar los entries
        self.entries = {}
        
        # Configurar ventana
        self.setup_window()
        
        # Crear interfaz
        self.create_ui()
    
    def setup_window(self):
        """Configurar propiedades de la ventana"""
        # Mapeo de nombres para display
        display_names = {
            "Maquinas": "Máquinas",
            "Ubicacion": "Ubicación",
            "Mantenimiento": "Mantenimiento",
            "Recaudacion": "Recaudación",
            "Stock": "Stock"
        }
        display_name = display_names.get(self.table_name, self.table_name)
        
        self.title(f"Editar {display_name}")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"500x600+{x}+{y}")
        
        # Hacer que la ventana sea modal
        self.transient(self.master)
        self.grab_set()
        
        # Configurar color de fondo
        self.configure(fg_color="#F5F7F9")
    
    def create_ui(self):
        """Crear la interfaz de usuario"""
        # Frame principal con scroll
        main_frame = ctk.CTkFrame(self, fg_color="#F5F7F9")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Editar Registro",
            font=("Arial", 24, "bold"),
            text_color="#1A1A1A"
        )
        title_label.pack(pady=(10, 20))
        
        # Frame para el formulario con scroll
        form_container = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#E0E0E0"
        )
        form_container.pack(fill="both", expand=True, pady=(0, 15))
        
        # Crear campos dinámicamente
        for i, (col_name, value) in enumerate(zip(self.column_names, self.record_data)):
            # Frame para cada campo
            field_frame = ctk.CTkFrame(form_container, fg_color="transparent")
            field_frame.pack(fill="x", padx=20, pady=10)
            
            # Label del campo
            label = ctk.CTkLabel(
                field_frame,
                text=col_name,
                font=("Arial", 12, "bold"),
                text_color="#333333",
                anchor="w"
            )
            label.pack(fill="x", pady=(0, 5))
            
            # Entry del campo
            entry = ctk.CTkEntry(
                field_frame,
                height=40,
                font=("Arial", 12),
                corner_radius=8,
                border_width=2,
                border_color="#E0E0E0"
            )
            entry.pack(fill="x")
            entry.insert(0, str(value) if value is not None else "")
            
            # Deshabilitar el campo de la PK (no editable)
            if col_name == self.pk_name:
                entry.configure(state="disabled", fg_color="#F0F0F0")
            
            # Guardar referencia al entry
            self.entries[col_name] = entry
        
        # Frame para botones de acción
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Botón Cancelar
        btn_cancel = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            width=140,
            height=45,
            corner_radius=10,
            fg_color="#6B6B6B",
            hover_color="#555555",
            font=("Arial", 14, "bold"),
            command=self.destroy
        )
        btn_cancel.pack(side="left", padx=5)
        
        # Botón Eliminar
        btn_delete = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Eliminar",
            width=140,
            height=45,
            corner_radius=10,
            fg_color="#D9534F",
            hover_color="#C9302C",
            font=("Arial", 14, "bold"),
            command=self.delete_record
        )
        btn_delete.pack(side="left", padx=5)
        
        # Botón Guardar
        btn_save = ctk.CTkButton(
            buttons_frame,
            text="💾 Guardar",
            width=140,
            height=45,
            corner_radius=10,
            fg_color="#1f538d",
            hover_color="#164270",
            font=("Arial", 14, "bold"),
            command=self.save_changes
        )
        btn_save.pack(side="right", padx=5)
    
    def save_changes(self):
        """Guardar los cambios en la base de datos"""
        try:
            # Recopilar los datos actualizados (excluyendo la PK)
            datos_actualizados = {}
            
            for col_name, entry in self.entries.items():
                # Saltar la PK
                if col_name == self.pk_name:
                    continue
                
                # Obtener el valor del entry
                valor = entry.get().strip()
                
                # Convertir vacío a None
                if valor == "":
                    valor = None
                
                datos_actualizados[col_name] = valor
            
            # Validar que hay algo que actualizar
            if not datos_actualizados:
                messagebox.showwarning(
                    "Advertencia",
                    "No hay cambios para guardar"
                )
                return
            
            # Actualizar en la base de datos
            filas_afectadas = db_manager.actualizar_registro_completo(
                self.table_name,
                self.pk_name,
                self.pk_value,
                datos_actualizados
            )
            
            if filas_afectadas > 0:
                messagebox.showinfo(
                    "Éxito",
                    "Registro actualizado correctamente"
                )
                
                # Cerrar ventana
                self.destroy()
                
                # Ejecutar callback de éxito
                if self.on_success:
                    self.on_success()
            else:
                messagebox.showwarning(
                    "Advertencia",
                    "No se encontró el registro o no hubo cambios"
                )
        
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al guardar cambios: {str(e)}"
            )
    
    def delete_record(self):
        """Eliminar el registro de la base de datos"""
        # Confirmación
        result = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar este registro?\n\n"
            f"Esta acción no se puede deshacer.",
            icon="warning"
        )
        
        if not result:
            return
        
        try:
            # Eliminar en la base de datos
            filas_eliminadas = db_manager.eliminar_registro(
                self.table_name,
                self.pk_name,
                self.pk_value
            )
            
            if filas_eliminadas > 0:
                messagebox.showinfo(
                    "Éxito",
                    "Registro eliminado correctamente"
                )
                
                # Cerrar ventana
                self.destroy()
                
                # Ejecutar callback de éxito
                if self.on_success:
                    self.on_success()
            else:
                messagebox.showwarning(
                    "Advertencia",
                    "No se encontró el registro para eliminar"
                )
        
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al eliminar registro: {str(e)}"
            )


class DashboardView:
    """
    Clase para manejar la vista del Panel de Gestión con tarjetas
    """
    
    def __init__(self, parent_container, on_card_click):
        """
        Args:
            parent_container: Frame contenedor donde se renderizará la vista
            on_card_click: Callback para manejar el clic en las tarjetas
        """
        self.container = parent_container
        self.on_card_click = on_card_click
        self.render()
    
    def render(self):
        """Renderizar la vista del dashboard con tarjetas"""
        # Frame para centrar contenido
        content_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )
        content_frame.pack(expand=True, fill="both", padx=50, pady=30)
        
        # Título del panel
        title = ctk.CTkLabel(
            content_frame,
            text="Panel de Gestión",
            font=("Arial", 36, "bold"),
            text_color="#1A1A1A"
        )
        title.pack(pady=(20, 50))
        
        # Frame para las tarjetas
        cards_frame = ctk.CTkFrame(
            content_frame,
            fg_color="transparent"
        )
        cards_frame.pack(expand=True)
        
        # Configuración de las tarjetas
        cards_config = [
            {
                "title": "MÁQUINAS",
                "subtitle": "Gestionar\nmáquinas",
                "icon": "🤖",
                "bg_color": "#E3F2FD",
                "text_color": "#1565C0",
                "hover_color": "#BBDEFB",
                "table": "Maquinas"
            },
            {
                "title": "UBICACIÓN",
                "subtitle": "Ver ubicaciones",
                "icon": "📍",
                "bg_color": "#E0F2F1",
                "text_color": "#00695C",
                "hover_color": "#B2DFDB",
                "table": "Ubicacion"
            },
            {
                "title": "MANTENIMIENTO",
                "subtitle": "Registrar servicios",
                "icon": "🔧",
                "bg_color": "#FFF3E0",
                "text_color": "#E65100",
                "hover_color": "#FFE0B2",
                "table": "Mantenimiento"
            },
            {
                "title": "RECAUDACIÓN",
                "subtitle": "Consultar\ningresos",
                "icon": "💲",
                "bg_color": "#F3E5F5",
                "text_color": "#6A1B9A",
                "hover_color": "#E1BEE7",
                "table": "Recaudacion"
            },
            {
                "title": "STOCK",
                "subtitle": "Controlar\ninventario",
                "icon": "📦",
                "bg_color": "#F5F5F5",
                "text_color": "#424242",
                "hover_color": "#EEEEEE",
                "table": "Stock"
            }
        ]
        
        # Crear las tarjetas
        for i, config in enumerate(cards_config):
            self.create_card(cards_frame, config, row=0, col=i)
        
        # Footer
        self.create_footer(content_frame)
    
    def create_card(self, parent, config, row, col):
        """Crear una tarjeta interactiva"""
        # Frame principal de la tarjeta
        card = ctk.CTkFrame(
            parent,
            width=220,
            height=240,
            corner_radius=20,
            fg_color=config["bg_color"],
            border_width=0
        )
        card.grid(row=row, column=col, padx=15, pady=20)
        card.grid_propagate(False)
        
        # Hacer la tarjeta clickeable
        card.bind("<Enter>", lambda e: card.configure(fg_color=config["hover_color"]))
        card.bind("<Leave>", lambda e: card.configure(fg_color=config["bg_color"]))
        card.bind("<Button-1>", lambda e: self.on_card_click(config["table"]))
        
        # Frame interno para contenido
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(expand=True)
        
        # Icono
        icon_label = ctk.CTkLabel(
            content,
            text=config["icon"],
            font=("Arial", 50),
            fg_color="transparent"
        )
        icon_label.pack(pady=(20, 15))
        icon_label.bind("<Button-1>", lambda e: self.on_card_click(config["table"]))
        
        # Título
        title_label = ctk.CTkLabel(
            content,
            text=config["title"],
            font=("Arial", 16, "bold"),
            text_color=config["text_color"],
            fg_color="transparent"
        )
        title_label.pack(pady=(0, 8))
        title_label.bind("<Button-1>", lambda e: self.on_card_click(config["table"]))
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(
            content,
            text=config["subtitle"],
            font=("Arial", 12),
            text_color=config["text_color"],
            fg_color="transparent",
            justify="center"
        )
        subtitle_label.pack()
        subtitle_label.bind("<Button-1>", lambda e: self.on_card_click(config["table"]))
    
    def create_footer(self, parent):
        """Crear el pie de página"""
        footer = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            height=60
        )
        footer.pack(side="bottom", fill="x", pady=(30, 10))
        
        # Links del footer
        links = ["Soporte", "Politicas de privacidad", "Terminos y condiciones"]
        links_frame = ctk.CTkFrame(footer, fg_color="transparent")
        links_frame.pack()
        
        for i, link in enumerate(links):
            if i > 0:
                separator = ctk.CTkLabel(
                    links_frame,
                    text="•",
                    font=("Arial", 12),
                    text_color="#999999"
                )
                separator.pack(side="left", padx=15)
            
            link_label = ctk.CTkLabel(
                links_frame,
                text=link,
                font=("Arial", 12),
                text_color="#666666",
                cursor="hand2"
            )
            link_label.pack(side="left")
        
        # Copyright
        copyright_label = ctk.CTkLabel(
            footer,
            text="© 2025 Proyecto SAMER. Todos los derechos reservados.",
            font=("Arial", 11),
            text_color="#999999"
        )
        copyright_label.pack(pady=(10, 0))
    
    def destroy(self):
        """Limpiar la vista"""
        for widget in self.container.winfo_children():
            widget.destroy()


class TableView:
    """
    Clase para manejar la vista de tabla con datos
    """
    
    def __init__(self, parent_container, table_name, callbacks):
        """
        Args:
            parent_container: Frame contenedor donde se renderizará la vista
            table_name: Nombre de la tabla a mostrar
            callbacks: Dict con callbacks para las acciones (add_item, filter, download)
        """
        print(f"\n=== Inicializando TableView ===")
        print(f"Tabla: {table_name}")
        print(f"Callbacks: {list(callbacks.keys())}")
        
        self.container = parent_container
        self.table_name = table_name
        self.callbacks = callbacks
        
        # Referencias locales a widgets que se actualizarán
        self.tree = None
        self.info_label = None
        
        try:
            print("Llamando a render()...")
            self.render()
            print("render() completado")
            
            print("Llamando a load_data()...")
            self.load_data()
            print("load_data() completado")
            
            print("=== TableView inicializado exitosamente ===\n")
        except Exception as e:
            print(f"ERROR en __init__ de TableView: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def render(self):
        """Renderizar la vista de tabla"""
        print("  -> Creando table_container...")
        # Frame principal de la tabla
        table_container = ctk.CTkFrame(
            self.container,
            fg_color="#F5F7F9"
        )
        table_container.pack(fill="both", expand=True, padx=30, pady=20)
        print("  -> table_container creado y packed")
        
        print("  -> Creando table_card...")
        # Tarjeta blanca para la tabla
        table_card = ctk.CTkFrame(
            table_container,
            corner_radius=15,
            fg_color="white",
            border_width=1,
            border_color="#E0E0E0"
        )
        table_card.pack(fill="both", expand=True)
        print("  -> table_card creado y packed")
        
        print("  -> Creando header...")
        # Header de la tarjeta
        self.create_table_header(table_card)
        print("  -> header creado")
        
        print("  -> Creando table_frame...")
        # Área para la tabla
        self.table_frame = ctk.CTkFrame(
            table_card,
            fg_color="#FAFAFA",
            corner_radius=10
        )
        self.table_frame.pack(fill="both", expand=True, padx=25, pady=(10, 20))
        print("  -> table_frame creado y packed")
        
        print("  -> Llamando a setup_table()...")
        # Configurar la tabla
        self.setup_table()
        print("  -> setup_table() completado")
        
        print("  -> Creando footer...")
        # Footer de la tarjeta
        self.create_table_footer(table_card)
        print("  -> footer creado")
        print("  -> render() completado exitosamente")
    
    def create_table_header(self, parent):
        """Crear el encabezado de la vista de tabla"""
        header = ctk.CTkFrame(
            parent,
            fg_color="white",
            height=80
        )
        header.pack(fill="x", padx=25, pady=(20, 10))
        header.pack_propagate(False)
        
        # Mapeo de nombres para display
        display_names = {
            "Maquinas": "Máquinas",
            "Ubicacion": "Ubicación",
            "Mantenimiento": "Mantenimiento",
            "Recaudacion": "Recaudación",
            "Stock": "Stock"
        }
        
        display_name = display_names.get(self.table_name, self.table_name)
        
        # Título
        title = ctk.CTkLabel(
            header,
            text=f"Gestión de {display_name}",
            font=("Arial", 24, "bold"),
            text_color="#1A1A1A"
        )
        title.pack(side="left", pady=15)
        
        # Frame para botones
        buttons_frame = ctk.CTkFrame(header, fg_color="transparent")
        buttons_frame.pack(side="right", pady=15)
        
        # Botón Filtrar
        btn_filter = ctk.CTkButton(
            buttons_frame,
            text="🔍 Filtrar",
            width=120,
            height=40,
            corner_radius=10,
            fg_color="#F0F0F0",
            hover_color="#E0E0E0",
            text_color="#1A1A1A",
            font=("Arial", 13, "bold"),
            command=self.callbacks.get('filter', lambda: None)
        )
        btn_filter.pack(side="left", padx=5)
        
        # Botón Editar (NUEVO)
        btn_edit = ctk.CTkButton(
            buttons_frame,
            text="✏️ Editar",
            width=120,
            height=40,
            corner_radius=10,
            fg_color="#5A9FD4",
            hover_color="#4A8FC4",
            text_color="white",
            font=("Arial", 13, "bold"),
            command=lambda: self.callbacks.get('edit_item', lambda: None)()
        )
        btn_edit.pack(side="left", padx=5)
        
        # Botón Agregar
        btn_add = ctk.CTkButton(
            buttons_frame,
            text=f"+ Agregar {display_name[:-1] if display_name.endswith('s') else display_name}",
            width=180,
            height=40,
            corner_radius=10,
            fg_color="#1f538d",
            hover_color="#164270",
            font=("Arial", 13, "bold"),
            text_color="white",
            command=lambda: self.callbacks.get('add_item', lambda x: None)(self.table_name)
        )
        btn_add.pack(side="left", padx=5)
    
    def setup_table(self):
        """Configurar el Treeview para mostrar datos"""
        # Crear estilo para el Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                       background="white",
                       foreground="#333333",
                       rowheight=35,
                       fieldbackground="white",
                       font=("Arial", 11),
                       borderwidth=0)
        style.configure("Treeview.Heading",
                       background="#1f538d",
                       foreground="white",
                       font=("Arial", 12, "bold"),
                       borderwidth=0,
                       relief="flat")
        style.map("Treeview",
                 background=[("selected", "#14b8a6")])
        style.map("Treeview.Heading",
                 background=[("active", "#164270")])
        
        # Frame para contener el Treeview y scrollbars
        tree_container = ctk.CTkFrame(self.table_frame, fg_color="white")
        tree_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")
        
        # Crear Treeview (guardar referencia local)
        self.tree = ttk.Treeview(
            tree_container,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            style="Treeview"
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Posicionar elementos
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
    
    def create_table_footer(self, parent):
        """Crear el pie de la tarjeta de tabla"""
        footer = ctk.CTkFrame(
            parent,
            fg_color="white",
            height=60
        )
        footer.pack(fill="x", padx=25, pady=(0, 20))
        footer.pack_propagate(False)
        
        # Botón Descargar Reporte
        btn_download = ctk.CTkButton(
            footer,
            text="📄 Descargar Reporte (.pdf)",
            width=220,
            height=40,
            corner_radius=10,
            fg_color="#1f538d",
            hover_color="#164270",
            font=("Arial", 13, "bold"),
            text_color="white",
            command=lambda: self.callbacks.get('download', lambda x: None)(self.table_name)
        )
        btn_download.pack(side="left", pady=10)
        
        # Label de información (guardar referencia local)
        self.info_label = ctk.CTkLabel(
            footer,
            text="",
            font=("Arial", 11),
            text_color="#666666"
        )
        self.info_label.pack(side="right", pady=10, padx=10)
    
    def load_data(self):
        """Cargar datos de la base de datos en el Treeview"""
        if not self.tree:
            print("Error: self.tree no está inicializado")
            return
        
        try:
            # Limpiar tabla actual
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Llamar a la función del módulo db_manager
            print(f"Cargando datos de la tabla: {self.table_name}")
            filas, nombres_columnas = db_manager.cargar_datos_tabla(self.table_name)
            print(f"Datos obtenidos: {len(filas)} filas, columnas: {nombres_columnas}")
            
            # Configurar columnas del Treeview
            self.tree["columns"] = nombres_columnas
            self.tree["show"] = "headings"
            
            # Configurar encabezados y anchos de columna
            for col in nombres_columnas:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150, anchor="center", minwidth=100)
            
            # Insertar datos en el Treeview
            for row in filas:
                self.tree.insert("", "end", values=row)
            
            # Actualizar información (usando referencia local)
            if self.info_label and self.info_label.winfo_exists():
                self.info_label.configure(text=f"Total de registros: {len(filas)}")
            
            print(f"Datos cargados exitosamente en el Treeview")
                
        except Exception as e:
            print(f"Error al cargar datos: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Error de Base de Datos", 
                f"Error al cargar datos: {str(e)}"
            )
    
    def get_selected_record(self):
        """
        Obtener el registro seleccionado en el Treeview
        
        Returns:
            tuple: (record_data, column_names) o (None, None) si no hay selección
        """
        if not self.tree:
            print("ERROR: self.tree no existe")
            return None, None
        
        # Obtener la selección
        selection = self.tree.selection()
        
        if not selection:
            print("No hay ninguna fila seleccionada")
            return None, None
        
        # Obtener los datos de la fila seleccionada
        item = selection[0]
        record_data = self.tree.item(item, "values")
        
        # Obtener los nombres de las columnas
        column_names = list(self.tree["columns"])
        
        print(f"Registro seleccionado: {record_data}")
        print(f"Columnas: {column_names}")
        
        return record_data, column_names
    
    def destroy(self):
        """Limpiar la vista y sus referencias"""
        # Limpiar referencias a widgets antes de destruir
        self.tree = None
        self.info_label = None
        
        # Destruir todos los widgets
        for widget in self.container.winfo_children():
            widget.destroy()


class ViewManager:
    """
    Gestor de vistas que coordina la creación y destrucción de vistas
    """
    
    def __init__(self, container):
        """
        Args:
            container: Frame contenedor principal donde se mostrarán las vistas
        """
        self.container = container
        self.current_view = None
        self.current_view_type = None
    
    def show_dashboard(self, on_card_click):
        """
        Mostrar la vista del dashboard
        
        Args:
            on_card_click: Callback para cuando se hace clic en una tarjeta
        """
        self.clear_current_view()
        try:
            self.current_view = DashboardView(self.container, on_card_click)
            self.current_view_type = "dashboard"
        except Exception as e:
            print(f"Error al mostrar dashboard: {e}")
            import traceback
            traceback.print_exc()
    
    def show_table(self, table_name, callbacks):
        """
        Mostrar la vista de tabla
        
        Args:
            table_name: Nombre de la tabla a mostrar
            callbacks: Dict con callbacks para las acciones
        """
        self.clear_current_view()
        try:
            self.current_view = TableView(self.container, table_name, callbacks)
            self.current_view_type = "table"
        except Exception as e:
            print(f"Error al mostrar tabla: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudo cargar la tabla: {str(e)}")
    
    def clear_current_view(self):
        """Limpiar la vista actual"""
        try:
            if self.current_view and hasattr(self.current_view, 'destroy'):
                self.current_view.destroy()
            self.current_view = None
            
            # Limpiar cualquier widget residual
            for widget in self.container.winfo_children():
                widget.destroy()
        except Exception as e:
            print(f"Error al limpiar vista: {e}")
    
    def get_current_view_type(self):
        """Obtener el tipo de vista actual"""
        return self.current_view_type
    
#---------------------------------
class AddRecordWindow(ctk.CTkToplevel):
    """
    Ventana emergente para agregar nuevos registros dinámicamente
    """
    
    def __init__(self, parent, table_name, on_success):
        """
        Args:
            parent: Ventana padre
            table_name: Nombre de la tabla
            on_success: Callback a ejecutar cuando se guarde exitosamente
        """
        super().__init__(parent)
        
        self.table_name = table_name
        self.on_success = on_success
        
        # Diccionario para almacenar los entries
        self.entries = {}
        
        # Obtener columnas dinámicamente (excluyendo IDs autoincrementales)
        try:
            self.columnas = db_manager.obtener_columnas_para_insert(table_name)
            if not self.columnas:
                messagebox.showerror("Error", "No se encontraron columnas para insertar")
                self.destroy()
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener estructura de tabla: {e}")
            self.destroy()
            return
        
        # Configurar ventana
        self.setup_window()
        
        # Crear interfaz
        self.create_ui()
    
    def setup_window(self):
        """Configurar propiedades de la ventana"""
        # Mapeo de nombres para display
        display_names = {
            "Maquinas": "Máquinas",
            "Ubicacion": "Ubicación",
            "Mantenimiento": "Mantenimiento",
            "Recaudacion": "Recaudación",
            "Stock": "Stock"
        }
        display_name = display_names.get(self.table_name, self.table_name)
        
        self.title(f"Agregar Nuevo en {display_name}")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"500x600+{x}+{y}")
        
        # Hacer que la ventana sea modal
        self.transient(self.master)
        self.grab_set()
        
        # Configurar color de fondo
        self.configure(fg_color="#F5F7F9")
    
    def create_ui(self):
        """Crear la interfaz de usuario"""
        # Frame principal con scroll
        main_frame = ctk.CTkFrame(self, fg_color="#F5F7F9")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        display_names = {
            "Maquinas": "Máquinas",
            "Ubicacion": "Ubicación",
            "Mantenimiento": "Mantenimiento",
            "Recaudacion": "Recaudación",
            "Stock": "Stock"
        }
        display_name = display_names.get(self.table_name, self.table_name)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Agregar Nuevo Registro",
            font=("Arial", 24, "bold"),
            text_color="#1A1A1A"
        )
        title_label.pack(pady=(10, 20))
        
        # Frame para el formulario con scroll
        form_container = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#E0E0E0"
        )
        form_container.pack(fill="both", expand=True, pady=(0, 15))
        
        # Crear campos dinámicamente basándose en las columnas
        for col_name in self.columnas:
            # Frame para cada campo
            field_frame = ctk.CTkFrame(form_container, fg_color="transparent")
            field_frame.pack(fill="x", padx=20, pady=10)
            
            # Label del campo
            label = ctk.CTkLabel(
                field_frame,
                text=col_name,
                font=("Arial", 12, "bold"),
                text_color="#333333",
                anchor="w"
            )
            label.pack(fill="x", pady=(0, 5))
            
            # Entry del campo
            entry = ctk.CTkEntry(
                field_frame,
                height=40,
                font=("Arial", 12),
                corner_radius=8,
                border_width=2,
                border_color="#E0E0E0",
                placeholder_text=f"Ingrese {col_name.lower()}"
            )
            entry.pack(fill="x")
            
            # Guardar referencia al entry
            self.entries[col_name] = entry
        
        # Frame para botones de acción
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Botón Cancelar
        btn_cancel = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            width=220,
            height=45,
            corner_radius=10,
            fg_color="#6B6B6B",
            hover_color="#555555",
            font=("Arial", 14, "bold"),
            command=self.destroy
        )
        btn_cancel.pack(side="left", padx=5)
        
        # Botón Guardar
        btn_save = ctk.CTkButton(
            buttons_frame,
            text="💾 Guardar",
            width=220,
            height=45,
            corner_radius=10,
            fg_color="#1f538d",
            hover_color="#164270",
            font=("Arial", 14, "bold"),
            command=self.save_record
        )
        btn_save.pack(side="right", padx=5)
    
    def save_record(self):
        """Guardar el nuevo registro en la base de datos"""
        try:
            # Recopilar los datos del formulario
            datos = {}
            campos_vacios = []
            
            for col_name, entry in self.entries.items():
                valor = entry.get().strip()
                
                # Validar que no esté vacío
                if valor == "":
                    campos_vacios.append(col_name)
                else:
                    datos[col_name] = valor
            
            # Validar que todos los campos tengan datos
            if campos_vacios:
                messagebox.showwarning(
                    "Campos Vacíos",
                    f"Por favor complete los siguientes campos:\n\n" + 
                    "\n".join(f"• {campo}" for campo in campos_vacios)
                )
                return
            
            # Insertar en la base de datos
            nuevo_id = db_manager.insertar_registro(self.table_name, datos)
            
            messagebox.showinfo(
                "Éxito",
                f"Registro agregado correctamente\nID: {nuevo_id}"
            )
            
            # Cerrar ventana
            self.destroy()
            
            # Ejecutar callback de éxito para recargar la tabla
            if self.on_success:
                self.on_success()
        
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al guardar el registro:\n{str(e)}"
            )