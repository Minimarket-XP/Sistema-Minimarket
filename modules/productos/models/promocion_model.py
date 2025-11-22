from datetime import datetime
from core.database import db


class PromocionModel:
    def __init__(self):
        pass

    def crear(self, nombre, descripcion, descuento_pct, fecha_inicio, fecha_fin, estado='inactiva'):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO promocion (nombre_promocion, descripcion_promocion, descuento, fecha_inicio, fecha_fin, estado_promocion)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (nombre, descripcion, float(descuento_pct), fecha_inicio, fecha_fin, estado)
        )
        conn.commit()
        last = cur.lastrowid
        conn.close()
        return last

    def obtener_activas(self, fecha=None):
        fecha = fecha or datetime.now()
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT id_promocion, nombre_promocion, descripcion_promocion, descuento, fecha_inicio, fecha_fin, estado_promocion
            FROM promocion
            WHERE estado_promocion = 'activa' AND datetime(fecha_inicio) <= datetime(?) AND datetime(fecha_fin) >= datetime(?)
        ''', (fecha, fecha))
        rows = cur.fetchall()
        conn.close()
        promos = []
        for r in rows:
            promos.append({
                'id_promocion': r[0],
                'nombre': r[1],
                'descripcion': r[2],
                'descuento': float(r[3]),
                'fecha_inicio': r[4],
                'fecha_fin': r[5],
                'estado': r[6]
            })
        return promos

    def obtener_por_id(self, id_promocion):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT id_promocion, nombre_promocion, descripcion_promocion, descuento, fecha_inicio, fecha_fin, estado_promocion FROM promocion WHERE id_promocion = ?', (id_promocion,))
        r = cur.fetchone()
        conn.close()
        if not r:
            return None
        return {
            'id_promocion': r[0],
            'nombre': r[1],
            'descripcion': r[2],
            'descuento': float(r[3]),
            'fecha_inicio': r[4],
            'fecha_fin': r[5],
            'estado': r[6]
        }

    def obtener_todas(self):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT id_promocion, nombre_promocion, descripcion_promocion, descuento, fecha_inicio, fecha_fin, estado_promocion
            FROM promocion
            ORDER BY id_promocion DESC
        ''')
        rows = cur.fetchall()
        conn.close()
        promos = []
        for r in rows:
            promos.append({
                'id_promocion': r[0],
                'nombre': r[1],
                'descripcion': r[2],
                'descuento': float(r[3]),
                'fecha_inicio': r[4],
                'fecha_fin': r[5],
                'estado': r[6]
            })
        return promos

    def actualizar_estado(self, id_promocion, estado):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute('UPDATE promocion SET estado_promocion = ? WHERE id_promocion = ?', (estado, id_promocion))
        conn.commit()
        conn.close()
        return True

    def eliminar(self, id_promocion):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM promocion WHERE id_promocion = ?', (id_promocion,))
        conn.commit()
        conn.close()
        return True

    # Asignaciones
    def asignar_producto(self, id_promocion, id_producto, descuento_aplicado=None):
        conn = db.get_connection()
        cur = conn.cursor()
        descuento_aplicado = float(descuento_aplicado) if descuento_aplicado is not None else 0.0
        cur.execute('''INSERT OR REPLACE INTO promocion_producto (descuento_aplicado, id_promocion, id_producto) VALUES (?, ?, ?)''', (descuento_aplicado, id_promocion, id_producto))
        conn.commit()
        conn.close()
        return True

    def asignar_categoria(self, id_promocion, id_categoria):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute('''INSERT OR REPLACE INTO promocion_categoria (id_promocion, id_categoria) VALUES (?, ?)''', (id_promocion, id_categoria))
        conn.commit()
        conn.close()
        return True
