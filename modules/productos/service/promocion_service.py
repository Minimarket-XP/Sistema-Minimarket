from core.database import db
from datetime import datetime


class PromocionService:
    """Servicio encargado de determinar descuentos aplicables a un producto.

    Lógica:
    - Busca promociones con estado 'activa' y dentro del rango de fechas.
    - Revisa asignaciones a producto (`promocion_producto`) y a categoría (`promocion_categoria`).
    - Si existen varias promociones aplicables toma el mayor porcentaje.
    - Si en `promocion_producto` existe `descuento_aplicado` > 0, ese valor tiene preferencia.
    """

    def __init__(self):
        pass

    def obtener_descuento_producto(self, id_producto: str) -> float:
        """Retorna el porcentaje de descuento (0-100) aplicable al producto.

        Busca promociones activas y revisa asignaciones. Devuelve 0.0 si no hay promociones.
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = db.get_connection()
        cur = conn.cursor()

        # Obtener categoría del producto
        cur.execute('SELECT id_categoria_productos FROM productos WHERE id_producto = ?', (id_producto,))
        row = cur.fetchone()
        id_categoria = row[0] if row else None

        # Promociones asignadas directamente al producto (pueden tener descuento_aplicado)
        cur.execute('''
            SELECT p.id_promocion, p.descuento, pp.descuento_aplicado
            FROM promocion p
            JOIN promocion_producto pp ON pp.id_promocion = p.id_promocion
            WHERE pp.id_producto = ?
              AND p.estado_promocion = 'activa'
              AND datetime(p.fecha_inicio) <= datetime(?)
              AND datetime(p.fecha_fin) >= datetime(?)
        ''', (id_producto, now, now))
        rows_prod = cur.fetchall()

        # Promociones asignadas a la categoría
        rows_cat = []
        if id_categoria is not None:
            cur.execute('''
                SELECT p.id_promocion, p.descuento
                FROM promocion p
                JOIN promocion_categoria pc ON pc.id_promocion = p.id_promocion
                WHERE pc.id_categoria = ?
                  AND p.estado_promocion = 'activa'
                  AND datetime(p.fecha_inicio) <= datetime(?)
                  AND datetime(p.fecha_fin) >= datetime(?)
            ''', (id_categoria, now, now))
            rows_cat = cur.fetchall()

        conn.close()

        candidatos = []  # lista de tuples (pct, id_promocion)
        # Considerar descuentos por producto (si descuento_aplicado > 0 usarlo, sino usar p.descuento)
        for r in rows_prod:
            id_prom, p_desc, pp_desc = r[0], float(r[1]), float(r[2]) if r[2] is not None else 0.0
            if pp_desc and pp_desc > 0:
                candidatos.append((pp_desc, id_prom))
            else:
                candidatos.append((p_desc, id_prom))

        # Considerar descuentos por categoría
        for r in rows_cat:
            id_prom = r[0]
            p_desc = float(r[1])
            candidatos.append((p_desc, id_prom))

        if not candidatos:
            return 0.0

        # Seleccionar el candidato con mayor porcentaje
        candidatos.sort(key=lambda x: x[0], reverse=True)
        mejor_pct, mejor_id = candidatos[0]
        # Guardar el id de promocion aplicada en la respuesta (si se solicita vía item)
        return mejor_pct

    def aplicar_descuento_a_item(self, item: dict) -> dict:
        """Modifica el `item` del carrito aplicando el porcentaje de promoción si existe.

        Espera que `item` tenga al menos keys: `id`, `precio`, `cantidad`, `base_total` o `total`.
        Retorna el item modificado (mutación in-place también ocurrirá).
        """
        id_producto = str(item.get('id'))
        descuento_pct = self.obtener_descuento_producto(id_producto)
        # recalcular base_total si no existe
        if 'base_total' in item:
            base = float(item['base_total'])
        else:
            base = float(item.get('precio', 0)) * float(item.get('cantidad', 0))
            item['base_total'] = base

        if descuento_pct and descuento_pct > 0:
            descuento_monto = round(base * (descuento_pct / 100.0), 2)
            nuevo_total = round(max(0.0, base - descuento_monto), 2)
            item['descuento'] = descuento_monto
            item['total'] = nuevo_total
            item['descuento_pct_aplicado'] = float(descuento_pct)
            # intentar obtener id_promocion aplicado para rastreo
            try:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                conn = db.get_connection()
                cur = conn.cursor()
                # buscar coincidencias por producto
                cur.execute('''
                    SELECT p.id_promocion, p.descuento, pp.descuento_aplicado
                    FROM promocion p
                    JOIN promocion_producto pp ON pp.id_promocion = p.id_promocion
                    WHERE pp.id_producto = ?
                      AND p.estado_promocion = 'activa'
                      AND datetime(p.fecha_inicio) <= datetime(?)
                      AND datetime(p.fecha_fin) >= datetime(?)
                ''', (id_producto, now, now))
                rows_prod = cur.fetchall()
                id_prom_aplicada = None
                candidatos = []
                for r in rows_prod:
                    id_prom, p_desc, pp_desc = r[0], float(r[1]), float(r[2]) if r[2] is not None else 0.0
                    if pp_desc and pp_desc > 0:
                        candidatos.append((pp_desc, id_prom))
                    else:
                        candidatos.append((p_desc, id_prom))

                # categorias
                cur.execute('SELECT id_categoria_productos FROM productos WHERE id_producto = ?', (id_producto,))
                row = cur.fetchone()
                id_categoria = row[0] if row else None
                if id_categoria is not None:
                    cur.execute('''
                        SELECT p.id_promocion, p.descuento
                        FROM promocion p
                        JOIN promocion_categoria pc ON pc.id_promocion = p.id_promocion
                        WHERE pc.id_categoria = ?
                          AND p.estado_promocion = 'activa'
                          AND datetime(p.fecha_inicio) <= datetime(?)
                          AND datetime(p.fecha_fin) >= datetime(?)
                    ''', (id_categoria, now, now))
                    for r in cur.fetchall():
                        candidatos.append((float(r[1]), r[0]))

                if candidatos:
                    candidatos.sort(key=lambda x: x[0], reverse=True)
                    id_prom_aplicada = candidatos[0][1]
                conn.close()
                item['id_promocion'] = id_prom_aplicada
            except Exception:
                item['id_promocion'] = None
        else:
            item['descuento'] = None
            item['descuento_pct_aplicado'] = 0.0
            item['total'] = round(base, 2)
            item['id_promocion'] = None

        return item
