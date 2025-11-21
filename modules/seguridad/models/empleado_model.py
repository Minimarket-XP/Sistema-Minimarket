## Modelo de Empleados - Sistema Minimarket
## Responsabilidad: Solo acceso a datos (CRUD)

import pandas as pd
from core.database import db

# → Modelo de datos para empleados: Realiza operaciones CRUD en la BD.
class EmpleadoModel:

# → Inserta un nuevo empleado    
    def crear_empleado(self, nombre_empleado, apellido_empleado, id_rol, estado_empleado='activo'):
        conexion = db.get_connection()
        cursor = conexion.cursor()
        
        cursor.execute('''
            INSERT INTO empleado (nombre_empleado, apellido_empleado, estado_empleado, id_rol)
            VALUES (?, ?, ?, ?)
        ''', (nombre_empleado, apellido_empleado, estado_empleado, id_rol))
        
        empleado_id = cursor.lastrowid
        conexion.commit()
        conexion.close()
        return empleado_id
    

# → Obtener al empleado por su rol 
    def obtener_empleado_por_rol(self, nombre_rol):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            cursor.execute('''
                SELECT e.id_empleado, e.nombre_empleado, e.apellido_empleado,
                          e.estado_empleado, e.fecha_contratacion, e.id_rol, r.nombre_rol
                FROM empleado e
                JOIN rol r ON e.id_rol = r.id_rol
                WHERE r.nombre_rol = ?
            ''', [nombre_rol])
            
            empleado = cursor.fetchall()
            conexion.close()
            
            if empleado:
                return [{
                    'id_empleado': e[0],
                    'nombre_empleado': e[1],
                    'apellido_empleado': e[2],
                    'estado_empleado': e[3],
                    'fecha_contratacion': e[4],
                    'id_rol': e[5],
                    'nombre_rol': e[6]
                } for e in empleado]
            return None
            
        except Exception as e:
            print(f"Error obteniendo empleado por rol: {e}")
            return None

# → Obtiene un empleado por su ID.
    def obtener_empleado_por_id(self, id_empleado):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            cursor.execute('''
                SELECT e.id_empleado, e.nombre_empleado, e.apellido_empleado, 
                       e.estado_empleado, e.fecha_contratacion, e.id_rol, r.nombre_rol
                FROM empleado e
                JOIN rol r ON e.id_rol = r.id_rol
                WHERE e.id_empleado = ?
            ''', [id_empleado])
            
            empleado = cursor.fetchone()
            conexion.close()
            
            if empleado:
                return {
                    'id_empleado': empleado[0],
                    'nombre_empleado': empleado[1],
                    'apellido_empleado': empleado[2],
                    'estado_empleado': empleado[3],
                    'fecha_contratacion': empleado[4],
                    'id_rol': empleado[5],
                    'nombre_rol': empleado[6]
                }
            return None
            
        except Exception as e:
            print(f"Error obteniendo empleado: {e}")
            return None

# → Obtiene todos los empleados activos.
    def obtener_empleados_activos(self):
        try:
            conexion = db.get_connection()
            empleados = pd.read_sql_query('''
                SELECT e.id_empleado, e.nombre_empleado, e.apellido_empleado, 
                       e.estado_empleado, e.fecha_contratacion, e.id_rol, r.nombre_rol
                FROM empleado e
                JOIN rol r ON e.id_rol = r.id_rol
                WHERE e.estado_empleado = 'activo'
                ORDER BY e.id_empleado ASC
            ''', conexion)
            conexion.close()
            return empleados.to_dict('records')
            
        except Exception as e:
            print(f"Error obteniendo empleados activos: {e}")
            return []
    
# → Obtiene todos los empleados inactivos.
    def obtener_empleados_inactivos(self):
        try:
            conexion = db.get_connection()
            empleados = pd.read_sql_query('''
                SELECT e.id_empleado, e.nombre_empleado, e.apellido_empleado, 
                       e.estado_empleado, e.fecha_contratacion, e.id_rol, r.nombre_rol
                FROM empleado e
                JOIN rol r ON e.id_rol = r.id_rol
                WHERE e.estado_empleado = 'inactivo'
                ORDER BY e.id_empleado ASC
            ''', conexion)
            conexion.close()
            return empleados.to_dict('records')
            
        except Exception as e:
            print(f"Error obteniendo empleados inactivos: {e}")
            return []
    
# → Obtiene todos los empleados (activos e inactivos).
    def obtener_todos_empleados(self):
        try:
            conexion = db.get_connection()
            empleados = pd.read_sql_query('''
                SELECT e.id_empleado, e.nombre_empleado, e.apellido_empleado, 
                       e.estado_empleado, e.fecha_contratacion, e.id_rol, r.nombre_rol
                FROM empleado e
                JOIN rol r ON e.id_rol = r.id_rol
                ORDER BY e.id_empleado ASC
            ''', conexion)
            conexion.close()
            return empleados.to_dict('records')
            
        except Exception as e:
            print(f"Error obteniendo empleados: {e}")
            return []
    
# → Actualiza los datos de un empleado existente.
    def actualizar_empleado(self, id_empleado, nombre_empleado=None, apellido_empleado=None, 
                           id_rol=None, estado_empleado=None):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            updates = []
            params = []
            
            if nombre_empleado is not None:
                updates.append("nombre_empleado = ?")
                params.append(nombre_empleado)
            if apellido_empleado is not None:
                updates.append("apellido_empleado = ?")
                params.append(apellido_empleado)
            if id_rol is not None:
                updates.append("id_rol = ?")
                params.append(id_rol)
            if estado_empleado is not None:
                updates.append("estado_empleado = ?")
                params.append(estado_empleado)
            
            if not updates:
                return True
            
            params.append(id_empleado)
            query = f"UPDATE empleado SET {', '.join(updates)} WHERE id_empleado = ?"
            
            cursor.execute(query, params)
            conexion.commit()
            conexion.close()
            return True
            
        except Exception as e:
            print(f"Error actualizando empleado: {e}")
            return False
    
# → Cambia el estado de un empleado (activo/inactivo).
    def desactivar_empleado(self, id_empleado):
        return self.actualizar_empleado(id_empleado, estado_empleado='inactivo')
    
# → Marca un empleado como activo.
    def activar_empleado(self, id_empleado):
        return self.actualizar_empleado(id_empleado, estado_empleado='activo')
    
# → Elimina permanentemente un empleado.
    def eliminar_empleado(self, id_empleado):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            cursor.execute('DELETE FROM empleado WHERE id_empleado = ?', [id_empleado])
            
            conexion.commit()
            conexion.close()
            return True
            
        except Exception as e:
            print(f"Error eliminando empleado: {e}")
            return False