## Modelo de Roles - Sistema Minimarket
## Responsabilidad: Solo acceso a datos (CRUD)

import pandas as pd
from core.database import db

# Modelo de datos para roles → Solo realiza operaciones CRUD en la BD. 
class RolModel:
# Insertar un nuevo rol en la DB
    def crear_rol(self, nombre_rol):
        conexion = db.get_connection()
        cursor = conexion.cursor()
        
        cursor.execute('''
            INSERT INTO rol (nombre_rol)
            VALUES (?)
        ''', [nombre_rol])
        
        rol_id = cursor.lastrowid
        conexion.commit()
        conexion.close()
        return rol_id
    
    def obtener_rol_por_id(self, id_rol):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            cursor.execute('SELECT id_rol, nombre_rol FROM rol WHERE id_rol = ?', [id_rol])
            rol = cursor.fetchone()
            conexion.close()
            
            if rol:
                return {'id_rol': rol[0], 'nombre_rol': rol[1]}
            return None
            
        except Exception as e:
            print(f"Error obteniendo rol: {e}")
            return None

    def obtener_todos_roles(self):
        try:
            conexion = db.get_connection()
            roles = pd.read_sql_query('SELECT id_rol, nombre_rol FROM rol ORDER BY nombre_rol', conexion)
            conexion.close()
            return roles.to_dict('records')
            
        except Exception as e:
            print(f"Error obteniendo roles: {e}")
            return []
    
    def actualizar_rol(self, id_rol, nombre_rol):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            cursor.execute('UPDATE rol SET nombre_rol = ? WHERE id_rol = ?', [nombre_rol, id_rol])
            
            conexion.commit()
            conexion.close()
            return True
            
        except Exception as e:
            print(f"Error actualizando rol: {e}")
            return False
    
    def eliminar_rol(self, id_rol):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            cursor.execute('DELETE FROM rol WHERE id_rol = ?', [id_rol])
            
            conexion.commit()
            conexion.close()
            return True
            
        except Exception as e:
            print(f"Error eliminando rol: {e}")
            return False
