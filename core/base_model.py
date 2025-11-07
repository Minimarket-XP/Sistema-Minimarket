## Modelo base con funciones CRUD para SQLite

import sqlite3
from datetime import datetime
from core.database import db

class BaseModel:  # Clase base para modelos CRUD
    def __init__(self, table_name, columns):
        self.table_name = table_name
        self.columns = columns

    def get_all(self, where_clause=None, params=None):
        query = f"SELECT * FROM {self.table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"

        conn = db.get_connection()
        conn.row_factory = sqlite3.Row  # → Para acceder por nombre de columna
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        rows = cursor.fetchall()
        conn.close()

        # Convertir a lista de diccionarios
        return [dict(row) for row in rows]

    def obtenerRegistro(self, record_id, id_column='id'):
        query = f"SELECT * FROM {self.table_name} WHERE {id_column} = ?"

        conn = db.get_connection()              # → Conectarse con la Base de Datos
        conn.row_factory = sqlite3.Row          # → Conexión que permite acceder a las columnas por nombre
        cursor = conn.cursor()                  # → Permite ejecutar comando SQL
        cursor.execute(query, (record_id,))     # → Ejecuta una consulta SQL (parametros necesarios) previene inyecciones
        row = cursor.fetchone()                 # → Recupera la primera fila de resultados arrojada
        conn.close()                            # → Cierra la conexión

        return dict(row) if row else None       # → Devuelve fila como diccionario.

    def crearRegistro(self, data):
        # Filtrar datos por columnas
        valid_data = {k: v for k, v in data.items() if k in self.columns}

        if not valid_data: # → verifica si hay datos
            raise ValueError("No hay datos válidos para insertar")

        columns = ', '.join(valid_data.keys())              # → Crea texto de columnas
        placeholders = ', '.join(['?' for _ in valid_data]) # → Crea texto de parametros
        values = list(valid_data.values())                  # → Obtiene lista de valores
        # → Construye la consulta SQL
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"

        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        last_id = cursor.lastrowid      # → Obtiene el último ID insertado
        conn.commit()
        conn.close()

        return last_id

    def actualizarRegistroID(self, record_id, data, id_column='id', cursor = None):
        conexion_Local = cursor is None # → Determina si se gestiona localmente
        # Obtener la conexión y el cursor
        conn = db.get_connection() if conexion_Local else cursor.connection
        # Usar el cursor pasado o crear uno nuevo
        current_cursor = conn.cursor() if conexion_Local else cursor
        # Filtrar solo las columnas válidas
        valid_data = {k: v for k, v in data.items() if k in self.columns and k != id_column}

        if not valid_data:
            return False

        # Procesar valores para manejar caracteres especiales
        processed_data = {}
        for k, v in valid_data.items():
            # Si es bytes (como contraseñas encriptadas con bcrypt), mantenerlo tal cual
            if isinstance(v, bytes):
                processed_data[k] = v
            elif isinstance(v, str):
                import unicodedata
                try:
                    normalized_value = unicodedata.normalize('NFC', v)
                    processed_data[k] = normalized_value
                except (UnicodeError, UnicodeEncodeError):
                    processed_data[k] = v
            else:
                processed_data[k] = v

        if 'fecha_actualizacion' in self.columns:
            processed_data['fecha_actualizacion'] = datetime.now().isoformat()

        set_clause = ', '.join([f"{k} = ?" for k in processed_data.keys()])
        values = list(processed_data.values()) + [record_id]
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {id_column} = ?"

        try:
            current_cursor.execute(query, values)
            rows_affected = current_cursor.rowcount
            if conexion_Local:
                conn.commit()
            return rows_affected > 0
        except Exception as e:
            if conexion_Local:
                conn.rollback()
            raise e
        finally:
            if conexion_Local:
                conn.close()

    def eliminarRegistroID(self, record_id, id_column='id'):
        query = f"DELETE FROM {self.table_name} WHERE {id_column} = ?"

        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (record_id,))

        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()

        return rows_affected > 0

    def buscarRegistro(self, search_term, search_columns):
        if not search_term.strip():
            return self.get_all()

        search_term = f"%{search_term.lower()}%"
        conditions = []
        params = []

        for column in search_columns:
            conditions.append(f"LOWER({column}) LIKE ?")
            params.append(search_term)

        where_clause = " OR ".join(conditions)

        return self.get_all(where_clause, params)

    def contarRegistro(self, where_clause=None, params=None):
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"

        conn = db.get_connection()
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        count = cursor.fetchone()[0]
        conn.close()

        return count

    def vericarRegistroID(self, record_id, id_column='id'):
        return self.contarRegistro(f"{id_column} = ?", (record_id,)) > 0

    def consultaPersonalizada(self, query, params=None):
        conn = db.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]