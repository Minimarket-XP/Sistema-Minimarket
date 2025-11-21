## Modelo para manejar categorías de productos

from core.database import db
import pandas as pd

# → Modelo para gestionar categorías de productos
class CategoriaModel:
    def __init__(self):
        self.tabla = 'categoria_productos'
    
# → Obtiene todas las categorías disponibles.
    def obtener_todas(self):
        try:
            conexion = db.get_connection()
            query = '''
                SELECT id_categoria_productos, nombre_categoria, descripcion
                FROM categoria_productos
                ORDER BY nombre_categoria ASC
            '''
            categorias = pd.read_sql_query(query, conexion)
            conexion.close()
            return categorias
        except Exception as e:
            print(f"Error obteniendo categorías: {e}")
            return pd.DataFrame(columns=['id_categoria_productos', 'nombre_categoria', 'descripcion'])
    
# → Obtiene una categoría específica por su ID.
    def obtener_por_id(self, id_categoria):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id_categoria_productos, nombre_categoria, descripcion FROM categoria_productos WHERE id_categoria_productos = ?",
                [id_categoria]
            )
            row = cursor.fetchone()
            conexion.close()
            
            if row:
                return {
                    'id_categoria_productos': row[0],
                    'nombre_categoria': row[1],
                    'descripcion': row[2]
                }
            return None
        except Exception as e:
            print(f"Error obteniendo categoría {id_categoria}: {e}")
            return None

# → Obtiene solo los nombres de las categorías para usar en ComboBox.
    def obtener_nombres(self):
        try:
            df = self.obtener_todas()
            return df['nombre_categoria'].tolist() if not df.empty else []
        except Exception as e:
            print(f"Error obteniendo nombres de categorías: {e}")
            return []

# → Crea una nueva categoría.    
    def crear(self, nombre, descripcion=''):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO categoria_productos (nombre_categoria, descripcion) VALUES (?, ?)",
                [nombre, descripcion]
            )
            nuevo_id = cursor.lastrowid
            conexion.commit()
            conexion.close()
            return nuevo_id
        except Exception as e:
            print(f"Error creando categoría: {e}")
            return None