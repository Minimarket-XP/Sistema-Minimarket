## Modelo de Detalle de Devoluciones - Sistema Minimarket → Solo acceso a datos (CRUD)

import pandas as pd
from core.database import db

class DetalleDevolucionModel:
    """Modelo de datos para detalles de devoluciones: Realiza operaciones CRUD en la BD."""
    
    def crear_detalle_devolucion(self, id_devolucion, id_producto, 
                                cantidad_devolucion, monto_devolucion, 
                                estado='completada'):
        """
        Crea un nuevo detalle de devolución (producto devuelto).
        NOTA: El trigger 'restaurar_stock_devolucion' actualizará el stock automáticamente.
        
        Args:
            id_devolucion: ID de la devolución padre
            id_producto: ID del producto devuelto
            cantidad_devolucion: Cantidad devuelta (en kg para productos por peso)
            monto_devolucion: Monto correspondiente a esta devolución
            estado: Estado del detalle (por defecto 'completada')
        
        Returns:
            ID del detalle de devolución creado
        """
        conexion = db.get_connection()
        cursor = conexion.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO detalle_devolucion 
                (id_devolucion, id_producto, cantidad_devolucion, 
                 monto_devolucion, estado_devolucion)
                VALUES (?, ?, ?, ?, ?)
            ''', (id_devolucion, id_producto, cantidad_devolucion, 
                  monto_devolucion, estado))
            
            id_detalle = cursor.lastrowid
            conexion.commit()
            return id_detalle
            
        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al crear detalle de devolución: {e}")
        finally:
            conexion.close()
    
    def obtener_detalles_por_devolucion(self, id_devolucion):
        """
        Obtiene todos los productos devueltos en una devolución específica.
        
        Args:
            id_devolucion: ID de la devolución
        
        Returns:
            DataFrame con los detalles de productos devueltos
        """
        try:
            conexion = db.get_connection()
            query = '''
                SELECT 
                    dd.id_detalle_devolucion,
                    dd.cantidad_devolucion,
                    dd.monto_devolucion,
                    dd.estado_devolucion,
                    p.id_producto,
                    p.nombre_producto,
                    p.precio_producto,
                    um.nombre_unidad
                FROM detalle_devolucion dd
                JOIN productos p ON dd.id_producto = p.id_producto
                JOIN unidad_medida um ON p.id_unidad_medida = um.id_unidad_medida
                WHERE dd.id_devolucion = ?
                ORDER BY dd.id_detalle_devolucion
            '''
            
            detalles = pd.read_sql_query(query, conexion, params=[id_devolucion])
            conexion.close()
            return detalles
            
        except Exception as e:
            print(f"Error al obtener detalles de devolución: {e}")
            return pd.DataFrame()
    
    def obtener_detalle_por_id(self, id_detalle_devolucion):
        """
        Obtiene un detalle de devolución específico.
        
        Args:
            id_detalle_devolucion: ID del detalle de devolución
        
        Returns:
            DataFrame con el detalle
        """
        try:
            conexion = db.get_connection()
            query = '''
                SELECT 
                    dd.*,
                    p.nombre_producto,
                    p.precio_producto
                FROM detalle_devolucion dd
                JOIN productos p ON dd.id_producto = p.id_producto
                WHERE dd.id_detalle_devolucion = ?
            '''
            
            detalle = pd.read_sql_query(query, conexion, params=[id_detalle_devolucion])
            conexion.close()
            return detalle
            
        except Exception as e:
            print(f"Error al obtener detalle de devolución: {e}")
            return pd.DataFrame()
    
    def actualizar_estado_detalle(self, id_detalle_devolucion, nuevo_estado):
        """
        Actualiza el estado de un detalle de devolución.
        
        Args:
            id_detalle_devolucion: ID del detalle de devolución
            nuevo_estado: Nuevo estado ('pendiente', 'completada', 'en proceso')
        
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        conexion = db.get_connection()
        cursor = conexion.cursor()
        
        try:
            cursor.execute('''
                UPDATE detalle_devolucion 
                SET estado_devolucion = ?
                WHERE id_detalle_devolucion = ?
            ''', (nuevo_estado, id_detalle_devolucion))
            
            conexion.commit()
            return True
            
        except Exception as e:
            conexion.rollback()
            print(f"Error al actualizar estado de detalle: {e}")
            return False
        finally:
            conexion.close()
