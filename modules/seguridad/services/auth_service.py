## Service de Autenticación - Sistema Minimarket
## Responsabilidad: Lógica de negocio de autenticación

import bcrypt
from modules.seguridad.models.usuario_model import UsuarioModel

# → Servicio de Autenticación. Se maneja el login y las validaciones de credenciales.
class AuthService:
    def __init__(self):
        self.usuario_model = UsuarioModel()
    
# → Valida las credencias de un usuario
    def validar_credenciales(self, username, password):
        try:
            usuario = self.usuario_model.obtener_usuario_por_username(username)
            if not usuario:
                return False
            # Verificar que usuario y empleado estén activos
            if usuario['estado_usuario'] != 'activo' or usuario['estado_empleado'] != 'activo':
                return False
            # Obtener el hash de la contraseña almacenada
            password_hash = usuario['password_hash']
            # Convertir a bytes si es necesario
            if isinstance(password_hash, str):
                password_hash = password_hash.encode('utf-8')
            
            # Verificar contraseña con bcrypt
            return bcrypt.checkpw(password.encode('utf-8'), password_hash)
            
        except Exception as e:
            print(f"Error validando credenciales: {e}")
            return False

# → Autentica un usuario y devuelve sus datos si es válido.
    def autenticar(self, username, password):
        try:
            if not self.validar_credenciales(username, password):
                return None
            # Obtener datos completos del usuario
            usuario = self.usuario_model.obtener_usuario_por_username(username)
            if not usuario:
                return None
            # Actualizar último login
            self.usuario_model.actualizar_ultimo_login(usuario['id_usuario'])
            # Remover password de los datos
            usuario_safe = {
                'id_usuario': usuario['id_usuario'],
                'username': usuario['username'],
                'id_empleado': usuario['id_empleado'],
                'nombre_empleado': usuario['nombre_empleado'],
                'apellido_empleado': usuario['apellido_empleado'],
                'id_rol': usuario['id_rol'],
                'nombre_rol': usuario['nombre_rol'],
                'estado_usuario': usuario['estado_usuario']
            }
            
            return usuario_safe
            
        except Exception as e:
            print(f"Error autenticando usuario: {e}")
            return None

# → Obtiene información completa del usuario autenticado
    def obtener_usuario_autenticado(self, username):
        try:
            usuario = self.usuario_model.obtener_usuario_por_username(username)
            
            if usuario:
                # Remover password de los datos
                return {
                    'id_usuario': usuario['id_usuario'],
                    'username': usuario['username'],
                    'id_empleado': usuario['id_empleado'],
                    'nombre_empleado': usuario['nombre_empleado'],
                    'apellido_empleado': usuario['apellido_empleado'],
                    'id_rol': usuario['id_rol'],
                    'nombre_rol': usuario['nombre_rol'],
                    'estado_usuario': usuario['estado_usuario'],
                    'estado_empleado': usuario['estado_empleado']
                }
            return None
            
        except Exception as e:
            print(f"Error obteniendo usuario autenticado: {e}")
            return None

# → Cambia la contraseña de un usuario validando la actual.
    def cambiar_contraseña(self, id_usuario, password_actual, password_nueva):
        try:
            # Obtener usuario
            usuario = self.usuario_model.obtener_usuario_por_id(id_usuario)
            if not usuario:
                return False, "Usuario no encontrado"
            
            # Validar contraseña actual
            password_hash = usuario['password_hash']
            if isinstance(password_hash, str):
                password_hash = password_hash.encode('utf-8')
            
            if not bcrypt.checkpw(password_actual.encode('utf-8'), password_hash):
                return False, "Contraseña actual incorrecta"
            
            # Validar nueva contraseña
            if len(password_nueva) < 4:
                return False, "La nueva contraseña debe tener al menos 4 caracteres"
            
            # Encriptar nueva contraseña
            nuevo_hash = bcrypt.hashpw(password_nueva.encode('utf-8'), bcrypt.gensalt())
            
            # Actualizar en BD
            success = self.usuario_model.actualizar_usuario(id_usuario, password_hash=nuevo_hash)
            
            if success:
                return True, "Contraseña actualizada exitosamente"
            else:
                return False, "Error al actualizar contraseña"
                
        except Exception as e:
            return False, f"Error: {str(e)}"

# → Resetea la contraseña de un usuario (solo admin).
    def resetear_contraseña(self, id_usuario, password_nueva):
        try:
            # Validar nueva contraseña
            if len(password_nueva) < 4:
                return False, "La contraseña debe tener al menos 4 caracteres"
            # Encriptar nueva contraseña
            nuevo_hash = bcrypt.hashpw(password_nueva.encode('utf-8'), bcrypt.gensalt())
            # Actualizar en BD
            success = self.usuario_model.actualizar_usuario(id_usuario, password_hash=nuevo_hash)
            if success:
                return True, "Contraseña reseteada exitosamente"
            else:
                return False, "Error al resetear contraseña"
        except Exception as e:
            return False, f"Error: {str(e)}"