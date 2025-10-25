## Modelo para manejar los datos de empleados - SQLite

from core.base_model import BaseModel

class EmpleadoModel(BaseModel):
    def __init__(self):
        # Definir columnas de la tabla empleados
        columns = ['id', 'nombre', 'apellido', 'usuario', 'contraseña', 'rol', 'activo']
        super().__init__('empleados', columns)
    
    def validarCredenciales(self, usuario, password):
        try:
            empleados = self.get_all(
                "usuario = ? AND contraseña = ? AND activo = 1",
                (usuario, password)
            )
            return len(empleados) > 0
        except Exception as e:
            print(f"Error validando credenciales: {e}")
            # Credenciales por defecto si hay error
            return usuario == "admin" and password == "admin"
    
    def validar_credenciales(self, usuario, password):
        """Alias para compatibilidad con el sistema de login"""
        return self.validarCredenciales(usuario, password)
    
    def obtenerUsuario(self, usuario):
        try:
            empleados = self.get_all("usuario = ? AND activo = 1", (usuario,))
            return empleados[0] if empleados else None
        except Exception as e:
            print(f"Error obteniendo empleado por usuario: {e}")
            return None
    
    def crear_empleado(self, nombre, apellido, usuario, contraseña, rol='empleado'):
        try:
            # Verificar que el usuario no exista
            if self.obtenerUsuario(usuario):
                raise ValueError(f"El usuario '{usuario}' ya existe")
            
            empleado_data = {
                'nombre': nombre,
                'apellido': apellido,
                'usuario': usuario,
                'contraseña': contraseña,
                'rol': rol,
                'activo': 1
            }
            
            return self.crearRegistro(empleado_data)
        except Exception as e:
            print(f"Error creando empleado: {e}")
            raise
    
    def actualizarEmpleado(self, empleado_id, datos):
        try:
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
    
    def get_by_id(self, empleado_id):
        """Obtener empleado por ID"""
        try:
            return self.obtenerRegistro(empleado_id)
        except Exception as e:
            print(f"Error obteniendo empleado por ID: {e}")
            return None