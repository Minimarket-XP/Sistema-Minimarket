## Service de Ventas - Sistema Minimarket → Lógica de negocio

from datetime import datetime
from modules.ventas.models.venta_model import VentaModel

# → Servicio de ventas. Contiene toda la lógica de negocio.
class VentaService:
    # __init__, venta_model = venta_model() sirve para inicializar el modelo de ventas
    def __init__(self):
        self.venta_model = VentaModel()

# → Genera un ID único para la venta usando timestamp.
    def generar_id_venta(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
        return f"V{timestamp}"

# → Procesa una venta completa con validación y manejo de transacciones. Los triggers de BD se encargan de validar stock y actualizar automáticamente.
# Las promociones se aplican automáticamente desde la BD según configuración previa.
    def procesar_venta_completa(self, carrito, empleado_id=1, metodo_pago="efectivo"):
        from core.database import db
        
        conexion = None
        try:
            # Validaciones de negocio
            if not carrito:
                return False, None, "El carrito está vacío", []

            # Capturar stock inicial para alertas
            from modules.productos.models.producto_model import ProductoModel
            pm_temp = ProductoModel()
            stock_inicial_map = {}
            try:
                for item in carrito:
                    df_temp = pm_temp.obtenerPorId(item['id'])
                    if not df_temp.empty:
                        stock_inicial_map[item['id']] = {
                            'stock': df_temp['Stock'].iloc[0],
                            'minimo': df_temp['Stock Mínimo'].iloc[0],
                            'nombre': df_temp['Nombre'].iloc[0]
                        }
            except Exception as e:
                print(f"Error capturando stock inicial: {e}")

            # Generar ID y calcular totales
            venta_id = self.generar_id_venta()
            fecha_hora = datetime.now()
            total = sum(item['total'] for item in carrito)

            # Iniciar transacción
            conexion = db.get_connection()
            cursor = conexion.cursor()

            # Calcular descuentos y totales a persistir
            descuento_total = sum(float(item.get('descuento') or 0.0) for item in carrito)
            descuento_pct_global = 0.0
            try:
                descuento_pct_global = max(float(item.get('descuento_pct_aplicado') or 0.0) for item in carrito)
            except Exception:
                descuento_pct_global = 0.0

            # 1. Insertar venta principal con descuentos calculados
            cursor.execute('''
                INSERT INTO ventas (id_venta, fecha_venta, id_empleado, total_venta, descuento_venta,
                                    descuento_pct, descuento_tipo, metodo_pago, estado_venta)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (venta_id, fecha_hora, empleado_id, total, round(descuento_total,2), descuento_pct_global, "promocion", metodo_pago, 'completado'))

            # 2. Insertar detalles de venta
            # Los triggers automáticamente:
            # - Validan stock suficiente
            # - Actualizan el stock
            # - Validan precios y cantidades positivas
            # Las promociones activas se aplican desde la BD
            for item in carrito:
                # Persistir detalle: guardar subtotal antes de descuento (base_total), descuento_aplicado y id_promocion si existe
                subtotal_detalle = float(item.get('base_total', item.get('precio',0) * item.get('cantidad',0)))
                descuento_aplicado = float(item.get('descuento') or 0.0)
                id_prom = item.get('id_promocion') if item.get('id_promocion') else None
                cursor.execute('''
                    INSERT INTO detalle_venta 
                    (id_venta, id_producto, cantidad_detalle, precio_unitario_detalle, subtotal_detalle, descuento_aplicado, id_promocion)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (venta_id, item['id'], item['cantidad'],
                      item['precio'], subtotal_detalle, descuento_aplicado, id_prom))

            conexion.commit()
            conexion.close()

            # Verificar alertas de stock (Después de commit para ver stock actualizado)
            from modules.productos.models.producto_model import ProductoModel
            from modules.productos.service.alertas_service import AlertasService
            
            alertas = []
            try:
                producto_model = ProductoModel()
                alertas_service = AlertasService()
                
                for item in carrito:
                    id_prod = item['id']
                    # Verificar si tenemos datos iniciales para comparar
                    if id_prod in stock_inicial_map:
                        df_nuevo = producto_model.obtenerPorId(id_prod)
                        if not df_nuevo.empty:
                            stock_nuevo = df_nuevo['Stock'].iloc[0]
                            datos_ini = stock_inicial_map[id_prod]
                            
                            if alertas_service.verificar_cambio_stock(datos_ini['stock'], stock_nuevo, datos_ini['minimo']):
                                alertas.append(f"⚠️ ALERTA: El stock de '{datos_ini['nombre']}' ha bajado del mínimo ({datos_ini['minimo']}). Stock actual: {stock_nuevo}")
            except Exception as e:
                print(f"Error verificando alertas: {e}")

            return True, venta_id, f"Venta {venta_id} procesada exitosamente", alertas

        except Exception as e:
            if conexion:
                conexion.rollback()
                conexion.close()

            # Interpretar errores de los triggers
            error_msg = str(e)
            if 'Stock insuficiente' in error_msg:
                return False, None, "Error: Stock insuficiente para uno o más productos", []
            elif 'precio unitario' in error_msg.lower():
                return False, None, "Error: El precio debe ser mayor a 0", []
            elif 'cantidad debe ser mayor' in error_msg.lower():
                return False, None, "Error: La cantidad debe ser mayor a 0", []
            else:
                return False, None, f"Error al procesar venta: {error_msg}", []

# → Obtiene información completa de una venta.
    def obtener_venta(self, venta_id):
        return self.venta_model.obtener_venta_por_id(venta_id)

# → Obtiene todas las ventas de una fecha específica (hoy por defecto).
    def obtener_ventas_del_dia(self, fecha=None):
        if fecha is None:
            fecha = datetime.now().date()
        # Convertir fecha a string formato YYYY-MM-DD para SQLite
        fecha_str = fecha.strftime('%Y-%m-%d') if hasattr(fecha, 'strftime') else str(fecha)
        return self.venta_model.obtener_ventas_por_fecha(fecha_str)

# → Genera resumen estadístico de ventas del día.
    def generar_resumen_dia(self, fecha=None):
        if fecha is None:
            fecha = datetime.now().date()
        
        # Convertir fecha a string formato YYYY-MM-DD para SQLite
        fecha_str = fecha.strftime('%Y-%m-%d') if hasattr(fecha, 'strftime') else str(fecha)
        estadisticas = self.venta_model.obtener_estadisticas_fecha(fecha_str)
        estadisticas['fecha'] = fecha
        return estadisticas

# → Obtiene reporte de productos más vendidos.
    def obtener_productos_mas_vendidos(self, limite=10, fecha=None):
        return self.venta_model.obtener_productos_mas_vendidos(limite, fecha)

# → Calcula totales del carrito para mostrar en UI.
    def calcular_totales_carrito(self, carrito):
        if not carrito:
            return {
                'subtotal': 0.0,
                'total_items': 0,
                'total_productos': 0
            }
        
        return {
            'subtotal': sum(item['total'] for item in carrito),
            'total_items': sum(item['cantidad'] for item in carrito),
            'total_productos': len(carrito)
        }

    # Alias para compatibilidad con código anterior
    def obtener_resumen_dia(self, fecha=None):
        return self.generar_resumen_dia(fecha)