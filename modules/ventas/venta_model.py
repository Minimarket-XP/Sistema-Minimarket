## Modelo de Ventas - Sistema Minimarket

import pandas as pd
from core.database import db
from datetime import datetime

class VentaModel:
    def __init__(self):
        pass

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
        try:
            conexion = db.get_connection()
            venta = pd.read_sql_query('''
                SELECT * FROM ventas WHERE id = ?
            ''', conexion, params=[venta_id])

            # Detalles de la venta
            detalles = pd.read_sql_query('''
                SELECT dv.*, p.nombre as producto_nombre 
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                WHERE dv.venta_id = ?
            ''', conexion, params=[venta_id])
            conexion.close()
            return venta, detalles

        except Exception as e:
            print(f"Error al obtener venta: {e}")
            return pd.DataFrame(), pd.DataFrame()

    def obtenerVentaxDia(self, fecha=None):
        if fecha is None:
            fecha = datetime.now().date()

        try:
            conexion = db.get_connection()
            query = '''
                SELECT v.*, COUNT(dv.id) as items_vendidos
                FROM ventas v
                LEFT JOIN detalle_ventas dv ON v.id = dv.venta_id
                WHERE DATE(v.fecha) = ?
                GROUP BY v.id
                ORDER BY v.fecha DESC
            '''
            ventas = pd.read_sql_query(query, conexion, params=[fecha])
            conexion.close()
            return ventas

        except Exception as e:
            print(f"Error al obtener ventas del día: {e}")
            return pd.DataFrame()

    def obtenerResumenDia(self, fecha=None):
        if fecha is None:
            fecha = datetime.now().date()

        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()

            # Total de ventas
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_ventas,
                    COALESCE(SUM(total), 0) as monto_total,
                    COALESCE(AVG(total), 0) as venta_promedio
                FROM ventas 
                WHERE DATE(fecha) = ?
            ''', [fecha])

            resumen = cursor.fetchone()
            conexion.close()

            return {
                'fecha': fecha,
                'total_ventas': resumen[0] if resumen else 0,
                'monto_total': resumen[1] if resumen else 0.0,
                'venta_promedio': resumen[2] if resumen else 0.0
            }

        except Exception as e:
            print(f"Error al obtener resumen: {e}")
            return {
                'fecha': fecha,
                'total_ventas': 0,
                'monto_total': 0.0,
                'venta_promedio': 0.0
            }

    def obtenerProductosMasVendidos(self, limite=10, fecha=None):
        fecha_filtro = ""
        params = [limite]
        if fecha:
            fecha_filtro = "WHERE DATE(v.fecha) = ?"
            params.append(fecha)
        params.append(limite)
        try:
            conexion = db.get_connection()
            query = f'''
                SELECT 
                    p.nombre as producto_nombre,
                    SUM(dv.cantidad) as total_vendido,
                    SUM(dv.subtotal) as ingresos_totales,
                    COUNT(DISTINCT dv.venta_id) as num_ventas
                FROM detalle_ventas dv
                JOIN ventas v ON dv.venta_id = v.id
                JOIN productos p ON dv.producto_id = p.id
                {fecha_filtro}
                GROUP BY dv.producto_id, p.nombre
                ORDER BY total_vendido DESC
                LIMIT ?
            '''

            productos = pd.read_sql_query(query, conexion, params=params)
            conexion.close()
            return productos
        except Exception as e:
            print(f"Error al obtener productos más vendidos: {e}")
            return pd.DataFrame()

    # Alias para compatibilidad con views/ventas.py
    def obtener_resumen_dia(self, fecha=None):
        return self.obtenerResumenDia(fecha)