"""
Módulo de Vistas para el Sistema SAMER
Maneja todas las interfaces visuales del dashboard y las tablas
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import datetime
import db_manager


# ============================================================================
# VENTANA DE EDICIÓN DE REGISTROS
# ============================================================================

class EditRecordWindow(ctk.CTkToplevel):
    """Ventana emergente para editar o eliminar registros"""
    
    def __init__(self, parent, table_name, record_data, column_names, on_success):
        super().__init__(parent)
        
        self.table_name = table_name
        self.record_data = record_data
        self.column_names = column_names
        self.on_success = on_success
        
        try:
            self.pk_name = db_manager.obtener_pk(table_name)
            self.pk_value = record_data[0]
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener la llave primaria: {e}")
            self.destroy()
            return
        
        self.entries = {}
        self.setup_window()
        self.create_ui()
    
    def setup_window(self):
        """Configurar propiedades de la ventana"""
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
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"500x600+{x}+{y}")
        
        self.transient(self.master)
        self.grab_set()
        self.configure(fg_color="#F5F7F9")
    
    def create_ui(self):
        """Crear la interfaz de usuario"""
        main_frame = ctk.CTkFrame(self, fg_color="#F5F7F9")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Editar Registro",
            font=("Arial", 24, "bold"),
            text_color="#1A1A1A"
        )
        title_label.pack(pady=(10, 20))
        
        form_container = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#E0E0E0"
        )
        form_container.pack(fill="both", expand=True, pady=(0, 15))
        
        for i, (col_name, value) in enumerate(zip(self.column_names, self.record_data)):
            field_frame = ctk.CTkFrame(form_container, fg_color="transparent")
            field_frame.pack(fill="x", padx=20, pady=10)
            
            label = ctk.CTkLabel(
                field_frame,
                text=col_name,
                font=("Arial", 12, "bold"),
                text_color="#333333",
                anchor="w"
            )
            label.pack(fill="x", pady=(0, 5))
            
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
            
            if col_name == self.pk_name:
                entry.configure(state="disabled", fg_color="#F0F0F0")
            
            self.entries[col_name] = entry
        
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
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
            datos_actualizados = {}
            
            for col_name, entry in self.entries.items():
                if col_name == self.pk_name:
                    continue
                
                valor = entry.get().strip()
                if valor == "":
                    valor = None
                
                datos_actualizados[col_name] = valor
            
            if not datos_actualizados:
                messagebox.showwarning(
                    "Advertencia",
                    "No hay cambios para guardar"
                )
                return
            
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
                self.destroy()
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
        result = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar este registro?\n\n"
            f"Esta acción no se puede deshacer.",
            icon="warning"
        )
        
        if not result:
            return
        
        try:
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
                self.destroy()
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



# ============================================================================
# VENTANA DE AGREGAR REGISTROS
# ============================================================================

class AddRecordWindow(ctk.CTkToplevel):
    """Ventana emergente para agregar nuevos registros dinámicamente"""
    
    def __init__(self, parent, table_name, on_success):
        super().__init__(parent)
        
        self.table_name = table_name
        self.on_success = on_success
        self.entries = {}
        self.maquinas_map = {} # Mapa para guardar info de máquinas (Recaudacion)
        
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
        
        self.setup_window()
        self.create_ui()
    
    def setup_window(self):
        """Configurar propiedades de la ventana"""
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
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"500x600+{x}+{y}")
        
        self.transient(self.master)
        self.grab_set()
        self.configure(fg_color="#F5F7F9")
    
    def create_ui(self):
        """Crear la interfaz de usuario"""
        main_frame = ctk.CTkFrame(self, fg_color="#F5F7F9")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Agregar Nuevo Registro",
            font=("Arial", 24, "bold"),
            text_color="#1A1A1A"
        )
        title_label.pack(pady=(10, 20))
        
        form_container = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#E0E0E0"
        )
        form_container.pack(fill="both", expand=True, pady=(0, 15))
        
        for col_name in self.columnas:
            # 3. En Maquinas, quitar idMaquina (se asume auto_increment)
            if self.table_name == "Maquinas" and col_name == "idMaquina":
                continue

            field_frame = ctk.CTkFrame(form_container, fg_color="transparent")
            field_frame.pack(fill="x", padx=20, pady=10)
            
            label = ctk.CTkLabel(
                field_frame,
                text=col_name,
                font=("Arial", 12, "bold"),
                text_color="#333333",
                anchor="w"
            )
            label.pack(fill="x", pady=(0, 5))
            
            # 1. Cambiar textboxs de fechas por calendarios
            if 'fecha' in col_name.lower():
                entry = DateEntry(
                    field_frame,
                    width=12,
                    background='#1f538d',
                    foreground='white',
                    borderwidth=2,
                    font=("Arial", 12),
                    date_pattern='yyyy-mm-dd',
                    locale='es_ES'
                )
                entry.pack(fill="x")
                self.entries[col_name] = entry
            
            # 4. En Recaudacion, Maquina_idMaquina es Combobox y Ubicacion es auto
            elif self.table_name == "Recaudacion" and col_name == "Maquina_idMaquina":
                try:
                    maquinas = db_manager.obtener_maquinas_con_ubicacion()
                    maquina_options = []
                    for m in maquinas:
                        # m = (id, nombre, ubicacion_id)
                        display_text = f"{m[1]} (ID: {m[0]})"
                        maquina_options.append(display_text)
                        self.maquinas_map[display_text] = {"id": m[0], "ubicacion": m[2]}
                    
                    entry = ctk.CTkComboBox(
                        field_frame,
                        values=maquina_options,
                        height=40,
                        font=("Arial", 12),
                        command=self.update_location
                    )
                    entry.pack(fill="x")
                    self.entries[col_name] = entry
                except Exception as e:
                    messagebox.showerror("Error", f"Error al cargar máquinas: {e}")
                    # Fallback a entry normal si falla
                    entry = ctk.CTkEntry(field_frame)
                    entry.pack(fill="x")
                    self.entries[col_name] = entry

            elif self.table_name == "Recaudacion" and col_name == "Ubicacion_idUbicacion":
                entry = ctk.CTkEntry(
                    field_frame,
                    height=40,
                    font=("Arial", 12),
                    corner_radius=8,
                    border_width=2,
                    border_color="#E0E0E0",
                    state="disabled" # Solo lectura
                )
                entry.pack(fill="x")
                self.entries[col_name] = entry
                
            else:
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
                self.entries[col_name] = entry
        
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
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
    
    def update_location(self, selection):
        """Actualizar el campo de ubicación basado en la máquina seleccionada"""
        if selection in self.maquinas_map and "Ubicacion_idUbicacion" in self.entries:
            ubicacion_id = self.maquinas_map[selection]["ubicacion"]
            entry = self.entries["Ubicacion_idUbicacion"]
            
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, str(ubicacion_id))
            entry.configure(state="disabled")

    def save_record(self):
        """Guardar el nuevo registro en la base de datos"""
        try:
            datos = {}
            campos_vacios = []
            
            for col_name, entry in self.entries.items():
                # Manejar DateEntry
                if hasattr(entry, 'get_date'):
                    valor = entry.get_date().strftime('%Y-%m-%d')
                # Manejar ComboBox (Recaudacion -> Maquina)
                elif isinstance(entry, ctk.CTkComboBox):
                    selection = entry.get()
                    if selection in self.maquinas_map:
                        valor = str(self.maquinas_map[selection]["id"])
                    else:
                        valor = ""
                # Manejar Entry normal
                else:
                    valor = entry.get().strip()
                
                if valor == "":
                    campos_vacios.append(col_name)
                else:
                    datos[col_name] = valor
            
            if campos_vacios:
                messagebox.showwarning(
                    "Campos Vacíos",
                    f"Por favor complete los siguientes campos:\n\n" + 
                    "\n".join(f"• {campo}" for campo in campos_vacios)
                )
                return
            
            nuevo_id = db_manager.insertar_registro(self.table_name, datos)
            
            messagebox.showinfo(
                "Éxito",
                f"Registro agregado correctamente\nID: {nuevo_id}"
            )
            
            self.destroy()
            
            if self.on_success:
                self.on_success()
        
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al guardar el registro:\n{str(e)}"
            )

# ============================================================================
# VENTANA DE FILTRADO DE REGISTROS
# ============================================================================

class FilterWindow(ctk.CTkToplevel):
    """Ventana emergente para filtrar registros de una tabla"""
    
    def __init__(self, parent, table_name, column_names, on_filter_apply):
        super().__init__(parent)
        
        self.table_name = table_name
        self.column_names = column_names
        self.on_filter_apply = on_filter_apply
        self.filter_widgets = {}
        
        self.setup_window()
        self.create_ui()
    
    def setup_window(self):
        """Configurar propiedades de la ventana"""
        display_names = {
            "Maquinas": "Máquinas",
            "Ubicacion": "Ubicación",
            "Mantenimiento": "Mantenimiento",
            "Recaudacion": "Recaudación",
            "Stock": "Stock"
        }
        display_name = display_names.get(self.table_name, self.table_name)
        
        self.title(f"Filtrar {display_name}")
        self.geometry("500x600")
        self.resizable(False, False)
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"500x600+{x}+{y}")
        
        self.transient(self.master)
        self.grab_set()
        self.configure(fg_color="#F5F7F9")
    
    def create_ui(self):
        """Crear la interfaz de usuario"""
        main_frame = ctk.CTkFrame(self, fg_color="#F5F7F9")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="Filtrar Registros",
            font=("Arial", 24, "bold"),
            text_color="#1A1A1A"
        )
        title_label.pack(pady=(10, 10))
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Complete los campos por los que desea filtrar\n(Deje vacío para ignorar)",
            font=("Arial", 11),
            text_color="#666666"
        )
        subtitle_label.pack(pady=(0, 15))
        
        form_container = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#E0E0E0"
        )
        form_container.pack(fill="both", expand=True, pady=(0, 15))
        
        for col_name in self.column_names:
            field_frame = ctk.CTkFrame(form_container, fg_color="transparent")
            field_frame.pack(fill="x", padx=20, pady=10)
            
            label = ctk.CTkLabel(
                field_frame,
                text=col_name,
                font=("Arial", 12, "bold"),
                text_color="#333333",
                anchor="w"
            )
            label.pack(fill="x", pady=(0, 5))
            
            es_fecha = 'fecha' in col_name.lower()
            
            if es_fecha:
                # 2. Check para validar si queremos filtrar por fecha o no
                check_var = ctk.BooleanVar(value=False)
                check = ctk.CTkCheckBox(
                    field_frame,
                    text="Filtrar por esta fecha",
                    variable=check_var,
                    font=("Arial", 11)
                )
                check.pack(fill="x", pady=(0, 5))
                self.filter_widgets[f"check_{col_name}"] = check_var

                date_widget = DateEntry(
                    field_frame,
                    width=45,
                    background='#1f538d',
                    foreground='white',
                    borderwidth=2,
                    font=("Arial", 11),
                    date_pattern='yyyy-mm-dd',
                    locale='es_ES'
                )
                date_widget.pack(fill="x", pady=(0, 5))
                
                hint_label = ctk.CTkLabel(
                    field_frame,
                    text="📅 Buscará desde esta fecha en adelante",
                    font=("Arial", 9),
                    text_color="#999999",
                    anchor="w"
                )
                hint_label.pack(fill="x")
                
                self.filter_widgets[col_name] = date_widget
            else:
                entry = ctk.CTkEntry(
                    field_frame,
                    height=40,
                    font=("Arial", 12),
                    corner_radius=8,
                    border_width=2,
                    border_color="#E0E0E0",
                    placeholder_text=f"Buscar por {col_name.lower()}"
                )
                entry.pack(fill="x")
                self.filter_widgets[col_name] = entry
        
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        btn_clear = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Limpiar Filtros",
            width=145,
            height=45,
            corner_radius=10,
            fg_color="#6B6B6B",
            hover_color="#555555",
            font=("Arial", 14, "bold"),
            command=self.clear_filters
        )
        btn_clear.pack(side="left", padx=5)
        
        btn_cancel = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            width=145,
            height=45,
            corner_radius=10,
            fg_color="#999999",
            hover_color="#777777",
            font=("Arial", 14, "bold"),
            command=self.destroy
        )
        btn_cancel.pack(side="left", padx=5)
        
        btn_apply = ctk.CTkButton(
            buttons_frame,
            text="🔍 Aplicar Filtros",
            width=145,
            height=45,
            corner_radius=10,
            fg_color="#1f538d",
            hover_color="#164270",
            font=("Arial", 14, "bold"),
            command=self.apply_filters
        )
        btn_apply.pack(side="right", padx=5)
    
    def get_filter_values(self):
        """Obtener los valores de los filtros"""
        filtros = {}
        
        for col_name, widget in self.filter_widgets.items():
            if col_name.startswith("check_"):
                continue
                
            if hasattr(widget, 'get_date'):
                # Verificar si el check está activo
                if f"check_{col_name}" in self.filter_widgets:
                    if not self.filter_widgets[f"check_{col_name}"].get():
                        continue

                fecha = widget.get_date()
                filtros[col_name] = fecha.strftime('%Y-%m-%d')
            else:
                valor = widget.get().strip()
                if valor:
                    filtros[col_name] = valor
        
        return filtros
    
    def clear_filters(self):
        """Limpiar todos los campos de filtro"""
        for widget in self.filter_widgets.values():
            if hasattr(widget, 'set_date'):
                widget.set_date(datetime.date.today())
            elif isinstance(widget, ctk.BooleanVar):
                widget.set(False)
            else:
                widget.delete(0, 'end')
        
        messagebox.showinfo(
            "Filtros Limpiados",
            "Los campos de filtro han sido restablecidos"
        )
    
    def apply_filters(self):
        """Aplicar los filtros y ejecutar el callback"""
        try:
            filtros = self.get_filter_values()
            
            if not filtros:
                messagebox.showwarning(
                    "Sin Filtros",
                    "Por favor ingrese al menos un criterio de búsqueda"
                )
                return
            
            self.destroy()
            
            if self.on_filter_apply:
                self.on_filter_apply(filtros)
        
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al aplicar filtros:\n{str(e)}"
            )


# ============================================================================
# VISTA DEL DASHBOARD
# ============================================================================

class DashboardView:
    """Clase para manejar la vista del Panel de Gestión con tarjetas"""
    
    def __init__(self, parent_container, on_card_click):
        self.container = parent_container
        self.on_card_click = on_card_click
        self.render()
    
    def render(self):
        """Renderizar la vista del dashboard con tarjetas"""
        content_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )
        content_frame.pack(expand=True, fill="both", padx=50, pady=30)
        
        title = ctk.CTkLabel(
            content_frame,
            text="Panel de Gestión",
            font=("Arial", 36, "bold"),
            text_color="#1A1A1A"
        )
        title.pack(pady=(20, 50))
        
        cards_frame = ctk.CTkFrame(
            content_frame,
            fg_color="transparent"
        )
        cards_frame.pack(expand=True)
        
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
        
        for i, config in enumerate(cards_config):
            self.create_card(cards_frame, config, row=0, col=i)
        
        self.create_footer(content_frame)
    
    def create_card(self, parent, config, row, col):
        """Crear una tarjeta interactiva"""
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
        
        card.bind("<Enter>", lambda e: card.configure(fg_color=config["hover_color"]))
        card.bind("<Leave>", lambda e: card.configure(fg_color=config["bg_color"]))
        card.bind("<Button-1>", lambda e: self.on_card_click(config["table"]))
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(expand=True)
        
        icon_label = ctk.CTkLabel(
            content,
            text=config["icon"],
            font=("Arial", 50),
            fg_color="transparent"
        )
        icon_label.pack(pady=(20, 15))
        icon_label.bind("<Button-1>", lambda e: self.on_card_click(config["table"]))
        
        title_label = ctk.CTkLabel(
            content,
            text=config["title"],
            font=("Arial", 16, "bold"),
            text_color=config["text_color"],
            fg_color="transparent"
        )
        title_label.pack(pady=(0, 8))
        title_label.bind("<Button-1>", lambda e: self.on_card_click(config["table"]))
        
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


# ============================================================================
# VISTA DE TABLA
# ============================================================================

class TableView:
    """Clase para manejar la vista de tabla con datos"""
    
    def __init__(self, parent_container, table_name, callbacks):
        self.container = parent_container
        self.table_name = table_name
        self.callbacks = callbacks
        self.tree = None
        self.info_label = None
        
        self.render()
        self.load_data()
    
    def render(self):
        """Renderizar la vista de tabla"""
        table_container = ctk.CTkFrame(
            self.container,
            fg_color="#F5F7F9"
        )
        table_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        table_card = ctk.CTkFrame(
            table_container,
            corner_radius=15,
            fg_color="white",
            border_width=1,
            border_color="#E0E0E0"
        )
        table_card.pack(fill="both", expand=True)
        
        self.create_table_header(table_card)
        
        self.table_frame = ctk.CTkFrame(
            table_card,
            fg_color="#FAFAFA",
            corner_radius=10
        )
        self.table_frame.pack(fill="both", expand=True, padx=25, pady=(10, 20))
        
        self.setup_table()
        self.create_table_footer(table_card)
    
    def create_table_header(self, parent):
        """Crear el encabezado de la vista de tabla"""
        header = ctk.CTkFrame(
            parent,
            fg_color="white",
            height=80
        )
        header.pack(fill="x", padx=25, pady=(20, 10))
        header.pack_propagate(False)
        
        display_names = {
            "Maquinas": "Máquinas",
            "Ubicacion": "Ubicación",
            "Mantenimiento": "Mantenimiento",
            "Recaudacion": "Recaudación",
            "Stock": "Stock"
        }
        
        display_name = display_names.get(self.table_name, self.table_name)
        
        title = ctk.CTkLabel(
            header,
            text=f"Gestión de {display_name}",
            font=("Arial", 24, "bold"),
            text_color="#1A1A1A"
        )
        title.pack(side="left", pady=15)
        
        buttons_frame = ctk.CTkFrame(header, fg_color="transparent")
        buttons_frame.pack(side="right", pady=15)
        
        btn_clear_filters = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Limpiar",
            width=100,
            height=40,
            corner_radius=10,
            fg_color="#999999",
            hover_color="#777777",
            text_color="white",
            font=("Arial", 13, "bold"),
            command=self.load_data
        )
        btn_clear_filters.pack(side="left", padx=5)
        
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
        
        tree_container = ctk.CTkFrame(self.table_frame, fg_color="white")
        tree_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")
        
        self.tree = ttk.Treeview(
            tree_container,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            style="Treeview"
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
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
            return
        
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            filas, nombres_columnas = db_manager.cargar_datos_tabla(self.table_name)
            
            self.tree["columns"] = nombres_columnas
            self.tree["show"] = "headings"
            
            for col in nombres_columnas:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150, anchor="center", minwidth=100)
            
            for row in filas:
                self.tree.insert("", "end", values=row)
            
            if self.info_label and self.info_label.winfo_exists():
                self.info_label.configure(text=f"Total de registros: {len(filas)}")
                
        except Exception as e:
            messagebox.showerror(
                "Error de Base de Datos", 
                f"Error al cargar datos: {str(e)}"
            )
    
    def update_table_data(self, filas, columnas):
        """Actualizar los datos del Treeview con nuevos datos"""
        if not self.tree:
            return
        
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.tree["columns"] = columnas
            self.tree["show"] = "headings"
            
            for col in columnas:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150, anchor="center", minwidth=100)
            
            for row in filas:
                self.tree.insert("", "end", values=row)
            
            if self.info_label and self.info_label.winfo_exists():
                self.info_label.configure(text=f"Total de registros: {len(filas)}")
                
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al actualizar datos: {str(e)}"
            )
    
    def get_selected_record(self):
        """Obtener el registro seleccionado en el Treeview"""
        if not self.tree:
            return None, None
        
        selection = self.tree.selection()
        
        if not selection:
            return None, None
        
        item = selection[0]
        record_data = self.tree.item(item, "values")
        column_names = list(self.tree["columns"])
        
        return record_data, column_names
    
    def destroy(self):
        """Limpiar la vista y sus referencias"""
        self.tree = None
        self.info_label = None
        
        for widget in self.container.winfo_children():
            widget.destroy()


# ============================================================================
# GESTOR DE VISTAS
# ============================================================================

class ViewManager:
    """Gestor de vistas que coordina la creación y destrucción de vistas"""
    
    def __init__(self, container):
        self.container = container
        self.current_view = None
        self.current_view_type = None
    
    def show_dashboard(self, on_card_click):
        """Mostrar la vista del dashboard"""
        self.clear_current_view()
        try:
            self.current_view = DashboardView(self.container, on_card_click)
            self.current_view_type = "dashboard"
        except Exception as e:
            pass
    
    def show_table(self, table_name, callbacks):
        """Mostrar la vista de tabla"""
        self.clear_current_view()
        try:
            self.current_view = TableView(self.container, table_name, callbacks)
            self.current_view_type = "table"
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la tabla: {str(e)}")
    
    def clear_current_view(self):
        """Limpiar la vista actual"""
        try:
            if self.current_view and hasattr(self.current_view, 'destroy'):
                self.current_view.destroy()
            self.current_view = None
            
            for widget in self.container.winfo_children():
                widget.destroy()
        except Exception as e:
            pass
    
    def get_current_view_type(self):
        """Obtener el tipo de vista actual"""
        return self.current_view_type