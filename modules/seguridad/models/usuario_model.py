## Modelo de Usuarios - Sistema Minimarket
## Responsabilidad: Solo acceso a datos (CRUD)

import pandas as pd
from core.database import db

class UsuarioModel:
    """Modelo de datos para usuarios (autenticación). Solo realiza operaciones CRUD en la BD."""
    
    def crear_usuario(self, username, password_hash, id_empleado, estado_usuario='activo'):
        """Inserta un nuevo usuario en la BD. Password ya debe venir encriptado."""
        conexion = db.get_connection()
        cursor = conexion.cursor()
        
        cursor.execute('''
            INSERT INTO usuario (username, password_hash, estado_usuario, id_empleado)
            VALUES (?, ?, ?, ?)
        ''', (username, password_hash, estado_usuario, id_empleado))
        
        usuario_id = cursor.lastrowid
        conexion.commit()
        conexion.close()
        return usuario_id
    
    def obtener_usuario_por_id(self, id_usuario):
        """Obtiene un usuario por su ID."""
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            cursor.execute('''
                SELECT u.id_usuario, u.username, u.password_hash, u.estado_usuario, 
                       u.ultimo_login, u.id_empleado,
                       e.nombre_empleado, e.apellido_empleado, e.id_rol, r.nombre_rol
                FROM usuario u
                JOIN empleado e ON u.id_empleado = e.id_empleado
                JOIN rol r ON e.id_rol = r.id_rol
                WHERE u.id_usuario = ?
            ''', [id_usuario])
            
            usuario = cursor.fetchone()
            conexion.close()
            
            if usuario:
                return {
                    'id_usuario': usuario[0],
                    'username': usuario[1],
                    'password_hash': usuario[2],
                    'estado_usuario': usuario[3],
                    'ultimo_login': usuario[4],
                    'id_empleado': usuario[5],
                    'nombre_empleado': usuario[6],
                    'apellido_empleado': usuario[7],
                    'id_rol': usuario[8],
                    'nombre_rol': usuario[9]
                }
            return None
            
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            return None
    
    def obtener_usuario_por_username(self, username):
        """Obtiene un usuario por su username."""
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            cursor.execute('''
                SELECT u.id_usuario, u.username, u.password_hash, u.estado_usuario, 
                       u.ultimo_login, u.id_empleado,
                       e.nombre_empleado, e.apellido_empleado, e.estado_empleado, e.id_rol, r.nombre_rol
                FROM usuario u
                JOIN empleado e ON u.id_empleado = e.id_empleado
                JOIN rol r ON e.id_rol = r.id_rol
                WHERE u.username = ?
            ''', [username])
            
            usuario = cursor.fetchone()
            conexion.close()
            
            if usuario:
                return {
                    'id_usuario': usuario[0],
                    'username': usuario[1],
                    'password_hash': usuario[2],
                    'estado_usuario': usuario[3],
                    'ultimo_login': usuario[4],
                    'id_empleado': usuario[5],
                    'nombre_empleado': usuario[6],
                    'apellido_empleado': usuario[7],
                    'estado_empleado': usuario[8],
                    'id_rol': usuario[9],
                    'nombre_rol': usuario[10]
                }
            return None
            
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            return None
    
    def obtener_usuario_por_empleado(self, id_empleado):
        """Obtiene un usuario asociado a un empleado."""
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            cursor.execute('''
                SELECT u.id_usuario, u.username, u.estado_usuario, u.ultimo_login
                FROM usuario u
                WHERE u.id_empleado = ?
            ''', [id_empleado])
            
            usuario = cursor.fetchone()
            conexion.close()
            
            if usuario:
                return {
                    'id_usuario': usuario[0],
                    'username': usuario[1],
                    'estado_usuario': usuario[2],
                    'ultimo_login': usuario[3]
                }
            return None
            
        except Exception as e:
            print(f"Error obteniendo usuario por empleado: {e}")
            return None
    
    def obtener_todos_usuarios(self):
        """Obtiene todos los usuarios."""
        try:
            conexion = db.get_connection()
            usuarios = pd.read_sql_query('''
                SELECT u.id_usuario, u.username, u.estado_usuario, u.ultimo_login, 
                       u.id_empleado, e.nombre_empleado, e.apellido_empleado, r.nombre_rol
                FROM usuario u
                JOIN empleado e ON u.id_empleado = e.id_empleado
                JOIN rol r ON e.id_rol = r.id_rol
                ORDER BY e.nombre_empleado, e.apellido_empleado
            ''', conexion)
            conexion.close()
            return usuarios.to_dict('records')
            
        except Exception as e:
            print(f"Error obteniendo usuarios: {e}")
            return []
    
    def actualizar_usuario(self, id_usuario, username=None, password_hash=None, estado_usuario=None):
        """Actualiza datos de un usuario."""
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            updates = []
            params = []
            
            if username is not None:
                updates.append("username = ?")
                params.append(username)
            if password_hash is not None:
                updates.append("password_hash = ?")
                params.append(password_hash)
            if estado_usuario is not None:
                updates.append("estado_usuario = ?")
                params.append(estado_usuario)
            
            if not updates:
                return True
            
            params.append(id_usuario)
            query = f"UPDATE usuario SET {', '.join(updates)} WHERE id_usuario = ?"
            
            cursor.execute(query, params)
            conexion.commit()
            conexion.close()
            return True
            
        except Exception as e:
            print(f"Error actualizando usuario: {e}")
            return False
    
    def actualizar_ultimo_login(self, id_usuario):
        """Actualiza la fecha de último login."""
        from datetime import datetime
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            cursor.execute('''
                UPDATE usuario SET ultimo_login = ? WHERE id_usuario = ?
            ''', [datetime.now(), id_usuario])
            
            conexion.commit()
            conexion.close()
            return True
            
        except Exception as e:
            print(f"Error actualizando último login: {e}")
            return False
    
    def desactivar_usuario(self, id_usuario):
        """Marca un usuario como inactivo."""
        return self.actualizar_usuario(id_usuario, estado_usuario='inactivo')
    
    def activar_usuario(self, id_usuario):
        """Marca un usuario como activo."""
        return self.actualizar_usuario(id_usuario, estado_usuario='activo')
    
    def eliminar_usuario(self, id_usuario):
        """Elimina permanentemente un usuario."""
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            cursor.execute('DELETE FROM usuario WHERE id_usuario = ?', [id_usuario])
            
            conexion.commit()
            conexion.close()
            return True
            
        except Exception as e:
            print(f"Error eliminando usuario: {e}")
            return False
