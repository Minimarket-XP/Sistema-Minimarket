from core.database import db

class ComprobantesAPI:
    def _ruc_emisor(self):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT valor FROM configuracion WHERE clave = ?", ('ruc_empresa',))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else ''

    def _siguiente(self, tipo):
        tipo = str(tipo).lower()
        serie = 'B001' if tipo == 'boleta' else 'F001'
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT COALESCE(MAX(CAST(numero_comprobante AS INTEGER)), 0) FROM comprobante WHERE tipo_comprobante = ? AND serie_comprobante = ?",
            (tipo, serie)
        )
        last = cur.fetchone()[0]
        conn.close()
        return serie, int(last) + 1

    def emitir(self, venta_id, tipo, cliente_id):
        tipo_norm = str(tipo).lower()
        serie, numero = self._siguiente(tipo_norm)
        ruc = self._ruc_emisor()
        conn = db.get_connection()
        cur = conn.cursor()

        cur.execute("SELECT total_venta FROM ventas WHERE id_venta = ?", (venta_id,))
        venta_row = cur.fetchone()
        monto_total = float(venta_row[0]) if venta_row else 0.0

        num_doc = None
        nombre_cli = None
        razon_social = None
        direccion = None
        if cliente_id:
            try:
                cur.execute("SELECT tipo_documento, num_documento, nombre, direccion FROM clientes WHERE id = ?", (cliente_id,))
                c = cur.fetchone()
                if c:
                    tipo_doc, num_doc_db, nombre_db, direccion_db = c
                    if tipo_norm == 'boleta':
                        num_doc = num_doc_db
                        nombre_cli = nombre_db
                    else:
                        razon_social = nombre_db
                        direccion = direccion_db
            except Exception:
                pass

        if tipo_norm == 'boleta' and not num_doc:
            num_doc = '00000000'
        if tipo_norm == 'boleta' and not nombre_cli:
            nombre_cli = 'Cliente Genérico'

        cur.execute(
            """
            INSERT INTO comprobante (
                tipo_comprobante, numero_comprobante, serie_comprobante,
                monto_total_comprobante, ruc_emisor, razon_social, direccion_fiscal,
                num_documento, nombre_cliente, xml_path, pdf_path, estado_sunat, id_venta
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tipo_norm, str(numero), serie, monto_total, ruc,
                razon_social, direccion, num_doc, nombre_cli,
                '', '', 'pendiente', venta_id
            )
        )
        cid = cur.lastrowid
        conn.commit()
        conn.close()
        return {'id': cid, 'tipo': tipo_norm.upper(), 'serie': serie, 'numero': numero}