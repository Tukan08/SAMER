"""
SAMER - Sistema de Administración de Máquinas Expendedoras Recreativas
Archivo principal que maneja la ventana, navegación y coordinación general
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from views import ViewManager
import db_manager
import report_manager
import os

# Configuración del tema
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class DashboardSAMER:
    """
    Clase principal que gestiona la aplicación
    Responsable de: ventana principal, header, navegación y coordinación de vistas
    """
    
    def __init__(self):
        # Crear ventana principal
        self.window = ctk.CTk()
        self.window.title("Sistema Adminitrador de Maquinas Expendedoras Recreativas - SAMER")
        self.window.geometry("1400x800")
        self.window.configure(fg_color="#F5F7F9")
        
        # Centrar ventana
        self.center_window()
        
        # Crear componentes estructurales
        self.create_header()
        self.create_main_container()
        
        # Inicializar gestor de vistas
        self.view_manager = ViewManager(self.main_container)
        
        # Mostrar dashboard inicial
        self.show_dashboard()
        
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.window.update_idletasks()
        width = 1000
        height = 800
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_header(self):
        """Crear la barra superior moderna"""
        self.header = ctk.CTkFrame(
            self.window,
            height=70,
            corner_radius=0,
            fg_color="white",
            border_width=1,
            border_color="#E0E0E0"
        )
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        
        # Frame izquierdo para logo y título
        left_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        left_frame.pack(side="left", padx=30, pady=15)
        
        # Logo emoji
        logo_label = ctk.CTkLabel(
            left_frame,
            text="🎮",
            font=("Arial", 28)
        )
        logo_label.pack(side="left", padx=(0, 15))
        
        # Título
        title_label = ctk.CTkLabel(
            left_frame,
            text="Software 'SAMER'",
            font=("Arial", 20, "bold"),
            text_color="#1A1A1A"
        )
        title_label.pack(side="left")
        
        # Frame derecho para botones
        right_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        right_frame.pack(side="right", padx=30, pady=15)
        
        # Botón Home (inicialmente oculto)
        self.btn_home = ctk.CTkButton(
            right_frame,
            text="🏠 Inicio",
            width=100,
            height=40,
            corner_radius=10,
            fg_color="#1f538d",
            hover_color="#164270",
            font=("Arial", 14, "bold"),
            command=self.show_dashboard
        )
        # No lo empaquetamos aún
        
        # Botón de Reporte General
        btn_general_report = ctk.CTkButton(
            right_frame,
            text="📊",
            width=45,
            height=45,
            corner_radius=22,
            fg_color="#F0F0F0",
            hover_color="#E0E0E0",
            text_color="#1A1A1A",
            font=("Arial", 18),
            command=self.generate_general_report
        )
        btn_general_report.pack(side="left", padx=5)
        
# Botón de Gestión de Usuarios (MODIFICADO - antes era Configuración)
        btn_user_management = ctk.CTkButton(
            right_frame,
            text="👤",
            width=45,
            height=45,
            corner_radius=22,
            fg_color="#F0F0F0",
            hover_color="#E0E0E0",
            text_color="#1A1A1A",
            font=("Arial", 18),
            command=self.open_user_management
        )
        btn_user_management.pack(side="left", padx=5)
        
        # Botón de Cerrar Sesión (MODIFICADO - antes era Perfil)
        btn_logout = ctk.CTkButton(
            right_frame,
            text="⬅",
            width=45,
            height=45,
            corner_radius=22,
            fg_color="#F0F0F0",
            hover_color="#D9534F",
            text_color="#1A1A1A",
            font=("Arial", 18),
            command=self.logout
        )
        btn_logout.pack(side="left", padx=5)
    
    def create_main_container(self):
        """Crear el contenedor principal donde se mostrarán las vistas"""
        self.main_container = ctk.CTkFrame(
            self.window,
            fg_color="#F5F7F9"
        )
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)
    
    # ==================== NAVEGACIÓN ====================
    
    def show_dashboard(self):
        """Mostrar la vista del panel de gestión"""
        # Ocultar botón home
        self.btn_home.pack_forget()
        
        # Mostrar vista del dashboard usando el ViewManager
        self.view_manager.show_dashboard(on_card_click=self.show_table_view)
    
    def show_table_view(self, table_name):
        """
        Mostrar la vista de tabla para una sección específica
        
        Args:
            table_name: Nombre de la tabla a mostrar
        """
        print(f"\n=== show_table_view llamado ===")
        print(f"Tabla solicitada: {table_name}")
        
        # Mostrar botón home
        self.btn_home.pack(side="left", padx=5)
        print("Botón home mostrado")
        
        # Preparar callbacks para la vista de tabla
        callbacks = {
            'add_item': self.add_item,
            'edit_item': self.edit_item,
            'filter': self.filter_data,
            'download': self.download_pdf
        }
        print(f"Callbacks preparados: {list(callbacks.keys())}")
        
        # Mostrar vista de tabla usando el ViewManager
        print("Llamando a view_manager.show_table()...")
        try:
            self.view_manager.show_table(table_name, callbacks)
            print("view_manager.show_table() completado")
        except Exception as e:
            print(f"ERROR en show_table(): {e}")
            import traceback
            traceback.print_exc()
        
        print("=== show_table_view completado ===\n")
    
    # ==================== ACCIONES ====================
    
    def edit_item(self):
        """Función para editar un registro seleccionado"""
        # Verificar que hay una vista de tabla activa
        if self.view_manager.get_current_view_type() != "table":
            messagebox.showwarning(
                "Advertencia",
                "Esta función solo está disponible en la vista de tabla"
            )
            return
        
        # Obtener el registro seleccionado
        current_view = self.view_manager.current_view
        record_data, column_names = current_view.get_selected_record()
        
        # Validar que hay una selección
        if record_data is None or column_names is None:
            messagebox.showwarning(
                "Advertencia",
                "Por favor, seleccione un registro de la tabla para editar"
            )
            return
        
        # Importar la clase de ventana de edición
        from views import EditRecordWindow
        
        # Crear ventana de edición
        edit_window = EditRecordWindow(
            parent=self.window,
            table_name=current_view.table_name,
            record_data=record_data,
            column_names=column_names,
            on_success=lambda: current_view.load_data()  # Recargar datos al guardar
        )
    
    def add_item(self, table_name):
        """Función para agregar nuevo elemento"""
        # Verificar que hay una vista de tabla activa
        if self.view_manager.get_current_view_type() != "table":
            messagebox.showwarning(
                "Advertencia",
                "Esta función solo está disponible en la vista de tabla"
            )
            return
        
        # Importar la clase de ventana de agregar
        from views import AddRecordWindow
        
        # Obtener la vista actual para recargar después
        current_view = self.view_manager.current_view
        
        # Crear ventana de agregar registro
        add_window = AddRecordWindow(
            parent=self.window,
            table_name=table_name,
            on_success=lambda: current_view.load_data()  # Recargar datos al guardar
        )
    
    def filter_data(self):
        """Función para filtrar datos"""
        if self.view_manager.get_current_view_type() != "table":
            messagebox.showwarning(
                "Advertencia",
                "Esta función solo está disponible en la vista de tabla"
            )
            return
        
        from views import FilterWindow
        
        current_view = self.view_manager.current_view
        
        try:
            _, column_names = db_manager.cargar_datos_tabla(current_view.table_name)
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudieron obtener las columnas: {str(e)}"
            )
            return
        
        def on_filter_apply(filtros_dict):
            """Callback que se ejecuta cuando el usuario aplica filtros"""
            try:
                filas_filtradas, columnas = db_manager.filtrar_registros(
                    current_view.table_name,
                    filtros_dict
                )
                
                current_view.update_table_data(filas_filtradas, columnas)
                
                messagebox.showinfo(
                    "Filtros Aplicados",
                    f"Se encontraron {len(filas_filtradas)} registro(s)\n\n"
                    f"Filtros aplicados: {len(filtros_dict)}"
                )
                
            except Exception as e:
                messagebox.showerror(
                    "Error al Filtrar",
                    f"Error al aplicar filtros:\n{str(e)}"
                )
        
        filter_window = FilterWindow(
            parent=self.window,
            table_name=current_view.table_name,
            column_names=column_names,
            on_filter_apply=on_filter_apply
        )
    
    def download_pdf(self, table_name):
        """Función para descargar reporte en PDF de una tabla específica"""
        display_names = {
            "Maquinas": "Máquinas",
            "Ubicacion": "Ubicación",
            "Mantenimiento": "Mantenimiento",
            "Recaudacion": "Recaudación",
            "Stock": "Stock"
        }
        display_name = display_names.get(table_name, table_name)
        
        try:
            # Abrir diálogo para seleccionar ubicación de guardado
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            filepath = filedialog.asksaveasfilename(
                title=f"Guardar Reporte de {display_name}",
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf")],
                initialfile=f"Reporte_{table_name}_{timestamp}.pdf"
            )
            
            # Si el usuario canceló, no hacer nada
            if not filepath:
                return
            
            # === VALIDACIÓN ESPECIAL PARA TABLA RECAUDACIÓN ===
            if table_name == "Recaudacion":
                # Solicitar número de meses al usuario
                dialog = ctk.CTkInputDialog(
                    text="Considerando este mes, ¿cuántos meses atrás desea visualizar?\n(Ingrese un número entre 1 y 12)",
                    title="Reporte Estadístico de Recaudación"
                )
                meses_input = dialog.get_input()
                
                # Validar entrada
                if not meses_input:
                    return  # Usuario canceló
                
                try:
                    meses_solicitados = int(meses_input)
                    if meses_solicitados < 1 or meses_solicitados > 12:
                        raise ValueError("Número fuera de rango")
                except ValueError:
                    messagebox.showerror(
                        "Error de Validación",
                        "Por favor ingrese un número válido entre 1 y 12"
                    )
                    return
                
                # Obtener datos para gráficos
                datos_graficos = db_manager.obtener_datos_recaudacion_graficos(meses_solicitados)
                
                # Obtener datos de la tabla
                filas, columnas = db_manager.cargar_datos_tabla(table_name)
                
                # Generar reporte estadístico con gráficos
                exito = report_manager.generar_reporte_recaudacion(
                    filepath,
                    (columnas, filas),
                    datos_graficos,
                    meses_solicitados
                )
            else:
                # === FLUJO NORMAL PARA OTRAS TABLAS ===
                # Obtener datos actuales de la tabla
                filas, columnas = db_manager.cargar_datos_tabla(table_name)
                
                # Generar el PDF
                titulo_reporte = f"Reporte de {display_name}"
                
                # Llamar al generador de PDF
                exito = report_manager.generar_reporte_tabla(
                    filepath,
                    titulo_reporte,
                    columnas,
                    filas
                )
            
            # === MENSAJE DE ÉXITO (COMÚN PARA AMBOS FLUJOS) ===
            if exito:
                # Mensaje de éxito con opción de abrir el archivo
                result = messagebox.askyesno(
                    "Reporte Generado",
                    f"✅ Reporte generado exitosamente\\n\\n"
                    f"📁 Ubicación: {filepath}\\n"
                    f"📊 Registros: {len(filas)}\\n\\n"
                    f"¿Desea abrir el archivo ahora?",
                    icon="info"
                )
                
                # Abrir el archivo si el usuario lo desea
                if result:
                    if os.name == 'nt':  # Windows
                        os.startfile(filepath)
            else:
                messagebox.showerror(
                    "Error",
                    "No se pudo generar el reporte PDF.\\n"
                    "Verifique que tiene permisos de escritura."
                )
        
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al generar el reporte:\\n{str(e)}"
            )
    
    def show_notifications(self):
        """Mostrar notificaciones"""
        messagebox.showinfo(
            "Notificaciones", 
            "No tienes nuevas notificaciones"
        )
    
    def show_settings(self):
        """Mostrar configuración"""
        messagebox.showinfo(
            "Configuración", 
            "Panel de configuración\n\n(En desarrollo)"
        )
    

    def generate_general_report(self):
        """Generar reporte general del sistema"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            filepath = filedialog.asksaveasfilename(
                title="Guardar Reporte General",
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf")],
                initialfile=f"Reporte_General_{timestamp}.pdf"
            )
            
            if not filepath:
                return
            
            # Obtener datos de todas las tablas
            tablas = ["Maquinas", "Ubicacion", "Mantenimiento", "Recaudacion", "Stock"]
            datos_completos = {}
            
            for tabla in tablas:
                try:
                    filas, columnas = db_manager.cargar_datos_tabla(tabla)
                    datos_completos[tabla] = (columnas, filas)
                except Exception as e:
                    print(f"Error al cargar {tabla}: {e}")
            
            # Generar el PDF
            exito = report_manager.generar_reporte_general(filepath, datos_completos)
            
            if exito:
                result = messagebox.askyesno(
                    "Reporte Generado",
                    f"✅ Reporte general generado exitosamente\\n\\n"
                    f"📁 Ubicación: {filepath}\\n\\n"
                    f"¿Desea abrir el archivo ahora?",
                    icon="info"
                )
                
                if result:
                    if os.name == 'nt':
                        os.startfile(filepath)
            else:
                messagebox.showerror(
                    "Error",
                    "No se pudo generar el reporte general."
                )
        
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al generar el reporte:\\n{str(e)}"
            )
    
    def open_user_management(self):
        """Abrir ventana de gestión de usuarios"""
        try:
            from views import TableView
            
            # Crear ventana emergente
            user_window = ctk.CTkToplevel(self.window)
            user_window.title("Gestión de Usuarios")
            user_window.geometry("1000x700")
            
            # Centrar ventana
            user_window.update_idletasks()
            width = 1000
            height = 700
            x = (user_window.winfo_screenwidth() // 2) - (width // 2)
            y = (user_window.winfo_screenheight() // 2) - (height // 2)
            user_window.geometry(f'{width}x{height}+{x}+{y}')
            
            # Hacer la ventana modal
            user_window.grab_set()
            
            # Crear frame contenedor
            container = ctk.CTkFrame(user_window, fg_color="#F5F7F9")
            container.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Callbacks para la tabla de usuarios
            def add_user_callback(table_name):
                from views import AddRecordWindow
                add_window = AddRecordWindow(
                    parent=user_window,
                    table_name="Usuarios",
                    on_success=lambda: table_view.load_data()
                )
            
            def edit_user_callback():
                record_data, column_names = table_view.get_selected_record()
                if record_data is None or column_names is None:
                    messagebox.showwarning(
                        "Advertencia",
                        "Por favor, seleccione un usuario para editar"
                    )
                    return
                
                from views import EditRecordWindow
                edit_window = EditRecordWindow(
                    parent=user_window,
                    table_name="Usuarios",
                    record_data=record_data,
                    column_names=column_names,
                    on_success=lambda: table_view.load_data()
                )
            
            def filter_user_callback():
                from views import FilterWindow
                
                try:
                    _, column_names = db_manager.cargar_datos_tabla("Usuarios")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudieron obtener las columnas: {str(e)}")
                    return
                
                def on_filter_apply(filtros_dict):
                    try:
                        filas_filtradas, columnas = db_manager.filtrar_registros("Usuarios", filtros_dict)
                        table_view.update_table_data(filas_filtradas, columnas)
                        messagebox.showinfo(
                            "Filtros Aplicados",
                            f"Se encontraron {len(filas_filtradas)} usuario(s)"
                        )
                    except Exception as e:
                        messagebox.showerror("Error al Filtrar", f"Error: {str(e)}")
                
                filter_window = FilterWindow(
                    parent=user_window,
                    table_name="Usuarios",
                    column_names=column_names,
                    on_filter_apply=on_filter_apply
                )
            
            def download_user_pdf(table_name):
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                filepath = filedialog.asksaveasfilename(
                    title="Guardar Reporte de Usuarios",
                    defaultextension=".pdf",
                    filetypes=[("Archivos PDF", "*.pdf")],
                    initialfile=f"Reporte_Usuarios_{timestamp}.pdf"
                )
                
                if not filepath:
                    return
                
                try:
                    filas, columnas = db_manager.cargar_datos_tabla("Usuarios")
                    exito = report_manager.generar_reporte_tabla(
                        filepath,
                        "Reporte de Usuarios",
                        columnas,
                        filas
                    )
                    
                    if exito:
                        result = messagebox.askyesno(
                            "Reporte Generado",
                            f"✅ Reporte generado exitosamente\\n\\n"
                            f"📁 Ubicación: {filepath}\\n\\n"
                            f"¿Desea abrir el archivo ahora?",
                            icon="info"
                        )
                        
                        if result and os.name == 'nt':
                            os.startfile(filepath)
                except Exception as e:
                    messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
            
            # Crear TableView para usuarios
            callbacks = {
                'add_item': add_user_callback,
                'edit_item': edit_user_callback,
                'filter': filter_user_callback,
                'download': download_user_pdf
            }
            
            table_view = TableView(container, "Usuarios", callbacks)
            # TableView se empaqueta automáticamente en su método render()
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al abrir gestión de usuarios:\\n{str(e)}"
            )
    
    def logout(self):
        """Cerrar sesión y volver a la ventana de login"""
        result = messagebox.askyesno(
            "Cerrar Sesión",
            "¿Estás seguro que deseas cerrar sesión?"
        )
        
        if result:
            # Destruir ventana actual
            self.window.destroy()
            
            # Importar y abrir ventana de login
            from login import LoginWindow
            login = LoginWindow()
            login.run()
    
    # ==================== EJECUCIÓN ====================
    
    def run(self):
        """Iniciar la aplicación"""
        self.window.mainloop()


# Punto de entrada
if __name__ == "__main__":
    app = DashboardSAMER()
    app.run()