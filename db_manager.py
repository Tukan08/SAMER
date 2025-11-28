"""
Módulo de gestión de base de datos (Data Access Layer / Business Logic Layer)
Centraliza toda la lógica de acceso a datos y operaciones CRUD
"""

import sqlite3
from sqlite3 import Error
import conexion_db


# ============================================================================
# FUNCIONES DE AUTENTICACIÓN
# ============================================================================

def autenticar_usuario(username, password):
    """
    Autentica un usuario verificando sus credenciales en la base de datos.
    
    Args:
        username (str): Nombre de usuario
        password (str): Contraseña del usuario
    
    Returns:
        tuple: Tupla con el registro del usuario si es válido, None si no se encuentra
        
    Raises:
        sqlite3.Error: Si hay un error de conexión o consulta a la base de datos
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Usuarios WHERE userName = ? AND password = ?",
            (username, password)
        )
        
        user = cursor.fetchone()
        return user
        
    except Error as e:
        raise Error(f"Error al autenticar usuario: {e}")
    
    finally:
        if conn:
            conn.close()


# ============================================================================
# FUNCIONES DE CONSULTA DE DATOS
# ============================================================================

def cargar_datos_tabla(table_name):
    """
    Carga todos los datos de una tabla específica.
    
    Args:
        table_name (str): Nombre de la tabla a consultar
    
    Returns:
        tuple: (filas, nombres_columnas) donde:
            - filas: lista de tuplas con los datos
            - nombres_columnas: lista con los nombres de las columnas
    
    Raises:
        sqlite3.Error: Si hay un error en la consulta
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        
        filas = cursor.fetchall()
        nombres_columnas = [description[0] for description in cursor.description]
        
        return (filas, nombres_columnas)
        
    except Error as e:
        raise Error(f"Error al cargar datos de la tabla '{table_name}': {e}")
    
    finally:
        if conn:
            conn.close()


def obtener_tablas():
    """
    Obtiene una lista de todas las tablas de usuario en la base de datos.
    Excluye las tablas internas de SQLite.
    
    Returns:
        list: Lista con los nombres de las tablas
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        )
        tablas = [tabla[0] for tabla in cursor.fetchall()]
        return tablas
        
    except Error as e:
        raise Error(f"Error al obtener lista de tablas: {e}")
    
    finally:
        if conn:
            conn.close()


def obtener_pk(tabla):
    """
    Encuentra el nombre de la columna que es la Llave Primaria (PK) de una tabla.
    
    Args:
        tabla (str): Nombre de la tabla
    
    Returns:
        str: Nombre de la columna PK, None si no se encuentra
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({tabla})")
        
        for info in cursor.fetchall():
            if info[5] == 1:  # info[5] es la columna 'pk'
                return info[1]  # info[1] es la columna 'name'
        return None
        
    except Error as e:
        raise Error(f"Error al obtener PK de la tabla '{tabla}': {e}")
    
    finally:
        if conn:
            conn.close()


def obtener_columnas_insert(tabla):
    """
    Obtiene las columnas para un INSERT.
    Omite las llaves primarias que sean AUTOINCREMENT.
    
    Args:
        tabla (str): Nombre de la tabla
    
    Returns:
        list: Lista con los nombres de las columnas para INSERT
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        
        # Obtener el comando SQL con el que se creó la tabla
        cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
            (tabla,)
        )
        schema = cursor.fetchone()[0].upper()
        
        # Obtener la info de las columnas
        cursor.execute(f"PRAGMA table_info({tabla})")
        columnas_info = cursor.fetchall()
        
        columnas_a_pedir = []
        
        for col in columnas_info:
            nombre = col[1]
            es_pk = col[5] == 1
            
            # Si es PK Y tiene AUTOINCREMENT, no la pedimos
            if es_pk and 'AUTOINCREMENT' in schema:
                continue
            
            columnas_a_pedir.append(nombre)
        
        return columnas_a_pedir
        
    except Error as e:
        raise Error(f"Error al obtener columnas de INSERT para '{tabla}': {e}")
    
    finally:
        if conn:
            conn.close()


def obtener_columnas_para_insert(tabla):
    """
    Obtiene las columnas necesarias para un INSERT.
    Excluye las llaves primarias que sean AUTOINCREMENT.
    
    Args:
        tabla (str): Nombre de la tabla
    
    Returns:
        list: Lista con los nombres de las columnas para el formulario
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        
        # Obtener el comando SQL con el que se creó la tabla
        cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
            (tabla,)
        )
        result = cursor.fetchone()
        if not result:
            raise Error(f"Tabla '{tabla}' no encontrada")
        
        schema = result[0].upper()
        
        # Obtener la info de las columnas
        cursor.execute(f"PRAGMA table_info({tabla})")
        columnas_info = cursor.fetchall()
        
        columnas_a_pedir = []
        
        for col in columnas_info:
            nombre = col[1]
            es_pk = col[5] == 1
            
            # Si es PK Y tiene AUTOINCREMENT, no la pedimos
            if es_pk and 'AUTOINCREMENT' in schema:
                continue
            
            columnas_a_pedir.append(nombre)
        
        return columnas_a_pedir
        
    except Error as e:
        raise Error(f"Error al obtener columnas de INSERT para '{tabla}': {e}")
    
    finally:
        if conn:
            conn.close()


