import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3

# Configuración del tema
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class DashboardSAMER:
    def __init__(self):
        # Crear ventana principal
        self.window = ctk.CTk()
        self.window.title("SAMER - Sistema de Administración de Maquinas Expendedoras Recreativas")
        self.window.geometry("1200x700")
        self.window.configure(fg_color="#E5E5E5")
        
        # Conexión a la base de datos
        try:
            self.conn = sqlite3.connect('MySQLite/gestion_garratorrinco.db')
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudo conectar a la base de datos: {str(e)}")
            self.window.destroy()
            return
        
        # Centrar ventana
        self.center_window()
        
        # Crear componentes
        self.create_header()
        self.create_body()
        
        # Cargar datos iniciales
        self.change_section("Maquinas")
        
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.window.update_idletasks()
        width = 1200
        height = 700
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_header(self):
        """Crear la barra superior (Header)"""
        self.header = ctk.CTkFrame(
            self.window,
            height=50,
            corner_radius=0,
            fg_color="#333333"
        )
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        
        # Título del header
        self.header_title = ctk.CTkLabel(
            self.header,
            text="SAMER - Sistema de Administración Expendetres",
            font=("Arial", 18, "bold"),
            text_color="white"
        )
        self.header_title.pack(side="left", padx=20, pady=10)
        
        # Botón de Cerrar Sesión
        self.btn_logout = ctk.CTkButton(
            self.header,
            text="Cerrar Sesión",
            width=130,
            height=35,
            corner_radius=8,
            fg_color="#D9534F",
            hover_color="#C9302C",
            font=("Arial", 13, "bold"),
            text_color="white",
            command=self.logout
        )
        self.btn_logout.pack(side="right", padx=20, pady=7)
    
    def logout(self):
        """Cerrar sesión y volver a la ventana de login"""
        # Cerrar conexión a la base de datos
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        
        # Destruir ventana actual
        self.window.destroy()
        
        # Importar y abrir ventana de login
        from login import LoginWindow
        login = LoginWindow()
        login.run()
    
    def create_body(self):
        """Crear el cuerpo principal (menú + contenido)"""
        # Frame contenedor del cuerpo
        self.body = ctk.CTkFrame(
            self.window,
            fg_color="#E5E5E5"
        )
        self.body.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Crear menú lateral y área de contenido
        self.create_menu()
        self.create_content_area()
    
    def create_menu(self):
        """Crear la columna de menú izquierda"""
        self.menu_frame = ctk.CTkFrame(
            self.body,
            width=250,
            corner_radius=0,
            fg_color="#F0F0F0"
        )
        self.menu_frame.pack(side="left", fill="y", padx=0, pady=0)
        self.menu_frame.pack_propagate(False)
        
        # Título del menú
        self.menu_title = ctk.CTkLabel(
            self.menu_frame,
            text="Secciones Principales\ndel Sistema",
            font=("Arial", 16, "bold"),
            text_color="#333333"
        )
        self.menu_title.pack(pady=(30, 10))
        
        # Subtítulo
        self.menu_subtitle = ctk.CTkLabel(
            self.menu_frame,
            text="Sección: Máquinas",
            font=("Arial", 13),
            text_color="#666666"
        )
        self.menu_subtitle.pack(pady=(5, 30))
        
        # Botones del menú
        self.btn_maquinas = ctk.CTkButton(
            self.menu_frame,
            text="MÁQUINAS",
            width=200,
            height=50,
            corner_radius=10,
            fg_color="#1f538d",
            hover_color="#164270",
            font=("Arial", 14, "bold"),
            command=lambda: self.change_section("Maquinas")
        )
        self.btn_maquinas.pack(pady=10)
        
        self.btn_mantenimiento = ctk.CTkButton(
            self.menu_frame,
            text="MANTENIMIENTO",
            width=200,
            height=50,
            corner_radius=10,
            fg_color="#8B8B8B",
            hover_color="#707070",
            font=("Arial", 14, "bold"),
            command=lambda: self.change_section("Mantenimiento")
        )
        self.btn_mantenimiento.pack(pady=10)
        
        self.btn_recaudacion = ctk.CTkButton(
            self.menu_frame,
            text="RECAUDACIÓN",
            width=200,
            height=50,
            corner_radius=10,
            fg_color="#8B8B8B",
            hover_color="#707070",
            font=("Arial", 14, "bold"),
            command=lambda: self.change_section("Recaudacion")
        )
        self.btn_recaudacion.pack(pady=10)
        
        self.btn_stock = ctk.CTkButton(
            self.menu_frame,
            text="STOCK",
            width=200,
            height=50,
            corner_radius=10,
            fg_color="#8B8B8B",
            hover_color="#707070",
            font=("Arial", 14, "bold"),
            command=lambda: self.change_section("Stock")
        )
        self.btn_stock.pack(pady=10)
    
    def create_content_area(self):
        """Crear el área de contenido derecha"""
        # Frame contenedor del área de contenido
        self.content_container = ctk.CTkFrame(
            self.body,
            fg_color="#E5E5E5"
        )
        self.content_container.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Tarjeta blanca principal
        self.content_card = ctk.CTkFrame(
            self.content_container,
            corner_radius=15,
            fg_color="white"
        )
        self.content_card.pack(fill="both", expand=True)
        
        # Header de la tarjeta
        self.create_card_header()
        
        # Área para la tabla
        self.table_frame = ctk.CTkFrame(
            self.content_card,
            fg_color="#F8F8F8",
            corner_radius=10
        )
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # Configurar la tabla
        self.setup_table()
        
        # Footer de la tarjeta
        self.create_card_footer()
    
    def setup_table(self):
        """Configurar el Treeview para mostrar datos"""
        # Crear estilo para el Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                       background="white",
                       foreground="#333333",
                       rowheight=30,
                       fieldbackground="white",
                       font=("Arial", 11))
        style.configure("Treeview.Heading",
                       background="#1f538d",
                       foreground="white",
                       font=("Arial", 12, "bold"))
        style.map("Treeview",
                 background=[("selected", "#14b8a6")])
        
        # Frame para contener el Treeview y scrollbars
        tree_container = ctk.CTkFrame(self.table_frame, fg_color="white")
        tree_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")
        
        # Crear Treeview
        self.tree = ttk.Treeview(
            tree_container,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Posicionar elementos
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
    
    def create_card_header(self):
        """Crear el encabezado de la tarjeta de contenido"""
        self.card_header = ctk.CTkFrame(
            self.content_card,
            fg_color="white",
            height=60
        )
        self.card_header.pack(fill="x", padx=20, pady=(20, 10))
        self.card_header.pack_propagate(False)
        
        # Título de la sección
        self.section_title = ctk.CTkLabel(
            self.card_header,
            text="Sección: Máquinas",
            font=("Arial", 22, "bold"),
            text_color="#333333"
        )
        self.section_title.pack(side="left", pady=10)
        
        # Frame para los botones a la derecha
        self.buttons_frame = ctk.CTkFrame(
            self.card_header,
            fg_color="white"
        )
        self.buttons_frame.pack(side="right", pady=10)
        
        # Botón Filtrar
        self.btn_filter = ctk.CTkButton(
            self.buttons_frame,
            text="Filtrar",
            width=120,
            height=35,
            corner_radius=8,
            fg_color="#6B6B6B",
            hover_color="#555555",
            font=("Arial", 13)
        )
        self.btn_filter.pack(side="right", padx=(10, 0))
        
        # Botón Agregar
        self.btn_add = ctk.CTkButton(
            self.buttons_frame,
            text="Agregar Máquina",
            width=150,
            height=35,
            corner_radius=8,
            fg_color="#1f538d",
            hover_color="#164270",
            font=("Arial", 13),
            command=self.add_item
        )
        self.btn_add.pack(side="right")
    
    def create_card_footer(self):
        """Crear el pie de la tarjeta de contenido"""
        self.card_footer = ctk.CTkFrame(
            self.content_card,
            fg_color="white",
            height=50
        )
        self.card_footer.pack(fill="x", padx=20, pady=(0, 20))
        self.card_footer.pack_propagate(False)
        
        # Botón Descargar Reporte
        self.btn_download = ctk.CTkButton(
            self.card_footer,
            text="Descargar Reporte (.pdf)",
            width=200,
            height=35,
            corner_radius=8,
            fg_color="#1f538d",
            hover_color="#164270",
            font=("Arial", 13, "bold"),
            command=self.download_pdf
        )
        self.btn_download.pack(side="left", pady=7)
    
    def change_section(self, section_name):
        """Cambiar de sección y actualizar la interfaz"""
        # Actualizar títulos
        display_name = section_name
        if section_name == "Maquinas":
            display_name = "Máquinas"
        elif section_name == "Recaudacion":
            display_name = "Recaudación"
        
        self.section_title.configure(text=f"Sección: {display_name}")
        self.menu_subtitle.configure(text=f"Sección: {display_name}")
        
        # Actualizar texto del botón agregar
        self.btn_add.configure(text=f"Agregar {display_name[:-1] if display_name.endswith('s') else display_name}")
        
        # Actualizar colores de botones del menú
        buttons = {
            "Maquinas": self.btn_maquinas,
            "Mantenimiento": self.btn_mantenimiento,
            "Recaudacion": self.btn_recaudacion,
            "Stock": self.btn_stock
        }
        
        for name, button in buttons.items():
            if name == section_name:
                button.configure(fg_color="#1f538d", hover_color="#164270")
            else:
                button.configure(fg_color="#8B8B8B", hover_color="#707070")
        
        # Cargar datos de la tabla
        self.load_data_to_table(section_name)
    
    def load_data_to_table(self, table_name):
        """Cargar datos de la base de datos en el Treeview"""
        try:
            # Limpiar tabla actual
            self.tree.delete(*self.tree.get_children())
            
            # Ejecutar consulta
            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()
            
            # Obtener nombres de columnas
            column_names = [description[0] for description in self.cursor.description]
            
            # Configurar columnas del Treeview
            self.tree["columns"] = column_names
            self.tree["show"] = "headings"
            
            # Configurar encabezados y anchos de columna
            for col in column_names:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120, anchor="center")
            
            # Insertar datos
            for row in rows:
                self.tree.insert("", "end", values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al cargar datos: {str(e)}")
    
    def add_item(self):
        """Función para agregar nuevo elemento"""
        section = self.section_title.cget("text").replace("Sección: ", "")
        messagebox.showinfo("Agregar", f"Funcionalidad para agregar nuevo elemento en {section}")
    
    def download_pdf(self):
        """Función para descargar reporte en PDF"""
        section = self.section_title.cget("text").replace("Sección: ", "")
        messagebox.showinfo("Descargar Reporte", f"Generando reporte PDF de {section}...")
    
    def run(self):
        """Iniciar la aplicación"""
        self.window.mainloop()
        
        # Cerrar conexión al cerrar la ventana
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

# Ejecutar la aplicación
if __name__ == "__main__":
    app = DashboardSAMER()
    app.run()