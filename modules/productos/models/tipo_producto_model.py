## Modelo para manejar tipos de productos

from core.database import db
import pandas as pd

# → Modelo para gestionar tipos de productos
class TipoProductoModel:
    def __init__(self):
        self.tabla = 'tipo_productos'
    
# → Obtiene todos los tipos de productos disponibles.
    def obtener_todos(self):
        try:
            conexion = db.get_connection()
            query = '''
                SELECT id_tipo_producto, nombre_tipo, descripcion
                FROM tipo_productos
                ORDER BY nombre_tipo ASC
            '''
            tipos = pd.read_sql_query(query, conexion)
            conexion.close()
            return tipos
        except Exception as e:
            print(f"Error obteniendo tipos de productos: {e}")
            return pd.DataFrame(columns=['id_tipo_producto', 'nombre_tipo', 'descripcion'])

# → Obtiene un tipo específico por su ID.
    def obtener_por_id(self, id_tipo):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id_tipo_producto, nombre_tipo, descripcion FROM tipo_productos WHERE id_tipo_producto = ?",
                [id_tipo]
            )
            row = cursor.fetchone()
            conexion.close()
            # if row para evitar error si no existe
            if row:
                return {
                    'id_tipo_producto': row[0],
                    'nombre_tipo': row[1],
                    'descripcion': row[2]
                }
            return None
        except Exception as e:
            print(f"Error obteniendo tipo {id_tipo}: {e}")
            return None
    
# → Obtiene solo los nombres de los tipos para usar en ComboBox.
    def obtener_nombres(self):
        try:
            df = self.obtener_todos()
            return df['nombre_tipo'].tolist() if not df.empty else []
        except Exception as e:
            print(f"Error obteniendo nombres de tipos: {e}")
            return []
    
# → Crea un nuevo tipo de producto.
    def crear(self, nombre, descripcion=''):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO tipo_productos (nombre_tipo, descripcion) VALUES (?, ?)",
                [nombre, descripcion]
            )
            nuevo_id = cursor.lastrowid
            conexion.commit()
            conexion.close()
            return nuevo_id
        except Exception as e:
            print(f"Error creando tipo de producto: {e}")
            return None