# ============================================================================
# FUNCIONES CRUD
# ============================================================================

def registrar_registro(tabla, valores_dict):
    """
    Inserta un nuevo registro en una tabla.
    
    Args:
        tabla (str): Nombre de la tabla
        valores_dict (dict): Diccionario {nombre_columna: valor}
    
    Returns:
        int: ID del registro insertado (lastrowid)
    
    Raises:
        sqlite3.Error: Si hay un error en la inserción
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        
        # Construcción dinámica de la consulta
        columnas = list(valores_dict.keys())
        valores = list(valores_dict.values())
        
        columnas_str = ", ".join(columnas)
        placeholders = ", ".join(["?"] * len(valores))
        
        sql = f"INSERT INTO {tabla} ({columnas_str}) VALUES ({placeholders})"
        
        cursor.execute(sql, valores)
        conn.commit()
        
        return cursor.lastrowid
        
    except Error as e:
        if conn:
            conn.rollback()
        raise Error(f"Error al registrar en '{tabla}': {e}")
    
    finally:
        if conn:
            conn.close()


def actualizar_registro(tabla, pk_nombre, pk_valor, columna, nuevo_valor):
    """
    Actualiza un registro existente (una sola columna).
    
    Args:
        tabla (str): Nombre de la tabla
        pk_nombre (str): Nombre de la columna PK
        pk_valor: Valor de la PK del registro a actualizar
        columna (str): Nombre de la columna a actualizar
        nuevo_valor: Nuevo valor para la columna
    
    Returns:
        int: Número de filas afectadas
    
    Raises:
        sqlite3.Error: Si hay un error en la actualización
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        
        sql = f"UPDATE {tabla} SET {columna} = ? WHERE {pk_nombre} = ?"
        cursor.execute(sql, (nuevo_valor, pk_valor))
        conn.commit()
        
        return cursor.rowcount
        
    except Error as e:
        if conn:
            conn.rollback()
        raise Error(f"Error al actualizar '{tabla}': {e}")
    
    finally:
        if conn:
            conn.close()


def actualizar_registro_completo(tabla, pk_nombre, pk_valor, datos_actualizados):
    """
    Actualiza múltiples columnas de un registro existente.
    
    Args:
        tabla (str): Nombre de la tabla
        pk_nombre (str): Nombre de la columna PK
        pk_valor: Valor de la PK del registro a actualizar
        datos_actualizados (dict): Diccionario {nombre_columna: nuevo_valor}
                                   No debe incluir la columna PK
    
    Returns:
        int: Número de filas afectadas
    
    Raises:
        sqlite3.Error: Si hay un error en la actualización
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        
        # Construir la consulta dinámicamente
        columnas = list(datos_actualizados.keys())
        valores = list(datos_actualizados.values())
        
        # Crear el SET clause: "columna1 = ?, columna2 = ?, ..."
        set_clause = ", ".join([f"{col} = ?" for col in columnas])
        
        # Agregar el valor de la PK al final
        valores.append(pk_valor)
        
        sql = f"UPDATE {tabla} SET {set_clause} WHERE {pk_nombre} = ?"
        cursor.execute(sql, valores)
        conn.commit()
        
        return cursor.rowcount
        
    except Error as e:
        if conn:
            conn.rollback()
        raise Error(f"Error al actualizar registro en '{tabla}': {e}")
    
    finally:
        if conn:
            conn.close()


def eliminar_registro(tabla, pk_nombre, pk_valor):
    """
    Elimina un registro de una tabla.
    
    Args:
        tabla (str): Nombre de la tabla
        pk_nombre (str): Nombre de la columna PK
        pk_valor: Valor de la PK del registro a eliminar
    
    Returns:
        int: Número de filas eliminadas
    
    Raises:
        sqlite3.Error: Si hay un error en la eliminación
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        
        sql = f"DELETE FROM {tabla} WHERE {pk_nombre} = ?"
        cursor.execute(sql, (pk_valor,))
        conn.commit()
        
        return cursor.rowcount
        
    except Error as e:
        if conn:
            conn.rollback()
        raise Error(f"Error al eliminar de '{tabla}': {e}")
    
    finally:
        if conn:
            conn.close()


