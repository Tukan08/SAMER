import sqlite3
from sqlite3 import Error

# Define el nombre de tu archivo de base de datos
DATABASE_NAME = "gestion_garratorrinco.db"

def crear_conexion():
    """
    Crea una conexión a la base de datos SQLite especificada por DATABASE_NAME
    :return: Objeto de conexión o None si hay error
    """
    conn = None
    try:
        # Intenta conectar a la base de datos
        conn = sqlite3.connect("MySQLite/" + DATABASE_NAME)
        # print(f"Conexión a {DATABASE_NAME} establecida.") # Puedes descomentar esto para depurar
        return conn
    except Error as e:
        # Maneja errores si la conexión falla
        print(f"Error al conectar a la base de datos: {e}")
        return None

if __name__ == '__main__':
    # --- Prueba de conexión ---
    # Este bloque solo se ejecuta si corres este archivo directamente
    # Sirve para probar que la conexión funciona.
    
    print("Probando la conexión...")
    conexion = crear_conexion()
    
    if conexion:
        print("¡Prueba de conexión exitosa!")
        
        # Opcional: Hacemos una consulta rápida para verificar
        try:
            cursor = conexion.cursor()
            # Usamos una de tus tablas: Ubicacion [cite: 26]
            cursor.execute("SELECT nombreLugar FROM Ubicacion WHERE idUbicacion = 1;")
            fila = cursor.fetchone()
            if fila:
                print(f"Dato de prueba recuperado: {fila[0]}") # Debería imprimir 'Plaza Central' [cite: 67]
            else:
                print("Se conectó, pero no se encontró el dato de prueba (ID 1).")
        except Error as e:
            print(f"Error al consultar: {e}")
            
        # No olvides cerrar la conexión cuando termines de usarla
        conexion.close()
        print("Conexión cerrada.")
    else:
        print("No se pudo establecer la conexión.")