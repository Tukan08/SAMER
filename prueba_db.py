"""
Script de prueba de la base de datos.
Ahora importa y utiliza las funciones del módulo db_manager.py
"""

import db_manager
from sqlite3 import Error


def seleccionar_tabla():
    """
    Muestra un menú para que el usuario elija una tabla y la devuelve.
    """
    print("\n--- Seleccione una Tabla ---")
    
    try:
        tablas = db_manager.obtener_tablas()
        
        if not tablas:
            print("Error: No se encontraron tablas en la base de datos.")
            return None
            
        for i, tabla in enumerate(tablas):
            print(f"[{i+1}] {tabla}")
        
        while True:
            try:
                opcion = int(input("Elija una tabla (número): "))
                if 1 <= opcion <= len(tablas):
                    return tablas[opcion-1]
                else:
                    print("Opción no válida.")
            except ValueError:
                print("Por favor, ingrese un número.")
                
    except Error as e:
        print(f"Error al obtener tablas: {e}")
        return None


# --- Funciones CRUD (ahora usan db_manager) ---

def registrar_registro():
    """
    Maneja el flujo para insertar un nuevo registro en una tabla.
    """
    tabla = seleccionar_tabla()
    if tabla is None: 
        return

    try:
        columnas = db_manager.obtener_columnas_insert(tabla)
        valores_dict = {}
        
        print(f"\n--- Registrando nuevo dato en '{tabla}' ---")
        for col in columnas:
            val = input(f"Ingrese valor para {col}: ")
            valores_dict[col] = val
        
        # Usar la función del módulo db_manager
        last_id = db_manager.registrar_registro(tabla, valores_dict)
        print(f"¡Registro insertado en '{tabla}' con éxito! (ID: {last_id})")
        
    except Error as e:
        print(f"\nError al registrar: {e}")
        print("Posible Causa: ¿Estás intentando insertar en 'Stock'?")
        print("Recuerda que la tabla 'Stock' tiene una llave foránea que apunta a 'Maquina' (con 'a') y no a 'Maquinas'.")


def actualizar_registro():
    """
    Maneja el flujo para actualizar un registro existente.
    """
    tabla = seleccionar_tabla()
    if tabla is None: 
        return
    
    try:
        pk = db_manager.obtener_pk(tabla)
        if pk is None:
            print(f"Error: La tabla '{tabla}' no tiene llave primaria. No se puede actualizar.")
            return

        id_val = input(f"\nIngrese el '{pk}' del registro que desea actualizar: ")
        
        # Obtener estructura de la tabla para mostrar columnas
        estructura = db_manager.obtener_estructura_tabla(tabla)
        columnas = [info[1] for info in estructura]
        
        print("\n¿Qué columna desea actualizar?")
        for i, col in enumerate(columnas):
            print(f"[{i+1}] {col}")
            
        op_col = int(input("Elija una columna: "))
        if not (1 <= op_col <= len(columnas)):
            print("Opción no válida.")
            return
            
        col_actualizar = columnas[op_col-1]
        nuevo_valor = input(f"Ingrese el nuevo valor para '{col_actualizar}': ")
        
        # Usar la función del módulo db_manager
        filas_afectadas = db_manager.actualizar_registro(
            tabla, pk, id_val, col_actualizar, nuevo_valor
        )
        
        if filas_afectadas == 0:
            print(f"No se encontró ningún registro con {pk} = {id_val}. No se actualizó nada.")
        else:
            print(f"¡Registro actualizado con éxito!")
            
    except Error as e:
        print(f"Error al actualizar: {e}")
    except (ValueError, IndexError):
        print("Entrada no válida.")


def eliminar_registro():
    """
    Maneja el flujo para eliminar un registro.
    """
    tabla = seleccionar_tabla()
    if tabla is None: 
        return

    try:
        pk = db_manager.obtener_pk(tabla)
        if pk is None:
            print(f"Error: La tabla '{tabla}' no tiene llave primaria. No se puede eliminar.")
            return
            
        id_val = input(f"\nIngrese el '{pk}' del registro que desea ELIMINAR: ")
        
        # --- Confirmación ---
        confirm = input(
            f"ADVERTENCIA: ¿Está seguro que desea eliminar el registro {pk}={id_val} "
            f"de la tabla '{tabla}'? Esta acción es irreversible. (s/n): "
        )
        
        if confirm.lower() != 's':
            print("Operación cancelada.")
            return
            
        # Usar la función del módulo db_manager
        filas_eliminadas = db_manager.eliminar_registro(tabla, pk, id_val)
        
        if filas_eliminadas == 0:
            print(f"No se encontró ningún registro con {pk} = {id_val}. No se eliminó nada.")
        else:
            print(f"¡Registro eliminado con éxito!")

    except Error as e:
        print(f"Error al eliminar: {e}")
    except ValueError:
        print("Entrada no válida.")


def consultar_registros():
    """
    Muestra todos los registros de una tabla.
    """
    tabla = seleccionar_tabla()
    if tabla is None: 
        return
    
    try:
        # Usar la función del módulo db_manager
        filas, cabeceras = db_manager.consultar_registros(tabla)
        
        print(f"\n--- Mostrando {len(filas)} registros de '{tabla}' ---")
        
        # Imprimir cabeceras
        print(" | ".join(cabeceras))
        print("-" * (sum(len(c) for c in cabeceras) + len(cabeceras) * 3))
        
        # Imprimir filas
        if not filas:
            print("(Tabla vacía)")
        else:
            for fila in filas:
                print(" | ".join(map(str, fila)))
        
        print("-" * (sum(len(c) for c in cabeceras) + len(cabeceras) * 3))

    except Error as e:
        print(f"Error al consultar: {e}")


# --- Menú Principal ---

def main():
    print("¡Bienvenido al Gestor de BD!")
    print("Este script ahora utiliza el módulo db_manager.py para todas las operaciones.")

    # Bucle del menú principal
    while True:
        print("\n--- Menú Principal ---")
        print("[1] Registrar nuevo dato")
        print("[2] Actualizar un dato existente")
        print("[3] Eliminar un dato")
        print("[4] Consultar todos los datos de una tabla")
        print("[5] Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            registrar_registro()
        elif opcion == '2':
            actualizar_registro()
        elif opcion == '3':
            eliminar_registro()
        elif opcion == '4':
            consultar_registros()
        elif opcion == '5':
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intente de nuevo.")


# --- Punto de entrada del script ---
if __name__ == '__main__':
    main()