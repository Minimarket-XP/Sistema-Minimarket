## Modelo de Devoluciones - Sistema Minimarket → Solo acceso a datos (CRUD)

import pandas as pd
from core.database import db

class DevolucionModel:
    """Modelo de datos para devoluciones: Realiza operaciones CRUD en la BD."""
    
    def crear_devolucion(self, id_venta, id_detalle_venta, monto_devolucion, 
                        motivo, tipo_devolucion='parcial', estado='completada'):
        """
        Crea un nuevo registro de devolución.
        
        Args:
            id_venta: ID de la venta relacionada
            id_detalle_venta: ID del detalle de venta
            monto_devolucion: Monto total de la devolución
            motivo: Motivo de la devolución
            tipo_devolucion: 'total' o 'parcial'
            estado: Estado de la devolución (por defecto 'completada')
        
        Returns:
            ID de la devolución creada
        """
        conexion = db.get_connection()
        cursor = conexion.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO devolucion 
                (id_venta, id_detalle_venta, monto_devolucion, motivo_devolucion, 
                 tipo_devolucion, estado_devolucion)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (id_venta, id_detalle_venta, monto_devolucion, motivo, 
                  tipo_devolucion, estado))
            
            id_devolucion = cursor.lastrowid
            conexion.commit()
            return id_devolucion
            
        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al crear devolución: {e}")
        finally:
            conexion.close()
    
    def obtener_devoluciones(self, limite=100, offset=0):
        """
        Obtiene todas las devoluciones registradas.
        
        Args:
            limite: Número máximo de registros a retornar
            offset: Número de registros a saltar
        
        Returns:
            DataFrame con las devoluciones
        """
        try:
            conexion = db.get_connection()
            query = '''
                SELECT 
                    d.id_devolucion,
                    d.id_venta,
                    d.fecha_devolucion,
                    d.motivo_devolucion,
                    d.monto_devolucion,
                    d.tipo_devolucion,
                    d.estado_devolucion,
                    v.total_venta,
                    e.nombre_empleado || ' ' || e.apellido_empleado as empleado
                FROM devolucion d
                JOIN ventas v ON d.id_venta = v.id_venta
                JOIN empleado e ON v.id_empleado = e.id_empleado
                ORDER BY d.fecha_devolucion DESC
                LIMIT ? OFFSET ?
            '''
            
            devoluciones = pd.read_sql_query(query, conexion, params=[limite, offset])
            conexion.close()
            return devoluciones
            
        except Exception as e:
            print(f"Error al obtener devoluciones: {e}")
            return pd.DataFrame()
    
    def obtener_devolucion_por_id(self, id_devolucion):
        """
        Obtiene los detalles de una devolución específica.
        
        Args:
            id_devolucion: ID de la devolución
        
        Returns:
            Tupla (info_devolucion, detalles_productos)
        """
        try:
            conexion = db.get_connection()
            
            # Información principal de la devolución
            devolucion = pd.read_sql_query('''
                SELECT 
                    d.*,
                    v.id_venta,
                    v.fecha_venta,
                    v.total_venta
                FROM devolucion d
                JOIN ventas v ON d.id_venta = v.id_venta
                WHERE d.id_devolucion = ?
            ''', conexion, params=[id_devolucion])
            
            # Detalles de productos devueltos
            detalles = pd.read_sql_query('''
                SELECT 
                    dd.*,
                    p.nombre_producto,
                    p.precio_producto
                FROM detalle_devolucion dd
                JOIN productos p ON dd.id_producto = p.id_producto
                WHERE dd.id_devolucion = ?
            ''', conexion, params=[id_devolucion])
            
            conexion.close()
            return devolucion, detalles
            
        except Exception as e:
            print(f"Error al obtener devolución: {e}")
            return pd.DataFrame(), pd.DataFrame()
    
    def obtener_devoluciones_por_venta(self, id_venta):
        """
        Obtiene todas las devoluciones de una venta específica.
        
        Args:
            id_venta: ID de la venta
        
        Returns:
            DataFrame con las devoluciones de esa venta
        """
        try:
            conexion = db.get_connection()
            query = '''
                SELECT * FROM devolucion 
                WHERE id_venta = ?
                ORDER BY fecha_devolucion DESC
            '''
            
            devoluciones = pd.read_sql_query(query, conexion, params=[id_venta])
            conexion.close()
            return devoluciones
            
        except Exception as e:
            print(f"Error al obtener devoluciones de venta: {e}")
            return pd.DataFrame()
    
    def actualizar_estado_devolucion(self, id_devolucion, nuevo_estado):
        """
        Actualiza el estado de una devolución.
        
        Args:
            id_devolucion: ID de la devolución
            nuevo_estado: Nuevo estado ('pendiente', 'completada', 'en proceso')
        
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        conexion = db.get_connection()
        cursor = conexion.cursor()
        
        try:
            cursor.execute('''
                UPDATE devolucion 
                SET estado_devolucion = ?
                WHERE id_devolucion = ?
            ''', (nuevo_estado, id_devolucion))
            
            conexion.commit()
            return True
            
        except Exception as e:
            conexion.rollback()
            print(f"Error al actualizar estado de devolución: {e}")
            return False
        finally:
            conexion.close()
