## Modelo para manejar unidades de medida

from core.database import db
import pandas as pd

# → Modelo para gestionar unidades de medida
class UnidadMedidaModel:
    def __init__(self):
        self.tabla = 'unidad_medida'
# → Obtiene todas las unidades de medida disponibles.
    def obtener_todas(self):
        try:
            conexion = db.get_connection()
            query = '''
                SELECT id_unidad_medida, nombre_unidad, descripcion
                FROM unidad_medida
                ORDER BY nombre_unidad ASC
            '''
            unidades = pd.read_sql_query(query, conexion)
            conexion.close()
            return unidades
        except Exception as e:
            print(f"Error obteniendo unidades de medida: {e}")
            return pd.DataFrame(columns=['id_unidad_medida', 'nombre_unidad', 'descripcion'])
    
# → Obtiene una unidad específica por su ID.
    def obtener_por_id(self, id_unidad):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id_unidad_medida, nombre_unidad, descripcion FROM unidad_medida WHERE id_unidad_medida = ?",
                [id_unidad]
            )
            row = cursor.fetchone()
            conexion.close()
            
            if row:
                return {
                    'id_unidad_medida': row[0],
                    'nombre_unidad': row[1],
                    'descripcion': row[2]
                }
            return None
        except Exception as e:
            print(f"Error obteniendo unidad {id_unidad}: {e}")
            return None
    
# → Obtiene solo los nombres de las unidades para usar en ComboBox.
    def obtener_nombres(self):
        try:
            df = self.obtener_todas()
            return df['nombre_unidad'].tolist() if not df.empty else []
        except Exception as e:
            print(f"Error obteniendo nombres de unidades: {e}")
            return []
    
# → Crea una nueva unidad de medida.
    def crear(self, nombre, descripcion=''):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO unidad_medida (nombre_unidad, descripcion) VALUES (?, ?)",
                [nombre, descripcion]
            )
            nuevo_id = cursor.lastrowid
            conexion.commit()
            conexion.close()
            return nuevo_id
        except Exception as e:
            print(f"Error creando unidad de medida: {e}")
            return None