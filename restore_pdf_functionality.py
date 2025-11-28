"""
Script para restaurar la funcionalidad de reportes PDF en index.py
"""

# Leer el archivo
with open('index.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Agregar imports necesarios
old_imports = """import customtkinter as ctk
from tkinter import messagebox
from views import ViewManager"""

new_imports = """import customtkinter as ctk
from tkinter import messagebox, filedialog
from views import ViewManager
import db_manager
import report_manager
import os"""

content = content.replace(old_imports, new_imports)

# 2. Reemplazar el método download_pdf
old_download_pdf = '''    def download_pdf(self, table_name):
        """Función para descargar reporte en PDF"""
        display_names = {
            "Maquinas": "Máquinas",
            "Ubicacion": "Ubicación",
            "Mantenimiento": "Mantenimiento",
            "Recaudacion": "Recaudación",
            "Stock": "Stock"
        }
        display_name = display_names.get(table_name, table_name)
        messagebox.showinfo(
            "Descargar Reporte", 
            f"Generando reporte PDF de {display_name}...\\n\\n(En desarrollo)"
        )'''

new_download_pdf = '''    def download_pdf(self, table_name):
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
            )'''

content = content.replace(old_download_pdf, new_download_pdf)

# 3. Reemplazar el método filter_data
old_filter_data = '''    def filter_data(self):
        """Función para filtrar datos"""
        messagebox.showinfo(
            "Filtrar", 
            "Funcionalidad de filtrado de datos\\n\\n(En desarrollo)"
        )'''

new_filter_data = '''    def filter_data(self):
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
                    f"Se encontraron {len(filas_filtradas)} registro(s)\\n\\n"
                    f"Filtros aplicados: {len(filtros_dict)}"
                )
                
            except Exception as e:
                messagebox.showerror(
                    "Error al Filtrar",
                    f"Error al aplicar filtros:\\n{str(e)}"
                )
        
        filter_window = FilterWindow(
            parent=self.window,
            table_name=current_view.table_name,
            column_names=column_names,
            on_filter_apply=on_filter_apply
        )'''

content = content.replace(old_filter_data, new_filter_data)

# Escribir el archivo modificado
with open('index.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Funcionalidad de reportes PDF restaurada exitosamente")
print("   - Imports agregados: filedialog, db_manager, report_manager, os")
print("   - Metodo download_pdf actualizado con generacion de PDF completa")
print("   - Metodo filter_data actualizado con filtrado funcional")
