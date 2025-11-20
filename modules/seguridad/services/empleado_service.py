## Service de Empleados - Sistema Minimarket → Lógica de negocio

import bcrypt
from modules.seguridad.models.empleado_model import EmpleadoModel
from modules.seguridad.models.usuario_model import UsuarioModel
from modules.seguridad.models.rol_model import RolModel

# → Servicio de empleados. Maneja la lógica de negocio de empleados y sus usuarios.
class EmpleadoService:
    def __init__(self):
        self.empleado_model = EmpleadoModel()
        self.usuario_model = UsuarioModel()
        self.rol_model = RolModel()

# → Crea un nuevo empleado junto con su usuario asociado.
    def crear_empleado_con_usuario(self, nombre, apellido, username, password, id_rol):
        try:
            # Validaciones de negocio
            if not nombre or not apellido or not username or not password:
                return False, None, "Todos los campos son obligatorios"
            # Validar longitud mínima de contraseña
            if len(password) < 6:
                return False, None, "La contraseña debe tener al menos 6 caracteres"
            # Verificar que el username no exista
            usuario_existente = self.usuario_model.obtener_usuario_por_username(username)
            if usuario_existente:
                return False, None, f"El usuario '{username}' ya existe"
            # Verificar que el rol existe
            # Solo puede haber 1 supervisor asignado por sistema 
            rol_nombre = self.rol_model.obtener_rol_por_id(id_rol)
            if rol_nombre and rol_nombre['nombre_rol'] == 'supervisor':
                empleado_supervisor = self.empleado_model.obtener_empleado_por_rol('supervisor')
                if empleado_supervisor and len(empleado_supervisor) >= 2: # Permitir hasta 2 supervisores 
                    return False, None, "Ya existe dos supervisores asignados"
            rol = self.rol_model.obtener_rol_por_id(id_rol)
            if not rol:
                return False, None, "El rol especificado no existe"
            # Crear empleado
            empleado_id = self.empleado_model.crear_empleado(nombre, apellido, id_rol)
            
            # Encriptar contraseña
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Crear usuario asociado
            usuario_id = self.usuario_model.crear_usuario(username, password_hash, empleado_id)
            
            return True, empleado_id, f"Empleado '{nombre} {apellido}' creado exitosamente"
            
        except Exception as e:
            return False, None, f"Error al crear empleado: {str(e)}"

# → Actualiza datos de un empleado.
    def actualizar_empleado(self, id_empleado, nombre=None, apellido=None, id_rol=None):
        try:
            # Verificar que el empleado existe
            empleado = self.empleado_model.obtener_empleado_por_id(id_empleado)
            if not empleado:
                return False, "Empleado no encontrado"
            
            # Si se cambia el rol, verificar que existe
            if id_rol and id_rol != empleado['id_rol']:
                rol = self.rol_model.obtener_rol_por_id(id_rol)
                if not rol:
                    return False, "El rol especificado no existe"
            
            # Actualizar empleado
            success = self.empleado_model.actualizar_empleado(
                id_empleado, nombre, apellido, id_rol
            )
            
            if success:
                return True, "Empleado actualizado exitosamente"
            else:
                return False, "Error al actualizar empleado"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
# → Actualiza las credenciales de un usuario asociado a un empleado.
    def actualizar_usuario(self, id_empleado, username=None, password=None):
        try:
            # Obtener usuario del empleado
            usuario = self.usuario_model.obtener_usuario_por_empleado(id_empleado)
            if not usuario:
                return False, "Usuario no encontrado"
            
            # Si se cambia el username, verificar que no exista
            if username and username != usuario['username']:
                usuario_existente = self.usuario_model.obtener_usuario_por_username(username)
                if usuario_existente:
                    return False, f"El usuario '{username}' ya existe"
            
            # Si se cambia la contraseña, validar y encriptar
            password_hash = None
            if password:
                if len(password) < 6:
                    return False, "La contraseña debe tener al menos 6 caracteres"
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Actualizar usuario
            success = self.usuario_model.actualizar_usuario(
                usuario['id_usuario'], username, password_hash
            )
            
            if success:
                return True, "Credenciales actualizadas exitosamente"
            else:
                return False, "Error al actualizar credenciales"
                
        except Exception as e:
            return False, f"Error: {str(e)}"

