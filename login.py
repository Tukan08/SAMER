import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageDraw
import os
import db_manager
from index import DashboardSAMER
from recuperacion import ForgotPasswordWindow

# Configuración del tema y color
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class LoginWindow:
    def __init__(self):
        # Crear ventana principal
        self.window = ctk.CTk()
        self.window.title("Inicio de Sesión")
        
        # Configurar tamaño fijo de la ventana
        window_width = 500
        window_height = 700
        self.window.geometry(f"{window_width}x{window_height}")
        self.window.resizable(False, False)
        self.window.configure(fg_color="#2b2b2b")
        
        # Centrar ventana en la pantalla
        self.center_window(window_width, window_height)
        
        # Frame blanco con esquinas redondeadas
        self.login_frame = ctk.CTkFrame(
            self.window,
            width=380,
            height=580,
            corner_radius=20,
            fg_color="white"
        )
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.login_frame.pack_propagate(False)
        
        # Logo
        self.create_logo()
        
        # Título
        self.title_label = ctk.CTkLabel(
            self.login_frame,
            text="INICIO DE SESIÓN",
            font=("Arial", 24, "bold"),
            text_color="#1f1f1f"
        )
        self.title_label.pack(pady=(20, 30))
        
        # Campo de usuario
        self.username_entry = ctk.CTkEntry(
            self.login_frame,
            width=300,
            height=45,
            placeholder_text="Nombre de Usuario",
            font=("Arial", 14),
            corner_radius=10,
            border_width=2,
            border_color="#e0e0e0",
            fg_color="white",
            text_color="#1f1f1f"
        )
        self.username_entry.pack(pady=15)
        
        # Campo de contraseña
        self.password_entry = ctk.CTkEntry(
            self.login_frame,
            width=300,
            height=45,
            placeholder_text="Contraseña",
            font=("Arial", 14),
            corner_radius=10,
            border_width=2,
            border_color="#e0e0e0",
            fg_color="white",
            text_color="#1f1f1f",
            show="●"
        )
        self.password_entry.pack(pady=15)
        
        # Botón de inicio de sesión
        self.login_button = ctk.CTkButton(
            self.login_frame,
            width=300,
            height=45,
            text="Iniciar Sesión",
            font=("Arial", 16, "bold"),
            corner_radius=10,
            fg_color="#14b8a6",
            hover_color="#0d9488",
            text_color="white",
            command=self.login
        )
        self.login_button.pack(pady=25)
        
        # Enlace "¿Olvidó su contraseña?"
        self.forgot_password = ctk.CTkLabel(
            self.login_frame,
            text="¿Olvidó su contraseña?",
            font=("Arial", 12, "underline"),
            text_color="#14b8a6",
            cursor="hand2"
        )
        self.forgot_password.pack(pady=10)
        self.forgot_password.bind("<Button-1>", lambda e: self.forgot_password_click())
        
        # Espaciador
        ctk.CTkLabel(self.login_frame, text="", fg_color="white").pack(expand=True)
        
        # Versión
        self.version_label = ctk.CTkLabel(
            self.login_frame,
            text="Versión 1.0",
            font=("Arial", 10),
            text_color="#999999"
        )
        self.version_label.pack(pady=(0, 20))
        
        # Bind Enter key para login
        self.window.bind('<Return>', lambda e: self.login())
    
    def center_window(self, width, height):
        """Centrar la ventana en la pantalla"""
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_logo(self):
        """Crear un logo placeholder circular"""
        try:
            # Intentar cargar logo.png si existe
            if os.path.exists("assets\img\logo.png"):
                logo_image = ctk.CTkImage(
                    light_image=Image.open("assets\img\logo.png"),
                    dark_image=Image.open("assets\img\logo.png"),
                    size=(100, 100)
                )
            else:
                # Crear logo placeholder
                img = Image.new('RGB', (100, 100), color='#14b8a6')
                draw = ImageDraw.Draw(img)
                draw.ellipse([10, 10, 90, 90], fill='#0d9488', outline='#14b8a6', width=3)
                draw.text((35, 35), "LS", fill='white')
                
                logo_image = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=(100, 100)
                )
            
            self.logo_label = ctk.CTkLabel(
                self.login_frame,
                image=logo_image,
                text=""
            )
            self.logo_label.pack(pady=(30, 10))
        except Exception as e:
            # Si hay error, mostrar texto simple
            self.logo_label = ctk.CTkLabel(
                self.login_frame,
                text="🔒",
                font=("Arial", 60),
                text_color="#14b8a6"
            )
            self.logo_label.pack(pady=(30, 10))
    
    def login(self):
        """Función para manejar el inicio de sesión"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning(
                "Advertencia", 
                "Por favor ingrese usuario y contraseña"
            )
            return
        
        try:
            user = db_manager.autenticar_usuario(username, password)
            
            if user:
                self.window.destroy()
                dashboard = DashboardSAMER()
                dashboard.run()
            else:
                messagebox.showerror(
                    "Error de Autenticación", 
                    "Usuario o contraseña incorrectos"
                )
        
        except Exception as e:
            messagebox.showerror(
                "Error de Base de Datos", 
                f"Error al conectar con la base de datos: {str(e)}"
            )
    
    def forgot_password_click(self):
        """Función para manejar clic en olvidó contraseña"""
        # Abrir ventana de recuperación de contraseña
        ForgotPasswordWindow(self.window)
    
    def run(self):
        """Iniciar la aplicación"""
        self.window.mainloop()

# Ejecutar la aplicación
if __name__ == "__main__":
    app = LoginWindow()
    app.run()