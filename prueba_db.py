import sqlite3
import conexion_db # Importamos nuestro módulo de conexión

def obtener_tablas(conn):
    """
    Obtiene una lista de todas las tablas de usuario en la BD.
    """
    cursor = conn.cursor()
    # Consultamos la tabla maestra de SQLite para encontrar todas las tablas
    # Excluimos las tablas internas de sqlite
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    # Extraemos el primer elemento (el nombre) de cada tupla resultante
    tablas = [tabla[0] for tabla in cursor.fetchall()]
    return tablas

def obtener_pk(conn, tabla):
    """
    Encuentra el nombre de la columna que es la Llave Primaria (PK) de una tabla.
    """
    cursor = conn.cursor()
    # PRAGMA table_info nos da la estructura de la tabla
    # El sexto elemento (índice 5) de la fila es 1 si es PK, 0 si no
    cursor.execute(f"PRAGMA table_info({tabla})")
    for info in cursor.fetchall():
        if info[5] == 1:  # info[5] es la columna 'pk'
            return info[1]  # info[1] es la columna 'name'
    return None # Si no se encuentra PK (mala práctica de diseño)

def obtener_columnas_insert(conn, tabla):
    """
    Obtiene las columnas para un INSERT.
    Omite las llaves primarias que sean AUTOINCREMENT.
    """
    cursor = conn.cursor()
    # 1. Obtenemos el comando SQL con el que se creó la tabla
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tabla,))
    schema = cursor.fetchone()[0].upper() # Ej: "CREATE TABLE UBICACION(... AUTOINCREMENT ...)"
    
    # 2. Obtenemos la info de las columnas
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas_info = cursor.fetchall()
    
    columnas_a_pedir = []
    
    for col in columnas_info:
        nombre = col[1]
        es_pk = col[5] == 1
        
        # 3. Decidimos si pedir la columna
        # Si es PK (es_pk) Y la palabra "AUTOINCREMENT" está en el esquema,
        # entonces no la pedimos.
        if es_pk and 'AUTOINCREMENT' in schema:
            continue
        
        # Si no es autoincremental (como idMaquina), sí la pedimos.
        columnas_a_pedir.append(nombre)
        
    return columnas_a_pedir


def seleccionar_tabla(conn):
    """
    Muestra un menú para que el usuario elija una tabla y la devuelve.
    """
    print("\n--- Seleccione una Tabla ---")
    tablas = obtener_tablas(conn)
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

# --- Funciones CRUD ---

def registrar_registro(conn):
    """
    Maneja el flujo para insertar un nuevo registro en una tabla.
    """
    tabla = seleccionar_tabla(conn)
    if tabla is None: return

    try:
        columnas = obtener_columnas_insert(conn, tabla)
        valores = []
        print(f"\n--- Registrando nuevo dato en '{tabla}' ---")
        for col in columnas:
            val = input(f"Ingrese valor para {col}: ")
            valores.append(val)
        
        # Construcción dinámica de la consulta
        columnas_str = ", ".join(columnas)
        placeholders = ", ".join(["?"] * len(valores)) # -> "?, ?, ?"
        
        sql = f"INSERT INTO {tabla} ({columnas_str}) VALUES ({placeholders})"
        
        cursor = conn.cursor()
        cursor.execute(sql, valores)
        conn.commit()
        print(f"¡Registro insertado en '{tabla}' con éxito! (ID: {cursor.lastrowid})")
        
    except sqlite3.Error as e:
        print(f"\nError al registrar: {e}")
        print("Posible Causa: ¿Estás intentando insertar en 'Stock'?")
        print("Recuerda que la tabla 'Stock' tiene una llave foránea que apunta a 'Maquina' (con 'a') y no a 'Maquinas'.")
        conn.rollback() # Revertir cambios si hay error


