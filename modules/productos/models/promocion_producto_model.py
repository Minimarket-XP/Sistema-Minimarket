from core.database import db


class PromocionProductoModel:
    def __init__(self):
        pass

    def obtener_por_producto(self, id_producto):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT pp.id_promocion, pp.descuento_aplicado, p.descuento
            FROM promocion_producto pp
            JOIN promocion p ON p.id_promocion = pp.id_promocion
            WHERE pp.id_producto = ? AND p.estado_promocion = 'activa' AND datetime(p.fecha_inicio) <= datetime('now') AND datetime(p.fecha_fin) >= datetime('now')
        ''', (id_producto,))
        rows = cur.fetchall()
        conn.close()
        results = []
        for r in rows:
            results.append({'id_promocion': r[0], 'descuento_aplicado': float(r[1]), 'descuento_promocion': float(r[2])})
        return results

    def eliminar_asignacion(self, id_promocion, id_producto):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM promocion_producto WHERE id_promocion = ? AND id_producto = ?', (id_promocion, id_producto))
        conn.commit()
        conn.close()
        return True