def consultar_registros(tabla):
    """
    Consulta todos los registros de una tabla con sus cabeceras.
    (Alias de cargar_datos_tabla para mantener compatibilidad)
    
    Args:
        tabla (str): Nombre de la tabla
    
    Returns:
        tuple: (filas, cabeceras)
    """
    return cargar_datos_tabla(tabla)


def insertar_registro(tabla, datos_dict):
    """
    Inserta un nuevo registro en una tabla de forma dinámica.
    
    Args:
        tabla (str): Nombre de la tabla
        datos_dict (dict): Diccionario {nombre_columna: valor}
    
    Returns:
        int: ID del registro insertado (lastrowid)
    
    Raises:
        sqlite3.Error: Si hay un error en la inserción
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        
        # Construcción dinámica de la consulta
        columnas = list(datos_dict.keys())
        valores = list(datos_dict.values())
        
        columnas_str = ", ".join(columnas)
        placeholders = ", ".join(["?"] * len(valores))
        
        sql = f"INSERT INTO {tabla} ({columnas_str}) VALUES ({placeholders})"
        
        cursor.execute(sql, valores)
        conn.commit()
        
        return cursor.lastrowid
        
    except Error as e:
        if conn:
            conn.rollback()
        raise Error(f"Error al insertar en '{tabla}': {e}")
    
    finally:
        if conn:
            conn.close()


def filtrar_registros(tabla, criterios_dict):
    """
    Filtra registros de una tabla según criterios específicos.
    
    Args:
        tabla (str): Nombre de la tabla
        criterios_dict (dict): Diccionario {nombre_columna: valor_a_buscar}
                              Los valores vacíos o None se ignoran
    
    Returns:
        tuple: (filas, nombres_columnas) donde:
            - filas: lista de tuplas con los datos filtrados
            - nombres_columnas: lista con los nombres de las columnas
    
    Raises:
        sqlite3.Error: Si hay un error en la consulta
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        
        # Construir la consulta base
        sql = f"SELECT * FROM {tabla}"
        
        # Filtrar criterios válidos (no vacíos)
        criterios_validos = {
            col: val for col, val in criterios_dict.items() 
            if val and str(val).strip()
        }
        
        # Si hay criterios válidos, construir la cláusula WHERE
        if criterios_validos:
            condiciones = []
            valores = []
            
            for columna, valor in criterios_validos.items():
                valor_str = str(valor).strip()
                
                # Detectar si es una fecha (formato YYYY-MM-DD o contiene "fecha" en el nombre)
                es_fecha = (
                    'fecha' in columna.lower() or 
                    len(valor_str) == 10 and valor_str.count('-') == 2
                )
                
                if es_fecha:
                    # Para fechas: buscar desde esa fecha en adelante
                    condiciones.append(f"{columna} >= ?")
                    valores.append(valor_str)
                else:
                    # Para texto/otros: búsqueda parcial (LIKE)
                    condiciones.append(f"{columna} LIKE ?")
                    valores.append(f"%{valor_str}%")
            
            # Unir todas las condiciones con AND
            sql += " WHERE " + " AND ".join(condiciones)
            
            cursor.execute(sql, valores)
        else:
            # Si no hay criterios, devolver todos los registros
            cursor.execute(sql)
        
        filas = cursor.fetchall()
        nombres_columnas = [description[0] for description in cursor.description]
        
        return (filas, nombres_columnas)
        
    except Error as e:
        raise Error(f"Error al filtrar datos de la tabla '{tabla}': {e}")
    
    finally:
        if conn:
            conn.close()


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def validar_tabla_existe(tabla):
    """
    Verifica si una tabla existe en la base de datos.
    
    Args:
        tabla (str): Nombre de la tabla
    
    Returns:
        bool: True si la tabla existe, False en caso contrario
    """
    try:
        tablas = obtener_tablas()
        return tabla in tablas
    except Error:
        return False


def obtener_estructura_tabla(tabla):
    """
    Obtiene la estructura completa de una tabla.
    
    Args:
        tabla (str): Nombre de la tabla
    
    Returns:
        list: Lista de tuplas con información de cada columna
              (cid, name, type, notnull, dflt_value, pk)
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        
        cursor = conn.cursor()
        
        sql = f"DELETE FROM {tabla} WHERE {pk_nombre} = ?"
        cursor.execute(sql, (pk_valor,))
        conn.commit()
        
        return cursor.rowcount
        
    except Error as e:
        if conn:
            conn.rollback()
        raise Error(f"Error al eliminar de '{tabla}': {e}")
    
    finally:
        if conn:
            conn.close()


def consultar_registros(tabla):
    """
    Consulta todos los registros de una tabla con sus cabeceras.
    (Alias de cargar_datos_tabla para mantener compatibilidad)
    
    Args:
        tabla (str): Nombre de la tabla
    
    Returns:
        tuple: (filas, cabeceras)
    """
    return cargar_datos_tabla(tabla)


def insertar_registro(tabla, datos_dict):
    """
    Inserta un nuevo registro en una tabla de forma dinámica.
    
    Args:
        tabla (str): Nombre de la tabla
        datos_dict (dict): Diccionario {nombre_columna: valor}
    
    Returns:
        int: ID del registro insertado (lastrowid)
    
    Raises:
        sqlite3.Error: Si hay un error en la inserción
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        
        # Construcción dinámica de la consulta
        columnas = list(datos_dict.keys())
        valores = list(datos_dict.values())
        
        columnas_str = ", ".join(columnas)
        placeholders = ", ".join(["?"] * len(valores))
        
        sql = f"INSERT INTO {tabla} ({columnas_str}) VALUES ({placeholders})"
        
        cursor.execute(sql, valores)
        conn.commit()
        
        return cursor.lastrowid
        
    except Error as e:
        if conn:
            conn.rollback()
        raise Error(f"Error al insertar en '{tabla}': {e}")
    
    finally:
        if conn:
            conn.close()


