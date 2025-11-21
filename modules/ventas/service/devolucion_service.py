## Servicio de Devoluciones - Sistema Minimarket → Lógica de negocio

from modules.ventas.models.devolucion_model import DevolucionModel
from modules.ventas.models.detalle_devolucion_model import DetalleDevolucionModel
from modules.ventas.models.venta_model import VentaModel
from modules.productos.models.producto_model import ProductoModel
from core.database import db
import pandas as pd

class DevolucionService:
    """
    Servicio que maneja la lógica de negocio de devoluciones.
    Coordina entre modelos y maneja transacciones complejas.
    """
    
    def __init__(self):
        self.devolucion_model = DevolucionModel()
        self.detalle_devolucion_model = DetalleDevolucionModel()
        self.venta_model = VentaModel()
        self.producto_model = ProductoModel()
    
    def procesar_devolucion(self, id_venta, productos_devolver, motivo):
        """
        Procesa una devolución completa de manera transaccional.
        
        Args:
            id_venta: ID de la venta a devolver
            productos_devolver: Lista de diccionarios con:
                - id_producto: ID del producto
                - id_detalle_venta: ID del detalle de venta
                - cantidad_devolver: Cantidad a devolver (en kg para productos por peso)
                - precio_unitario: Precio unitario del producto
                - cantidad_original: Cantidad original vendida
            motivo: Motivo de la devolución
        
        Returns:
            Tupla (success, id_devolucion, mensaje)
        """
        conexion = None
        
        try:
            # Validar que la venta existe
            venta_info, _ = self.venta_model.obtener_venta_por_id(id_venta)
            if venta_info.empty:
                return False, None, "La venta no existe"
            
            # Validar que hay productos a devolver
            if not productos_devolver or len(productos_devolver) == 0:
                return False, None, "Debe seleccionar al menos un producto para devolver"
            
            # Validar que tenemos id_detalle_venta válido
            id_detalle_venta_ref = productos_devolver[0].get('id_detalle_venta')
            print(f"DEBUG: id_detalle_venta_ref = {id_detalle_venta_ref}, tipo: {type(id_detalle_venta_ref)}")
            if not id_detalle_venta_ref or id_detalle_venta_ref == 0:
                return False, None, "Error: No se pudo obtener el detalle de venta. Por favor intente nuevamente."
            
            # Calcular monto total de la devolución
            monto_total_devolucion = 0.0
            for producto in productos_devolver:
                cantidad = float(producto['cantidad_devolver'])
                precio = float(producto['precio_unitario'])
                monto_total_devolucion += cantidad * precio
            
            # Determinar tipo de devolución (total o parcial)
            tipo_devolucion = 'parcial'  # Por defecto parcial
            
            # Iniciar transacción
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            # Verificar que el id_detalle_venta existe en la base de datos
            cursor.execute('''
                SELECT id_detalle_venta FROM detalle_venta 
                WHERE id_detalle_venta = ? AND id_venta = ?
            ''', (id_detalle_venta_ref, id_venta))
            
            resultado = cursor.fetchone()
            print(f"DEBUG: Verificación BD - id_detalle_venta: {id_detalle_venta_ref}, id_venta: {id_venta}, encontrado: {resultado}")
            
            if not resultado:
                # Intentar obtener cualquier detalle válido para esta venta
                cursor.execute('''
                    SELECT id_detalle_venta FROM detalle_venta 
                    WHERE id_venta = ?
                    LIMIT 1
                ''', (id_venta,))
                detalle_alternativo = cursor.fetchone()
                
                if detalle_alternativo:
                    print(f"DEBUG: Encontrado detalle alternativo: {detalle_alternativo[0]}")
                    id_detalle_venta_ref = detalle_alternativo[0]
                else:
                    return False, None, f"Error: No se encontraron detalles de venta para la venta {id_venta}"
            
            # Crear la devolución principal
            cursor.execute('''
                INSERT INTO devolucion 
                (id_venta, id_detalle_venta, monto_devolucion, motivo_devolucion, 
                 tipo_devolucion, estado_devolucion)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (id_venta, id_detalle_venta_ref, monto_total_devolucion, 
                  motivo, tipo_devolucion, 'completada'))
            
            id_devolucion = cursor.lastrowid
            
            # Crear los detalles de devolución para cada producto
            for producto in productos_devolver:
                id_producto = producto['id_producto']
                cantidad_devolver = float(producto['cantidad_devolver'])
                precio_unitario = float(producto['precio_unitario'])
                cantidad_original = float(producto['cantidad_original'])
                
                # Validar que la cantidad a devolver no exceda la cantidad vendida
                if cantidad_devolver > cantidad_original:
                    raise Exception(f"La cantidad a devolver ({cantidad_devolver}) "
                                  f"no puede ser mayor a la cantidad vendida ({cantidad_original})")
                
                if cantidad_devolver <= 0:
                    raise Exception("La cantidad a devolver debe ser mayor a 0")
                
                # Calcular monto para este producto
                monto_producto = cantidad_devolver * precio_unitario
                
                # Insertar detalle de devolución
                # NOTA: El trigger 'restaurar_stock_devolucion' actualizará 
                # automáticamente el stock cuando estado_devolucion = 'completada'
                cursor.execute('''
                    INSERT INTO detalle_devolucion 
                    (id_devolucion, id_producto, cantidad_devolucion, 
                     monto_devolucion, estado_devolucion)
                    VALUES (?, ?, ?, ?, ?)
                ''', (id_devolucion, id_producto, cantidad_devolver, 
                      monto_producto, 'completada'))
            
            # Commit de la transacción
            conexion.commit()
            
            return True, id_devolucion, f"Devolución procesada exitosamente. ID: {id_devolucion}"
            
        except Exception as e:
            if conexion:
                conexion.rollback()
            error_msg = str(e)
            print(f"Error al procesar devolución: {error_msg}")
            return False, None, f"Error al procesar devolución: {error_msg}"
        
        finally:
            if conexion:
                conexion.close()
    
    def obtener_devoluciones_historicas(self, limite=100):
        """
        Obtiene el histórico de devoluciones formateado para mostrar en tabla.
        
        Args:
            limite: Número máximo de registros
        
        Returns:
            DataFrame con devoluciones formateadas
        """
        try:
            devoluciones = self.devolucion_model.obtener_devoluciones(limite=limite)
            
            if not devoluciones.empty:
                # Formatear fechas
                devoluciones['fecha_devolucion'] = pd.to_datetime(
                    devoluciones['fecha_devolucion']
                ).dt.strftime('%Y-%m-%d %H:%M')
            
            return devoluciones
            
        except Exception as e:
            print(f"Error al obtener histórico: {e}")
            return pd.DataFrame()
    
    def obtener_productos_venta(self, id_venta):
        """
        Obtiene los productos de una venta específica para mostrar 
        en la interfaz de devolución.
        
        Args:
            id_venta: ID de la venta
        
        Returns:
            Tupla (success, productos_df, mensaje)
        """
        try:
            venta_info, detalles = self.venta_model.obtener_venta_por_id(id_venta)
            
            if venta_info.empty:
                return False, pd.DataFrame(), "Venta no encontrada"
            
            if detalles.empty:
                return False, pd.DataFrame(), "La venta no tiene productos"
            
            # Verificar estado de la venta
            estado_venta = venta_info.iloc[0]['estado_venta']
            if estado_venta == 'cancelado':
                return False, pd.DataFrame(), "No se pueden hacer devoluciones de ventas canceladas"
            
            return True, detalles, "Productos cargados correctamente"
            
        except Exception as e:
            error_msg = f"Error al obtener productos de la venta: {str(e)}"
            print(error_msg)
            return False, pd.DataFrame(), error_msg
    
    def validar_devolucion(self, id_venta, productos_devolver):
        """
        Valida que una devolución sea posible antes de procesarla.
        
        Args:
            id_venta: ID de la venta
            productos_devolver: Lista de productos a devolver
        
        Returns:
            Tupla (es_valido, mensaje)
        """
        try:
            # Verificar que la venta existe
            venta_info, detalles_venta = self.venta_model.obtener_venta_por_id(id_venta)
            if venta_info.empty:
                return False, "La venta no existe"
            
            # Verificar que hay productos
            if not productos_devolver:
                return False, "Debe seleccionar al menos un producto"
            
            # Validar cada producto
            for producto in productos_devolver:
                cantidad_devolver = float(producto.get('cantidad_devolver', 0))
                cantidad_original = float(producto.get('cantidad_original', 0))
                
                if cantidad_devolver <= 0:
                    return False, "Las cantidades a devolver deben ser mayores a 0"
                
                if cantidad_devolver > cantidad_original:
                    nombre = producto.get('nombre_producto', 'Producto')
                    return False, f"Cantidad a devolver de '{nombre}' excede la cantidad vendida"
            
            return True, "Validación exitosa"
            
        except Exception as e:
            return False, f"Error en validación: {str(e)}"