# → Desactiva un empleado y su usuario (soft delete).
    def desactivar_empleado(self, id_empleado):
        try:
            # Desactivar empleado
            success_emp = self.empleado_model.desactivar_empleado(id_empleado)
            
            # Desactivar usuario asociado
            usuario = self.usuario_model.obtener_usuario_por_empleado(id_empleado)
            success_usr = True
            if usuario:
                success_usr = self.usuario_model.desactivar_usuario(usuario['id_usuario'])
            # success_emp y success_usr deben ser True
            if success_emp and success_usr:
                return True, "Empleado desactivado exitosamente"
            return False, "Error al desactivar empleado"
        except Exception as e:
            return False, f"Error: {str(e)}"

# → Activa un empleado y su usuario.
    def activar_empleado(self, id_empleado):
        try:
            # Activar empleado
            success_emp = self.empleado_model.activar_empleado(id_empleado)
            
            # Activar usuario asociado
            usuario = self.usuario_model.obtener_usuario_por_empleado(id_empleado)
            success_usr = True
            if usuario:
                success_usr = self.usuario_model.activar_usuario(usuario['id_usuario'])
            
            if success_emp and success_usr:
                return True, "Empleado activado exitosamente"
            return False, "Error al activar empleado"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def eliminar_empleado_permanente(self, id_empleado):
        """
        Elimina permanentemente un empleado y su usuario.
        CUIDADO: Esta operación no se puede deshacer.
        """
        try:
            empleado = self.empleado_model.obtener_empleado_por_id(id_empleado)
            if not empleado:
                return False, "Empleado no encontrado"
            
            # Eliminar usuario asociado
            usuario = self.usuario_model.obtener_usuario_por_empleado(id_empleado)
            if usuario:
                self.usuario_model.eliminar_usuario(usuario['id_usuario'])
            
            # Eliminar empleado
            success = self.empleado_model.eliminar_empleado(id_empleado)
            
            if success:
                return True, "Empleado eliminado permanentemente"
            return False, "Error al eliminar empleado"
        except Exception as e:
            return False, f"Error: {str(e)}"

# → Obtiene lista de empleados activos.
    def obtener_empleados_activos(self):
        empleados = self.empleado_model.obtener_empleados_activos()
        
        # Agregar información de usuario a cada empleado
        for emp in empleados:
            usuario = self.usuario_model.obtener_usuario_por_empleado(emp['id_empleado'])
            if usuario:
                emp['username'] = usuario['username']
                emp['ultimo_login'] = usuario['ultimo_login']
            else:
                emp['username'] = None
                emp['ultimo_login'] = None
        
        return empleados

# → Obtiene lista de empleados inactivos.
    def obtener_empleados_inactivos(self):
        empleados = self.empleado_model.obtener_empleados_inactivos()
        
        # Agregar información de usuario a cada empleado
        for emp in empleados:
            usuario = self.usuario_model.obtener_usuario_por_empleado(emp['id_empleado'])
            if usuario:
                emp['username'] = usuario['username']
            else:
                emp['username'] = None
        
        return empleados

# → Obtiene lista de todos los empleados con su información de usuario.
    def obtener_todos_empleados(self):
        from core.database import db
        import pandas as pd
        
        try:
            conexion = db.get_connection()
            empleados = pd.read_sql_query('''
                SELECT e.id_empleado, e.nombre_empleado, e.apellido_empleado, 
                       e.estado_empleado, e.fecha_contratacion, e.id_rol, r.nombre_rol,
                       u.id_usuario, u.username, u.ultimo_login
                FROM empleado e
                JOIN rol r ON e.id_rol = r.id_rol
                LEFT JOIN usuario u ON e.id_empleado = u.id_empleado
                ORDER BY e.estado_empleado DESC, e.nombre_empleado, e.apellido_empleado
            ''', conexion)
            conexion.close()
            return empleados.to_dict('records')
        except Exception as e:
            print(f"Error obteniendo empleados: {e}")
            return []

# → Obtiene un empleado por ID con su información de usuario.
    def obtener_empleado_por_id(self, id_empleado):
        empleado = self.empleado_model.obtener_empleado_por_id(id_empleado)
        # Sirve para agregar info de usuario
        if empleado:
            usuario = self.usuario_model.obtener_usuario_por_empleado(id_empleado)
            if usuario:
                empleado['username'] = usuario['username']
                empleado['id_usuario'] = usuario['id_usuario']
                empleado['estado_usuario'] = usuario['estado_usuario']
            else:
                empleado['username'] = None
                empleado['id_usuario'] = None
        
        return empleado

# → Obtiene lista de roles disponibles.
    def obtener_roles_disponibles(self):
        return self.rol_model.obtener_todos_roles()