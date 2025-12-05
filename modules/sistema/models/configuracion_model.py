## Modelo para gestión de configuraciones del sistema

from core.database import Database

class ConfiguracionModel:
    def __init__(self):
        self.db = Database()

    def obtener_configuracion(self, clave):
        """Obtiene el valor de una configuración específica"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT valor FROM configuracion WHERE clave = ?
            ''', (clave,))
            resultado = cursor.fetchone()
            conn.close()
            return resultado[0] if resultado else None
        except Exception as e:
            print(f"Error al obtener configuración {clave}: {e}")
            return None

    def obtener_todas_configuraciones(self):
        """Obtiene todas las configuraciones del sistema"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT clave, valor, descripcion, fecha_actualizacion 
                FROM configuracion
                ORDER BY clave
            ''')
            configuraciones = cursor.fetchall()
            conn.close()

            return [{
                'clave': config[0],
                'valor': config[1],
                'descripcion': config[2],
                'fecha_actualizacion': config[3]
            } for config in configuraciones]
        except Exception as e:
            print(f"Error al obtener configuraciones: {e}")
            return []

    def actualizar_configuracion(self, clave, valor):
        """Actualiza el valor de una configuración"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE configuracion 
                SET valor = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE clave = ?
            ''', (valor, clave))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al actualizar configuración {clave}: {e}")
            return False

    def crear_configuracion(self, clave, valor, descripcion):
        """Crea una nueva configuración"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO configuracion (clave, valor, descripcion)
                VALUES (?, ?, ?)
            ''', (clave, valor, descripcion))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al crear configuración {clave}: {e}")
            return False

    def obtener_configuraciones_agrupadas(self):
        """Obtiene las configuraciones agrupadas por categoría"""
        configs = self.obtener_todas_configuraciones()

        grupos = {
            'Datos de la Empresa': [],
            'Configuración de Ventas': [],
            'Configuración de Inventario': [],
            'Configuración de Sistema': [],
            'Otras': []
        }

        for config in configs:
            clave = config['clave']
            if clave in ['nombre_empresa', 'ruc_empresa', 'direccion_empresa', 'telefono_empresa', 'email_empresa']:
                grupos['Datos de la Empresa'].append(config)
            elif clave in ['igv', 'moneda', 'serie_boleta', 'serie_factura']:
                grupos['Configuración de Ventas'].append(config)
            elif clave in ['stock_minimo_global', 'dias_alerta_vencimiento']:
                grupos['Configuración de Inventario'].append(config)
            elif clave in ['ruta_backups', 'dias_retencion_auditoria', 'tiempo_sesion']:
                grupos['Configuración de Sistema'].append(config)
            else:
                grupos['Otras'].append(config)

        return grupos

