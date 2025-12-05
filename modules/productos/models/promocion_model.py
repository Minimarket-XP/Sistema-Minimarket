from datetime import datetime
from core.database import db

class PromocionModel:
    def __init__(self):
        pass

    def crear(self, nombre, descripcion, descuento_pct, fecha_inicio, fecha_fin, estado='inactiva'):
        query = '''INSERT INTO promocion (nombre_promocion, descripcion_promocion, descuento, fecha_inicio, fecha_fin, estado_promocion)
                   VALUES (?, ?, ?, ?, ?, ?)'''
        params = (nombre, descripcion, float(descuento_pct), fecha_inicio, fecha_fin, estado)
        # use execute_insert helper to get lastrowid and handle connection lifecycle
        last = db.execute_insert(query, params)
        return last

    def obtener_activas(self, fecha=None):
        # Use view that centralizes the logic for active promotions
        rows = db.fetchall('SELECT id_promocion, nombre, descripcion, descuento, fecha_inicio, fecha_fin, estado FROM view_promociones_activas')
        promos = []
        for r in rows:
            promos.append({
                'id_promocion': r[0],
                'nombre': r[1],
                'descripcion': r[2],
                'descuento': float(r[3]) if r[3] is not None else 0.0,
                'fecha_inicio': r[4],
                'fecha_fin': r[5],
                'estado': r[6]
            })
        return promos

    def obtener_por_id(self, id_promocion):
        r = db.fetchone('SELECT id_promocion, nombre, descripcion, descuento, fecha_inicio, fecha_fin, estado FROM view_promociones WHERE id_promocion = ?', (id_promocion,))
        if not r:
            return None
        return {
            'id_promocion': r[0],
            'nombre': r[1],
            'descripcion': r[2],
            'descuento': float(r[3]) if r[3] is not None else 0.0,
            'fecha_inicio': r[4],
            'fecha_fin': r[5],
            'estado': r[6]
        }

    def obtener_todas(self):
        rows = db.fetchall('SELECT id_promocion, nombre, descripcion, descuento, fecha_inicio, fecha_fin, estado FROM view_promociones ORDER BY id_promocion DESC')
        promos = []
        for r in rows:
            promos.append({
                'id_promocion': r[0],
                'nombre': r[1],
                'descripcion': r[2],
                'descuento': float(r[3]) if r[3] is not None else 0.0,
                'fecha_inicio': r[4],
                'fecha_fin': r[5],
                'estado': r[6]
            })
        return promos

    def actualizar_estado(self, id_promocion, estado):
        db.execute('UPDATE promocion SET estado_promocion = ? WHERE id_promocion = ?', (estado, id_promocion), commit=True)
        return True

    def actualizar(self, id_promocion, nombre=None, descripcion=None, descuento_pct=None, fecha_inicio=None, fecha_fin=None, estado=None):
        """Actualiza los campos de una promoción. Solo los parámetros no-None serán actualizados."""
        updates = []
        params = []
        if nombre is not None:
            updates.append('nombre_promocion = ?')
            params.append(nombre)
        if descripcion is not None:
            updates.append('descripcion_promocion = ?')
            params.append(descripcion)
        if descuento_pct is not None:
            updates.append('descuento = ?')
            params.append(float(descuento_pct))
        if fecha_inicio is not None:
            updates.append('fecha_inicio = ?')
            params.append(fecha_inicio)
        if fecha_fin is not None:
            updates.append('fecha_fin = ?')
            params.append(fecha_fin)
        if estado is not None:
            updates.append('estado_promocion = ?')
            params.append(estado)

        if not updates:
            return False

        params.append(id_promocion)
        sql = f"UPDATE promocion SET {', '.join(updates)} WHERE id_promocion = ?"
        db.execute(sql, tuple(params), commit=True)
        return True

    def eliminar(self, id_promocion):
        db.execute('DELETE FROM promocion WHERE id_promocion = ?', (id_promocion,), commit=True)
        return True

    # Asignaciones
    def asignar_producto(self, id_promocion, id_producto, descuento_aplicado=None):
        descuento_aplicado = float(descuento_aplicado) if descuento_aplicado is not None else 0.0
        db.execute('INSERT OR REPLACE INTO promocion_producto (descuento_aplicado, id_promocion, id_producto) VALUES (?, ?, ?)', (descuento_aplicado, id_promocion, id_producto), commit=True)
        return True

    def asignar_categoria(self, id_promocion, id_categoria):
        db.execute('INSERT OR REPLACE INTO promocion_categoria (id_promocion, id_categoria) VALUES (?, ?)', (id_promocion, id_categoria), commit=True)
        return True

    #FALTA CREAR TRIGGER PARA QUE NO ASIGNE DOS VECES EL MISMO PRODUCTO O CATEGORIA
    def obtener_categorias_asignadas(self, id_promocion):
        """Devuelve las categorías asignadas a una promoción: lista de dicts con id y nombre."""
        sql = '''
            SELECT c.id_categoria_productos, c.nombre_categoria
            FROM promocion_categoria pc
            JOIN categoria_productos c ON c.id_categoria_productos = pc.id_categoria
            WHERE pc.id_promocion = ?
        '''
        rows = db.fetchall(sql, (id_promocion,))
        res = []
        for r in rows:
            res.append({'id_categoria_productos': int(r[0]), 'nombre_categoria': r[1]})
        return res

    def remover_categoria(self, id_promocion, id_categoria):
        """Elimina la asignación de una categoría a una promoción."""
        db.execute('DELETE FROM promocion_categoria WHERE id_promocion = ? AND id_categoria = ?', (id_promocion, id_categoria), commit=True)
        return True