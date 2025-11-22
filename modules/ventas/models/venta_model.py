## Modelo de Ventas - Sistema Minimarket → Solo acceso a datos (CRUD)

import pandas as pd
from core.database import db

# → Modelo de datos para ventas: Realiza operaciones CRUD en la BD.
class VentaModel:
# → Inserta una nueva venta  
    def crear_venta(self, venta_id, fecha, empleado_id, total, descuento, 
                    descuento_pct, descuento_tipo, metodo_pago, estado='completado'):
        conexion = db.get_connection()
        cursor = conexion.cursor()
        
        cursor.execute('''
            INSERT INTO ventas (id_venta, fecha_venta, id_empleado, total_venta, descuento_venta,
                                descuento_pct, descuento_tipo, metodo_pago, estado_venta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (venta_id, fecha, empleado_id, total, descuento,
              descuento_pct, descuento_tipo, metodo_pago, estado))
        
        conexion.commit()
        conexion.close()
    
# → Inserta un nuevo detalle de venta - los triggers de BD validan stock y actualizan automáticamente.    
    def crear_detalle_venta(self, venta_id, producto_id, cantidad, precio_unitario, subtotal, descuento=0):
        conexion = db.get_connection()
        cursor = conexion.cursor()
        
        cursor.execute('''
            INSERT INTO detalle_venta 
            (id_venta, id_producto, cantidad_detalle, precio_unitario_detalle, subtotal_detalle, descuento_aplicado)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (venta_id, producto_id, cantidad, precio_unitario, subtotal, descuento))
        
        conexion.commit()
        conexion.close()

# → Obtiene una venta y sus detalles por ID
    def obtener_venta_por_id(self, venta_id):
        try:
            conexion = db.get_connection()
            
            # Información principal de la venta
            venta = pd.read_sql_query('''
                SELECT * FROM ventas WHERE id_venta = ?
            ''', conexion, params=[venta_id])

            # Detalles de la venta
            detalles = pd.read_sql_query('''
                SELECT dv.id_detalle_venta, dv.id_venta, dv.id_producto, 
                       dv.cantidad_detalle, dv.precio_unitario_detalle, 
                       dv.descuento_aplicado, dv.subtotal_detalle,
                       p.nombre_producto as producto_nombre,
                       um.nombre_unidad
                FROM detalle_venta dv
                JOIN productos p ON dv.id_producto = p.id_producto
                LEFT JOIN unidad_medida um ON p.id_unidad_medida = um.id_unidad_medida
                WHERE dv.id_venta = ?
            ''', conexion, params=[venta_id])
            
            conexion.close()
            return venta, detalles

        except Exception as e:
            print(f"Error al obtener venta: {e}")
            return pd.DataFrame(), pd.DataFrame()

# → Obtiene todas las ventas de una fecha específica.
    def obtener_ventas_por_fecha(self, fecha):
        try:
            conexion = db.get_connection()
            query = '''
                SELECT v.*, COUNT(dv.id_detalle_venta) as items_vendidos
                FROM ventas v
                LEFT JOIN detalle_venta dv ON v.id_venta = dv.id_venta
                WHERE DATE(v.fecha_venta) = ?
                GROUP BY v.id_venta
                ORDER BY v.fecha_venta DESC
            '''
            # pd.read_sql_query para mayor eficiencia con grandes volúmenes de datos
            ventas = pd.read_sql_query(query, conexion, params=[fecha])
            conexion.close()
            return ventas

        except Exception as e:
            print(f"Error al obtener ventas del día: {e}")
            return pd.DataFrame()

# → Obtiene estadísticas agregadas de ventas para una fecha
    def obtener_estadisticas_fecha(self, fecha):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()

            cursor.execute('''
                SELECT 
                    COUNT(*) as total_ventas,
                    COALESCE(SUM(total_venta), 0) as monto_total,
                    COALESCE(AVG(total_venta), 0) as venta_promedio
                FROM ventas 
                WHERE DATE(fecha_venta) = ?
            ''', [fecha])

            resumen = cursor.fetchone()
            conexion.close()

            return {
                'total_ventas': resumen[0] if resumen else 0,
                'monto_total': resumen[1] if resumen else 0.0,
                'venta_promedio': resumen[2] if resumen else 0.0
            }

        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return {
                'total_ventas': 0,
                'monto_total': 0.0,
                'venta_promedio': 0.0
            }

# → Obtiene los productos más vendidos con filtro opcional de fecha.
    def obtener_productos_mas_vendidos(self, limite=10, fecha=None):
        # params para consulta SQL
        fecha_filtro = ""
        params = []
        
        if fecha:
            fecha_filtro = "WHERE DATE(v.fecha_venta) = ?"
            params.append(fecha)
        # append es para agregar elementos a la lista params
        params.append(limite)
        
        try:
            conexion = db.get_connection()
            query = f'''
                SELECT 
                    p.nombre_producto as producto_nombre,
                    SUM(dv.cantidad_detalle) as total_vendido,
                    SUM(dv.subtotal_detalle) as ingresos_totales,
                    COUNT(DISTINCT dv.id_venta) as num_ventas
                FROM detalle_venta dv
                JOIN ventas v ON dv.id_venta = v.id_venta
                JOIN productos p ON dv.id_producto = p.id_producto
                {fecha_filtro}
                GROUP BY dv.id_producto, p.nombre_producto
                ORDER BY total_vendido DESC
                LIMIT ?
            '''

            productos = pd.read_sql_query(query, conexion, params=params)
            conexion.close()
            return productos
            
        except Exception as e:
            print(f"Error al obtener productos más vendidos: {e}")
            return pd.DataFrame()