def actualizar_registro(conn):
    """
    Maneja el flujo para actualizar un registro existente.
    """
    tabla = seleccionar_tabla(conn)
    if tabla is None: return
    
    pk = obtener_pk(conn, tabla)
    if pk is None:
        print(f"Error: La tabla '{tabla}' no tiene llave primaria. No se puede actualizar.")
        return

    try:
        id_val = input(f"\nIngrese el '{pk}' del registro que desea actualizar: ")
        
        # Obtener todas las columnas para elegir cuál actualizar
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({tabla})")
        columnas = [info[1] for info in cursor.fetchall()]
        
        print("\n¿Qué columna desea actualizar?")
        for i, col in enumerate(columnas):
            print(f"[{i+1}] {col}")
            
        op_col = int(input("Elija una columna: "))
        if not (1 <= op_col <= len(columnas)):
            print("Opción no válida.")
            return
            
        col_actualizar = columnas[op_col-1]
        nuevo_valor = input(f"Ingrese el nuevo valor para '{col_actualizar}': ")
        
        # Construcción dinámica
        sql = f"UPDATE {tabla} SET {col_actualizar} = ? WHERE {pk} = ?"
        
        cursor.execute(sql, (nuevo_valor, id_val))
        conn.commit()
        
        if cursor.rowcount == 0:
            print(f"No se encontró ningún registro con {pk} = {id_val}. No se actualizó nada.")
        else:
            print(f"¡Registro actualizado con éxito!")
            
    except sqlite3.Error as e:
        print(f"Error al actualizar: {e}")
        conn.rollback()
    except (ValueError, IndexError):
        print("Entrada no válida.")


def eliminar_registro(conn):
    """
    Maneja el flujo para eliminar un registro.
    """
    tabla = seleccionar_tabla(conn)
    if tabla is None: return

    pk = obtener_pk(conn, tabla)
    if pk is None:
        print(f"Error: La tabla '{tabla}' no tiene llave primaria. No se puede eliminar.")
        return
        
    try:
        id_val = input(f"\nIngrese el '{pk}' del registro que desea ELIMINAR: ")
        
        # --- Confirmación ---
        confirm = input(f"ADVERTENCIA: ¿Está seguro que desea eliminar el registro {pk}={id_val} de la tabla '{tabla}'? Esta acción es irreversible. (s/n): ")
        
        if confirm.lower() != 's':
            print("Operación cancelada.")
            return
            
        # Construcción dinámica
        sql = f"DELETE FROM {tabla} WHERE {pk} = ?"
        
        cursor = conn.cursor()
        cursor.execute(sql, (id_val,))
        conn.commit()
        
        if cursor.rowcount == 0:
            print(f"No se encontró ningún registro con {pk} = {id_val}. No se eliminó nada.")
        else:
            print(f"¡Registro eliminado con éxito!")

    except sqlite3.Error as e:
        print(f"Error al eliminar: {e}")
        conn.rollback()
    except ValueError:
        print("Entrada no válida.")

def consultar_registros(conn):
    """
    Muestra todos los registros de una tabla.
    """
    tabla = seleccionar_tabla(conn)
    if tabla is None: return
    
    try:
        cursor = conn.cursor()
        
        # Obtener nombres de columnas (cabeceras)
        cursor.execute(f"PRAGMA table_info({tabla})")
        cabeceras = [info[1] for info in cursor.fetchall()]
        
        # Obtener todos los datos
        cursor.execute(f"SELECT * FROM {tabla}")
        filas = cursor.fetchall()
        
        print(f"\n--- Mostrando {len(filas)} registros de '{tabla}' ---")
        
        # Imprimir cabeceras
        print(" | ".join(cabeceras))
        print("-" * (sum(len(c) for c in cabeceras) + len(cabeceras) * 3)) # Línea separadora
        
        # Imprimir filas
        if not filas:
            print("(Tabla vacía)")
        else:
            for fila in filas:
                # Convertimos cada item de la fila a string para unirlo
                print(" | ".join(map(str, fila)))
        
        print("-" * (sum(len(c) for c in cabeceras) + len(cabeceras) * 3))

    except sqlite3.Error as e:
        print(f"Error al consultar: {e}")


# --- Menú Principal ---

def main():
    # 1. Conectar a la BD
    conn = conexion_db.crear_conexion()
    if conn is None:
        print("Error crítico: No se pudo conectar a la base de datos.")
        return # Salir del script si no hay conexión

    print("¡Conexión establecida! Bienvenido al Gestor de BD.")

    # 2. Bucle del menú principal
    while True:
        print("\n--- Menú Principal ---")
        print("[1] Registrar nuevo dato")
        print("[2] Actualizar un dato existente")
        print("[3] Eliminar un dato")
        print("[4] Consultar todos los datos de una tabla")
        print("[5] Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            registrar_registro(conn)
        elif opcion == '2':
            actualizar_registro(conn)
        elif opcion == '3':
            eliminar_registro(conn)
        elif opcion == '4':
            consultar_registros(conn)
        elif opcion == '5':
            print("Cerrando conexión. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intente de nuevo.")
            
    # 3. Cerrar conexión al salir
    conn.close()


# --- Punto de entrada del script ---
if __name__ == '__main__':
    main()