from core.database import db


class PromocionProductoModel:
    def __init__(self):
        pass

    def obtener_por_producto(self, id_producto):
        # Use the active promotions view joined with asignaciones to avoid logic in code
        sql = '''
            SELECT pp.id_promocion, pp.descuento_aplicado, p.descuento
            FROM promocion_producto pp
            JOIN promocion p ON p.id_promocion = pp.id_promocion
            WHERE pp.id_producto = ? AND p.estado_promocion = 'activa' AND datetime(p.fecha_inicio) <= datetime('now') AND datetime(p.fecha_fin) >= datetime('now')
        '''
        rows = db.fetchall(sql, (id_producto,))
        results = []
        for r in rows:
            results.append({'id_promocion': r[0], 'descuento_aplicado': float(r[1]) if r[1] is not None else 0.0, 'descuento_promocion': float(r[2]) if r[2] is not None else 0.0})
        return results

    def eliminar_asignacion(self, id_promocion, id_producto):
        db.execute('DELETE FROM promocion_producto WHERE id_promocion = ? AND id_producto = ?', (id_promocion, id_producto), commit=True)
        return True
