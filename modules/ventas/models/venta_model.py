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

<<<<<<< HEAD
    def getConexion(self):
        return db.get_connection()

    def generarIDVenta(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]  # Sin microsegundos completos
        return f"V{timestamp}"

<<<<<<< HEAD
    def procesar_venta(self, carrito: list, empleado="Admin", metodo_pago="efectivo", descuento_total: float = 0.0, descuento_pct: float = 0.0, descuento_tipo: str = ""):
=======
    def procesar_venta(self, carrito: list, empleado="Admin", metodo_pago="efectivo",
        descuento_total: float = 0.0, descuento_pct: float = 0.0, descuento_tipo: str = ""):
>>>>>>> a690a5d (Fix: Significant improvements were made to modules and sharedfolder.)
        """
        Procesa una venta completa. Los triggers de la BD se encargan de:
        - Validar stock disponible
        - Actualizar stock automáticamente
        - Validar precios y cantidades positivas

        Args:
            carrito (list): Lista de productos en el carrito
            empleado (str): Nombre del empleado que procesa la venta
            metodo_pago (str): Método de pago utilizado
            descuento_total (float): Descuento aplicado
            descuento_pct (float): Porcentaje de descuento
            descuento_tipo (str): Tipo de descuento aplicado

        Returns:
            tuple: (success, venta_id, mensaje)
        """
        conexion = None
        try:
            venta_id = self.generarIDVenta()
            fecha_hora = datetime.now()
            total = sum(item['total'] for item in carrito)
            descuento_total = float(descuento_total or 0.0)
<<<<<<< HEAD
<<<<<<< HEAD
            # Asegurar que el total no sea negativo luego de aplicar descuento
=======
            # El total no debe ser negativo luego de aplicar el descuento
>>>>>>> a690a5d (Fix: Significant improvements were made to modules and sharedfolder.)
=======
>>>>>>> 963e400 (Implementación de Triggers para una mejor integración en los files empleados y ventas)
            total_con_descuento = max(0.0, total - descuento_total)

            conexion = db.get_connection()
            cursor = conexion.cursor()

<<<<<<< HEAD
<<<<<<< HEAD
            # Insertar venta principal (usando estructura existente)
            # Insertar venta principal incluyendo campos de descuento (monto, pct y tipo)
            cursor.execute('''
                INSERT INTO ventas (id, fecha, empleado_id, total, descuento, descuento_pct, descuento_tipo, metodo_pago, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (venta_id, fecha_hora, 1, total_con_descuento, descuento_total, float(descuento_pct or 0.0), descuento_tipo or '', metodo_pago, 'completada'))  # empleado_id = 1 por defecto
=======
            # Insertar venta principal incluyendo los campos de descuento
=======
            # Insertar venta principal
>>>>>>> 963e400 (Implementación de Triggers para una mejor integración en los files empleados y ventas)
            cursor.execute('''
                INSERT INTO ventas (id, fecha, empleado_id, total, descuento,
                                    descuento_pct, descuento_tipo, metodo_pago, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (venta_id, fecha_hora, 1, total_con_descuento, descuento_total,
<<<<<<< HEAD
                  float(descuento_pct or 0.0), descuento_tipo or "", metodo_pago, 'completada'))  # empleado_id = 1 por defecto
>>>>>>> a690a5d (Fix: Significant improvements were made to modules and sharedfolder.)

            # Insertar detalles de venta y actualizar stock
            producto_model = ProductoModel()
=======
                  float(descuento_pct or 0.0), descuento_tipo or "", metodo_pago, 'completada'))
>>>>>>> 963e400 (Implementación de Triggers para una mejor integración en los files empleados y ventas)

            # Insertar detalles de venta
            # Los triggers se encargan de:
            # - Validar que hay stock suficiente
            # - Actualizar el stock automáticamente
            # - Validar precios y cantidades positivas
            for item in carrito:
<<<<<<< HEAD
                # Insertar detalle de venta
                # Insertar detalle de venta (incluir descuento por línea si existe)
=======
>>>>>>> 963e400 (Implementación de Triggers para una mejor integración en los files empleados y ventas)
                cursor.execute('''
                    INSERT INTO detalle_ventas 
                    (venta_id, producto_id, cantidad, precio_unitario, subtotal, descuento)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (venta_id, item['id'], item['cantidad'],
<<<<<<< HEAD
<<<<<<< HEAD
                      item['precio'], item['total'], item.get('descuento')))
=======
                      item['precio'], item['total'], item['descuento']))
>>>>>>> a690a5d (Fix: Significant improvements were made to modules and sharedfolder.)
=======
                      item['precio'], item['total'], item.get('descuento', 0)))
>>>>>>> 963e400 (Implementación de Triggers para una mejor integración en los files empleados y ventas)

            conexion.commit()
            conexion.close()
            return True, venta_id, f"Venta {venta_id} procesada exitosamente"

        except Exception as e:
            if conexion:
                conexion.rollback()
                conexion.close()

            # Mensajes de error más descriptivos basados en los triggers
            error_msg = str(e)
            if 'Stock insuficiente' in error_msg:
                return False, None, "Error: Stock insuficiente para uno o más productos"
            elif 'precio unitario' in error_msg:
                return False, None, "Error: El precio debe ser mayor a 0"
            elif 'cantidad debe ser mayor' in error_msg:
                return False, None, "Error: La cantidad debe ser mayor a 0"
            else:
                return False, None, f"Error al procesar venta: {error_msg}"

    def obtenerVenta(self, venta_id): # → Información principal de la venta
=======
# → Obtiene una venta y sus detalles por ID
    def obtener_venta_por_id(self, venta_id):
>>>>>>> 55cce56 (refactoring)
        try:
            conexion = db.get_connection()
            
            # Información principal de la venta
            venta = pd.read_sql_query('''
                SELECT * FROM ventas WHERE id_venta = ?
            ''', conexion, params=[venta_id])

            # Detalles de la venta
            detalles = pd.read_sql_query('''
                SELECT dv.*, p.nombre_producto as producto_nombre 
                FROM detalle_venta dv
                JOIN productos p ON dv.id_producto = p.id_producto
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