def filtrar_registros(tabla, criterios_dict):
    """
    Filtra registros de una tabla según criterios específicos.
    
    Args:
        tabla (str): Nombre de la tabla
        criterios_dict (dict): Diccionario {nombre_columna: valor_a_buscar}
                              Los valores vacíos o None se ignoran
    
    Returns:
        tuple: (filas, nombres_columnas) donde:
            - filas: lista de tuplas con los datos filtrados
            - nombres_columnas: lista con los nombres de las columnas
    
    Raises:
        sqlite3.Error: Si hay un error en la consulta
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        
        # Construir la consulta base
        sql = f"SELECT * FROM {tabla}"
        
        # Filtrar criterios válidos (no vacíos)
        criterios_validos = {
            col: val for col, val in criterios_dict.items() 
            if val and str(val).strip()
        }
        
        # Si hay criterios válidos, construir la cláusula WHERE
        if criterios_validos:
            condiciones = []
            valores = []
            
            for columna, valor in criterios_validos.items():
                valor_str = str(valor).strip()
                
                # Detectar si es una fecha (formato YYYY-MM-DD o contiene "fecha" en el nombre)
                es_fecha = (
                    'fecha' in columna.lower() or 
                    len(valor_str) == 10 and valor_str.count('-') == 2
                )
                
                if es_fecha:
                    # Para fechas: buscar desde esa fecha en adelante
                    condiciones.append(f"{columna} >= ?")
                    valores.append(valor_str)
                else:
                    # Para texto/otros: búsqueda parcial (LIKE)
                    condiciones.append(f"{columna} LIKE ?")
                    valores.append(f"%{valor_str}%")
            
            # Unir todas las condiciones con AND
            sql += " WHERE " + " AND ".join(condiciones)
            
            cursor.execute(sql, valores)
        else:
            # Si no hay criterios, devolver todos los registros
            cursor.execute(sql)
        
        filas = cursor.fetchall()
        nombres_columnas = [description[0] for description in cursor.description]
        
        return (filas, nombres_columnas)
        
    except Error as e:
        raise Error(f"Error al filtrar datos de la tabla '{tabla}': {e}")
    
    finally:
        if conn:
            conn.close()


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def validar_tabla_existe(tabla):
    """
    Verifica si una tabla existe en la base de datos.
    
    Args:
        tabla (str): Nombre de la tabla
    
    Returns:
        bool: True si la tabla existe, False en caso contrario
    """
    try:
        tablas = obtener_tablas()
        return tabla in tablas
    except Error:
        return False


def obtener_estructura_tabla(tabla):
    """
    Obtiene la estructura completa de una tabla.
    
    Args:
        tabla (str): Nombre de la tabla
    
    Returns:
        list: Lista de tuplas con información de cada columna
              (cid, name, type, notnull, dflt_value, pk)
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({tabla})")
        
        return cursor.fetchall()
        
    except Error as e:
        raise Error(f"Error al obtener estructura de '{tabla}': {e}")
    
    finally:
        if conn:
            conn.close()


def obtener_maquinas_con_ubicacion():
    """
    Obtiene una lista de máquinas con su ID, nombre y ID de ubicación.
    
    Returns:
        list: Lista de tuplas (idMaquina, nombreMaquina, Ubicacion_idUbicacion)
    """
    conn = None
    try:
        conn = conexion_db.crear_conexion()
        if conn is None:
            raise Error("No se pudo establecer conexión con la base de datos")
        
        cursor = conn.cursor()
        cursor.execute("SELECT idMaquina, nombreMaquina, Ubicacion_idUbicacion FROM Maquinas")
        
        return cursor.fetchall()
        
    except Error as e:
        raise Error(f"Error al obtener máquinas con ubicación: {e}")
    
    finally:
        if conn:
            conn.close()