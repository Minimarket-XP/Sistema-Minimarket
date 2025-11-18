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
                return False, None, "El carrito está vacío"

            # Generar ID y calcular totales
            venta_id = self.generar_id_venta()
            fecha_hora = datetime.now()
            total = sum(item['total'] for item in carrito)

            # Iniciar transacción
            conexion = db.get_connection()
            cursor = conexion.cursor()

            # 1. Insertar venta principal (sin descuentos manuales, se aplican desde BD)
            cursor.execute('''
                INSERT INTO ventas (id_venta, fecha_venta, id_empleado, total_venta, descuento_venta,
                                    descuento_pct, descuento_tipo, metodo_pago, estado_venta)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (venta_id, fecha_hora, empleado_id, total, 0.0, 0.0, "", metodo_pago, 'completado'))

            # 2. Insertar detalles de venta
            # Los triggers automáticamente:
            # - Validan stock suficiente
            # - Actualizan el stock
            # - Validan precios y cantidades positivas
            # Las promociones activas se aplican desde la BD
            for item in carrito:
                cursor.execute('''
                    INSERT INTO detalle_venta 
                    (id_venta, id_producto, cantidad_detalle, precio_unitario_detalle, subtotal_detalle, descuento_aplicado)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (venta_id, item['id'], item['cantidad'],
                      item['precio'], item['total'], 0.0))

            conexion.commit()
            conexion.close()
            return True, venta_id, f"Venta {venta_id} procesada exitosamente"

        except Exception as e:
            if conexion:
                conexion.rollback()
                conexion.close()

            # Interpretar errores de los triggers
            error_msg = str(e)
            if 'Stock insuficiente' in error_msg:
                return False, None, "Error: Stock insuficiente para uno o más productos"
            elif 'precio unitario' in error_msg.lower():
                return False, None, "Error: El precio debe ser mayor a 0"
            elif 'cantidad debe ser mayor' in error_msg.lower():
                return False, None, "Error: La cantidad debe ser mayor a 0"
            else:
                return False, None, f"Error al procesar venta: {error_msg}"

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
        """Alias para compatibilidad."""
        return self.generar_resumen_dia(fecha)