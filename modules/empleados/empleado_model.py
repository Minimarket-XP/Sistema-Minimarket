## Modelo para manejar los datos de empleados - SQLite

import bcrypt
from core.base_model import BaseModel

class EmpleadoModel(BaseModel):
    def __init__(self):
        # Definir columnas de la tabla empleados
        columns = ['id', 'nombre', 'apellido', 'usuario', 'contraseña', 'rol', 'activo']
        super().__init__('empleados', columns)
    
    def validar_credenciales(self, usuario, password):
        """Valida las credenciales usando bcrypt para comparar contraseñas encriptadas"""
        try:
            # Obtener el empleado por usuario
            empleados = self.get_all("usuario = ? AND activo = 1", (usuario,))
            if not empleados:
                return False
            # Obtener la contraseña encriptada de la base de datos (get_all retorna diccionarios)
            empleado = empleados[0]
            hashed_password = empleado['contraseña']  # Acceder por nombre de columna
            # Si es bytes, usar directamente; si es string, codificar
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode('utf-8')
            
            # Verificar contraseña con bcrypt
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
            
        except Exception as e:
            print(f"Error validando credenciales: {e}")
            return False

    def obtenerUsuario(self, usuario):
        try:
            empleados = self.get_all("usuario = ? AND activo = 1", (usuario,))
            return empleados[0] if empleados else None
        except Exception as e:
            print(f"Error obteniendo empleado por usuario: {e}")
            return None
    
    def crear_empleado(self, nombre, apellido, usuario, contraseña, rol='empleado'):
        """Crea un empleado con contraseña encriptada"""
        try:
            # Verificar que el usuario no exista
            if self.obtenerUsuario(usuario):
                raise ValueError(f"El usuario '{usuario}' ya existe")
            
            # Encriptar la contraseña antes de guardar
            hashed_password = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())
            
            empleado_data = {
                'nombre': nombre,
                'apellido': apellido,
                'usuario': usuario,
                'contraseña': hashed_password,  # Guardar la contraseña encriptada
                'rol': rol,
                'activo': 1
            }
            
            return self.crearRegistro(empleado_data)
        except Exception as e:
            print(f"Error creando empleado: {e}")
            raise
    
    def actualizarEmpleado(self, empleado_id, datos):
        """Actualiza un empleado. Si se actualiza la contraseña, la encripta"""
        try:
            # Si se está actualizando la contraseña, encriptarla
            if 'contraseña' in datos and datos['contraseña']:
                datos['contraseña'] = bcrypt.hashpw(
                    datos['contraseña'].encode('utf-8'), 
                    bcrypt.gensalt()
                )
            
            return self.actualizarRegistroID(empleado_id, datos)
        except Exception as e:
            print(f"Error actualizando empleado: {e}")
            raise
    
    def desactivarEmpleado(self, empleado_id):
        try:
            return self.actualizarRegistroID(empleado_id, {'activo': 0})
        except Exception as e:
            print(f"Error desactivando empleado: {e}")
            return False
    
    def obtenerEmpleadosActivos(self):
        try:
            return self.get_all("activo = 1")
        except Exception as e:
            print(f"Error obteniendo empleados activos: {e}")
            return []
    
    def obtenerEmpleadosInactivos(self):
        try:
            return self.get_all("activo = 0")
        except Exception as e:
            print(f"Error obteniendo empleados inactivos: {e}")
            return []


    def get_by_id(self, empleado_id):
        """Obtener empleado por ID"""
        try:
            return self.obtenerRegistro(empleado_id)
        except Exception as e:
            print(f"Error obteniendo empleado por ID: {e}")
            return None