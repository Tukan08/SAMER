"""
Módulo de recuperación de contraseña
Maneja el flujo de recuperación de contraseña mediante código de verificación por email
"""

import customtkinter as ctk
from tkinter import messagebox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import db_manager


class ForgotPasswordWindow(ctk.CTkToplevel):
    """
    Ventana modal para recuperación de contraseña.
    Implementa un flujo de 3 etapas:
    1. Solicitud: Usuario + Email
    2. Verificación: Código de 6 dígitos
    3. Cambio: Nueva contraseña
    """
    
    # Configuración SMTP (hardcodeada para pruebas)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_EMAIL = "zaidenriqueb@gmail.com"
    SMTP_PASSWORD = "yxzzhdzmwdlvquub"
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configuración de la ventana
        self.title("Recuperar Contraseña")
        window_width = 450
        window_height = 500
        self.geometry(f"{window_width}x{window_height}")
        self.resizable(False, False)
        self.configure(fg_color="#2b2b2b")
        
        # Centrar ventana
        self.center_window(window_width, window_height)
        
        # Hacer la ventana modal
        self.grab_set()
        self.transient(parent)
        
        # Variables de estado
        self.etapa_actual = 1
        self.username = None
        self.email = None
        self.codigo_generado = None
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(
            self,
            width=380,
            height=450,
            corner_radius=20,
            fg_color="white"
        )
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.main_frame.pack_propagate(False)
        
        # Mostrar etapa inicial
        self.mostrar_etapa_solicitud()
    
    def center_window(self, width, height):
        """Centrar la ventana en la pantalla"""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def limpiar_frame(self):
        """Elimina todos los widgets del frame principal"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    # ========================================================================
    # ETAPA 1: SOLICITUD
    # ========================================================================
    
    def mostrar_etapa_solicitud(self):
        """Muestra la interfaz de solicitud (Usuario + Email)"""
        self.limpiar_frame()
        self.etapa_actual = 1
        
        # Título
        titulo = ctk.CTkLabel(
            self.main_frame,
            text="Recuperar Contraseña",
            font=("Arial", 24, "bold"),
            text_color="#1f1f1f"
        )
        titulo.pack(pady=(40, 10))
        
        # Subtítulo
        subtitulo = ctk.CTkLabel(
            self.main_frame,
            text="Ingrese su usuario y el correo donde recibirá el código",
            font=("Arial", 12),
            text_color="#666666",
            wraplength=300
        )
        subtitulo.pack(pady=(0, 30))
        
        # Campo de usuario
        self.entry_usuario = ctk.CTkEntry(
            self.main_frame,
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
        self.entry_usuario.pack(pady=15)
        
        # Campo de email
        self.entry_email = ctk.CTkEntry(
            self.main_frame,
            width=300,
            height=45,
            placeholder_text="Correo Electrónico",
            font=("Arial", 14),
            corner_radius=10,
            border_width=2,
            border_color="#e0e0e0",
            fg_color="white",
            text_color="#1f1f1f"
        )
        self.entry_email.pack(pady=15)
        
        # Botón enviar código
        btn_enviar = ctk.CTkButton(
            self.main_frame,
            width=300,
            height=45,
            text="Enviar Código",
            font=("Arial", 16, "bold"),
            corner_radius=10,
            fg_color="#14b8a6",
            hover_color="#0d9488",
            text_color="white",
            command=self.enviar_codigo
        )
        btn_enviar.pack(pady=25)
        
        # Botón cancelar
        btn_cancelar = ctk.CTkButton(
            self.main_frame,
            width=300,
            height=40,
            text="Cancelar",
            font=("Arial", 14),
            corner_radius=10,
            fg_color="#999999",
            hover_color="#777777",
            text_color="white",
            command=self.destroy
        )
        btn_cancelar.pack(pady=10)
        
        # Bind Enter key
        self.bind('<Return>', lambda e: self.enviar_codigo())
    
    def enviar_codigo(self):
        """Valida usuario/email y envía código de verificación"""
        usuario = self.entry_usuario.get().strip()
        email = self.entry_email.get().strip()
        
        # Validar campos vacíos
        if not usuario or not email:
            messagebox.showwarning(
                "Campos Vacíos",
                "Por favor ingrese usuario y correo electrónico"
            )
            return
        
        # Validar en base de datos (solo el usuario)
        try:
            if not db_manager.verificar_usuario_email(usuario, email):
                messagebox.showerror(
                    "Usuario No Encontrado",
                    "El usuario ingresado no existe en el sistema"
                )
                return
        except Exception as e:
            messagebox.showerror(
                "Error de Base de Datos",
                f"Error al verificar datos: {str(e)}"
            )
            return
        
        # Generar código aleatorio de 6 dígitos
        self.codigo_generado = ''.join(random.choices(string.digits, k=6))
        self.username = usuario
        self.email = email
        
        # Enviar código por correo
        if self.enviar_email_codigo():
            messagebox.showinfo(
                "Código Enviado",
                f"Se ha enviado un código de verificación a {email}"
            )
            self.mostrar_etapa_verificacion()
        else:
            messagebox.showerror(
                "Error de Envío",
                "No se pudo enviar el correo. Verifique su conexión a internet."
            )
    
    def enviar_email_codigo(self):
        """Envía el código de verificación por correo electrónico"""
        try:
            # Crear mensaje
            mensaje = MIMEMultipart()
            mensaje['From'] = self.SMTP_EMAIL
            mensaje['To'] = self.email
            mensaje['Subject'] = "Código de Recuperación - SAMER"
            
            # Cuerpo del mensaje
            cuerpo = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #14b8a6;">Recuperación de Contraseña - SAMER</h2>
                    <p>Hola <strong>{self.username}</strong>,</p>
                    <p>Has solicitado recuperar tu contraseña. Tu código de verificación es:</p>
                    <h1 style="color: #14b8a6; letter-spacing: 5px;">{self.codigo_generado}</h1>
                    <p>Este código es válido por 10 minutos.</p>
                    <p>Si no solicitaste este cambio, ignora este mensaje.</p>
                    <hr>
                    <p style="color: #999999; font-size: 12px;">Sistema SAMER - Gestión de Máquinas</p>
                </body>
            </html>
            """
            
            mensaje.attach(MIMEText(cuerpo, 'html'))
            
            # Conectar y enviar
            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.starttls()
                server.login(self.SMTP_EMAIL, self.SMTP_PASSWORD)
                server.send_message(mensaje)
            
            return True
            
        except smtplib.SMTPException as e:
            print(f"Error SMTP: {e}")
            return False
        except Exception as e:
            print(f"Error al enviar email: {e}")
            return False
    
    # ========================================================================
    # ETAPA 2: VERIFICACIÓN
    # ========================================================================
    
    def mostrar_etapa_verificacion(self):
        """Muestra la interfaz de verificación de código"""
        self.limpiar_frame()
        self.etapa_actual = 2
        
        # Título
        titulo = ctk.CTkLabel(
            self.main_frame,
            text="Verificar Código",
            font=("Arial", 24, "bold"),
            text_color="#1f1f1f"
        )
        titulo.pack(pady=(40, 10))
        
        # Subtítulo
        subtitulo = ctk.CTkLabel(
            self.main_frame,
            text=f"Ingrese el código enviado a {self.email}",
            font=("Arial", 12),
            text_color="#666666",
            wraplength=300
        )
        subtitulo.pack(pady=(0, 30))
        
        # Campo de código
        self.entry_codigo = ctk.CTkEntry(
            self.main_frame,
            width=300,
            height=45,
            placeholder_text="Código de 6 dígitos",
            font=("Arial", 18, "bold"),
            corner_radius=10,
            border_width=2,
            border_color="#e0e0e0",
            fg_color="white",
            text_color="#1f1f1f",
            justify="center"
        )
        self.entry_codigo.pack(pady=15)
        
        # Botón verificar
        btn_verificar = ctk.CTkButton(
            self.main_frame,
            width=300,
            height=45,
            text="Verificar Código",
            font=("Arial", 16, "bold"),
            corner_radius=10,
            fg_color="#14b8a6",
            hover_color="#0d9488",
            text_color="white",
            command=self.verificar_codigo
        )
        btn_verificar.pack(pady=25)
        
        # Botón volver
        btn_volver = ctk.CTkButton(
            self.main_frame,
            width=300,
            height=40,
            text="Volver",
            font=("Arial", 14),
            corner_radius=10,
            fg_color="#999999",
            hover_color="#777777",
            text_color="white",
            command=self.mostrar_etapa_solicitud
        )
        btn_volver.pack(pady=10)
        
        # Bind Enter key
        self.bind('<Return>', lambda e: self.verificar_codigo())
    
    def verificar_codigo(self):
        """Verifica que el código ingresado sea correcto"""
        codigo_ingresado = self.entry_codigo.get().strip()
        
        if not codigo_ingresado:
            messagebox.showwarning(
                "Campo Vacío",
                "Por favor ingrese el código de verificación"
            )
            return
        
        if codigo_ingresado == self.codigo_generado:
            self.mostrar_etapa_cambio()
        else:
            messagebox.showerror(
                "Código Incorrecto",
                "El código ingresado no es válido. Intente nuevamente."
            )
            self.entry_codigo.delete(0, 'end')
    
    # ========================================================================
    # ETAPA 3: CAMBIO DE CONTRASEÑA
    # ========================================================================
    
    def mostrar_etapa_cambio(self):
        """Muestra la interfaz de cambio de contraseña"""
        self.limpiar_frame()
        self.etapa_actual = 3
        
        # Título
        titulo = ctk.CTkLabel(
            self.main_frame,
            text="Nueva Contraseña",
            font=("Arial", 24, "bold"),
            text_color="#1f1f1f"
        )
        titulo.pack(pady=(40, 10))
        
        # Subtítulo
        subtitulo = ctk.CTkLabel(
            self.main_frame,
            text="Ingrese su nueva contraseña",
            font=("Arial", 12),
            text_color="#666666"
        )
        subtitulo.pack(pady=(0, 30))
        
        # Campo nueva contraseña
        self.entry_nueva_password = ctk.CTkEntry(
            self.main_frame,
            width=300,
            height=45,
            placeholder_text="Nueva Contraseña",
            font=("Arial", 14),
            corner_radius=10,
            border_width=2,
            border_color="#e0e0e0",
            fg_color="white",
            text_color="#1f1f1f",
            show="●"
        )
        self.entry_nueva_password.pack(pady=15)
        
        # Campo confirmar contraseña
        self.entry_confirmar_password = ctk.CTkEntry(
            self.main_frame,
            width=300,
            height=45,
            placeholder_text="Confirmar Contraseña",
            font=("Arial", 14),
            corner_radius=10,
            border_width=2,
            border_color="#e0e0e0",
            fg_color="white",
            text_color="#1f1f1f",
            show="●"
        )
        self.entry_confirmar_password.pack(pady=15)
        
        # Botón cambiar contraseña
        btn_cambiar = ctk.CTkButton(
            self.main_frame,
            width=300,
            height=45,
            text="Cambiar Contraseña",
            font=("Arial", 16, "bold"),
            corner_radius=10,
            fg_color="#14b8a6",
            hover_color="#0d9488",
            text_color="white",
            command=self.cambiar_password
        )
        btn_cambiar.pack(pady=25)
        
        # Botón cancelar
        btn_cancelar = ctk.CTkButton(
            self.main_frame,
            width=300,
            height=40,
            text="Cancelar",
            font=("Arial", 14),
            corner_radius=10,
            fg_color="#999999",
            hover_color="#777777",
            text_color="white",
            command=self.destroy
        )
        btn_cancelar.pack(pady=10)
        
        # Bind Enter key
        self.bind('<Return>', lambda e: self.cambiar_password())
    
    def cambiar_password(self):
        """Valida y actualiza la contraseña en la base de datos"""
        nueva_password = self.entry_nueva_password.get()
        confirmar_password = self.entry_confirmar_password.get()
        
        # Validar campos vacíos
        if not nueva_password or not confirmar_password:
            messagebox.showwarning(
                "Campos Vacíos",
                "Por favor complete ambos campos"
            )
            return
        
        # Validar que las contraseñas coincidan
        if nueva_password != confirmar_password:
            messagebox.showerror(
                "Contraseñas No Coinciden",
                "Las contraseñas ingresadas no coinciden"
            )
            self.entry_confirmar_password.delete(0, 'end')
            return
        
        # Validar longitud mínima
        if len(nueva_password) < 4:
            messagebox.showwarning(
                "Contraseña Débil",
                "La contraseña debe tener al menos 4 caracteres"
            )
            return
        
        # Actualizar en base de datos
        try:
            filas_afectadas = db_manager.actualizar_contrasena(
                self.username,
                nueva_password
            )
            
            if filas_afectadas > 0:
                messagebox.showinfo(
                    "Contraseña Actualizada",
                    "Su contraseña ha sido actualizada exitosamente"
                )
                self.destroy()
            else:
                messagebox.showerror(
                    "Error",
                    "No se pudo actualizar la contraseña"
                )
        
        except Exception as e:
            messagebox.showerror(
                "Error de Base de Datos",
                f"Error al actualizar contraseña: {str(e)}"
            )
